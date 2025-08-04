#!/usr/bin/env python3
"""
Simple test script for the evaluator generator
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from generate_evaluators import EvaluatorGenerator
    
    print("✅ Successfully imported EvaluatorGenerator")
    
    # Create generator instance
    generator = EvaluatorGenerator()
    print("✅ Successfully created generator instance")
    
    # Test generating evaluator for get_technical_analysis
    tool_dir = Path("tools/get_technical_analysis")
    if tool_dir.exists():
        print(f"✅ Found tool directory: {tool_dir}")
        
        # Check if training data exists
        training_data_file = tool_dir / "training_data.json"
        if training_data_file.exists():
            print(f"✅ Training data exists: {training_data_file}")
            
            # Test the generation process
            print("🔄 Testing evaluator generation...")
            generator._generate_single_evaluator(tool_dir)
            print("✅ Evaluator generation completed")
        else:
            print(f"❌ Training data missing: {training_data_file}")
    else:
        print(f"❌ Tool directory not found: {tool_dir}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()