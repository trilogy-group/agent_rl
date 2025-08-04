#!/usr/bin/env python3
"""
Debug the error handling detection
"""

from pathlib import Path

# Read the evaluator code
tool_dir = Path("tools/get_technical_analysis")
evaluator_file = tool_dir / "evaluator.py"

with open(evaluator_file, 'r') as f:
    evaluator_code = f.read()

main_function = "get_technical_analysis"

print("🔍 Debugging error handling detection:")
print(f"Main function: {main_function}")

# Check basic conditions
has_try_except = "try:" in evaluator_code and "except:" in evaluator_code
print(f"Has try/except: {has_try_except}")

# Check for tool function calls
has_tool_calls = f"tool_module.{main_function}" in evaluator_code or "tool_function(" in evaluator_code
print(f"Has tool calls: {has_tool_calls}")

if has_try_except and has_tool_calls:
    print("\n🔍 Analyzing try blocks:")
    try_sections = evaluator_code.split("try:")
    print(f"Number of try blocks: {len(try_sections) - 1}")
    
    for i, section in enumerate(try_sections[1:], 1):
        except_pos = section.find("except")
        if except_pos != -1:
            try_content = section[:except_pos]
            print(f"\nTry block {i}:")
            print(f"  Length: {len(try_content)}")
            print(f"  Contains tool_module.{main_function}: {f'tool_module.{main_function}' in try_content}")
            print(f"  Contains tool_function(: {'tool_function(' in try_content}")
            
            # Show a snippet of the try content
            lines = try_content.strip().split('\n')[:5]
            for line in lines:
                print(f"    {line}")
            if len(try_content.strip().split('\n')) > 5:
                print("    ...")

print(f"\n🔍 Raw search results:")
print(f"'tool_module.get_technical_analysis' in code: {'tool_module.get_technical_analysis' in evaluator_code}")
print(f"'tool_function(' in code: {'tool_function(' in evaluator_code}")

# Show the specific lines around the tool call
lines = evaluator_code.split('\n')
for i, line in enumerate(lines):
    if 'tool_module.get_technical_analysis' in line:
        print(f"\nFound tool call at line {i+1}:")
        start = max(0, i-3)
        end = min(len(lines), i+4)
        for j in range(start, end):
            marker = ">>> " if j == i else "    "
            print(f"{marker}{j+1:3d}: {lines[j]}")