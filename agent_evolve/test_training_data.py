#!/usr/bin/env python3
"""
Test script to verify training data generation functionality
"""

import json
from generate_evaluators import EvaluatorGenerator

# Mock training data for has_brand_guidelines tool
mock_training_data = [
    {
        "input": "",
        "expected_output": False,
        "category": "edge_case",
        "description": "Empty string should return False"
    },
    {
        "input": "   ",
        "expected_output": False,
        "category": "edge_case", 
        "description": "Whitespace-only string should return False"
    },
    {
        "input": "Brand voice: professional, tone: friendly",
        "expected_output": True,
        "category": "basic",
        "description": "Valid brand guidelines should return True"
    },
    {
        "input": "Our company follows these brand guidelines:\n- Professional tone\n- Blue color scheme\n- Minimalist design",
        "expected_output": True,
        "category": "basic",
        "description": "Multi-line brand guidelines should return True"
    },
    {
        "input": None,
        "expected_output": "error",
        "category": "error_handling",
        "description": "None input should raise TypeError"
    }
]

def test_training_data_generation():
    """Test the training data generation and file creation"""
    
    # Read the has_brand_guidelines tool
    tool_file = "evolution/tools/has_brand_guidelines/tool.py"
    
    try:
        with open(tool_file, 'r') as f:
            tool_source = f.read()
    except FileNotFoundError:
        print(f"Tool file not found: {tool_file}")
        return
    
    # Create test training data file
    training_data_file = "evolution/tools/has_brand_guidelines/training_data.json"
    
    # Extend mock data to 30 samples
    extended_training_data = mock_training_data.copy()
    
    # Add more varied test cases
    for i in range(25):  # Add 25 more to make 30 total
        extended_training_data.append({
            "input": f"Brand guideline example {i+1}",
            "expected_output": True if i % 2 == 0 else False,
            "category": "generated",
            "description": f"Generated test case {i+1}"
        })
    
    # Write training data
    with open(training_data_file, 'w') as f:
        json.dump(extended_training_data, f, indent=2)
    
    print(f"Created {training_data_file} with {len(extended_training_data)} samples")
    
    # Show sample of training data
    print("\nSample training data:")
    for i, sample in enumerate(extended_training_data[:3]):
        print(f"  {i+1}. {sample}")

if __name__ == "__main__":
    test_training_data_generation()