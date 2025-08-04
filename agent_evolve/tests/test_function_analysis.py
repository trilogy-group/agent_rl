#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from generate_evaluators import EvaluatorGenerator

def test_function_analysis():
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable is required")
        return
    
    generator = EvaluatorGenerator()
    
    # Test with generate_essay
    tool_dir = Path("tools/generate_essay")
    if tool_dir.exists():
        print(f"Testing function analysis for: {tool_dir}")
        description, metrics = generator._analyze_function_and_metrics(tool_dir)
        print(f"Description: {description}")
        print(f"Metrics: {metrics}")
    else:
        print(f"Tool directory {tool_dir} not found")
    
    # Test with generate_brand_guidelines
    tool_dir = Path("tools/generate_brand_guidelines")
    if tool_dir.exists():
        print(f"\nTesting function analysis for: {tool_dir}")
        description, metrics = generator._analyze_function_and_metrics(tool_dir)
        print(f"Description: {description}")
        print(f"Metrics: {metrics}")
    else:
        print(f"Tool directory {tool_dir} not found")

if __name__ == "__main__":
    test_function_analysis()