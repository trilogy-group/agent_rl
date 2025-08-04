#!/usr/bin/env python3
"""
Test the quantitative evaluator generation
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from generate_evaluators import EvaluatorGenerator
    
    print("✅ Successfully imported EvaluatorGenerator")
    
    # Test function type classification
    generator = EvaluatorGenerator()
    tool_dir = Path("tools/get_technical_analysis")
    
    if tool_dir.exists():
        print(f"✅ Found tool directory: {tool_dir}")
        
        # Test the analysis function
        print("🔍 Testing function analysis and classification...")
        try:
            description, function_type, metrics = generator._analyze_function_and_metrics(tool_dir)
            
            print(f"📊 Analysis Results:")
            print(f"  Description: {description}")
            print(f"  Function Type: {function_type}")
            print(f"  Metrics: {metrics}")
            
            # Test prompt generation based on type
            if function_type == "quantitative" or "analytic" in function_type:
                print("✅ Correctly identified as quantitative function")
                print("📝 Would use quantitative evaluation prompt")
            else:
                print("⚠️  Identified as creative/content function")
                print("📝 Would use content evaluation prompt")
                
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
    else:
        print(f"❌ Tool directory not found: {tool_dir}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()