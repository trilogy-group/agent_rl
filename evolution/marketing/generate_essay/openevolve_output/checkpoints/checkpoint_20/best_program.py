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

WRITER_PROMPT = """As a seasoned LinkedIn content strategist, your goal is to create a captivating and insightful LinkedIn post using the outline and research materials provided. The content must resonate with a professional audience and encourage meaningful interaction.

Instructions:
1. **Hook the Reader**: Begin with an engaging narrative or question that directly addresses the audience's challenges and interests.
2. **Articulate Key Points**: Present 2-3 main ideas, supported by data and examples. Use storytelling and analogies for enhanced engagement and comprehension.
3. **Professional Tone**: Maintain an authoritative yet approachable tone, consistent with the brand's voice.
4. **Clear Structure**: Organize the content into well-defined, concise paragraphs, using line breaks for readability.
5. **Impactful Conclusion**: End with a compelling call to action that encourages comments and further discussion.
6. **Optimize Visibility**: Use 3-5 relevant hashtags to increase the post's reach and engagement.

Tailor the content to the audience's persona, reflecting their interests and aligning with the brand's goals:

Audience Persona: {audience_persona}

Ensure adherence to these brand guidelines for authenticity:
{brand_guidelines}

Incorporate the following research insights to strengthen your post:

------

{content}
"""


def generate_essay(task: str, plan: str, content: List[str], brand_guidelines: str, audience_persona: str = "General Professional", revision_number: int = 1) -> tuple[str, int]:
    """Generate LinkedIn post from plan and research content"""
    logger.info("Generating LinkedIn post")
    
    content_text = "\n\n".join(content or [])
    logger.info(f"Using {len(content or [])} content pieces for generation")
    
    user_message = HumanMessage(
        content=f"{task}\n\nHere is my plan:\n\n{plan}")
    generation_messages = [
        SystemMessage(
            content=WRITER_PROMPT.format(content=content_text, brand_guidelines=brand_guidelines, audience_persona=audience_persona)
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
