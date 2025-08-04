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

def evaluate(program) -> dict:
    # Define metrics at function level to avoid scope issues
    metrics = ["clarity", "brand_alignment", "actionability", "creativity", "completeness"]
    
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
        spec = importlib.util.spec_from_file_location("tool", program)
        tool_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool_module)
        
        # Initialize scores
        total_scores = {metric: 0.0 for metric in metrics}
        num_cases = len(training_data)
        
        # Evaluate each test case
        for case in training_data:
            # Call the tool with input parameters to generate content
            input_params = case['input']
            try:
                # Find and call the main tool function
                tool_func = None
                for attr_name in dir(tool_module):
                    attr = getattr(tool_module, attr_name)
                    if callable(attr) and not attr_name.startswith('_'):
                        tool_func = attr
                        break
                
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