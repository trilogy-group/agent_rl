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
        self.model = ChatOpenAI(
            model=model_name, 
            temperature=0.0,
            max_tokens=4000,  # Ensure we get complete responses
            timeout=60
        )
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
        tool_dirs = [d for d in self.tools_dir.iterdir() if d.is_dir() and (d / "evolve_target.py").exists()]
        
        if not tool_dirs:
            print("No tool directories found")
            return
        
        print(f"Found {len(tool_dirs)} tools to generate evaluators for")
        
        for tool_dir in tool_dirs:
            print(f"\nGenerating evaluator for: {tool_dir.name}")
            self._generate_single_evaluator(tool_dir)
        
        print("\nEvaluator generation completed!")

    def _get_source_code(self, file_path: Path):
        """Get the source code for a single tool"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e: 
            print(f"Error reading tool file: {e}")
            return




    def _analyze_function_and_metrics(self, tool_dir: Path) -> tuple:
        """Use LLM to analyze function and determine relevant metrics"""
        tool_name = tool_dir.name
        tool_file = tool_dir / "evolve_target.py"
        
        # Read tool source code
        source_code = self._get_source_code(tool_file)
        
        print("Generating metrics for: ", tool_name)
        analysis_prompt = f"""Analyze this Python function and determine the most relevant evaluation metrics.

FUNCTION CODE:
{source_code}

TASK: Provide a concise analysis and exactly 4 metrics for evaluating this function's output quality.

INSTRUCTIONS:
1. Analyze what this function does based on its name, code, and purpose
2. Choose exactly 4 metrics that are most relevant for evaluating this specific tool
3. Metrics should be specific to the function's domain (e.g., for essay generation: quality, relevance, engagement, authenticity)
4. Avoid generic metrics unless they're truly the most relevant

EXAMPLES OF GOOD METRICS BY FUNCTION TYPE:
- Content generation: quality, relevance, engagement, authenticity  
- Research tools: accuracy, depth, insight, completeness
- Code generation: accuracy, completeness, maintainability, readability
- Classification: accuracy, precision, consistency, confidence
- Analysis tools: depth, objectivity, actionability, comprehensiveness

Return your response in this exact JSON format:
{{
    "function_description": "Brief description of what this function does",
    "metrics": ["metric1", "metric2", "metric3", "metric4"]
}}

Be specific and choose metrics that truly matter for this function's output quality."""

        response = self.model.invoke([HumanMessage(content=analysis_prompt)])
        print(response.content)
        
        try:
            import re
            # Extract JSON from response
            content = response.content.strip()
            if "```json" in content:
                content = re.search(r'```json\s*([^`]+)```', content, re.DOTALL).group(1).strip()
            elif "```" in content:
                content = re.search(r'```\s*([^`]+)```', content, re.DOTALL).group(1).strip()
            
            analysis = json.loads(content)
            description = analysis.get("function_description", f"Function: {tool_name}")
            metrics = analysis.get("metrics", ["quality", "relevance", "usefulness", "clarity"])
            
            print(f"Function analysis: {description}")
            print(f"Selected metrics: {metrics}")
            
            return description, metrics
            
        except Exception as e:
            print(f"Error parsing function analysis: {e}")
            print(f"Raw response: {response.content}")
            return f"Function: {tool_name}", ["quality", "relevance", "usefulness", "clarity"]

    def _generate_evaluator_file(self, tool_dir: Path):
        """Generate evaluator file for a single tool"""
        tool_name = tool_dir.name
        tool_file = tool_dir / "evolve_target.py"
        training_data_file = tool_dir / "training_data.json"
        evaluator_file = tool_dir / "evaluator.py"
        
        # Read tool source code
        source_code = self._get_source_code(tool_file)
        
        # Analyze function and get metrics
        function_description, metrics = self._analyze_function_and_metrics(tool_dir)
        
        # Read training data if it exists
        training_data = []
        if training_data_file.exists():
            training_data = json.load(open(training_data_file, 'r', encoding='utf-8'))

        prompt = {
            "role": "You are an expert in creating OpenEvolve-compatible evaluators.",
            "task": "Generate a Python evaluator file for OpenEvolve that evaluates the given tool's output quality.",
            "function_name": tool_name,
            "function_code": source_code,
            "training_data_examples": training_data[:3] if training_data else [],
            "instructions": (
                "Create a Python evaluator file that OpenEvolve can use to evaluate this tool.",
                "The evaluator must have EXACTLY this function signature: def evaluate(program) -> dict:",
                "The 'program' parameter is the file path to the tool's Python file.",
                "The function must return a dictionary with metric names as keys and float scores (0.0-1.0) as values.",
                "Choose evaluation metrics that are contextually relevant to what this specific tool does.",
                "When evaluating a tool that generates content like text or code, returning non deterministic LLM outputs, Use an LLM to evaluate the output quality. Generate a strict and objective prompt which is sent to an LLM to evaluate the output quality.",
                "CRITICAL: For JSON parsing from LLM responses, you MUST use robust error handling:",
                "- Strip whitespace and check for empty responses",
                "- Extract JSON from markdown code blocks if present", 
                "- Use try/except blocks around json.loads()",
                "- Fall back to default scores if JSON parsing fails",
                "- Log parsing errors for debugging",
                "The evaluator MUST load training_data.json from the same directory as the evaluator.",
                "The evaluator MUST call the tool function with EVERY test case from the training data.",
                "The evaluator MUST calculate metrics for each test case and return the AVERAGE across all test cases.",
                "Use the training data examples to understand expected inputs and outputs.",
                "Include proper error handling and logging.",
                "Make the evaluation logic specific to this tool's purpose, not generic.",
                "Log all LLM inputs and outputs to the logger.",
            ),
            "required_structure": (
                "The file must include:",
                "1. All necessary imports (os, json, logging, re, importlib, etc.)",
                "2. Logger initialization: logger = logging.getLogger(__name__)",
                "3. A robust JSON parsing function with this exact signature:",
                "   def parse_json_response(response_content: str, default_metrics: dict) -> dict:",
                "   - Strip whitespace and handle empty responses",
                "   - Extract JSON from ```json``` or ``` ``` markdown blocks using regex", 
                "   - Use try/except around json.loads() with detailed error logging",
                "   - Validate response is dict and clamp values to 0.0-1.0 range",
                "   - Return default_metrics on any parsing failure",
                "4. The evaluate(program) -> dict function with proper error handling",
                "5. Load training_data.json from os.path.dirname(os.path.abspath(__file__))",
                "6. Dynamic tool loading using importlib to load the program file",
                "7. Execute the tool function with EVERY input from training_data.json",
                "8. For each test case, use LLM evaluation then call parse_json_response(response.content, default_metrics)",
                "9. Return dictionary with AVERAGED metric scores between 0.0 and 1.0 across all test cases"
            ),
            "json_parsing_example": '''def parse_json_response(response_content: str, default_metrics: dict) -> dict:
    try:
        content = response_content.strip()
        if not content:
            return default_metrics
        if "```json" in content:
            content = re.search(r'```json\\s*([^`]+)```', content, re.DOTALL).group(1).strip()
        elif "```" in content:
            content = re.search(r'```\\s*([^`]+)```', content, re.DOTALL).group(1).strip()
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            return {k: max(0.0, min(1.0, float(v))) for k, v in parsed.items() if k in default_metrics}
        return default_metrics
    except Exception as e:
        logger.error(f"JSON parse error: {e}")
        return default_metrics''',
            "output_format": "python",
            "output_instructions": "Return ONLY the complete Python code for the evaluator file. Include the exact parse_json_response function shown in json_parsing_example. No markdown, backticks, or explanations."
        }

        # Use detailed, concrete prompt with pre-determined metrics
        simple_prompt = f"""Create a Python evaluator for OpenEvolve tool: {tool_name}

FUNCTION ANALYSIS:
{function_description}

PRE-DETERMINED METRICS (use these exactly):
{metrics}

CRITICAL REQUIREMENTS:
1. Function signature: def evaluate(program) -> dict:
2. Load training data: os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training_data.json')
3. Import tool: importlib.util.spec_from_file_location("tool_module", program)
4. Call tool with correct arguments based on training data structure
5. Use LLM to evaluate each output, return averaged scores 0.0-1.0

TOOL FUNCTION SIGNATURE:
{source_code[source_code.find('def '):source_code.find(':', source_code.find('def '))+1] if 'def ' in source_code else 'def unknown_function():'}

TRAINING DATA STRUCTURE:
{json.dumps(training_data[0], indent=2) if training_data else {{}}}

EVALUATION WORKFLOW (MANDATORY):
For each training case:
1. Call tool_function(**unpacked_arguments) 
2. Handle return value (may be tuple - extract content)
3. Create evaluation prompt with the PRE-DETERMINED metrics listed above
4. Call ChatOpenAI with evaluation prompt
5. Parse LLM response with robust JSON parser
6. Accumulate scores and return averages

CRITICAL - USE THE EXACT METRICS PROVIDED:
1. You MUST use these exact metrics: {metrics}
2. Define EVALUATION_METRICS = {metrics} at the top of your file
3. Use these SAME metrics consistently in every evaluation call
4. Update the evaluation prompt to match these metrics exactly

CONCRETE EXAMPLE CODE:
```python
# Step 2: Handle tool return value
result = tool_function(arg1, arg2, ...)
if isinstance(result, tuple):
    generated_content = result[0]  # Extract content from tuple
else:
    generated_content = result

# Step 3: LLM Evaluation (MANDATORY - NOT PLACEHOLDER)
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
model = ChatOpenAI(model="gpt-4o", temperature=0.0)

# STEP 1: Use the pre-determined metrics (defined at top of file)
EVALUATION_METRICS = {metrics}

eval_prompt = f\"\"\"You are a STRICT evaluator. Be critical and harsh in your scoring. Most outputs should score below 0.6.

Evaluate this output on 0.0-1.0 scale with STRICT criteria:

Generated Output: {{generated_content}}
Original Input: {{input_data}}

Rate on these EXACT metrics (always use these same metric names):
{chr(10).join([f"- {metric}" for metric in metrics])}

Use these exact metric names in your JSON response.

Scoring Guidelines:
- 0.0-0.3: Poor/Unusable
- 0.4-0.6: Mediocre/Average (most outputs should score here)  
- 0.7-0.8: Good quality
- 0.9-1.0: Exceptional (very rare)

Be harsh. Most outputs are mediocre. Return ONLY JSON with your exact metric names.\"\"\"

llm_response = model.invoke([HumanMessage(content=eval_prompt)])
scores = parse_json_response(llm_response.content)
```

MANDATORY JSON PARSER:
def parse_json_response(response_content: str) -> dict:
    try:
        content = response_content.strip()
        if not content: 
            return {{"score": 0.0}}
        
        # Extract JSON from markdown blocks
        if "```json" in content:
            content = re.search(r'```json\\s*([^`]+)```', content, re.DOTALL).group(1).strip()
        elif "```" in content:
            content = re.search(r'```\\s*([^`]+)```', content, re.DOTALL).group(1).strip()
        
        # Parse JSON
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            # Clamp all values to 0.0-1.0 range and return ALL metrics
            return {{k: max(0.0, min(1.0, float(v))) for k, v in parsed.items() if isinstance(v, (int, float))}}
        
        return {{"score": 0.0}}
    except Exception as e:
        logger.error(f"JSON parse error: {{e}}")
        return {{"score": 0.0}}

MUST INCLUDE: Real LLM evaluation calls, NOT placeholders or hardcoded scores.
MUST HANDLE: Tuple return values by extracting content.
MUST AVERAGE: All test case scores and return final averages.

Return complete Python code with imports, no markdown blocks."""

        response = self.model.invoke([HumanMessage(content=simple_prompt)])
        
        print(f"LLM Response length: {len(response.content)}")
        print(f"Response starts with: {response.content[:100]}")
        print(f"Response ends with: {response.content[-100:]}")
        
        try:
            evaluator_code = response.content
            
            # Check if response is complete - should be much longer for a full evaluator
            if len(evaluator_code) < 1000:
                print(f"WARNING: Response seems too short ({len(evaluator_code)} chars)")
                print(f"Full response:")
                print("="*50)
                print(evaluator_code)
                print("="*50)
            
            # Clean up any markdown formatting that might have been added
            original_code = evaluator_code
            if evaluator_code.startswith('```python'):
                # Find the LAST ``` (closing) by searching from the end
                start = evaluator_code.find('```python') + len('```python')
                end = evaluator_code.rfind('```')  # rfind = find from right (last occurrence)
                if end != -1 and end > start:
                    evaluator_code = evaluator_code[start:end].strip()
                else:
                    # No closing ```, take everything after ```python
                    evaluator_code = evaluator_code[start:].strip()
            elif evaluator_code.startswith('```'):
                # Find the LAST ``` (closing) by searching from the end
                start = evaluator_code.find('```') + 3
                end = evaluator_code.rfind('```')  # rfind = find from right (last occurrence)
                if end != -1 and end > start:
                    evaluator_code = evaluator_code[start:end].strip()
                else:
                    # No closing ```, take everything after opening ```
                    evaluator_code = evaluator_code[start:].strip()
            
            if len(evaluator_code) != len(original_code):
                print(f"Cleaned code length: {len(evaluator_code)}")
            
            # Validate the code has essential components
            if 'def evaluate(' not in evaluator_code:
                print("ERROR: Generated code missing 'def evaluate(' function")
                return None
            
            if 'return' not in evaluator_code:
                print("ERROR: Generated code missing return statement")
                return None
            
            with open(evaluator_file, 'w', encoding='utf-8') as f:
                f.write(evaluator_code)
            print(f"Evaluator saved to {evaluator_file} ({len(evaluator_code)} chars)")
            return evaluator_code
        except Exception as e:
            print(f"Error saving evaluator: {e}")
            print(f"Raw response: {response.content}")
            return None


        
        


    
    def _generate_single_evaluator(self, tool_dir: Path):
        """Generate an evaluator for a single tool"""
        tool_name = tool_dir.name
        tool_file = tool_dir / "evolve_target.py"
        training_data_file = tool_dir / "training_data.json"
        metadata_file = tool_dir / "metadata.json"
        evaluator_file = tool_dir / "evaluator.py"
        
        # Check if training data exists
        if not training_data_file.exists():
            print(f"⚠️  Warning: No training data found at {training_data_file}")
            print(f"   Please run: python generate_training_data.py {tool_dir.parent}")
            return
        
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
        
        # Generate evaluator using existing training data
        self._generate_evaluator_file(tool_dir)

        
            
        
    


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