import logging
import uuid
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import AIMessage
from langgraph.graph.message import add_messages
from agent_evolve import evolve


from src.marketing.tools import (
    classify_intent, chat_response, improve_draft, create_plan,
    research_for_plan, generate_essay, reflect_on_draft, research_for_critique,
    has_brand_guidelines, research_for_brand, generate_brand_guidelines
)
try:
    # Try relative import first (when running as package)
    from .imports import track_node
except ImportError:
    # Fallback to absolute import (when running directly)
    try:
        from src.marketing.imports import track_node
    except ImportError:
        # Final fallback: dummy decorator
        def track_node(*args, **kwargs):
            def decorator(func):
                return func
            return decorator if args else decorator(args[0]) if len(args) == 1 else decorator
from langgraph.types import interrupt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os

# Ensure data directory exists and use absolute path
data_dir = os.path.join(os.path.dirname(__file__), '../../data')
os.makedirs(data_dir, exist_ok=True)
db_path = os.path.join(data_dir, 'graph.db')
memory = SqliteSaver.from_conn_string(db_path)


class AgentState(TypedDict):
    brand_guidelines: str
    messages: Annotated[list, add_messages]
    intent: str
    task: str
    plan: str
    draft: str
    critique: str
    research: List[str]
    revision_number: int
    max_revisions: int


@track_node()
def orchestrator_node(state: AgentState):
    logger.info("Orchestrator node started")

    # Find the last human message in the conversation
    last_human_message = None
    for message in reversed(state["messages"]):
        if getattr(message, "type", None) == "human":
            last_human_message = message
            break

    if last_human_message is None:
        logger.warning("No human message found in messages.")
        task = ""
    else:
        task = last_human_message.content

    intent = classify_intent(state["messages"])
    logger.info(f"Task: {task}")

    return {"intent": intent, "task": task}


@track_node()
def chatbot_node(state: AgentState):
    logger.info("Chatbot node started")
    
    response_content = chat_response(state['messages'])
    
    return {"messages": [AIMessage(content=response_content)]}


@track_node()
def improve_draft_node(state: AgentState):
    logger.info("Improve draft node started")
    
    existing_draft = state.get('draft', '')
    improved_draft = improve_draft(state['messages'], existing_draft)
    
    return {
        "draft": improved_draft, 
        "messages": [AIMessage(content=improved_draft)]
    }

@evolve()
@track_node()
def brand_guidelines_node(state: AgentState):
    logger.info("Brand guidelines node started")

    brand_guidelines = state.get('brand_guidelines', '')
    if not has_brand_guidelines(brand_guidelines):
        logger.info("Brand guidelines missing, requesting human input")

        message = (
            "To create authentic LinkedIn content that matches your brand, I need to research and generate brand guidelines.\n\n"
            "Please provide either:\n"
            "- Your company/brand website URL, or\n"
            "- Your company/brand name\n\n"
            "I'll research your brand to understand your voice, values, and messaging style, then create comprehensive guidelines for content creation."
        )

        # Create proper interrupt structure to display message and get response
        interrupt_data = {
            "action_request": {
                "action": "brand_info_request",
                "args": {
                    "message": message
                }
            },
            "config": {
                "allow_edit": False,
                "allow_respond": True,
                "allow_accept": False,
                "allow_ignore": False
            }
        }

        # Get user input for brand information
        user_brand_info = interrupt(interrupt_data)
        logger.info(f"Received brand info from user: {user_brand_info}")

        # Extract string from interrupt response structure: [{'type': 'response', 'args': 'actual_content'}]
        if isinstance(user_brand_info, list) and user_brand_info:
            first_item = user_brand_info[0]
            if isinstance(first_item, dict) and first_item.get('type') == 'response':
                brand_info_str = first_item.get('args', '')
            elif isinstance(first_item, dict):
                # Fallback for other dict structures
                brand_info_str = (first_item.get('content') or 
                                 first_item.get('text') or 
                                 first_item.get('message') or 
                                 str(first_item))
            else:
                brand_info_str = str(first_item)
        elif isinstance(user_brand_info, dict):
            # Direct dict response
            brand_info_str = (user_brand_info.get('content') or 
                             user_brand_info.get('text') or 
                             user_brand_info.get('message') or 
                             str(user_brand_info))
        else:
            brand_info_str = str(user_brand_info) if user_brand_info else ""
        
        logger.info(f"Processing brand info: {brand_info_str}")

        # Use tools to research and generate brand guidelines
        logger.info("Researching brand information")
        brand_research = research_for_brand(brand_info_str)
        
        logger.info("Generating brand guidelines from research")
        generated_guidelines = generate_brand_guidelines(brand_research)
        
        logger.info(f"Generated brand guidelines with {len(generated_guidelines)} characters")

        # Return the message to display and the generated brand guidelines
        return {
            "messages": [AIMessage(content=message)],
            "brand_guidelines": generated_guidelines
        }

    logger.info(f"Using existing brand guidelines with {len(brand_guidelines)} characters")
    
    return {"brand_guidelines": brand_guidelines}



@track_node()
def plan_node(state: AgentState):
    logger.info("Plan node started")
    plan = create_plan(state['messages'])
    
    return {"plan": plan}


@track_node()
def research_plan_node(state: AgentState):
    logger.info("Research plan node started")
    
    existing_content = state.get('content', [])
    research = research_for_plan(state['task'], existing_content)
    
    return {"research": research}


@track_node()
def generation_node(state: AgentState):
    logger.info("Generation node started")
    
    task = state['task']
    plan = state['plan']
    research = state.get('research', [])
    brand_guidelines = state.get('brand_guidelines', 'Professional and conversational tone')
    revision_number = state.get("revision_number", 0)
    
    draft, new_revision = generate_essay(task, plan, research, brand_guidelines, revision_number)
    
    return {
        "draft": draft, 
        "revision_number": new_revision,
        "messages": [AIMessage(content=draft)]
    }



@track_node()
def route_from_orchestrator(state):
    logger.info(f"Routing from orchestrator with state: {state}")
    intent = state["intent"]
    logger.info(f"Routing from orchestrator with intent: {intent}")

    brand_guidelines = state.get('brand_guidelines', '')

    if intent == "research_and_write" and not has_brand_guidelines(brand_guidelines):
        return "brand_guidelines"
    elif intent == "research_and_write" and has_brand_guidelines(brand_guidelines):
        return "planner"
    elif intent == "improve_and_rewrite_draft":
        return "improve_draft"
    else:
        return "chatbot"


builder = StateGraph(AgentState)

builder.add_node("orchestrator", orchestrator_node)
builder.add_node("chatbot", chatbot_node)
builder.add_node("improve_draft", improve_draft_node)
builder.add_node("brand_guidelines", brand_guidelines_node)
builder.add_node("planner", plan_node)
builder.add_node("generate", generation_node)

builder.add_node("research_plan", research_plan_node)

builder.set_entry_point("orchestrator")

builder.add_conditional_edges(
    "orchestrator",
    route_from_orchestrator,
    {"planner": "planner", "chatbot": "chatbot", "improve_draft": "improve_draft", "brand_guidelines": "brand_guidelines"}
)

builder.add_edge("chatbot", END)
builder.add_edge("improve_draft", END)
builder.add_edge("brand_guidelines", "planner")


builder.add_edge("planner", "research_plan")
builder.add_edge("research_plan", "generate")
builder.add_edge("generate", END)


graph = builder.compile(checkpointer=memory)


