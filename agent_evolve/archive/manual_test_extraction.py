#!/usr/bin/env python3
import re

# Manually test extraction
def extract_evaluator_metrics(file_path):
    try:
        with open(file_path, 'r') as f:
            evaluator_code = f.read()
        
        print(f"Testing extraction from: {file_path}")
        
        # Look for EVALUATION_METRICS = [...] pattern
        metrics_pattern = r'EVALUATION_METRICS\s*=\s*\[([^\]]+)\]'
        metrics_match = re.search(metrics_pattern, evaluator_code)
        
        if metrics_match:
            print(f"Found pattern: {metrics_match.group(0)}")
            # Extract the content inside the brackets
            metrics_content = metrics_match.group(1)
            print(f"Content inside brackets: {metrics_content}")
            
            # Find all quoted strings (metric names) - try both single and double quotes
            metric_matches = re.findall(r"'([^']+)'", metrics_content)
            if not metric_matches:
                metric_matches = re.findall(r'"([^"]+)"', metrics_content)
            if metric_matches:
                print(f"Extracted metrics: {metric_matches}")
                return metric_matches[:4]
        
        print("No EVALUATION_METRICS pattern found")
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test both files
print("=" * 50)
result1 = extract_evaluator_metrics("tools/generate_essay/evaluator.py")
print(f"Result: {result1}")

print("\n" + "=" * 50)
result2 = extract_evaluator_metrics("tools/generate_brand_guidelines/evaluator.py")
print(f"Result: {result2}")

print("\n" + "=" * 50)
print("Testing complete!")