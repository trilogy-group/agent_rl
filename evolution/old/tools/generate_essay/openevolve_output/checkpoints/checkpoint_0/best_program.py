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

WRITER_PROMPT = """You are a seasoned LinkedIn content strategist known for crafting engaging and professional posts that resonate with a diverse audience. Your task is to create a LinkedIn post based on the provided outline and research material.

Guidelines:
- Craft a post between 150-300 words.
- Open with a captivating hook that captures attention immediately.
- Clearly present 2-3 insightful points.
- Format with line breaks to enhance readability, adhering to LinkedIn norms.
- Conclude with a persuasive call to action.
- Integrate 3-5 pertinent hashtags for broader reach.

Adhere strictly to these brand guidelines to ensure alignment:
{brand_guidelines}

Ensure the tone is sophisticated yet approachable, reflecting the brand’s unique voice. Utilize the research content below to substantiate your points and add depth:

------

{content}"""

logger = logging.getLogger(__name__)
model = ChatOpenAI(model="gpt-4o", temperature=0.2)

def generate_essay(task: str, plan: str, content: List[str], brand_guidelines: str, revision_number: int = 1) -> tuple[str, int]:
    """Generate LinkedIn post from plan and research content"""
    logger.info("Generating LinkedIn post")
    
    content_text = "\n\n".join(content or [])
    logger.info(f"Using {len(content or [])} content pieces for generation")
    
    user_message = HumanMessage(
        content=f"Task: {task}\nPlan Overview:\n{plan}\n\nProceed with generating a LinkedIn post as per the instructions."
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