#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from generate_evaluators import EvaluatorGenerator

# Test the FINALLY fixed evaluator generator
generator = EvaluatorGenerator()

# Regenerate with the mandatory logger requirement
tool_dir = Path("tools/generate_brand_guidelines") 
if tool_dir.exists():
    print("Testing evaluator generator with MANDATORY logger requirement...")
    generator.generate_for_tool("generate_brand_guidelines", str(tool_dir))
    print("Done! Checking if logger is now included...")
    
    # Check the generated evaluator
    evaluator_file = tool_dir / "evaluator.py"
    if evaluator_file.exists():
        with open(evaluator_file, 'r') as f:
            content = f.read()
            if "logger = logging.getLogger(__name__)" in content:
                print("✅ SUCCESS: Logger is now properly included in the generated evaluator!")
            else:
                print("❌ FAIL: Logger is still missing from the generated evaluator")
    else:
        print("❌ Evaluator file not found")
else:
    print("Tool directory not found")