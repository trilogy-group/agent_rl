"""
Tool: generate_brand_guidelines
Extracted from: tools.py

Function generate_brand_guidelines
"""

import os
import logging
from typing import List
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

load_dotenv()

logger = logging.getLogger(__name__)

model = ChatOpenAI(model="gpt-4o", temperature=0.2)

BRAND_GUIDELINES_GENERATION_PROMPT = """You are a brand strategist tasked with creating comprehensive brand guidelines based on research. \

Using the research provided, create detailed brand guidelines that include:

1. **Brand Voice & Tone**:
   - Writing style (formal, casual, professional, friendly, etc.)
   - Personality traits (innovative, trustworthy, approachable, etc.)
   - Communication style preferences

2. **Content Guidelines**:
   - Preferred content themes and topics
   - Language and vocabulary preferences
   - Messaging patterns and key phrases

3. **LinkedIn-Specific Guidelines**:
   - Post structure preferences
   - Engagement style
   - Professional positioning
   - Call-to-action preferences

4. **Brand Values & Mission**:
   - Core values and principles
   - Mission and vision alignment
   - Key differentiators

Create comprehensive, actionable guidelines that can be used to generate authentic brand-aligned content.

Research Information:
{research}"""

def generate_brand_guidelines(brand_research: List[str]) -> str:
    """Generate brand guidelines from research content"""
    logger.info("Generating brand guidelines from research")
    
    research_text = "\n\n".join(brand_research or [])
    logger.info(f"Using {len(brand_research or [])} research pieces for guidelines generation")
    
    guidelines_messages = [
        SystemMessage(content=BRAND_GUIDELINES_GENERATION_PROMPT.format(research=research_text)),
        HumanMessage(content="Generate comprehensive brand guidelines based on the research provided.")
    ]
    
    logger.info("Invoking model for brand guidelines generation")
    response = model.invoke(guidelines_messages)
    logger.info(f"Generated brand guidelines with {len(response.content)} characters")
    
    return response.content

if __name__ == "__main__":
    # Test the tool here
    # result = generate_brand_guidelines(...)
    pass
