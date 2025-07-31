#!/usr/bin/env python3
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from generate_openevolve_configs import OpenEvolveConfigGenerator

def test_metrics_extraction():
    generator = OpenEvolveConfigGenerator("tools")
    
    # Test with generate_essay
    tool_dir = Path("tools/generate_essay")
    if tool_dir.exists():
        print(f"Testing extraction for: {tool_dir}")
        metrics = generator._extract_evaluator_metrics(tool_dir)
        print(f"Extracted metrics: {metrics}")
    
    # Test with generate_brand_guidelines
    tool_dir = Path("tools/generate_brand_guidelines")
    if tool_dir.exists():
        print(f"\nTesting extraction for: {tool_dir}")
        metrics = generator._extract_evaluator_metrics(tool_dir)
        print(f"Extracted metrics: {metrics}")

if __name__ == "__main__":
    test_metrics_extraction()