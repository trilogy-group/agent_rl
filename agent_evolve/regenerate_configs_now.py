#!/usr/bin/env python3
"""
Direct regeneration of configs with correct metrics extraction
"""
import os
import sys
import yaml
import re
from pathlib import Path
from typing import Dict, List, Any

def extract_evaluator_metrics(tool_dir: Path) -> List[str]:
    """Extract metrics from EVALUATION_METRICS variable in evaluator code"""
    evaluator_file = tool_dir / "evaluator.py"
    
    try:
        with open(evaluator_file, 'r') as f:
            evaluator_code = f.read()
        
        # Look for EVALUATION_METRICS = [...] pattern
        metrics_pattern = r'EVALUATION_METRICS\s*=\s*\[([^\]]+)\]'
        metrics_match = re.search(metrics_pattern, evaluator_code)
        
        if metrics_match:
            # Extract the content inside the brackets
            metrics_content = metrics_match.group(1)
            # Find all quoted strings (metric names) - try both single and double quotes
            metric_matches = re.findall(r"'([^']+)'", metrics_content)
            if not metric_matches:
                metric_matches = re.findall(r'"([^"]+)"', metrics_content)
            if metric_matches:
                print(f"    Found EVALUATION_METRICS: {metric_matches}")
                return metric_matches[:4]  # Limit to 4 for MAP-Elites
        
        # Fallback: Look for old METRICS = [...] pattern
        metrics_pattern_old = r'METRICS\s*=\s*\[([^\]]+)\]'
        metrics_match_old = re.search(metrics_pattern_old, evaluator_code)
        
        if metrics_match_old:
            # Extract the content inside the brackets
            metrics_content = metrics_match_old.group(1)
            # Find all quoted strings (metric names) - try both single and double quotes
            metric_matches = re.findall(r"'([^']+)'", metrics_content)
            if not metric_matches:
                metric_matches = re.findall(r'"([^"]+)"', metrics_content)
            if metric_matches:
                print(f"    Found METRICS: {metric_matches}")
                return metric_matches[:4]  # Limit to 4 for MAP-Elites
        
        # Final fallback
        print(f"    No metrics variable found, using defaults")
        return ['quality', 'relevance', 'usefulness', 'clarity']
        
    except Exception as e:
        print(f"    Warning: Could not extract metrics from evaluator: {e}")
        return ['quality', 'relevance', 'usefulness', 'clarity']

def update_config_with_metrics(config_file: Path, metrics: List[str]):
    """Update OpenEvolve config with extracted metrics"""
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update feature_dimensions
        config['database']['feature_dimensions'] = metrics
        
        # Update system message to reflect the correct metrics
        metrics_text = '\n'.join([f'    - {metric.replace("_", " ").title()}' for metric in metrics])
        
        # Replace the metrics section in system message
        old_system_message = config['prompt']['system_message']
        
        # Find and replace the EVALUATION METRICS section
        updated_message = re.sub(
            r'EVALUATION METRICS TO OPTIMIZE FOR:\s*\n(?:\s*-[^\n]*\n)*',
            f'EVALUATION METRICS TO OPTIMIZE FOR:\n\n{metrics_text}\n\n',
            old_system_message
        )
        config['prompt']['system_message'] = updated_message
        
        # Save updated config
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2, sort_keys=False)
        
        print(f"  → Updated {config_file}")
        return True
    except Exception as e:
        print(f"  Error updating config: {e}")
        return False

def main():
    tools_dir = Path("tools")
    
    if not tools_dir.exists():
        print(f"Error: Tools directory '{tools_dir}' does not exist")
        return
    
    # Find all tool directories with evaluators
    tool_dirs = []
    for item in tools_dir.iterdir():
        if item.is_dir():
            tool_file = item / "evolve_target.py"
            evaluator_file = item / "evaluator.py"
            if tool_file.exists() and evaluator_file.exists():
                tool_dirs.append(item)
    
    if not tool_dirs:
        print("No tool directories with evaluators found")
        return
    
    print(f"Regenerating OpenEvolve configs for {len(tool_dirs)} tools...")
    
    for tool_dir in tool_dirs:
        tool_name = tool_dir.name
        print(f"\nProcessing: {tool_name}")
        
        # Extract metrics from evaluator
        metrics = extract_evaluator_metrics(tool_dir)
        
        # Update config file
        config_file = tool_dir / "openevolve_config.yaml"
        if config_file.exists():
            update_config_with_metrics(config_file, metrics)
        else:
            print(f"  Warning: Config file not found: {config_file}")
    
    print(f"\nConfig regeneration completed!")

if __name__ == "__main__":
    main()