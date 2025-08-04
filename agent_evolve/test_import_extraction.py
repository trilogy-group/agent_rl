#!/usr/bin/env python3
"""
Test the unused import removal functionality
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from extract_decorated_tools import DecoratedToolExtractor

def test_import_extraction():
    """Test the import extraction logic"""
    
    # Test with the get_technical_analysis tool
    extractor = DecoratedToolExtractor()
    
    # Check the current tool file
    tool_file = Path("tools/get_technical_analysis/evolve_target.py")
    if not tool_file.exists():
        print(f"❌ Tool file not found: {tool_file}")
        return
    
    print("🔍 Testing import extraction on get_technical_analysis")
    
    # Read the current tool source
    with open(tool_file, 'r') as f:
        current_content = f.read()
    
    print(f"\n📄 Current file length: {len(current_content)} chars")
    
    # Count current imports
    current_imports = [line for line in current_content.split('\n') if line.strip().startswith(('import ', 'from '))]
    print(f"📦 Current imports ({len(current_imports)}):")
    for imp in current_imports:
        print(f"  {imp}")
    
    # Test the new import extraction
    original_source_file = "backend/src/stockmarket/tools.py"  # From metadata
    if Path(original_source_file).exists():
        print(f"\n🔍 Extracting imports from original source: {original_source_file}")
        
        # Extract only needed imports
        needed_imports = extractor._extract_imports(original_source_file, "get_technical_analysis")
        
        print(f"\n📦 Needed imports:")
        if needed_imports:
            for line in needed_imports.split('\n'):
                if line.strip():
                    print(f"  {line}")
        else:
            print("  No imports detected as needed")
        
        # Compare
        needed_count = len([line for line in needed_imports.split('\n') if line.strip()])
        print(f"\n📊 Comparison:")
        print(f"  Current: {len(current_imports)} imports")
        print(f"  Needed:  {needed_count} imports")
        print(f"  Savings: {len(current_imports) - needed_count} unused imports removed")
        
    else:
        print(f"❌ Original source file not found: {original_source_file}")
        print("   Testing with current extracted file instead...")
        
        # Test with current extracted file
        needed_imports = extractor._extract_imports(str(tool_file), "get_technical_analysis")
        
        print(f"\n📦 Needed imports from extracted file:")
        if needed_imports:
            for line in needed_imports.split('\n'):
                if line.strip():
                    print(f"  {line}")
        else:
            print("  No imports detected as needed")

if __name__ == "__main__":
    test_import_extraction()