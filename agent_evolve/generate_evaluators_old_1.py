#!/usr/bin/env python3
"""
Evaluator Generation Script for Agent Evolution Framework

This script uses an LLM to generate OpenEvolve-compatible evaluators
for each extracted tool. The evaluators assess tool performance across
multiple dimensions relevant to agent capabilities.

Usage:
    python generate_evaluators.py [tools_directory]
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


class EvaluatorGenerator:
    """Generates OpenEvolve evaluators for agent tools using LLM"""
    
    def __init__(self, model_name: str = "gpt-4o"):
        self.model = ChatOpenAI(model=model_name, temperature=0.2)
        self.tools_dir = Path("evolution/tools")
    
    def generate_evaluators(self, tools_directory: str = None):
        """Generate evaluators for all tools in the directory"""
        if tools_directory:
            self.tools_dir = Path(tools_directory)
        
        if not self.tools_dir.exists():
            print(f"Error: Tools directory '{self.tools_dir}' does not exist")
            return
        
        print(f"Generating evaluators for tools in: {self.tools_dir}")
        
        # Find all tool directories
        tool_dirs = [d for d in self.tools_dir.iterdir() if d.is_dir() and (d / "tool.py").exists()]
        
        if not tool_dirs:
            print("No tool directories found")
            return
        
        print(f"Found {len(tool_dirs)} tools to generate evaluators for")
        
        for tool_dir in tool_dirs:
            print(f"\nGenerating evaluator for: {tool_dir.name}")
            self._generate_single_evaluator(tool_dir)
        
        print("\nEvaluator generation completed!")
    
    def _generate_single_evaluator(self, tool_dir: Path):
        """Generate an evaluator for a single tool"""
        tool_name = tool_dir.name
        tool_file = tool_dir / "tool.py"
        metadata_file = tool_dir / "metadata.json"
        evaluator_file = tool_dir / "evaluator.py"
        
        # Read tool source code
        try:
            with open(tool_file, 'r', encoding='utf-8') as f:
                tool_source = f.read()
        except Exception as e:
            print(f"Error reading tool file: {e}")
            return
        
        # Read metadata if available
        metadata = {}
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except Exception as e:
                print(f"Warning: Could not read metadata: {e}")
        
        # Generate training data and evaluator using LLM
        try:
            self._current_tool_name = tool_name  # Store for cleanup method
            
            # Enhance metadata with LLM if needed
            enhanced_metadata = self._enhance_metadata_with_llm(tool_name, tool_source, metadata)
            print(f"Enhanced metadata: {enhanced_metadata}")
            
            # Determine tool category for specialized evaluation using LLM
            tool_category = self._get_tool_category_with_llm(tool_name, tool_source)
            print(f"LLM detected tool category: {tool_category}")
            
            # Generate training data samples
            print(f"Generating training data for: {tool_name}")
            training_data = self._generate_training_data(tool_name, tool_source, enhanced_metadata, tool_category)
            
            # Generate evaluator with training data (LLM will choose metrics)
            evaluator_code = self._create_evaluator_with_llm(tool_name, tool_source, enhanced_metadata, training_data, tool_category)
            
            # Validate generated code
            if self._validate_python_code(evaluator_code):
                # Write evaluator file
                with open(evaluator_file, 'w', encoding='utf-8') as f:
                    f.write(evaluator_code)
                
                # Write training data file
                training_data_file = tool_dir / "training_data.json"
                with open(training_data_file, 'w', encoding='utf-8') as f:
                    json.dump(training_data, f, indent=2)
                
                print(f"Created: {evaluator_file}")
                print(f"Created: {training_data_file} ({len(training_data)} samples)")
            else:
                print(f"Error: Generated code for {tool_name} is not valid Python")
            
        except Exception as e:
            print(f"Error generating evaluator: {e}")
    
    def _enhance_metadata_with_llm(self, tool_name: str, tool_source: str, existing_metadata: Dict) -> Dict:
        """Use LLM to generate missing metadata fields"""
        
        # Check what's missing
        name = existing_metadata.get('name')
        description = existing_metadata.get('description')
        metrics = existing_metadata.get('metrics', [])
        metadata = existing_metadata.get('metadata', {})
        
        # If everything is provided, return as-is
        if name and description and metrics and metadata:
            return existing_metadata
        
        enhancement_prompt = f"""Analyze this tool and generate appropriate metadata for it.

Tool Source Code:
{tool_source[:2000]}

Current metadata:
{json.dumps(existing_metadata, indent=2)}

Generate metadata with these fields:
1. name: A clear, descriptive name for the tool (if not provided). Use the function name: {tool_name}
2. description: A concise description of what the tool does (if not provided)
3. metrics: A list of 3-5 relevant quality metrics to evaluate this tool (if not provided). Examples:
   - For NLG tools: ["coherence", "engagement", "clarity", "creativity", "relevance"]
   - For research tools: ["accuracy", "completeness", "relevance", "timeliness", "source_quality"]
   - For classification: ["accuracy", "precision", "recall", "confidence", "consistency"]
   - For utility: ["correctness", "efficiency", "reliability", "usefulness", "robustness"]
4. metadata: Additional metadata as a dictionary (if not provided). Examples:
   - For content generation: {{"platform": "linkedin", "max_length": 300, "target_audience": "professionals"}}
   - For research: {{"max_results": 10, "time_range": "30_days", "source_types": ["web", "academic"]}}

Return ONLY a JSON object with the complete metadata (including existing fields).
"""

        try:
            response = self.model.invoke([
                SystemMessage(content=enhancement_prompt)
            ])
            
            # Parse the response
            response_text = self._clean_json_response(response.content)
            enhanced = json.loads(response_text)
            
            # Merge with existing metadata, preferring existing values
            result = {
                'name': existing_metadata.get('name') or enhanced.get('name') or tool_name,
                'description': existing_metadata.get('description') or enhanced.get('description'),
                'metrics': existing_metadata.get('metrics') or enhanced.get('metrics', []),
                'metadata': existing_metadata.get('metadata') or enhanced.get('metadata', {}),
                'category': existing_metadata.get('category')  # Preserve if exists
            }
            
            return result
            
        except Exception as e:
            print(f"Error enhancing metadata with LLM: {e}")
            # Return with defaults
            return {
                'name': existing_metadata.get('name') or tool_name,
                'description': existing_metadata.get('description') or f"Tool: {tool_name}",
                'metrics': existing_metadata.get('metrics') or ["quality", "accuracy", "usefulness", "reliability", "efficiency"],
                'metadata': existing_metadata.get('metadata') or {},
                'category': existing_metadata.get('category')
            }
    
    def _analyze_tool_functionality(self, tool_name: str, tool_source: str, training_data: List[Dict]) -> str:
        """Analyze what the tool does to create better evaluation"""
        analysis_prompt = f"""Analyze this tool and describe what it does in 2-3 sentences:

Tool: {tool_name}
Source Code (first 1000 chars):
{tool_source[:1000]}

Example Input/Output:
{json.dumps(training_data[0] if training_data else {}, indent=2)}

Provide a brief, clear description of the tool's purpose and expected output quality."""

        try:
            response = self.model.invoke([SystemMessage(content=analysis_prompt)])
            return response.content.strip()
        except:
            return f"Tool that performs {tool_name} functionality"
    
    def _get_tool_category_with_llm(self, tool_name: str, tool_source: str) -> str:
        """Use LLM to determine tool category based on name and source code"""
        
        classification_prompt = f"""Analyze this tool and classify it into one of these categories:

1. "natural_language_generation" - Functions that generate text, content, writing, posts, articles, summaries, responses, brand guidelines, etc.
2. "research" - Functions that search, query, fetch data, web scraping, information gathering, analysis, etc.  
3. "classification" - Functions that classify, categorize, predict, detect, score, rate, assess sentiment, intent, etc.
4. "utility" - Other utility functions, data processing, calculations, file operations, etc.

Tool Name: {tool_name}

Tool Source Code:
{tool_source[:2000]}  

Respond with ONLY the category name (one of: natural_language_generation, research, classification, utility)"""

        try:
            response = self.model.invoke([
                SystemMessage(content=classification_prompt)
            ])
            
            category = response.content.strip().lower()
            valid_categories = ["natural_language_generation", "research", "classification", "utility"]
            
            if category in valid_categories:
                return category
            else:
                print(f"LLM returned invalid category '{category}', defaulting to 'utility'")
                return "utility"
                
        except Exception as e:
            print(f"Error classifying tool with LLM: {e}, defaulting to 'utility'")
            return "utility"
    
    def _generate_training_data(self, tool_name: str, tool_source: str, metadata: Dict, tool_category: str = "utility") -> List[Dict]:
        """Generate 30 diverse training data samples for the tool"""
        
        system_prompt = """You are an expert at creating evaluation data for agent tools. Your goal is to test tool QUALITY, ACCURACY, and USEFULNESS - not basic input validation.

For each tool, create realistic scenarios that would occur in actual agent usage. Focus on:
1. Real-world inputs the tool would receive from users or other agents
2. Expected high-quality outputs that demonstrate the tool working well
3. Scenarios where the tool's accuracy and usefulness can be measured
4. Complex, realistic use cases that test the tool's core functionality

AVOID:
- Empty strings, null values, or basic input validation tests
- Trivial edge cases that don't reflect real usage
- Error handling for malformed inputs
- Simple "does it work" tests

FOCUS ON:
- Realistic user scenarios and agent workflows
- Output quality assessment (accuracy, completeness, usefulness)
- Different complexity levels of real-world inputs
- Variations in domain knowledge and context
- Measuring how well the tool achieves its intended purpose

Return ONLY a JSON array of test cases in this exact format:
[
  {
    "input": {...realistic input parameters...},
    "expected_output": {...what good output should look like...},
    "category": "quality_assessment|accuracy_test|usefulness_evaluation|complexity_variation",
    "description": "What aspect of tool quality this tests"
  }
]

Do not include any markdown, explanations, or other text - just the JSON array."""

        # Customize prompt based on tool category
        if tool_category == "natural_language_generation":
            evaluation_focus = """Create test cases with INPUT PARAMETERS for the tool to generate content:
- Diverse topics and requirements (12 cases)
- Different complexity levels and styles (10 cases) 
- Various contexts and constraints (5 cases)
- Edge cases and special requirements (3 cases)

CRITICAL: For NLG tools, provide INPUT PARAMETERS that the tool needs, NOT pre-generated content.
The input should contain tool parameters like: {"topic": "AI ethics", "style": "professional", "length": "500 words"}
The expected_output should specify evaluation criteria: {"quality_criteria": ["coherent", "engaging", "well_structured"], "min_score": 0.7}"""
        else:
            evaluation_focus = """Create test cases that evaluate:
- Output accuracy and correctness (12 cases)
- Usefulness and completeness of results (10 cases) 
- Performance on complex real-world scenarios (5 cases)
- Quality across different input variations (3 cases)

For classification tools: Use ONLY the categories/intents/classes found in the source code. 
Do not invent new categories. Cover all existing categories with realistic examples."""

        # For NLG tools, generate realistic content in smaller batches
        if tool_category == "natural_language_generation":
            human_prompt = f"""Generate 10 evaluation test cases with INPUT PARAMETERS for this {tool_category} tool:

Tool: {tool_name}
Category: {tool_category}  
Tool Source: {tool_source}

CRITICAL REQUIREMENTS:
- Create INPUT PARAMETERS that the tool needs to generate content
- Include realistic topics, requirements, constraints that users would provide
- Vary complexity: simple topics, complex topics, specific requirements
- Cover different domains, styles, and use cases
- Make parameters realistic for actual tool usage

{evaluation_focus}

For each test case, provide the INPUT PARAMETERS the tool needs:
{{"topic": "specific topic here", "requirements": "any constraints", "style": "tone/style", ...}}

Generate 10 realistic test cases with input parameters.
Output ONLY JSON array."""
        else:
            # For classification tools, analyze source code to extract valid classes/intents
            analysis_instruction = ""
            if tool_category == "classification" or "intent" in tool_name.lower() or "classify" in tool_name.lower():
                analysis_instruction = """
CRITICAL FOR CLASSIFICATION TOOLS:
1. ANALYZE the tool source code to identify ALL valid classes/intents/categories
2. Look for lists, enums, if/elif chains, or hardcoded categories in the code
3. Extract the EXACT class names/intents that the tool can return
4. ONLY use these existing categories in test cases - DO NOT invent new ones
5. Create test cases that cover all existing categories with realistic examples

First analyze the source code, then generate test cases using ONLY the categories found in the code."""
            
            human_prompt = f"""Generate 30 realistic evaluation scenarios for this {tool_category} tool that test OUTPUT QUALITY and USEFULNESS:

Tool: {tool_name}
Category: {tool_category}
Metadata: {json.dumps(metadata, indent=2) if metadata else "None"}

Tool Source:
{tool_source}

{analysis_instruction}

{evaluation_focus}

Each test should use realistic inputs that an agent would actually encounter, and measure whether the tool produces high-quality, useful output.

Output ONLY JSON array of 30 test cases."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        try:
            # For NLG tools, generate multiple batches of realistic content
            if tool_category == "natural_language_generation":
                all_training_data = []
                batches = 1  # Generate 3 batches of 10 = 30 total
                
                for batch_num in range(batches):
                    print(f"Generating batch {batch_num + 1}/{batches} of realistic training data...")
                    response = self.model.invoke(messages)
                    training_data_text = self._clean_json_response(response.content)
                    batch_data = json.loads(training_data_text)
                    all_training_data.extend(batch_data)
                    
                print(f"Generated {len(all_training_data)} total realistic training samples")
                return all_training_data
            else:
                # For non-NLG tools, use single batch generation
                response = self.model.invoke(messages)
                training_data_text = self._clean_json_response(response.content)
                training_data = json.loads(training_data_text)
                
                # Validate we got the expected number of samples
                if len(training_data) < 20:  # Allow some flexibility
                    print(f"Warning: Only generated {len(training_data)} training samples")
                
                return training_data
            
        except json.JSONDecodeError as e:
            print(f"Error parsing training data JSON: {e}")
            # Return basic fallback training data
            return self._create_fallback_training_data(tool_name)
        except Exception as e:
            print(f"Error generating training data: {e}")
            return self._create_fallback_training_data(tool_name)
    
    def _clean_json_response(self, response_text: str) -> str:
        """Clean LLM response to extract valid JSON"""
        # Remove markdown code blocks
        text = response_text.strip()
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]
        
        if text.endswith('```'):
            text = text[:-3]
        
        # Find the JSON array bounds
        start_idx = text.find('[')
        end_idx = text.rfind(']')
        
        if start_idx != -1 and end_idx != -1:
            return text[start_idx:end_idx+1]
        
        return text.strip()
    
    def _create_fallback_training_data(self, tool_name: str) -> List[Dict]:
        """Create realistic fallback training data if LLM generation fails"""
        # Create tool-specific realistic scenarios based on tool name
        if "brand" in tool_name.lower() and "generate" in tool_name.lower():
            return [
                {
                    "input": {"brand_info": "TechCorp Inc. - innovative software solutions"},
                    "expected_output": {
                        "quality_criteria": ["professional_tone", "comprehensive_coverage", "actionable_guidelines"],
                        "min_coherence_score": 0.7,
                        "min_relevance_score": 0.8,
                        "min_completeness_score": 0.7,
                        "min_creativity_score": 0.6
                    },
                    "category": "quality_assessment",
                    "description": "Evaluates quality of brand guideline generation for tech company"
                },
                {
                    "input": {"brand_info": "GreenEarth Organic Foods - sustainable farming practices"},
                    "expected_output": {
                        "quality_criteria": ["sustainability_focus", "authentic_voice", "clear_positioning"],
                        "min_coherence_score": 0.7,
                        "min_relevance_score": 0.8,
                        "min_completeness_score": 0.6,
                        "min_creativity_score": 0.7
                    },
                    "category": "accuracy_test",
                    "description": "Tests accuracy of brand voice capture for environmental company"
                }
            ]
        elif "brand" in tool_name.lower():
            return [
                {
                    "input": {"brand_guidelines": "Our brand uses a blue and white color scheme with Arial font."},
                    "expected_output": True,
                    "category": "quality_assessment",
                    "description": "Evaluates detection of valid brand guidelines"
                }
            ]
        elif "reflect" in tool_name.lower() or "critique" in tool_name.lower():
            return [
                {
                    "input": {"draft": """🚀 Exciting news! After 18 months of development, we're officially launching our new AI-powered analytics platform at TechFlow Solutions.

The journey hasn't been easy. Our team of 12 engineers worked tirelessly, conducting over 200 user interviews and processing 50TB of data to understand what businesses really need from their analytics tools.

Key highlights of our platform:
✅ 300% faster data processing than industry standards
✅ Real-time insights across 15+ data sources  
✅ Intuitive drag-and-drop dashboard builder
✅ Enterprise-grade security with SOC 2 compliance

We're offering early access to the first 100 companies who sign up this month. Interested in revolutionizing your data strategy?

#Analytics #AI #ProductLaunch #DataScience #TechInnovation"""},
                    "expected_output": {
                        "quality_criteria": ["actionable_feedback", "professional_tone", "comprehensive_analysis", "specific_suggestions"],
                        "min_coherence_score": 0.8,
                        "min_relevance_score": 0.8,
                        "min_completeness_score": 0.7,
                        "min_creativity_score": 0.6,
                        "min_actionability_score": 0.8
                    },
                    "category": "quality_assessment",
                    "description": "Evaluates critique quality for realistic product launch post"
                }
            ]
        elif "research" in tool_name.lower():
            return [
                {
                    "input": {"query": "artificial intelligence market trends 2024"},
                    "expected_output": "Current, relevant research findings with sources",
                    "category": "quality_assessment", 
                    "description": "Evaluates research quality and relevance for AI market analysis"
                }
            ]
        else:
            return [
                {
                    "input": {"realistic_scenario": f"Common use case for {tool_name}"},
                    "expected_output": "High-quality, useful output appropriate for the tool's purpose",
                    "category": "quality_assessment",
                    "description": f"Evaluates overall quality and usefulness of {tool_name} output"
                }
            ]

    def _create_evaluator_with_llm(self, tool_name: str, tool_source: str, metadata: Dict, training_data: List[Dict] = None, tool_category: str = "utility") -> str:
        """Use LLM to generate a custom evaluator for the specific tool"""
        
        metrics = metadata.get('metrics', ["quality", "accuracy", "usefulness", "reliability", "efficiency"])
        
        # Simplified prompt that focuses on the specific tool
        prompt = f"""Create a Python evaluator specifically for the tool '{tool_name}'.

TOOL DETAILS:
- Description: {metadata.get('description', 'No description')}
- Category: {tool_category}
- Metrics to evaluate: {metrics}

TOOL SOURCE CODE:
```python
{tool_source[:2000]}
```

EXAMPLE TEST CASE:
Input: {json.dumps(training_data[0]['input'] if training_data else {}, indent=2)}
Expected qualities: {json.dumps(training_data[0].get('expected_output', {}), indent=2) if training_data else 'High quality output'}

Create an evaluator that:
1. Imports and runs THIS specific tool ({tool_name})
2. Evaluates outputs based on what {tool_name} is supposed to produce
3. Uses evaluation logic specific to {tool_name}'s purpose
4. Scores each metric from 0.0-1.0

For example:
- If {tool_name} generates brand guidelines, evaluate comprehensiveness, clarity, actionability
- If {tool_name} classifies text, evaluate accuracy, confidence calibration
- If {tool_name} creates content, evaluate quality, engagement, relevance

The evaluator must:

```python
import os
import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

# Initialize logger
logger = logging.getLogger(__name__)

def evaluate(program) -> dict:
    # Metrics specifically chosen for {tool_name}
    metrics = {json.dumps(metrics)}
    
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
```

Follow this structure EXACTLY but customize the metrics and evaluation logic for the specific tool.

IMPORTANT: Output ONLY the Python code for evaluator.py. Start with imports, no markdown formatting."""
        else:
            system_prompt = """You are an expert Python developer creating OpenEvolve evaluators for utility/classification tools.

CRITICAL: You must output ONLY valid Python code. No markdown, no explanations, no comments outside the code.

MANDATORY: Your code MUST start with these EXACT imports and logger initialization:
```
import os
import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

# Initialize logger
logger = logging.getLogger(__name__)
```

STEP 1: ANALYZE THE TOOL
First, carefully analyze the tool's functionality, purpose, and expected outputs to determine what quality dimensions matter most.

STEP 2: CHOOSE APPROPRIATE METRICS
Based on your analysis, select 5 specific quality metrics that are most relevant for evaluating THE TOOL'S OUTPUT.
Choose metric names that reflect what the tool actually produces:
- For classification tools: accuracy, precision, consistency, coverage, confidence
- For research tools: information_accuracy, source_credibility, completeness, relevance, timeliness  
- For analysis tools: insight_depth, actionability, evidence_quality, objectivity, comprehensiveness

STEP 3: IMPLEMENT EVALUATION
Your evaluator should focus on:
1. OUTPUT QUALITY - How accurate, complete, and useful are the tool's actual outputs?
2. REAL-WORLD PERFORMANCE - How well does the tool work on realistic inputs?
3. CONSISTENCY - Does the tool produce reliable results across similar inputs?
4. USEFULNESS - How valuable are the outputs for their intended purpose?

OpenEvolve Evaluator Requirements:
1. Must contain an evaluate(program) -> dict function
2. Must return a dictionary with tool-specific metric keys
3. Should measure 5 TOOL-SPECIFIC metrics that evaluate what the tool produces
4. Must handle exceptions gracefully and return all metrics as 0.0 on failure
5. Should evaluate actual tool output quality, not code structure
6. Use meaningful metric names specific to the tool's purpose
7. Example: {"classification_accuracy": 0.8, "edge_case_handling": 0.7, "consistency": 0.9, "confidence_calibration": 0.6, "coverage": 0.8}

Your evaluator should:
- Import the tool dynamically from the program parameter  
- Test it with realistic, complex inputs from training data
- Assess the QUALITY and USEFULNESS of what the tool actually outputs
- Measure how well the tool achieves its intended purpose
- Use efficient evaluation methods - batch operations when possible
- Compare outputs against expected high-quality results
- Focus on real-world performance scenarios
- Return dictionary with tool-specific metric keys

IMPORTANT: Output ONLY the Python code for evaluator.py. Start with imports, no markdown formatting."""

        training_data_str = json.dumps(training_data, indent=2) if training_data else "None"
        
        # Customize human prompt based on tool category
        if tool_category == "natural_language_generation":
            requirements_text = """Requirements:
- FIRST: Analyze the tool's functionality and choose 5 most relevant quality metrics with meaningful names
- evaluate(program) -> dict function
- Use the provided training data to assess NLG OUTPUT QUALITY
- Import ChatOpenAI from langchain_openai for qualitative evaluation
- For each test case, call the tool and use LLM to score the output quality using BLIND evaluation
- CRITICAL: Do NOT show expected output or characteristics to the evaluation LLM
- CRITICAL: Use ONE LLM request per test case to score ALL metrics simultaneously for efficiency
- Use structured prompts that return all metric scores as NUMERIC VALUES (0.0-1.0) in JSON format with meaningful keys
- Include clear JSON format requirements in prompts: "Return ONLY a JSON object with numeric scores between 0.0 and 1.0"
- Provide explicit format example with STRICT evaluation instructions: {"metric1": 0.8, "metric2": 0.7, "metric3": 0.9} - Be objective but unforgiving in scoring
- Implement robust JSON parsing with try/catch blocks and validation
- Use generic quality assessment prompts that evaluate content independently
- Extract quality criteria/thresholds from training data but evaluate outputs blindly
- Return dictionary with tool-specific metric keys (e.g., "critique_quality", "actionability", "specificity")
- Handle missing dependencies gracefully, return all metrics as 0.0 on failure
- NO string matching - only LLM-based quality assessment
- NO markdown, NO explanations, ONLY Python code

The evaluator should load training_data.json, extract quality criteria, then use an LLM to blindly evaluate generated content without showing expected answers. Must return dictionary with meaningful metric keys that reflect what the tool produces."""
        else:
            requirements_text = """Requirements:
- FIRST: Analyze the tool's functionality and choose 5 most relevant quality metrics with meaningful names
- evaluate(program) -> dict function
- Use the provided training data to assess TOOL OUTPUT QUALITY
- CRITICAL: Evaluate metrics efficiently - avoid unnecessary LLM calls when possible
- Focus on how well the tool achieves its intended purpose
- Compare actual outputs against expected high-quality results
- Return dictionary with tool-specific metric keys that reflect what the tool produces
- Handle missing dependencies gracefully, return all metrics as 0.0 on failure
- Use meaningful metric names (e.g., "classification_accuracy", "information_completeness")
- NO markdown, NO explanations, ONLY Python code

The evaluator should load training_data.json from the same directory and evaluate whether the tool produces accurate, useful, and complete outputs for realistic scenarios. Must return dictionary with meaningful metric keys that reflect the tool's output quality."""

        human_prompt = f"""Create evaluator.py for this {tool_category} tool that evaluates OUTPUT QUALITY and USEFULNESS. OUTPUT ONLY PYTHON CODE:

Tool: {tool_name}
Category: {tool_category}
Metadata: {json.dumps(metadata, indent=2) if metadata else "None"}

Tool Source:
{tool_source}

Training Data ({len(training_data) if training_data else 0} samples):
{training_data_str}

{requirements_text}"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.model.invoke(messages)
        return self._clean_generated_code(response.content)
    
    def _clean_generated_code(self, generated_text: str) -> str:
        """Clean up LLM-generated code to extract only Python code"""
        lines = generated_text.split('\n')
        code_lines = []
        in_code_block = False
        found_python_code = False
        
        for line in lines:
            # Skip markdown code block markers
            if line.strip().startswith('```'):
                if 'python' in line.lower():
                    in_code_block = True
                    found_python_code = True
                    continue
                elif in_code_block:
                    in_code_block = False
                    continue
                else:
                    continue
            
            # If we found a code block, only include lines within it
            if found_python_code and not in_code_block:
                continue
            
            # Skip obvious non-code lines (explanations, headers)
            if (line.strip().startswith('#') and 
                any(word in line.lower() for word in ['explanation', 'overview', 'summary', 'note:', 'important:'])):
                continue
            
            # Skip lines that look like markdown headers or explanations
            if (line.strip().startswith('**') or 
                line.strip().startswith('###') or
                line.strip().startswith('Below is') or
                line.strip().startswith('This evaluator') or
                line.strip().startswith('Explanation:')):
                continue
            
            # Include the line if we're in a code block or if it looks like Python code
            if (in_code_block or 
                line.strip().startswith(('import ', 'from ', 'def ', 'class ', 'if ', 'try:', 'except', 'return')) or
                line.strip() == '' or
                line.startswith('    ') or  # Indented lines (likely code)
                '=' in line or
                line.strip().endswith(':')):
                code_lines.append(line)
        
        # If no code block was found, try to extract Python-looking lines
        if not found_python_code:
            code_lines = []
            for line in lines:
                # Skip obvious explanation lines
                if (line.strip().startswith('**') or 
                    line.strip().startswith('###') or
                    line.strip().startswith('Below is') or
                    line.strip().startswith('This evaluator') or
                    line.strip().startswith('Explanation:') or
                    'combined_score' in line and 'Assessed by' in line):
                    continue
                
                # Include lines that look like Python code
                if (line.strip().startswith(('import ', 'from ', 'def ', 'class ', 'if ', 'try:', 'except', 'return')) or
                    line.strip() == '' or
                    line.startswith('    ') or  # Indented lines
                    '=' in line and not line.strip().startswith('-') or  # Assignment but not list items
                    line.strip().endswith(':')):
                    code_lines.append(line)
        
        cleaned_code = '\n'.join(code_lines).strip()
        
        # Add header comment if missing
        if not cleaned_code.startswith('#!/usr/bin/env python3'):
            header = f'''#!/usr/bin/env python3
"""
OpenEvolve Evaluator for {self._current_tool_name if hasattr(self, '_current_tool_name') else 'tool'}
Generated automatically by LLM-based evaluator generator
"""

'''
            cleaned_code = header + cleaned_code
        
        return cleaned_code
    
    def _validate_python_code(self, code: str) -> bool:
        """Validate that the generated code is syntactically correct Python"""
        try:
            import ast
            ast.parse(code)
            
            # Additional checks for required components
            if 'def evaluate(' not in code:
                print("Warning: Generated code missing evaluate function")
                return False
            
            # Skip combined_score check - we now return dictionaries
            # if 'combined_score' not in code:
            #     print("Warning: Generated code missing combined_score")
            #     return False
            
            return True
        except SyntaxError as e:
            print(f"Syntax error in generated code: {e}")
            # Print first few lines for debugging
            lines = code.split('\n')[:10]
            print("First 10 lines of generated code:")
            for i, line in enumerate(lines, 1):
                print(f"{i:3}: {line}")
            return False
        except Exception as e:
            print(f"Error validating code: {e}")
            return False
    
    def _get_tool_category(self, tool_name: str, tool_source: str) -> str:
        """Determine the category of tool for specialized evaluation"""
        tool_lower = tool_name.lower()
        source_lower = tool_source.lower()
        
        # Check for natural language generation patterns
        nlg_keywords = ['generate', 'create', 'write', 'compose', 'draft', 'produce']
        nlg_outputs = ['guidelines', 'content', 'text', 'response', 'message', 'description']
        
        # Research tools take priority over generation detection
        if any(keyword in tool_lower for keyword in ['research', 'search', 'query']):
            return "research"
        elif (any(keyword in tool_lower for keyword in nlg_keywords) and 
            any(output in tool_lower for output in nlg_outputs)) or \
           any(pattern in source_lower for pattern in ['chatgpt', 'gpt', 'llm', 'language_model', 'generate.*text']):
            return "natural_language_generation"
        elif any(keyword in tool_lower for keyword in ['classify', 'intent', 'analyze']):
            return "classification"
        elif any(keyword in tool_lower for keyword in ['improve', 'enhance', 'refactor']):
            return "improvement"
        elif any(keyword in tool_lower for keyword in ['chat', 'response', 'conversation']):
            return "conversation"
        elif any(keyword in tool_lower for keyword in ['has_', 'is_', 'check_']):
            return "utility"
        else:
            return "utility"


def main():
    """Main entry point"""
    if len(sys.argv) > 2:
        print("Usage: python generate_evaluators.py [tools_directory]")
        print("Example: python generate_evaluators.py evolution/tools")
        sys.exit(1)
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable is required")
        print("Please set your OpenAI API key: export OPENAI_API_KEY=your_key_here")
        sys.exit(1)
    
    tools_directory = sys.argv[1] if len(sys.argv) == 2 else None
    
    generator = EvaluatorGenerator()
    generator.generate_evaluators(tools_directory)


if __name__ == "__main__":
    main()