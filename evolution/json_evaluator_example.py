#!/usr/bin/env python3
"""
Example of reliable JSON-based evaluator parsing
"""

import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

def demonstrate_json_evaluation():
    """Show the difference between unreliable line parsing and reliable JSON parsing"""
    
    print("=== UNRELIABLE LINE PARSING (CURRENT PROBLEM) ===")
    print("❌ Fragile string parsing that can easily break:")
    
    unreliable_code = '''
# BAD: Fragile line parsing
for line in response.content.split('\\n'):
    for metric in metrics:
        if line.startswith(metric):
            try:
                scores[metric] = float(line.split(':')[1].strip())
            except (IndexError, ValueError):
                scores[metric] = 0.0  # Fails silently!

# Problems:
# - LLM might format differently: "Engagement Potential: 0.8" vs "engagement_potential: 0.8"
# - Extra text breaks parsing: "The engagement_potential score is: 0.8 (good)"
# - Missing colons, different separators, line breaks in unexpected places
# - Silent failures with 0.0 defaults
'''
    print(unreliable_code)
    
    print("=== RELIABLE JSON PARSING (SOLUTION) ===") 
    print("✅ Robust JSON parsing with proper error handling:")
    
    reliable_code = '''
# GOOD: Reliable JSON parsing
evaluation_prompt = f"""
Evaluate the following content on these quality dimensions (score 0.0-1.0):

Content to evaluate:
{tool_output}

Return your evaluation as a JSON object with the following structure:
{{
    "specificity": 0.8,
    "constructiveness": 0.9,
    "actionability": 0.7,
    "comprehensiveness": 0.6,
    "accuracy": 0.8
}}

IMPORTANT: Return ONLY the JSON object, no additional text.
"""

response = model.invoke([SystemMessage(content=evaluation_prompt)])

# Safe JSON parsing with error handling
try:
    scores = json.loads(response.content.strip())
    # Validate all expected metrics are present
    for metric in expected_metrics:
        if metric not in scores:
            scores[metric] = 0.0
        else:
            # Ensure values are floats in valid range
            scores[metric] = max(0.0, min(1.0, float(scores[metric])))
except (json.JSONDecodeError, ValueError, TypeError) as e:
    print(f"JSON parsing failed: {e}")
    # Fallback to default scores
    scores = {metric: 0.0 for metric in expected_metrics}
'''
    print(reliable_code)
    
    print("=== JSON PROMPT EXAMPLE ===")
    
    example_prompt = '''
Evaluate the following LinkedIn post critique on these quality dimensions (score 0.0-1.0):

Critique to evaluate:
"This post has good energy but could be improved by adding specific metrics, 
including a clearer call-to-action, and using more targeted hashtags like 
#ProductLaunch instead of generic #innovation."

Return your evaluation as a JSON object with the following structure:
{
    "specificity": 0.8,
    "constructiveness": 0.9,
    "actionability": 0.7,
    "comprehensiveness": 0.6,
    "accuracy": 0.8
}

IMPORTANT: Return ONLY the JSON object, no additional text.
'''
    
    print(example_prompt)
    
    print("=== EXPECTED LLM RESPONSE ===")
    expected_response = '''{
    "specificity": 0.8,
    "constructiveness": 0.9,
    "actionability": 0.7,
    "comprehensiveness": 0.6,
    "accuracy": 0.8
}'''
    print(expected_response)
    
    print("\n=== BENEFITS OF JSON PARSING ===")
    print("✅ **Structured Format**: Clear, unambiguous structure")
    print("✅ **Reliable Parsing**: json.loads() handles edge cases")
    print("✅ **Error Handling**: Graceful fallback when parsing fails")
    print("✅ **Validation**: Can check for missing metrics and valid ranges")
    print("✅ **Extensible**: Easy to add new metrics without changing parsing logic")
    print("✅ **Consistent**: Same format regardless of LLM variations")

    print("\n=== ERROR HANDLING EXAMPLES ===")
    error_examples = [
        ("Malformed JSON", '{"specificity": 0.8, "constructiveness": }'),
        ("Extra text", 'Here are the scores: {"specificity": 0.8}'),
        ("Wrong format", 'specificity: 0.8, constructiveness: 0.9'),
        ("Missing metrics", '{"specificity": 0.8}'),
        ("Invalid values", '{"specificity": 1.5, "constructiveness": -0.2}')
    ]
    
    for error_type, example in error_examples:
        print(f"❌ **{error_type}**: `{example}`")
        print("   → Handled gracefully with fallback scores")

if __name__ == "__main__":
    demonstrate_json_evaluation()