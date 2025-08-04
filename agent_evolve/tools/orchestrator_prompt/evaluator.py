import os
import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import logging

logger = logging.getLogger(__name__)
EVALUATION_METRICS = ['accuracy', 'clarity', 'effectiveness', 'consistency']

def parse_json_response(response_content: str) -> dict:
    try:
        content = response_content.strip()
        if not content:
            return {metric: 0.0 for metric in EVALUATION_METRICS}
        
        if "```json" in content:
            content = re.search(r'```json\s*([^`]+)```', content, re.DOTALL).group(1).strip()
        elif "```" in content:
            content = re.search(r'```\s*([^`]+)```', content, re.DOTALL).group(1).strip()
            
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            result = {}
            for metric in EVALUATION_METRICS:
                if metric in parsed:
                    result[metric] = max(0.0, min(1.0, float(parsed[metric])))
                else:
                    result[metric] = 0.0
            return result
        
        return {metric: 0.0 for metric in EVALUATION_METRICS}
    except Exception as e:
        logger.error(f"JSON parsing error: {e}")
        return {metric: 0.0 for metric in EVALUATION_METRICS}

def evaluate(program) -> dict:
    training_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training_data.json')
    with open(training_data_path, 'r') as f:
        training_data = json.load(f)
    
    with open(program, 'r') as f:
        file_content = f.read()
    
    prompt_match = re.search(r'([A-Z_]+)\s*=\s*"""(.*?)"""', file_content, re.DOTALL)
    if not prompt_match:
        logger.error("Could not find prompt template in file")
        return {metric: 0.0 for metric in EVALUATION_METRICS}
    
    prompt_template = prompt_match.group(2).strip()
    
    model = ChatOpenAI(model="gpt-4o", temperature=0.0)
    
    scores = {metric: 0.0 for metric in EVALUATION_METRICS}
    num_cases = len(training_data)
    
    for test_case in training_data:
        try:
            formatted_prompt = prompt_template.format(**test_case)
        except:
            formatted_prompt = prompt_template
            
        response = model.invoke([HumanMessage(content=formatted_prompt)])
        llm_output = response.content
        
        eval_prompt = f"""You are evaluating a PROMPT TEMPLATE and the output it generates.

ORIGINAL PROMPT TEMPLATE:
{prompt_template}

TEST PARAMETERS: {test_case}
FORMATTED PROMPT SENT TO LLM:
{formatted_prompt}

LLM RESPONSE TO THE PROMPT:
{llm_output}

EVALUATION CRITERIA FOR INTENT CLASSIFICATION:

1. ACCURACY ASSESSMENT:
   - Does the LLM output match the expected_intent exactly?
   - How reliably does the prompt produce correct classifications?
   - Are the classification instructions clear enough for consistent results?

2. PROMPT QUALITY (Secondary):
   - Is the prompt clear and well-structured?
   - Does it provide adequate context and examples?
   - Are the intent categories clearly defined?

EVALUATION APPROACH:
For intent classification, calculate accuracy by comparing LLM output with expected_intent:
- If LLM output == expected_intent: Contribute 1.0 to accuracy
- If LLM output != expected_intent: Contribute 0.0 to accuracy
- Average across all test cases for final accuracy score

Rate on these EXACT metrics (0.0-1.0 scale):
- accuracy: Primary metric - exact match between LLM output and expected_intent
- clarity: Secondary metric - how clear are the prompt instructions
- effectiveness: Secondary metric - overall prompt performance  
- consistency: Secondary metric - how consistently the prompt performs

Return ONLY JSON with exact metric names."""
        
        eval_response = model.invoke([HumanMessage(content=eval_prompt)])
        case_scores = parse_json_response(eval_response.content)
        
        for metric in EVALUATION_METRICS:
            scores[metric] += case_scores[metric]
    
    for metric in EVALUATION_METRICS:
        scores[metric] /= num_cases
        
    return scores