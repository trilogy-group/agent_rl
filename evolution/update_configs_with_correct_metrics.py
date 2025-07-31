#!/usr/bin/env python3
import yaml
import re
from pathlib import Path

def extract_metrics_from_evaluator(evaluator_file):
    """Extract metrics from EVALUATION_METRICS variable"""
    try:
        with open(evaluator_file, 'r') as f:
            evaluator_code = f.read()
        
        # Look for EVALUATION_METRICS = [...] pattern
        metrics_pattern = r'EVALUATION_METRICS\s*=\s*\[([^\]]+)\]'
        metrics_match = re.search(metrics_pattern, evaluator_code)
        
        if metrics_match:
            # Extract the content inside the brackets
            metrics_content = metrics_match.group(1)
            # Find all quoted strings (metric names)
            metric_matches = re.findall(r"'([^']+)'", metrics_content)
            if metric_matches:
                return metric_matches
        
        return None
    except Exception as e:
        print(f"Error extracting metrics: {e}")
        return None

def update_config_with_metrics(config_file, metrics):
    """Update OpenEvolve config with correct metrics"""
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update feature_dimensions
        config['database']['feature_dimensions'] = metrics
        
        # Update system message to reflect the correct metrics
        metrics_text = '\n'.join([f'- {metric.replace("_", " ").title()}' for metric in metrics])
        
        # Replace the metrics section in system message
        old_system_message = config['prompt']['system_message']
        # Find and replace the metrics section
        import re
        updated_message = re.sub(
            r'EVALUATION METRICS TO OPTIMIZE FOR:\n[^"]+',
            f'EVALUATION METRICS TO OPTIMIZE FOR:\n{metrics_text}\n',
            old_system_message
        )
        config['prompt']['system_message'] = updated_message
        
        # Save updated config
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2, sort_keys=False)
        
        print(f"Updated {config_file} with metrics: {metrics}")
        return True
    except Exception as e:
        print(f"Error updating config: {e}")
        return False

# Update generate_essay config
evaluator_file = Path("tools/generate_essay/evaluator.py")
config_file = Path("tools/generate_essay/openevolve_config.yaml")

if evaluator_file.exists() and config_file.exists():
    metrics = extract_metrics_from_evaluator(evaluator_file)
    if metrics:
        update_config_with_metrics(config_file, metrics)
    else:
        print("Could not extract metrics from generate_essay evaluator")

# Update generate_brand_guidelines config
evaluator_file = Path("tools/generate_brand_guidelines/evaluator.py")
config_file = Path("tools/generate_brand_guidelines/openevolve_config.yaml")

if evaluator_file.exists() and config_file.exists():
    metrics = extract_metrics_from_evaluator(evaluator_file)
    if metrics:
        update_config_with_metrics(config_file, metrics)
    else:
        print("Could not extract metrics from generate_brand_guidelines evaluator")