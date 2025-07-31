#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from extract_decorated_tools import DecoratedToolExtractor

# Clean re-extraction with improved prompt handling
extractor = DecoratedToolExtractor('tools')
tools = extractor.extract_from_file('../backend/src/marketing/tools.py')

for tool in tools:
    print(f"Re-extracting with improved prompt handling: {tool['name']}")
    extractor.save_extracted_tool(tool)

print("Complete!")