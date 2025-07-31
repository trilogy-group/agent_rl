#!/usr/bin/env python3
"""
Test script demonstrating proper blind evaluation for NLG tools
"""

import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

def test_blind_evaluation():
    """Demonstrate proper blind evaluation approach"""
    
    # Example training data with quality criteria instead of expected text
    proper_training_data = [
        {
            "input": {
                "draft": "Excited to announce our new product launch next month! Stay tuned for more updates. #innovation #tech"
            },
            "expected_output": {
                "quality_criteria": ["professional_tone", "clear_messaging", "appropriate_length"],
                "min_coherence_score": 0.7,
                "min_relevance_score": 0.6,
                "min_completeness_score": 0.5,
                "min_creativity_score": 0.6
            },
            "category": "quality_assessment",
            "description": "Tests critique quality for product launch announcement"
        }
    ]
    
    # Simulate tool output (what reflect_on_draft might return)
    tool_output = """This LinkedIn post has good energy and professional tone. However, it could be improved by:
    1. Adding more specific details about the product
    2. Including a clear call-to-action for reader engagement  
    3. Using more targeted hashtags beyond generic #innovation
    4. Providing a timeline or teaser to build anticipation
    Overall, it follows LinkedIn best practices but lacks depth and engagement elements."""
    
    print("=== PROPER BLIND EVALUATION APPROACH ===")
    print(f"Tool Output: {tool_output}")
    print()
    
    # This is how the evaluator SHOULD work - blind assessment
    blind_evaluation_prompt = """
    Evaluate the following LinkedIn post critique on these dimensions (score 0.0-1.0):

    Critique to evaluate:
    {tool_output}

    Please provide scores for:
    1. Coherence: How well-structured and logical is the critique?
    2. Relevance: How relevant are the suggestions to LinkedIn content?
    3. Completeness: How thorough is the analysis?
    4. Creativity: How innovative are the improvement suggestions?

    Return only the scores in this format:
    Coherence: 0.X
    Relevance: 0.X  
    Completeness: 0.X
    Creativity: 0.X
    """
    
    print("BLIND EVALUATION PROMPT (GOOD):")
    print(blind_evaluation_prompt.format(tool_output=tool_output))
    print()
    
    # This is the WRONG approach that was being used
    wrong_evaluation_prompt = f"""
    Evaluate the following critique based on the expected characteristics:
    
    Generated Critique: {tool_output}
    
    Expected Characteristics:
    - Engagement potential: "Strong hook with excitement, but could improve by adding a question to engage readers."
    - Professional tone: "Maintains a professional tone, but could enhance authenticity with a personal story."  
    - Length appropriateness: "Appropriate length, concise and to the point."
    
    Provide scores for coherence, relevance, completeness, creativity.
    """
    
    print("BIASED EVALUATION PROMPT (BAD - shows expected answers):")
    print(wrong_evaluation_prompt)
    print()
    
    print("=== KEY DIFFERENCES ===")
    print("✅ GOOD: Evaluates output blindly without showing expected answers")
    print("❌ BAD: Shows expected answers to the LLM, making evaluation meaningless")
    print()
    print("✅ GOOD: Training data has quality criteria and minimum thresholds")  
    print("❌ BAD: Training data has detailed expected text content")

if __name__ == "__main__":
    test_blind_evaluation()