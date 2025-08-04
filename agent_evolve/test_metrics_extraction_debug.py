#!/usr/bin/env python3
import re
from pathlib import Path

def test_metrics_extraction(evaluator_file):
    """Test metrics extraction from evaluator file"""
    print(f"\nTesting: {evaluator_file}")
    
    try:
        with open(evaluator_file, 'r') as f:
            evaluator_code = f.read()
        
        print("File contents preview:")
        lines = evaluator_code.split('\n')
        for i, line in enumerate(lines[:15]):
            print(f"{i+1:2d}: {line}")
        
        # Look for EVALUATION_METRICS = [...] pattern
        metrics_pattern = r'EVALUATION_METRICS\s*=\s*\[([^\]]+)\]'
        metrics_match = re.search(metrics_pattern, evaluator_code)
        
        if metrics_match:
            print(f"\nFound EVALUATION_METRICS pattern!")
            print(f"Match: {metrics_match.group(0)}")
            
            # Extract the content inside the brackets
            metrics_content = metrics_match.group(1)
            print(f"Content inside brackets: {metrics_content}")
            
            # Find all quoted strings (metric names)
            metric_matches = re.findall(r"'([^']+)'", metrics_content)
            print(f"Extracted metrics: {metric_matches}")
            return metric_matches
        else:
            print("No EVALUATION_METRICS pattern found")
            
            # Look for old METRICS = [...] pattern
            metrics_pattern_old = r'METRICS\s*=\s*\[([^\]]+)\]'
            metrics_match_old = re.search(metrics_pattern_old, evaluator_code)
            
            if metrics_match_old:
                print(f"Found old METRICS pattern: {metrics_match_old.group(0)}")
                metrics_content = metrics_match_old.group(1)
                metric_matches = re.findall(r'"([^"]+)"', metrics_content)
                print(f"Extracted metrics: {metric_matches}")
                return metric_matches
            else:
                print("No METRICS pattern found either")
        
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test both evaluator files
test_metrics_extraction(Path("tools/generate_essay/evaluator.py"))
test_metrics_extraction(Path("tools/generate_brand_guidelines/evaluator.py"))