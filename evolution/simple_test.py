import sys
sys.path.insert(0, '.')
from extract_decorated_tools import DecoratedToolExtractor

extractor = DecoratedToolExtractor('tools')
print("Running extraction...")
tools = extractor.extract_from_file('../backend/src/marketing/tools.py')
print(f"Found {len(tools)} tools")

for tool in tools:
    print(f"Saving tool: {tool['name']}")
    extractor.save_extracted_tool(tool)

print("Done!")