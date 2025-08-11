#!/usr/bin/env python3
"""Test evaluator generation"""

from pathlib import Path
import sys
sys.path.append('evolution')

from generate_evaluators import EvaluatorGenerator

# Test with one tool
gen = EvaluatorGenerator()
tool_dir = Path("evolution/tools/generate_essay")
gen._generate_evaluator_file(tool_dir)