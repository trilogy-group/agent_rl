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

WRITER_PROMPT = """As a LinkedIn content strategist, your role is to create a highly engaging and insightful post using the provided outline and research. The aim is to connect with a broad audience, fostering meaningful interactions.

**Content Creation Instructions:**
1. **Capture Attention Instantly**: Start with a compelling hook or vivid narrative to immediately draw in the reader.
2. **Articulate Key Ideas**: Expand on 2-3 main ideas, backed by research, utilizing storytelling techniques to enhance clarity and engagement.
3. **Maintain Professionalism**: Write with a balance of professionalism and approachability, reflecting the unique voice of the brand.
4. **Enhance Readability**: Organize the post into clear, concise paragraphs with strategic line breaks for better readability.
5. **Conclude with Impact**: Finish with a strong call to action that invites audience interaction.
6. **Optimize for Visibility**: Integrate 3-5 pertinent hashtags to maximize reach.

**Authenticity and Consistency:**
Adhere to the brand guidelines to maintain consistency:
{brand_guidelines}

Develop content that deeply resonates with the audience while staying true to the brand's core values. Use the research material below to inform your writing:

------

{content}"""


def generate_essay(task: str, plan: str, content: List[str], brand_guidelines: str, revision_number: int = 1) -> tuple[str, int]:
    """Generate LinkedIn post from plan and research content"""
    logger.info("Generating LinkedIn post")
    
    content_text = "\n\n".join(content or [])
    logger.info(f"Using {len(content or [])} content pieces for generation")
    
    user_message = HumanMessage(
        content=f"Task: {task}\n\nPlan Overview:\n{plan}\n\nCraft a LinkedIn post with the outlined details. Ensure the content is dynamic, professional, and resonates with the audience."
    )
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
