from firecrawl import FirecrawlApp
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
import os

load_dotenv()

# Initialize the client with your API key
app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

@tool
def search_tool(query: str) -> list:
    """Searches the web using the Firecrawl API and returns the top 5 results.

    Args:
        query: The search query string.

    Returns:
        A list containing the search results data.
    """
    search_result = app.search(query, limit=5)
    print("Search result: ", search_result.data)
    return search_result.data

search_tool_node = ToolNode([search_tool])