import os
import logging
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel  
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize model and clients
model = ChatOpenAI(model="gpt-4o", temperature=0.2)
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# Prompts
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

CHATBOT_PROMPT = """You are a helpful and friendly chatbot assistant.
Engage in natural conversation with the user, answer their questions, provide information, 
and assist with general tasks that don't involve research and writing. 
Be conversational, helpful, and responsive to what the user is asking."""

IMPROVE_AND_REWRITE_DRAFT_PROMPT = """You are a LinkedIn content expert specializing in optimizing posts for maximum engagement. 
Your task is to improve an existing LinkedIn post draft based on specific user feedback.

Focus on these LinkedIn-specific improvements:
- Enhancing the hook to grab attention in the LinkedIn feed
- Optimizing length (150-300 words ideal)
- Improving readability with proper line breaks
- Strengthening professional tone while keeping it conversational
- Adding or refining the call to action
- Updating hashtags for better discoverability
- Increasing engagement potential
- Addressing the specific user feedback provided

Provide the improved LinkedIn post that incorporates all feedback while following LinkedIn best practices."""

PLAN_PROMPT = """You are an expert LinkedIn content creator tasked with creating a structure for an engaging LinkedIn post. \
Create a clear outline for the user's requested topic that includes:
1. Hook/Opening (attention-grabbing first line)
2. Key points or insights (2-3 main ideas)
3. Supporting details or examples
4. Call to action or engagement prompt
5. Relevant hashtags suggestions

Keep the structure concise and optimized for LinkedIn's professional audience. The final post should be 150-300 words maximum."""

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

REFLECTION_PROMPT = """You are a LinkedIn content strategist reviewing a LinkedIn post draft. \
Analyze the post and provide constructive feedback focusing on:

- Engagement potential (hook strength, readability)
- Professional tone and authenticity
- Length appropriateness (150-300 words ideal)
- Call to action effectiveness
- Hashtag relevance and quantity
- Overall LinkedIn best practices
- Areas for improvement to increase visibility and engagement

Provide specific, actionable recommendations to enhance the post's performance on LinkedIn."""

RESEARCH_PLAN_PROMPT = """You are a researcher gathering current information for a LinkedIn post. \
Generate a list of search queries that will find relevant, up-to-date information including:
- Recent trends and statistics
- Expert opinions and insights
- Real-world examples and case studies
- Industry news and developments

Generate 3 targeted search queries maximum."""

RESEARCH_CRITIQUE_PROMPT = """You are a researcher finding additional information to improve a LinkedIn post based on feedback. \
Generate search queries that will find:
- More compelling examples or statistics
- Additional expert perspectives
- Current industry insights
- Supporting data or case studies

Based on the critique feedback, generate 3 targeted search queries maximum."""

BRAND_RESEARCH_PROMPT = """You are a brand researcher tasked with analyzing a company or brand to understand their brand guidelines. \
Generate search queries to find information about:
- Brand voice and tone
- Visual identity and style
- Core values and mission
- Target audience and positioning
- Content style and messaging patterns
- Brand personality and characteristics

Generate 3 targeted search queries maximum to gather comprehensive brand information."""

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


class Queries(BaseModel):
    queries: List[str]

def has_brand_guidelines(brand_guidelines: str) -> bool:
    """Check if brand guidelines information is provided"""
    if not brand_guidelines or brand_guidelines.strip() == "":
        return False
    return True


def classify_intent(messages: List) -> str:
    """Classify user intent from messages"""
    logger.info("Classifying user intent")
    
    classification_messages = [
        SystemMessage(content=ORCHESTRATOR_PROMPT)
    ] + messages[-1:]

    print("Classification messages: ", classification_messages)
    
    logger.info("Invoking model for intent classification")
    response = model.invoke(classification_messages)

    print("Response: ", response.content)
    
    intent = response.content.strip().lower()
    logger.info(f"Detected intent: {intent}")
    
    return intent

def chat_response(messages: List) -> str:
    """Generate chatbot response"""
    logger.info("Generating chatbot response")
    
    chat_messages = [
        SystemMessage(content=CHATBOT_PROMPT)
    ] + messages
    
    logger.info("Invoking model for general chatbot response")
    response = model.invoke(chat_messages)
    logger.info(f"Generated chatbot response with {len(response.content)} characters")
    
    return response.content

def improve_draft(messages: List, existing_draft: str = "") -> str:
    """Improve existing draft based on user feedback"""
    logger.info("Improving draft based on feedback")
    
    # Get the user's feedback from the latest message
    user_feedback = messages[-1].content
    logger.info(f"User feedback: {user_feedback}")
    
    # Look for existing draft in conversation history if not provided
    if not existing_draft:
        # Try to find a draft in previous messages
        for msg in reversed(messages[:-1]):  # Exclude the latest feedback message
            if hasattr(msg, 'content') and len(msg.content) > 200:  # Assume longer messages might be drafts
                existing_draft = msg.content
                break
    
    logger.info(f"Found existing draft with {len(existing_draft)} characters")
    
    improvement_messages = [
        SystemMessage(content=IMPROVE_AND_REWRITE_DRAFT_PROMPT),
        HumanMessage(content=f"Here is the existing draft:\n\n{existing_draft}\n\nUser feedback: {user_feedback}\n\nPlease provide an improved version of the draft based on this feedback.")
    ]
    
    logger.info("Invoking model for draft improvement")
    response = model.invoke(improvement_messages)
    logger.info(f"Generated improved draft with {len(response.content)} characters")
    
    return response.content

def create_plan(messages: List) -> str:
    """Create essay plan from user request"""
    logger.info("Creating essay plan")
    
    plan_messages = [
        SystemMessage(content=PLAN_PROMPT), 
    ] + messages
    
    logger.info("Invoking model for essay planning")
    response = model.invoke(plan_messages)
    logger.info(f"Generated plan with {len(response.content)} characters")
    
    return response.content

def research_for_plan(task: str, existing_content: List[str] = None) -> List[str]:
    """Research content for essay plan"""
    logger.info("Researching content for plan")
    
    logger.info("Generating research queries")
    research_messages = [
        SystemMessage(content=RESEARCH_PLAN_PROMPT),
        HumanMessage(content=task)
    ]
    
    queries = model.with_structured_output(Queries).invoke(research_messages)
    logger.info(f"Generated {len(queries.queries)} research queries: {queries.queries}")
    
    content = existing_content or []
    for i, q in enumerate(queries.queries):
        logger.info(f"Searching for query {i+1}/{len(queries.queries)}: {q}")
        response = tavily.search(query=q, max_results=2)
        logger.info(f"Found {len(response['results'])} results for query: {q}")
        for r in response['results']:
            content.append(r['content'])
    
    logger.info(f"Research plan completed with {len(content)} content pieces")
    return content

def research_for_brand(brand_info: str, existing_content: List[str] = None) -> List[str]:
    """Research brand information for guidelines generation"""
    logger.info("Researching brand information for guidelines")
    
    logger.info("Generating brand research queries")
    research_messages = [
        SystemMessage(content=BRAND_RESEARCH_PROMPT),
        HumanMessage(content=f"Research this brand/company: {brand_info}")
    ]
    
    queries = model.with_structured_output(Queries).invoke(research_messages)
    logger.info(f"Generated {len(queries.queries)} brand research queries: {queries.queries}")
    
    content = existing_content or []
    for i, q in enumerate(queries.queries):
        logger.info(f"Searching for brand query {i+1}/{len(queries.queries)}: {q}")
        response = tavily.search(query=q, max_results=3)
        logger.info(f"Found {len(response['results'])} results for brand query: {q}")
        for r in response['results']:
            content.append(r['content'])
    
    logger.info(f"Brand research completed with {len(content)} content pieces")
    return content

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

def reflect_on_draft(draft: str) -> str:
    """Generate critique and reflection on draft"""
    logger.info("Reflecting on draft")
    
    logger.info(f"Reflecting on draft with {len(draft)} characters")
    reflection_messages = [
        SystemMessage(content=REFLECTION_PROMPT), 
        HumanMessage(content=draft)
    ]
    
    logger.info("Invoking model for draft critique")
    response = model.invoke(reflection_messages)
    logger.info(f"Generated critique with {len(response.content)} characters")
    
    return response.content

def research_for_critique(critique: str, existing_content: List[str] = None) -> List[str]:
    """Research additional content based on critique"""
    logger.info("Researching content based on critique")
    
    logger.info("Generating research queries based on critique")
    research_messages = [
        SystemMessage(content=RESEARCH_CRITIQUE_PROMPT),
        HumanMessage(content=critique)
    ]
    
    queries = model.with_structured_output(Queries).invoke(research_messages)
    logger.info(f"Generated {len(queries.queries)} critique-based queries: {queries.queries}")
    
    content = existing_content or []
    for i, q in enumerate(queries.queries):
        logger.info(f"Searching for critique query {i+1}/{len(queries.queries)}: {q}")
        response = tavily.search(query=q, max_results=2)
        logger.info(f"Found {len(response['results'])} results for critique query: {q}")
        for r in response['results']:
            content.append(r['content'])
    
    logger.info(f"Research critique completed with {len(content)} total content pieces")
    return content