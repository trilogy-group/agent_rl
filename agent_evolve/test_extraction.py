#!/usr/bin/env python3
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from extract_decorated_tools import DecoratedToolExtractor

try:
    extractor = DecoratedToolExtractor("evolution/tools")
    tools = extractor.extract_from_file("backend/src/stockmarket/tools.py")
    
    print(f"Found {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool['name']}")
        
        # Save the tool
        extractor.save_extracted_tool(tool)
        print(f"    Saved to evolution/tools/{tool['name']}/")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()