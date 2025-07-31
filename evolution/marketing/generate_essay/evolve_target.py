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

WRITER_PROMPT = """As an expert LinkedIn content strategist, your mission is to create an engaging and insightful LinkedIn post using the provided outline and research materials. The post should engage a broad audience and encourage meaningful interaction.

Instructions:
1. **Engage Immediately**: Begin with a captivating hook or story to grab attention.
2. **Develop Key Points**: Elaborate on 2-3 main ideas, supported by research, and use storytelling or analogies for clarity.
3. **Professional Tone**: Maintain a tone that is professional yet approachable and aligns with the brand's voice.
4. **Structure and Readability**: Ensure the post is logically structured with clear paragraphs and line breaks.
5. **Conclude Effectively**: End with a strong call to action that encourages readers to engage.
6. **Enhance Visibility**: Include 3-5 relevant hashtags to increase reach.

Adhere to these brand guidelines for consistency and authenticity:
{brand_guidelines}

Your content should resonate with the audience while staying true to the brand's values. Use the following research content to inform your writing:

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
