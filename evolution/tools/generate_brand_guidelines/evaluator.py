#!/usr/bin/env python3
"""
OpenEvolve Evaluator for generate_brand_guidelines
Generated automatically by LLM-based evaluator generator
"""

import os
import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

# Initialize logger
logger = logging.getLogger(__name__)

def evaluate(program) -> dict:
    # Define metrics at function level to avoid scope issues
    metrics = ["brand_alignment", "clarity", "readability", "engagement", "structure"]
    
    try:
        # Initialize model
        model = ChatOpenAI(model="gpt-4o", temperature=0.2)
        
        # Load training data from same directory
        evaluator_dir = os.path.dirname(os.path.abspath(__file__))
        training_data_path = os.path.join(evaluator_dir, 'training_data.json')
        with open(training_data_path, 'r') as f:
            training_data = json.load(f)
        
        # Import tool dynamically using importlib
        import importlib.util
        import sys
        
        # Temporarily add tool directory to sys.path for imports
        tool_dir = os.path.dirname(program)
        if tool_dir not in sys.path:
            sys.path.insert(0, tool_dir)
            path_added = True
        else:
            path_added = False
            
        try:
            spec = importlib.util.spec_from_file_location("tool", program)
            tool_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tool_module)
        except ImportError as e:
            logger.error(f"Failed to import tool due to missing dependency: {e}")
            return {metric: 0.0 for metric in metrics}
        finally:
            # Clean up sys.path
            if path_added and tool_dir in sys.path:
                sys.path.remove(tool_dir)
        
        # Initialize scores
        total_scores = {metric: 0.0 for metric in metrics}
        num_cases = len(training_data)
        
        # Evaluate each test case
        for case in training_data:
            # Call the tool with input parameters to generate content
            input_params = case['input']
            try:
                # Find and call the main tool function by looking for functions defined in the tool module
                tool_func = None
                import inspect
                
                # First try to find a function that matches the tool name or has _evolve_candidate attribute
                for attr_name in dir(tool_module):
                    attr = getattr(tool_module, attr_name)
                    if (inspect.isfunction(attr) and 
                        attr.__module__ == 'tool' and
                        not attr_name.startswith('_')):
                        # Prefer functions with _evolve_candidate attribute (decorated functions)
                        if hasattr(attr, '_evolve_candidate'):
                            tool_func = attr
                            break
                        # Fallback to any function defined in the tool module
                        elif tool_func is None:
                            tool_func = attr
                
                if tool_func is None:
                    continue
                    
                # Call tool with input parameters - handle different function signatures
                import inspect
                sig = inspect.signature(tool_func)
                filtered_params = {k: v for k, v in input_params.items() if k in sig.parameters}
                result = tool_func(**filtered_params)
                
                # Handle different return types
                if isinstance(result, tuple):
                    generated_content = result[0]  # Take first element if tuple
                else:
                    generated_content = result
            except Exception as e:
                continue
            
            # Create strict evaluation prompt
            prompt = f"Rate this content on {', '.join(metrics)}. Scale 0.0-1.0 where 0.0=poor, 1.0=excellent. Be STRICT - only high quality deserves >0.7. Return JSON: {generated_content}"
            
            # Get LLM response with proper message format
            response = model.invoke([SystemMessage(content=prompt)])
            
            # Parse JSON safely
            try:
                scores = json.loads(response.content)
                for metric in metrics:
                    if metric in scores and 0.0 <= scores[metric] <= 1.0:
                        total_scores[metric] += scores[metric]
            except:
                continue
        
        # Return average scores as dictionary
        return {metric: total / num_cases for metric, total in total_scores.items()}
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return {metric: 0.0 for metric in metrics}