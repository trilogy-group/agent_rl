#!/usr/bin/env python3
"""
Fix existing evaluators with robust JSON parsing
"""

import os
import re
from pathlib import Path

def create_robust_json_parser():
    """Create robust JSON parsing function"""
    return '''
def parse_json_response(response_content: str, default_metrics: dict) -> dict:
    """Robust JSON parsing with fallbacks"""
    try:
        # Strip whitespace
        content = response_content.strip()
        
        # Handle empty responses
        if not content:
            logger.warning("Empty LLM response, using default metrics")
            return default_metrics
        
        # Extract JSON from markdown code blocks
        if "```json" in content:
            json_match = re.search(r'```json\\s*([^`]+)```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1).strip()
        elif "```" in content:
            json_match = re.search(r'```\\s*([^`]+)```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1).strip()
        
        # Try to parse JSON
        parsed = json.loads(content)
        
        # Validate it's a dictionary with expected keys
        if isinstance(parsed, dict):
            # Filter to only include metric keys that exist in default_metrics
            filtered = {}
            for key in default_metrics.keys():
                if key in parsed and isinstance(parsed[key], (int, float)):
                    # Clamp values to 0.0-1.0 range
                    filtered[key] = max(0.0, min(1.0, float(parsed[key])))
                else:
                    filtered[key] = default_metrics[key]
            return filtered
        else:
            logger.warning(f"LLM returned non-dict JSON: {type(parsed)}, using defaults")
            return default_metrics
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        logger.error(f"Raw content: {response_content[:200]}...")
        return default_metrics
    except Exception as e:
        logger.error(f"Unexpected error parsing response: {e}")
        return default_metrics
'''

def fix_evaluator_file(evaluator_path: Path):
    """Fix a single evaluator file"""
    with open(evaluator_path, 'r') as f:
        content = f.read()
    
    # Check if already has robust parsing
    if 'parse_json_response' in content:
        print(f"  ✓ {evaluator_path.name} already has robust parsing")
        return False
    
    # Add imports if missing
    imports_to_add = []
    if 'import re' not in content:
        imports_to_add.append('import re')
    
    # Find the location to insert the robust parser
    lines = content.split('\n')
    insert_index = -1
    
    # Look for logger initialization
    for i, line in enumerate(lines):
        if 'logger = logging.getLogger' in line:
            insert_index = i + 1
            break
    
    if insert_index == -1:
        # Look for imports section end
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('import') and not line.startswith('from'):
                insert_index = i
                break
    
    if insert_index == -1:
        print(f"  ❌ Could not find insertion point in {evaluator_path.name}")
        return False
    
    # Insert imports
    for imp in reversed(imports_to_add):
        lines.insert(insert_index, imp)
        insert_index += 1
    
    # Insert robust parser function
    parser_lines = create_robust_json_parser().strip().split('\n')
    for line in reversed(parser_lines):
        lines.insert(insert_index, line)
    
    # Fix JSON parsing calls
    fixed_content = '\n'.join(lines)
    
    # Replace direct json.loads calls with robust parser
    pattern = r'json\.loads\(([^)]+)\)'
    
    def replace_json_loads(match):
        var_name = match.group(1)
        # Try to find the default metrics dict
        metrics_match = re.search(r'metrics\s*=\s*\{([^}]+)\}', fixed_content)
        if metrics_match:
            return f'parse_json_response({var_name}, metrics)'
        else:
            # Fallback to a generic default
            return f'parse_json_response({var_name}, {{"quality": 0.0, "accuracy": 0.0}})'
    
    fixed_content = re.sub(pattern, replace_json_loads, fixed_content)
    
    # Write back
    with open(evaluator_path, 'w') as f:
        f.write(fixed_content)
    
    print(f"  ✅ Fixed {evaluator_path.name}")
    return True

def main():
    """Fix all evaluators in tools directory"""
    tools_dir = Path("evolution/tools")
    
    if not tools_dir.exists():
        print(f"Tools directory {tools_dir} not found")
        return
    
    print("Fixing evaluator JSON parsing...")
    
    fixed_count = 0
    for tool_dir in tools_dir.iterdir():
        if tool_dir.is_dir():
            evaluator_file = tool_dir / "evaluator.py"
            if evaluator_file.exists():
                print(f"Processing {tool_dir.name}...")
                if fix_evaluator_file(evaluator_file):
                    fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} evaluators")

if __name__ == "__main__":
    main()