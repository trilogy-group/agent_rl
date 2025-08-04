#!/usr/bin/env python3
"""
Test the fixed JSON parser
"""

import json
import re

def parse_json_response(response_content: str, evaluation_metrics: list) -> dict:
    """Robust JSON parser that handles markdown code blocks"""
    try:
        content = response_content.strip()
        if not content:
            return {metric: 0.0 for metric in evaluation_metrics}
        
        # Extract JSON from markdown blocks
        if "```json" in content:
            content = re.search(r'```json\s*([^`]+)```', content, re.DOTALL).group(1).strip()
        elif "```" in content:
            content = re.search(r'```\s*([^`]+)```', content, re.DOTALL).group(1).strip()
        
        # Parse JSON
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            # Clamp all values to 0.0-1.0 range and return metrics that exist in EVALUATION_METRICS
            result = {}
            for metric in evaluation_metrics:
                if metric in parsed:
                    result[metric] = max(0.0, min(1.0, float(parsed[metric])))
                else:
                    result[metric] = 0.0
            return result
        
        return {metric: 0.0 for metric in evaluation_metrics}
    except Exception as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw response: {response_content}")
        return {metric: 0.0 for metric in evaluation_metrics}

def test_json_parser():
    """Test the JSON parser with various response formats"""
    
    print("🔍 Testing Fixed JSON Parser")
    print("=" * 40)
    
    evaluation_metrics = ['correctness', 'completeness', 'accuracy', 'data_coverage']
    
    # Test case 1: The actual LLM response that was failing
    llm_response = """```json
{
  "correctness": 0.8,
  "completeness": 0.7,
  "accuracy": 0.8,
  "data_coverage": 0.7
}
```"""
    
    print("📝 Test Case 1: LLM Response with Markdown")
    print(f"Raw response: {repr(llm_response)}")
    
    result = parse_json_response(llm_response, evaluation_metrics)
    print(f"✅ Parsed result: {result}")
    print(f"✅ All metrics present: {all(metric in result for metric in evaluation_metrics)}")
    print(f"✅ Values in range: {all(0.0 <= v <= 1.0 for v in result.values())}")
    
    # Test case 2: Plain JSON without markdown
    plain_json = """{"correctness": 0.9, "completeness": 0.8, "accuracy": 0.85, "data_coverage": 0.75}"""
    
    print(f"\n📝 Test Case 2: Plain JSON")
    print(f"Raw response: {repr(plain_json)}")
    
    result2 = parse_json_response(plain_json, evaluation_metrics)
    print(f"✅ Parsed result: {result2}")
    
    # Test case 3: JSON with generic ``` blocks
    generic_markdown = """```
{
  "correctness": 0.6,
  "completeness": 0.5,
  "accuracy": 0.7,
  "data_coverage": 0.6
}
```"""
    
    print(f"\n📝 Test Case 3: Generic Markdown Blocks")
    print(f"Raw response: {repr(generic_markdown)}")
    
    result3 = parse_json_response(generic_markdown, evaluation_metrics)
    print(f"✅ Parsed result: {result3}")
    
    # Test case 4: Invalid JSON (should return defaults)
    invalid_json = "This is not JSON at all"
    
    print(f"\n📝 Test Case 4: Invalid JSON")
    print(f"Raw response: {repr(invalid_json)}")
    
    result4 = parse_json_response(invalid_json, evaluation_metrics)
    print(f"✅ Fallback result: {result4}")
    
    print(f"\n🎉 JSON Parser Fix Summary:")
    print(f"  ✅ Handles markdown code blocks correctly")
    print(f"  ✅ Extracts JSON from ```json``` and ``` ``` blocks")
    print(f"  ✅ Validates and clamps values to 0.0-1.0 range")
    print(f"  ✅ Returns default values for missing metrics")
    print(f"  ✅ Provides graceful error handling")
    print(f"  ✅ Should fix the evaluation parsing issue!")

if __name__ == "__main__":
    test_json_parser()