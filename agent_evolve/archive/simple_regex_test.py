import re

# Test the regex pattern directly
test_string = "EVALUATION_METRICS = ['engagement', 'relevance', 'brand_alignment', 'quality']"

print(f"Test string: {test_string}")

# Test the pattern
metrics_pattern = r'EVALUATION_METRICS\s*=\s*\[([^\]]+)\]'
metrics_match = re.search(metrics_pattern, test_string)

if metrics_match:
    print(f"Pattern matched: {metrics_match.group(0)}")
    metrics_content = metrics_match.group(1)
    print(f"Content inside brackets: {metrics_content}")
    
    # Try single quotes
    metric_matches = re.findall(r"'([^']+)'", metrics_content)
    print(f"Single quote matches: {metric_matches}")
    
    # Try double quotes
    metric_matches_double = re.findall(r'"([^"]+)"', metrics_content)
    print(f"Double quote matches: {metric_matches_double}")
else:
    print("Pattern did not match")

print("\nTesting with actual file content:")

# Read actual file
try:
    with open("tools/generate_essay/evaluator.py", 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    for i, line in enumerate(lines[:12]):
        if 'EVALUATION_METRICS' in line:
            print(f"Line {i+1}: {line}")
            
            # Test pattern on this line
            match = re.search(metrics_pattern, line)
            if match:
                print(f"  Pattern matched!")
                metrics_content = match.group(1)
                metric_matches = re.findall(r"'([^']+)'", metrics_content)
                print(f"  Extracted: {metric_matches}")
            else:
                print(f"  Pattern did not match")
                
except Exception as e:
    print(f"Error reading file: {e}")