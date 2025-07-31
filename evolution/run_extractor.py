#!/usr/bin/env python3
"""
Simple script to run the extractor.
"""
import sys
import os
sys.path.insert(0, '.')

from extract_decorated_tools import DecoratedToolExtractor

def main():
    extractor = DecoratedToolExtractor('tools')
    tools = extractor.extract_from_file('../backend/src/marketing/tools.py')
    
    for tool in tools:
        extractor.save_extracted_tool(tool)
        
    print(f"Extracted {len(tools)} tools")

if __name__ == "__main__":
    main()