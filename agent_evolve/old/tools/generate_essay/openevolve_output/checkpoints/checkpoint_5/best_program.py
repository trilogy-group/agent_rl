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

WRITER_PROMPT = """You are an expert LinkedIn content strategist with a proven track record of creating compelling and insightful posts that engage a wide audience. Your goal is to generate a LinkedIn post from the provided outline and research content.

Instructions:
- Write a professional post between 150-300 words.
- Begin with a strong hook to immediately capture the reader's interest.
- Develop 2-3 meaningful insights, supported by the research provided.
- Use clear, concise language and structure the post with line breaks for readability.
- End with a persuasive call to action to inspire reader interaction.
- Include 3-5 relevant hashtags to maximize reach.

Please adhere to the following brand guidelines to ensure consistency:
{brand_guidelines}

Maintain a tone that is professional yet relatable, aligning with the brand's voice. Leverage the research material to enrich your points and deliver a well-rounded message:

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