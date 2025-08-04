#!/usr/bin/env python3

# Direct test of the extraction logic
import re
from pathlib import Path

def extract_metrics(tool_dir_name):
    evaluator_file = Path(f"tools/{tool_dir_name}/evaluator.py")
    
    if not evaluator_file.exists():
        print(f"File not found: {evaluator_file}")
        return None
    
    try:
        with open(evaluator_file, 'r') as f:
            evaluator_code = f.read()
        
        print(f"\n=== Testing {tool_dir_name} ===")
        
        # Look for EVALUATION_METRICS = [...] pattern
        metrics_pattern = r'EVALUATION_METRICS\s*=\s*\[([^\]]+)\]'
        metrics_match = re.search(metrics_pattern, evaluator_code)
        
        if metrics_match:
            print(f"✓ Found EVALUATION_METRICS pattern")
            metrics_content = metrics_match.group(1)
            print(f"  Content: {metrics_content}")
            
            # Find all quoted strings - try single quotes first
            metric_matches = re.findall(r"'([^']+)'", metrics_content)
            if not metric_matches:
                metric_matches = re.findall(r'"([^"]+)"', metrics_content)
            
            if metric_matches:
                print(f"  ✓ Extracted metrics: {metric_matches}")
                return metric_matches[:4]
            else:
                print(f"  ✗ No quoted strings found in: {metrics_content}")
        else:
            print(f"✗ No EVALUATION_METRICS pattern found")
            # Show first few lines for debugging
            lines = evaluator_code.split('\n')[:15]
            for i, line in enumerate(lines):
                if 'EVALUATION_METRICS' in line:
                    print(f"  Found at line {i+1}: {line}")
        
        return None
        
    except Exception as e:
        print(f"Error reading {evaluator_file}: {e}")
        return None

# Test both tools
result1 = extract_metrics("generate_essay")
result2 = extract_metrics("generate_brand_guidelines")

print(f"\n=== RESULTS ===")
print(f"generate_essay: {result1}")
print(f"generate_brand_guidelines: {result2}")

# Now test the actual config generator method
print(f"\n=== Testing actual config generator ===")

try:
    import sys
    sys.path.append('.')
    from generate_openevolve_configs import OpenEvolveConfigGenerator
    
    generator = OpenEvolveConfigGenerator("tools")
    
    for tool_name in ["generate_essay", "generate_brand_guidelines"]:
        tool_dir = Path(f"tools/{tool_name}")
        print(f"\nTesting {tool_name}:")
        metrics = generator._extract_evaluator_metrics(tool_dir)
        print(f"  Result: {metrics}")
        
except Exception as e:
    print(f"Error testing config generator: {e}")
    import traceback
    traceback.print_exc()