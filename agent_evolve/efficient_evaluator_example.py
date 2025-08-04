#!/usr/bin/env python3
"""
Example of efficient evaluator that scores ALL metrics in a single LLM request
"""

import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

def demonstrate_efficient_evaluation():
    """Show the difference between inefficient and efficient evaluation approaches"""
    
    print("=== INEFFICIENT APPROACH (CURRENT PROBLEM) ===")
    print("❌ Makes separate LLM request for each metric:")
    
    inefficient_code = '''
# BAD: Multiple LLM requests per test case
for metric in expected_criteria:
    evaluation_prompt = f"Evaluate the following reflection for {metric}: {reflection}"
    evaluation_response = model.invoke([HumanMessage(content=evaluation_prompt)])  # SEPARATE REQUEST!
    evaluation_scores[metric] = float(evaluation_response.content.strip())

# Result: 30 test cases × 4 metrics = 120 LLM requests!
'''
    print(inefficient_code)
    
    print("=== EFFICIENT APPROACH (SOLUTION) ===") 
    print("✅ Makes single LLM request to score ALL metrics:")
    
    efficient_code = '''
# GOOD: Single LLM request per test case
evaluation_prompt = f"""
Evaluate the following content on these quality dimensions (score 0.0-1.0):

Content to evaluate:
{tool_output}

Please provide scores in this exact format:
specificity: 0.X
constructiveness: 0.X
actionability: 0.X
comprehensiveness: 0.X
accuracy: 0.X
"""

response = model.invoke([HumanMessage(content=evaluation_prompt)])
# Parse all scores from single response
scores = parse_scores(response.content)

# Result: 30 test cases × 1 request = 30 LLM requests total!
'''
    print(efficient_code)
    
    print("=== COMPARISON ===")
    print("❌ INEFFICIENT: 120 LLM requests (30 cases × 4 metrics)")
    print("✅ EFFICIENT: 30 LLM requests (30 cases × 1 request)")
    print("🚀 IMPROVEMENT: 75% reduction in API calls!")
    
    print("\n=== EXAMPLE EFFICIENT EVALUATION PROMPT ===")
    
    example_prompt = '''
Evaluate the following LinkedIn post critique on these quality dimensions (score 0.0-1.0):

Critique to evaluate:
"This post has good energy but could be improved by adding specific metrics, 
including a clearer call-to-action, and using more targeted hashtags like 
#ProductLaunch instead of generic #innovation."

Please provide scores in this exact format:
specificity: 0.8
constructiveness: 0.9
actionability: 0.7
comprehensiveness: 0.6
accuracy: 0.8
'''
    
    print(example_prompt)
    
    print("=== PARSING THE RESPONSE ===")
    parsing_code = '''
def parse_metric_scores(response_text: str) -> Dict[str, float]:
    """Parse structured LLM response to extract metric scores"""
    scores = {}
    for line in response_text.strip().split('\\n'):
        if ':' in line:
            metric, score = line.split(':', 1)
            scores[metric.strip()] = float(score.strip())
    return scores
'''
    print(parsing_code)

if __name__ == "__main__":
    demonstrate_efficient_evaluation()