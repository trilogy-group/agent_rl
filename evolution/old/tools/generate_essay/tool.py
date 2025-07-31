"""
Tool: generate_essay
Extracted from: tools.py

Generate LinkedIn post from plan and research content
"""

import logging
from typing import List
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

WRITER_PROMPT = """You are a LinkedIn content expert tasked with writing engaging, professional LinkedIn posts.\
Create a compelling LinkedIn post based on the user's request and outline. \

Key requirements:
- Keep it between 150-300 words maximum
- Use a strong, attention-grabbing opening hook
- Include 2-3 key insights or main points
- Add line breaks for readability (LinkedIn format)
- Include a clear call to action
- End with 3-5 relevant hashtags
- Make it engaging and shareable

IMPORTANT: Follow these brand guidelines exactly:
{brand_guidelines}

Make sure the tone, style, messaging, and personality of the post aligns perfectly with the brand guidelines above.

Use the research content below to support your points:

------

{content}"""

model = ChatOpenAI(model="gpt-4o", temperature=0.2)
logger = logging.getLogger(__name__)

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