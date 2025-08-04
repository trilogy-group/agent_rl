"""
Tool: orchestrator_prompt
Extracted from: tools.py
Type: Prompt/Template Constant

Prompt/template constant: ORCHESTRATOR_PROMPT
"""

# The target prompt/template for evolution
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


def orchestrator_prompt():
    """Return the optimized prompt/template"""
    return ORCHESTRATOR_PROMPT


if __name__ == "__main__":
    # Test the prompt
    print(orchestrator_prompt())
