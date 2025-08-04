#!/usr/bin/env python3
"""
Test just the validation logic without LLM initialization
"""

import os
import sys
import json
import ast
import re
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def analyze_evaluator_standalone(evaluator_code: str, tool_dir: Path):
    """Standalone version of the analyzer without LLM dependencies"""
    
    tool_name = tool_dir.name
    tool_file = tool_dir / "evolve_target.py"
    training_data_file = tool_dir / "training_data.json"
    
    issues = []
    fixes = []
    
    # Read tool source to understand the main function
    try:
        with open(tool_file, 'r') as f:
            tool_source = f.read()
    except:
        return {"issues": ["Could not read tool source"], "fixes": []}
    
    # Read training data to understand expected inputs
    try:
        with open(training_data_file, 'r') as f:
            training_data = json.load(f)
            sample_input = training_data[0] if training_data else {}
    except:
        return {"issues": ["Could not read training data"], "fixes": []}
    
    # Find the main function name from tool source
    try:
        tree = ast.parse(tool_source)
        main_functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip helper functions, find the main tool function
                if not node.name.startswith('_') and node.name not in ['main', 'test']:
                    main_functions.append(node.name)
        
        # The main function is likely the one matching the tool name or the longest one
        main_function = None
        if main_functions:
            # Try to find function matching tool name pattern
            for func in main_functions:
                if tool_name.replace('_', '').lower() in func.replace('_', '').lower():
                    main_function = func
                    break
            
            # Fallback to first non-helper function
            if not main_function:
                main_function = main_functions[0]
    except:
        main_function = None
    
    print(f"  Detected main function: {main_function}")
    
    # Check 1: Wrong function being called (getattr pattern)
    if main_function:
        if f"getattr(tool_module, '{main_function}')" not in evaluator_code:
            # Find what function is being called with getattr
            getattr_matches = re.findall(r"getattr\(tool_module,\s*['\"]([^'\"]+)['\"]", evaluator_code)
            if getattr_matches:
                wrong_function = getattr_matches[0]
                issues.append(f"Wrong function called: '{wrong_function}' instead of '{main_function}'")
                fixes.append(f"Replace 'getattr(tool_module, '{wrong_function}')' with 'getattr(tool_module, '{main_function}')'")
            else:
                issues.append(f"Could not find getattr call for main function '{main_function}'")
                fixes.append(f"Add 'tool_function = getattr(tool_module, '{main_function}')'")
    
    # Check 1b: Wrong function being called (direct call pattern)
    if main_function:
        # Check for direct tool_module.function_name() calls
        direct_call_pattern = r"tool_module\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
        direct_matches = re.findall(direct_call_pattern, evaluator_code)
        if direct_matches:
            for called_function in direct_matches:
                if called_function != main_function:
                    issues.append(f"Direct wrong function call: 'tool_module.{called_function}()' instead of 'tool_module.{main_function}()'")
                    fixes.append(f"Replace 'tool_module.{called_function}(' with 'tool_module.{main_function}('")
    
    # Check 2: Error handling for tool execution  
    has_try_except = re.search(r'\btry\s*:', evaluator_code) and re.search(r'\bexcept\b', evaluator_code)
    # Check if the try block contains the tool function call
    has_tool_error_handling = False
    if has_try_except:
        # Look for tool function calls inside try blocks
        if f"tool_module.{main_function}" in evaluator_code or "tool_function(" in evaluator_code:
            # Check if there's a try block around tool calls
            try_sections = evaluator_code.split("try:")
            for section in try_sections[1:]:  # Skip first split (before any try)
                except_pos = section.find("except")
                if except_pos != -1:
                    try_content = section[:except_pos]
                    if f"tool_module.{main_function}" in try_content or "tool_function(" in try_content:
                        has_tool_error_handling = True
                        break
    
    if not has_tool_error_handling:
        issues.append("No error handling for tool execution")
        fixes.append("Add try-except block around tool function call")
    
    return {
        "issues": issues,
        "fixes": fixes,
        "main_function": main_function,
        "training_data_structure": type(training_data).__name__,
        "sample_input": sample_input
    }

try:
    # Read the current broken evaluator code
    tool_dir = Path("tools/get_technical_analysis")
    evaluator_file = tool_dir / "evaluator.py"
    
    with open(evaluator_file, 'r') as f:
        evaluator_code = f.read()
    
    print("🔍 Testing validation logic on current evaluator:")
    print(f"Evaluator length: {len(evaluator_code)} chars")
    
    # Test the analysis function
    analysis = analyze_evaluator_standalone(evaluator_code, tool_dir)
    
    print(f"\n📊 Analysis Results:")
    print(f"Main function detected: {analysis.get('main_function', 'Not found')}")
    print(f"Issues found: {len(analysis['issues'])}")
    
    for i, issue in enumerate(analysis['issues'], 1):
        print(f"  {i}. {issue}")
    
    print(f"\nFixes suggested: {len(analysis['fixes'])}")
    for i, fix in enumerate(analysis['fixes'], 1):
        print(f"  {i}. {fix}")
    
    # Test if we can detect the specific issue
    if "tool_module.analyze_macd" in evaluator_code:
        print("\n🐛 Current Issue Detected:")
        print("❌ Evaluator is calling 'tool_module.analyze_macd()' instead of 'tool_module.get_technical_analysis()'")
        
        # Check if our validation logic catches this
        direct_call_issues = [issue for issue in analysis['issues'] if "Direct wrong function call" in issue and "analyze_macd" in issue]
        if direct_call_issues:
            print("✅ Validation logic correctly detected the direct function call issue!")
        else:
            print("❌ Validation logic missed the direct function call issue")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()