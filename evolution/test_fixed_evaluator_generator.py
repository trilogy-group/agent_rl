#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from generate_evaluators import EvaluatorGenerator

# Test the fixed evaluator generator
generator = EvaluatorGenerator()

# Regenerate the evaluator for generate_brand_guidelines
tool_dir = Path("tools/generate_brand_guidelines")
if tool_dir.exists():
    print("Regenerating evaluator with fixed logger...")
    generator.generate_for_tool("generate_brand_guidelines", str(tool_dir))
    print("Fixed evaluator generated!")
else:
    print("Tool directory not found")