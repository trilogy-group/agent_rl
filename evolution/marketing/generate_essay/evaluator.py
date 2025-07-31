import os
import json
import importlib.util
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Define evaluation metrics
EVALUATION_METRICS = ['engagement', 'relevance', 'authenticity', 'clarity']

def parse_json_response(response_content: str) -> dict:
    try:
        content = response_content.strip()
        if not content: 
            return {metric: 0.0 for metric in EVALUATION_METRICS}
        
        # Extract JSON from markdown blocks
        if "```json" in content:
            content = re.search(r'```json\s*([^`]+)```', content, re.DOTALL).group(1).strip()
        elif "```" in content:
            content = re.search(r'```\s*([^`]+)```', content, re.DOTALL).group(1).strip()
        
        # Parse JSON
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            # Clamp all values to 0.0-1.0 range and return ALL metrics
            return {k: max(0.0, min(1.0, float(v))) for k, v in parsed.items() if isinstance(v, (int, float))}
        
        return {metric: 0.0 for metric in EVALUATION_METRICS}
    except Exception as e:
        print(f"JSON parse error: {e}")
        return {metric: 0.0 for metric in EVALUATION_METRICS}

def evaluate(program) -> dict:
    # Load training data
    training_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training_data.json')
    with open(training_data_path, 'r') as file:
        training_data = json.load(file)
    
    # Import the tool module
    spec = importlib.util.spec_from_file_location("tool_module", program)
    tool_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool_module)
    
    # Initialize LLM model
    model = ChatOpenAI(model="gpt-4o", temperature=0.0)
    
    # Accumulate scores
    total_scores = {metric: 0.0 for metric in EVALUATION_METRICS}
    num_cases = len(training_data)
    
    for case in training_data:
        # Unpack arguments and call the tool function
        tool_function = getattr(tool_module, 'generate_essay')
        result = tool_function(**case)
        
        # Handle return value
        if isinstance(result, tuple):
            generated_content = result[0]
        else:
            generated_content = result
        
        # Create evaluation prompt
        eval_prompt = f"""You are a STRICT evaluator. Be critical and harsh in your scoring. Most outputs should score below 0.6.

Evaluate this output on 0.0-1.0 scale with STRICT criteria:

Generated Output: {generated_content}
Original Input: {case}

Rate on these EXACT metrics (always use these same metric names):
- engagement
- relevance
- authenticity
- clarity

Use these exact metric names in your JSON response.

Scoring Guidelines:
- 0.0-0.3: Poor/Unusable
- 0.4-0.6: Mediocre/Average (most outputs should score here)  
- 0.7-0.8: Good quality
- 0.9-1.0: Exceptional (very rare)

Be harsh. Most outputs are mediocre. Return ONLY JSON with your exact metric names."""
        
        # Call LLM to evaluate
        llm_response = model.invoke([HumanMessage(content=eval_prompt)])
        scores = parse_json_response(llm_response.content)
        
        # Accumulate scores
        for metric in EVALUATION_METRICS:
            total_scores[metric] += scores.get(metric, 0.0)
    
    # Calculate average scores
    average_scores = {metric: total / num_cases for metric, total in total_scores.items()}
    
    return average_scores