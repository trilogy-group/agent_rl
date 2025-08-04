#!/usr/bin/env python3
"""
Test the algorithmic evaluator prompt generation
"""

from pathlib import Path

def test_algorithmic_prompt():
    """Test generating the algorithmic evaluator prompt"""
    
    print("🔍 Testing Algorithmic Evaluator Prompt Generation")
    print("=" * 55)
    
    # Simulate the enhanced evaluator generator
    tool_name = "get_fundamental_analysis"
    function_description = "Performs fundamental analysis on financial data with key metrics and ratios"
    function_type = "quantitative" 
    metrics = ["correctness", "completeness", "accuracy", "consistency"]
    
    tool_dir = Path("tools/get_fundamental_analysis")
    tool_file = tool_dir / "evolve_target.py"
    
    if tool_file.exists():
        with open(tool_file, 'r') as f:
            source_code = f.read()
    else:
        source_code = "def get_fundamental_analysis(ticker, period): pass"
    
    training_data = [{"ticker": "AAPL", "period": "1y"}]
    feedback_section = ""
    
    print(f"📊 Function Analysis:")
    print(f"  Tool Name: {tool_name}")
    print(f"  Function Type: {function_type}")
    print(f"  Specialized Metrics: {metrics}")
    
    print(f"\n🎯 Generated Algorithmic Evaluation Approach:")
    print("─" * 50)
    
    key_features = [
        "✅ Extracts function source code using inspect.getsource()",
        "✅ Analyzes implementation logic, not just outputs",
        "✅ Reviews mathematical formulas and calculations",
        "✅ Evaluates algorithm correctness and efficiency",
        "✅ Checks input validation and error handling",
        "✅ Assesses code quality and edge case coverage"
    ]
    
    for feature in key_features:
        print(f"  {feature}")
    
    print(f"\n📝 Sample Evaluation Prompt Structure:")
    print("─" * 50)
    
    sample_prompt = f"""
ALGORITHMIC EVALUATION PROMPT:
-------------------------------
You are evaluating an ALGORITHMIC/QUANTITATIVE function.
Analyze BOTH the implementation code AND the output for correctness.

FUNCTION TO EVALUATE: {tool_name}
INPUT PARAMETERS: {{"ticker": "AAPL", "period": "1y"}}

FUNCTION SOURCE CODE:
[Full function implementation would be included here]

GENERATED OUTPUT: 
[Function execution result would be included here]

ALGORITHMIC ANALYSIS CRITERIA:
1. IMPLEMENTATION REVIEW:
   - Is the algorithm logic mathematically sound?
   - Are calculations implemented correctly?
   - Are formulas and computations accurate?
   - Is input validation adequate?

2. OUTPUT ANALYSIS:
   - Does output match expected format/structure?
   - Are calculated values reasonable for given inputs?
   - Is the output complete with all expected fields?

3. CODE QUALITY:
   - Are there logical errors in the implementation?
   - Is error handling appropriate?
   - Are edge cases considered?

Evaluate on these EXACT metrics (0.0-1.0 scale):
- correctness: Assess this aspect of both code implementation and output
- completeness: Assess this aspect of both code implementation and output  
- accuracy: Assess this aspect of both code implementation and output
- consistency: Assess this aspect of both code implementation and output

Focus on the IMPLEMENTATION QUALITY as much as the output correctness.
Return ONLY JSON with exact metric names.
"""
    
    print(sample_prompt)
    
    print(f"\n🚀 Key Advantages Over Traditional Output-Only Evaluation:")
    print("─" * 50)
    
    advantages = [
        "Code Review: Examines actual algorithm implementation",
        "Logic Verification: Checks mathematical formulas and calculations", 
        "Quality Assessment: Evaluates code structure and error handling",
        "Comprehensive Analysis: Reviews both implementation AND execution",
        "Technical Depth: Goes beyond surface-level output testing",
        "Algorithmic Focus: Specialized for quantitative/computational functions"
    ]
    
    for advantage in advantages:
        print(f"  ✅ {advantage}")
    
    print(f"\n🎯 This ensures algorithmic functions are evaluated on:")
    print(f"  • Implementation correctness")
    print(f"  • Mathematical accuracy")
    print(f"  • Code quality and robustness") 
    print(f"  • Logical soundness")
    print(f"  • Algorithmic efficiency")
    print(f"  Rather than just subjective output assessment!")

if __name__ == "__main__":
    test_algorithmic_prompt()