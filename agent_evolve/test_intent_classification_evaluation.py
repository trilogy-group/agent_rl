#!/usr/bin/env python3
"""
Test the correct intent classification evaluation approach
"""

import json
import re


def test_intent_classification_evaluation():
    """Test how intent classification should be evaluated"""
    
    print("🎯 Intent Classification Evaluation")
    print("=" * 40)

    # Sample training data (what was updated)
    training_data = [
        {
            "user_message": "Draft a LinkedIn post on sustainable energy",
            "expected_intent": "research_and_write"
        },
        {
            "user_message": "Can you provide feedback on this draft?",
            "expected_intent": "improve_and_rewrite_draft"
        },
        {
            "user_message": "How do I get to the nearest gas station?",
            "expected_intent": "other"
        }
    ]
    
    # Sample prompt template
    orchestrator_prompt = """You are an orchestrator that determines what the user wants to do. 
Analyze the user's message and determine if they want to:
1. "research_and_write" - They want to research a topic and write a LinkedIn post about it
2. "improve_and_rewrite_draft" - They are providing feedback on an existing draft and want to improve it based on their feedback
3. "other" - They want something else that doesn't involve research and writing

### Examples
Write a LinkedIn post about 'The Impact of AI on Society'. - Intent: research_and_write
Create a LinkedIn post on remote work trends. - Intent: research_and_write
Make this more engaging and add a call to action. - Intent: improve_and_rewrite_draft
What is the weather in Tokyo? - Intent: other

Respond with just the category name: either "research_and_write", "improve_and_rewrite_draft", or "other"."""

    print("📊 Evaluation Approach for Intent Classification:")
    print("─" * 50)
    
    accuracy_scores = []
    
    for i, test_case in enumerate(training_data, 1):
        user_message = test_case["user_message"]
        expected_intent = test_case["expected_intent"]
        
        print(f"\n🧪 Test Case {i}:")
        print(f"  Input: {user_message}")
        print(f"  Expected: {expected_intent}")
        
        # Format the prompt with the user message
        formatted_prompt = f"{orchestrator_prompt}\n\nUser message: {user_message}"
        
        # Simulate LLM response (in real evaluation, this would be sent to LLM)
        # For demo, assume perfect classification
        simulated_llm_output = expected_intent
        print(f"  LLM Output: {simulated_llm_output}")
        
        # Calculate accuracy - this is the KEY difference for classification
        if simulated_llm_output.strip().lower() == expected_intent.strip().lower():
            case_accuracy = 1.0
            print(f"  ✅ Correct classification: accuracy = 1.0")
        else:
            case_accuracy = 0.0
            print(f"  ❌ Wrong classification: accuracy = 0.0")
        
        accuracy_scores.append(case_accuracy)
    
    # Calculate overall accuracy
    overall_accuracy = sum(accuracy_scores) / len(accuracy_scores)
    
    print(f"\n📈 Overall Results:")
    print(f"  Test Cases: {len(training_data)}")
    print(f"  Correct: {sum(accuracy_scores)}")
    print(f"  Accuracy: {overall_accuracy:.2f}")
    
    print(f"\n🎯 Key Differences for Intent Classification:")
    print("─" * 50)
    
    differences = [
        "✅ Primary Metric: ACCURACY (exact match with expected_intent)",
        "✅ Evaluation Method: Compare LLM output == expected_intent", 
        "✅ Scoring: 1.0 for correct, 0.0 for incorrect",
        "✅ Focus: Classification correctness, not prompt aesthetics",
        "",
        "❌ Wrong: Subjective prompt quality metrics",
        "❌ Wrong: Evaluating 'clarity' or 'specificity' primarily",
        "❌ Wrong: Complex multi-dimensional scoring for simple classification"
    ]
    
    for diff in differences:
        print(f"  {diff}")
    
    print(f"\n💡 Correct Evaluator Structure for Intent Classification:")
    print("─" * 60)
    
    evaluator_structure = """
def evaluate(program) -> dict:
    # Load training data
    with open('training_data.json', 'r') as f:
        training_data = json.load(f)
    
    # Extract prompt template from evolve_target.py
    with open(program, 'r') as f:
        content = f.read()
    prompt_template = extract_prompt_from_file(content)
    
    # Initialize LLM
    model = ChatOpenAI(model="gpt-4o", temperature=0.0)
    
    correct_count = 0
    total_count = len(training_data)
    
    for test_case in training_data:
        # Format prompt with user message
        formatted_prompt = f"{prompt_template}\\n\\nUser message: {test_case['user_message']}"
        
        # Send to LLM
        response = model.invoke([HumanMessage(content=formatted_prompt)])
        llm_output = response.content.strip()
        
        # Calculate accuracy (exact match)
        if llm_output.lower() == test_case['expected_intent'].lower():
            correct_count += 1
    
    # Return accuracy as primary metric
    accuracy = correct_count / total_count
    return {
        'accuracy': accuracy,
        'clarity': accuracy,  # For compatibility, but accuracy is primary
        'effectiveness': accuracy,
        'consistency': accuracy
    }
"""
    
    print(evaluator_structure)
    
    print(f"\n🚀 This approach ensures:")
    print(f"  • Intent classification accuracy is properly measured")
    print(f"  • Prompt optimization focuses on classification correctness")  
    print(f"  • Evolution improves the prompt's ability to classify intents")
    print(f"  • Metrics reflect actual task performance, not subjective quality")


if __name__ == "__main__":
    test_intent_classification_evaluation()