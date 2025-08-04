#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from extract_decorated_tools import DecoratedToolExtractor
    
    print("🔄 Starting extraction...")
    extractor = DecoratedToolExtractor('tools')
    
    # Extract from the marketing tools file
    tools = extractor.extract_from_file('../backend/src/marketing/tools.py')
    print(f"✅ Found {len(tools)} decorated tools")
    
    # Save each tool
    for tool in tools:
        print(f"💾 Saving tool: {tool['name']}")
        extractor.save_extracted_tool(tool)
    
    print("🎉 Extraction completed successfully!")
    
except Exception as e:
    print(f"❌ Error during extraction: {e}")
    import traceback
    traceback.print_exc()