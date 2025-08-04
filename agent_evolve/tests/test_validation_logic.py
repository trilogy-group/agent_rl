#!/usr/bin/env python3
"""
Test the validation logic without calling LLM APIs
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from generate_evaluators import EvaluatorGenerator
    
    # Create generator instance (without API key needed for testing validation)
    generator = EvaluatorGenerator()
    
    # Read the current broken evaluator code
    tool_dir = Path("tools/get_technical_analysis")
    evaluator_file = tool_dir / "evaluator.py"
    
    with open(evaluator_file, 'r') as f:
        evaluator_code = f.read()
    
    print("🔍 Testing validation logic on current evaluator:")
    print(f"Evaluator length: {len(evaluator_code)} chars")
    
    # Test the analysis function
    analysis = generator._analyze_evaluator(evaluator_code, tool_dir)
    
    print(f"\n📊 Analysis Results:")
    print(f"Main function detected: {analysis.get('main_function', 'Not found')}")
    print(f"Issues found: {len(analysis['issues'])}")
    
    for i, issue in enumerate(analysis['issues'], 1):
        print(f"  {i}. {issue}")
    
    print(f"\nFixes suggested: {len(analysis['fixes'])}")
    for i, fix in enumerate(analysis['fixes'], 1):
        print(f"  {i}. {fix}")
    
    # Test the fix application
    if analysis['fixes']:
        print("\n🔧 Testing fix application:")
        fixed_code = generator._fix_evaluator_code(evaluator_code, analysis)
        
        if fixed_code != evaluator_code:
            print("✅ Code was modified by fixes")
            print(f"Original length: {len(evaluator_code)}")
            print(f"Fixed length: {len(fixed_code)}")
            
            # Show the key difference
            if "tool_module.analyze_macd" in evaluator_code and "tool_module.get_technical_analysis" in fixed_code:
                print("✅ Successfully fixed function call: analyze_macd → get_technical_analysis")
        else:
            print("❌ No changes applied")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()