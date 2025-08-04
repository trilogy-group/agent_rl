#!/usr/bin/env python3
"""
Test the correct prompt evaluation approach
"""

import json
import re


def test_prompt_evaluation_workflow():
    """Demonstrate the correct prompt evaluation workflow"""
    
    print("🎯 CORRECT Prompt Evaluation Workflow")
    print("=" * 50)
    
    # Simulate reading the evolve_target.py file
    evolve_target_content = '''"""
Tool: orchestrator_prompt
Extracted from: tools.py
Type: Prompt/Template Constant

Prompt/template constant: ORCHESTRATOR_PROMPT
"""

# The target prompt/template for evolution
ORCHESTRATOR_PROMPT = """You are an orchestrator that determines what the user wants to do. 
Analyze the user's message and determine if they want to:
1. "research_and_write" - They want to research a topic and write a LinkedIn post about it
2. "improve_and_rewrite_draft" - They are providing feedback on an existing draft and want to improve it based on their feedback
3. "other" - They want something else that doesn't involve research and writing


### Examples
Write a LinkedIn post about 'The Impact of AI on Society'. - Intent: research_and_write
Create a LinkedIn post on remote work trends. - Intent: research_and_write
Make this more engaging and add a call to action. - Intent: improve_and_rewrite_draft
What is the weather in Tokyo? - Intent: other
"

Respond with just the category name: either "research_and_write", "improve_and_rewrite_draft", or "other"."""


def orchestrator_prompt():
    """Return the optimized prompt/template"""
    return ORCHESTRATOR_PROMPT
'''
    
    # Training data for prompt evaluation
    training_data = [
        {
            "user_message": "Write a LinkedIn post about AI in healthcare",
            "expected_intent": "research_and_write"
        },
        {
            "user_message": "Make this more engaging",
            "expected_intent": "improve_and_rewrite_draft"
        },
        {
            "user_message": "What's the weather today?",
            "expected_intent": "other"
        }
    ]
    
    print("📝 Step 1: Extract Prompt Template")
    print("─" * 30)
    
    # Extract the prompt template from the file  
    prompt_match = re.search(r'([A-Z_]+)\s*=\s*"""(.*?)"""', evolve_target_content, re.DOTALL)
    prompt_template = ""
    if prompt_match:
        prompt_name = prompt_match.group(1)
        prompt_template = prompt_match.group(2).strip()
        print(f"✅ Found prompt: {prompt_name}")
        print(f"✅ Template length: {len(prompt_template)} characters")
        print(f"✅ Template preview: {prompt_template[:100]}...")
    else:
        print("❌ Could not extract prompt template")
        return
    
    print(f"\n🧪 Step 2: Test Prompt with Training Data")
    print("─" * 40)
    
    for i, test_case in enumerate(training_data, 1):
        print(f"\n📋 Test Case {i}:")
        print(f"  User Message: {test_case['user_message']}")
        print(f"  Expected Intent: {test_case['expected_intent']}")
        
        # The ORCHESTRATOR_PROMPT doesn't use .format() - it's used as context
        # In real evaluation, we'd send: prompt + "\n\nUser message: " + user_message
        formatted_prompt = f"{prompt_template}\n\nUser message: {test_case['user_message']}"
        
        print(f"  📤 Formatted prompt length: {len(formatted_prompt)} chars")
        print(f"  🤖 Would send to LLM: [PROMPT + USER MESSAGE]")
        
        # Simulate LLM response
        simulated_llm_response = test_case['expected_intent']  # Perfect response for demo
        print(f"  📥 Simulated LLM response: '{simulated_llm_response}'")
        
        # Create evaluation prompt
        eval_prompt = f"""You are evaluating a PROMPT TEMPLATE and the output it generates.

ORIGINAL PROMPT TEMPLATE:
{prompt_template}

TEST PARAMETERS: {test_case}
FORMATTED PROMPT SENT TO LLM:
{formatted_prompt}

LLM RESPONSE TO THE PROMPT:
{simulated_llm_response}

EVALUATION CRITERIA:
1. PROMPT QUALITY:
   - Is the prompt clear and well-structured?
   - Does it provide adequate context and instructions?
   - Is the language precise and unambiguous?

2. OUTPUT EFFECTIVENESS:
   - Does the LLM response align with the prompt's intent?
   - Is the output relevant and appropriate?
   - Does the prompt successfully guide the LLM behavior?

3. PROMPT ENGINEERING:
   - Does the prompt handle the input parameters well?
   - Is the prompt format optimal for LLM understanding?
   - Could the prompt be improved for better results?

Rate on these EXACT metrics (0.0-1.0 scale):
- clarity: Evaluate prompt clarity and instructions
- specificity: Evaluate how specific the prompt requirements are
- effectiveness: Evaluate how well the prompt achieves its goal
- completeness: Evaluate if the prompt covers all necessary aspects

Return ONLY JSON with exact metric names."""
        
        print(f"  📊 Evaluation prompt created: {len(eval_prompt)} chars")
        
        # Simulate evaluation response
        simulated_eval_response = """```json
{
  "clarity": 0.85,
  "specificity": 0.80,
  "effectiveness": 0.90,
  "completeness": 0.75
}
```"""
        
        print(f"  📈 Simulated evaluation: clarity=0.85, effectiveness=0.90")
    
    print(f"\n🎯 Key Differences from Function Evaluation:")
    print("─" * 50)
    
    differences = [
        "❌ Functions: Execute code → Compare output to expected",
        "✅ Prompts: Format template → Send to LLM → Evaluate response",
        "",
        "❌ Functions: Training data has input/output pairs",  
        "✅ Prompts: Training data has template parameters only",
        "",
        "❌ Functions: Direct output comparison",
        "✅ Prompts: Qualitative evaluation of LLM response",
        "",
        "❌ Functions: Code execution evaluation",
        "✅ Prompts: Prompt engineering effectiveness evaluation"
    ]
    
    for diff in differences:
        print(f"  {diff}")
    
    print(f"\n✨ Prompt Evaluation Flow Summary:")
    print("─" * 40)
    
    flow_steps = [
        "1. 📂 Extract prompt template from evolve_target.py",
        "2. 📋 Load training data (parameters, not input/output)",
        "3. 🔧 Format prompt with test parameters",
        "4. 🤖 Send formatted prompt to LLM",
        "5. 📥 Receive LLM response",
        "6. 📊 Create evaluation prompt for response quality",
        "7. 🎯 Send evaluation prompt to LLM",
        "8. 📈 Parse evaluation scores (clarity, effectiveness, etc.)",
        "9. 🔄 Repeat for all test cases",
        "10. 📊 Return averaged evaluation metrics"
    ]
    
    for step in flow_steps:
        print(f"  {step}")
    
    print(f"\n🚀 This approach will properly optimize prompts for:")
    print(f"  • Better instruction clarity")
    print(f"  • More specific guidance")
    print(f"  • Improved LLM response quality")
    print(f"  • Enhanced task completion effectiveness")


if __name__ == "__main__":
    test_prompt_evaluation_workflow()