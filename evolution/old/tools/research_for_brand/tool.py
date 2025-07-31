"""
Tool: research_for_brand
Extracted from: tools.py

Research brand information for guidelines generation
"""

import os
import logging
from typing import List
from pydantic import BaseModel
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

BRAND_RESEARCH_PROMPT = """You are a brand researcher tasked with analyzing a company or brand to understand their brand guidelines. \

The user has provided: {brand_input}

Generate search queries to find information about:
- Brand voice and tone
- Core values and mission
- Target audience and positioning
- Content style and messaging patterns
- Brand personality and characteristics
- Recent content and communications

Generate 3 targeted search queries maximum to gather comprehensive brand information about this specific brand/company."""

model = ChatOpenAI(model="gpt-4o", temperature=0.2)
logger = logging.getLogger(__name__)
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

class Queries(BaseModel):
    queries: List[str]

def research_for_brand(brand_info: str, existing_content: List[str] = None) -> List[str]:
    """Research brand information for guidelines generation"""
    logger.info("Researching brand information for guidelines")
    
    content = existing_content or []
    
    # Check if brand_info is a URL
    is_url = brand_info.strip().startswith(('http://', 'https://')) or '.' in brand_info and ' ' not in brand_info.strip()
    
    if is_url:
        logger.info(f"Detected URL input: {brand_info}")
        # Try to get content directly from the URL
        try:
            url_response = tavily.search(query=f"site:{brand_info}", max_results=3, days=30)
            logger.info(f"Found {len(url_response['results'])} results from website")
            for r in url_response['results']:
                content.append(f"Website content: {r['content']}")
        except Exception as e:
            logger.warning(f"Could not fetch website content: {e}")
    
    logger.info("Generating brand research queries")
    research_messages = [
        SystemMessage(content=BRAND_RESEARCH_PROMPT.format(brand_input=brand_info)),
        HumanMessage(content=f"Generate targeted search queries for this brand/company: {brand_info}")
    ]
    
    queries = model.with_structured_output(Queries).invoke(research_messages)
    logger.info(f"Generated {len(queries.queries)} brand research queries: {queries.queries}")
    
    for i, q in enumerate(queries.queries):
        logger.info(f"Searching for brand query {i+1}/{len(queries.queries)}: {q}")
        response = tavily.search(query=q, max_results=3, days=30)
        logger.info(f"Found {len(response['results'])} results for brand query: {q}")
        for r in response['results']:
            content.append(r['content'])
    
    logger.info(f"Brand research completed with {len(content)} content pieces")
    return content

if __name__ == "__main__":
    # Test the tool here
    # result = research_for_brand(...)
    pass