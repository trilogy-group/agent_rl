"""
Tool: classify_intent
Extracted from: tools.py

Classify user intent from messages
"""

import logging
from typing import List
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

ORCHESTRATOR_PROMPT = """You are an orchestrator that determines what the user wants to do. 
Analyze the user's message and determine if they want to:
1. "research_and_write" - They want to research a topic and write a LinkedIn post about it
2. "improve_and_rewrite_draft" - They are providing feedback on an existing draft and want to improve it based on their feedback
3. "other" - They want something else that doesn't involve research and writing


### Examples
Write a LinkedIn post about 'The Impact of AI on Society'. - Intent: research_and_write
Create a LinkedIn post on remote work trends. - Intent: research_and_write
Make this more engaging and add a call to action. - Intent: improve_and_rewrite_draft
What is the weather in Tokyo? - Intent: other
"

Respond with just the category name: either "research_and_write", "improve_and_rewrite_draft", or "other"."""

model = ChatOpenAI(model="gpt-4o", temperature=0.2)
logger = logging.getLogger(__name__)

def classify_intent(messages: List) -> str:
    """Classify user intent from messages"""
    logger.info("Classifying user intent")
    
    classification_messages = [
        SystemMessage(content=ORCHESTRATOR_PROMPT)
    ] + messages[-5:]

    print("Classification messages: ", classification_messages)
    
    logger.info("Invoking model for intent classification")
    response = model.invoke(classification_messages)

    print("Response: ", response.content)
    
    intent = response.content.strip().lower()
    logger.info(f"Detected intent: {intent}")
    
    return intent

if __name__ == "__main__":
    # Test the tool here
    # result = classify_intent(...)
    pass