"""
Tool: generate_essay
Extracted from: tools.py

Function generate_essay
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

WRITER_PROMPT = """You are a seasoned LinkedIn content strategist tasked with crafting a compelling and insightful LinkedIn post. Your content should captivate a wide audience and foster meaningful interaction.

Instructions:
1. **Immediate Engagement**: Start with a powerful hook or narrative to capture the audience's attention from the first line.
2. **Contextual Relevance**: Seamlessly integrate the provided research and plan to establish relevance with the audience's interests and current trends.
3. **Professional and Clear Tone**: Maintain professionalism and clarity, ensuring the content aligns with the brand's voice yet remains accessible.
4. **Logical Structure**: Organize your content with clear sections, using headings and bullet points where necessary for better readability.
5. **Effective Conclusion**: Conclude with a compelling call to action that inspires readers to engage further.
6. **Visibility Enhancement**: Strategically include 3-5 pertinent hashtags to broaden post reach.

Consistently adhere to these brand guidelines for authenticity:
{brand_guidelines}

Your writing should not only resonate deeply with the target audience but also uphold the core values of the brand. Use the following research content as a foundational basis:

------

{content}"""


def generate_essay(task: str, plan: str, content: List[str], brand_guidelines: str, revision_number: int = 1) -> tuple[str, int]:
    """Generate LinkedIn post from plan and research content"""
    logger.info("Generating LinkedIn post")
    
    content_text = "\n\n".join(content or [])
    logger.info(f"Using {len(content or [])} content pieces for generation")
    
    user_message = HumanMessage(
        content=f"{task}\n\nHere is my plan:\n\n{plan}")
    generation_messages = [
        SystemMessage(
            content=WRITER_PROMPT.format(content=content_text, brand_guidelines=brand_guidelines)
        ),
        user_message
    ]
    
    logger.info("Invoking model for LinkedIn post generation")
    response = model.invoke(generation_messages)
    new_revision_number = revision_number + 1
    logger.info(f"Generated draft (revision {new_revision_number}) with {len(response.content)} characters")
    
    return response.content, new_revision_number

if __name__ == "__main__":
    # Test the tool here
    # result = generate_essay(...)
    pass
