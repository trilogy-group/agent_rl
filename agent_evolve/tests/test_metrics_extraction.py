#!/usr/bin/env python3
import re
from pathlib import Path

def extract_evaluator_metrics(tool_dir: Path) -> list:
    """Extract metrics from METRICS constant in evaluator code"""
    evaluator_file = tool_dir / "evaluator.py"
    
    try:
        with open(evaluator_file, 'r') as f:
            evaluator_code = f.read()
        
        # Look for METRICS = [...] pattern
        metrics_pattern = r'METRICS\s*=\s*\[([^\]]+)\]'
        metrics_match = re.search(metrics_pattern, evaluator_code)
        
        if metrics_match:
            # Extract the content inside the brackets
            metrics_content = metrics_match.group(1)
            # Find all quoted strings (metric names)
            metric_matches = re.findall(r'"([^"]+)"', metrics_content)
            if metric_matches:
                print(f"    Found metrics: {metric_matches}")
                return metric_matches[:4]  # Limit to 4 for MAP-Elites
        
        # Fallback: look for metrics in evaluation prompts
        eval_prompt_matches = re.findall(r'- ([a-zA-Z_]+)\s*$', evaluator_code, re.MULTILINE)
        if eval_prompt_matches:
            # Filter out common non-metric words
            exclude_words = {'quality', 'rate', 'evaluate', 'score', 'output', 'input', 'generated', 'original'}
            filtered_metrics = [m for m in eval_prompt_matches if m not in exclude_words and len(m) > 2]
            if filtered_metrics:
                return filtered_metrics[:4]
        
        # Final fallback
        return ['quality', 'relevance', 'usefulness', 'clarity']
        
    except Exception as e:
        print(f"    Warning: Could not extract metrics from evaluator: {e}")
        return ['quality', 'relevance', 'usefulness', 'clarity']

# Test with generate_essay
tool_dir = Path("tools/generate_essay")
print(f"Testing metrics extraction for: {tool_dir}")
metrics = extract_evaluator_metrics(tool_dir)
print(f"Extracted metrics: {metrics}")

# Test with generate_brand_guidelines  
tool_dir = Path("tools/generate_brand_guidelines")
print(f"\nTesting metrics extraction for: {tool_dir}")
metrics = extract_evaluator_metrics(tool_dir)
print(f"Extracted metrics: {metrics}")