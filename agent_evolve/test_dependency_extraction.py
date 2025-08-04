#!/usr/bin/env python3
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from extract_decorated_tools import DecoratedToolExtractor

def test_dependency_extraction():
    extractor = DecoratedToolExtractor("evolution/tools")
    
    # Test the dependency extraction specifically
    source_file = "backend/src/stockmarket/tools.py"
    function_name = "get_technical_analysis"
    
    print(f"Testing dependency extraction for {function_name} from {source_file}")
    
    try:
        dependencies = extractor._extract_dependencies(source_file, function_name)
        print(f"\nExtracted dependencies:")
        print("=" * 60)
        print(dependencies)
        print("=" * 60)
        
        # Check if helper functions are included
        helper_functions = ['calculate_rsi', 'calculate_macd', 'analyze_trend', 'analyze_macd', 'analyze_rsi']
        
        for func in helper_functions:
            if f"def {func}" in dependencies:
                print(f"✅ Found: {func}")
            else:
                print(f"❌ Missing: {func}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dependency_extraction()