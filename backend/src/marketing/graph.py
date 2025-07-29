import logging
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import AIMessage
from langgraph.graph.message import add_messages



from src.marketing.tools import (
    classify_intent, chat_response, improve_draft, create_plan,
    research_for_plan, generate_essay, reflect_on_draft, research_for_critique,
    has_brand_guidelines, research_for_brand, generate_brand_guidelines
)
from langgraph.types import interrupt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

memory = SqliteSaver.from_conn_string('data/graph.db')


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



# Node functions


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


def chatbot_node(state: AgentState):
    logger.info("Chatbot node started")
    
    response_content = chat_response(state['messages'])
    
    return {"messages": [AIMessage(content=response_content)]}


def improve_draft_node(state: AgentState):
    logger.info("Improve draft node started")
    
    existing_draft = state.get('draft', '')
    improved_draft = improve_draft(state['messages'], existing_draft)
    
    return {
        "draft": improved_draft, 
        "messages": [AIMessage(content=improved_draft)]
    }


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

        # Get brand info from user
        brand_info = interrupt(message)
        logger.info(f"Received brand info: {brand_info}")
        
        # Research brand information
        logger.info("Starting brand research")
        brand_research = research_for_brand(brand_info)
        
        # Generate brand guidelines from research
        logger.info("Generating brand guidelines from research")
        brand_guidelines = generate_brand_guidelines(brand_research)
        
        logger.info(f"Generated brand guidelines with {len(brand_guidelines)} characters")
        
        return {"brand_guidelines": brand_guidelines}

    logger.info(f"Using existing brand guidelines with {len(brand_guidelines)} characters")
    
    return {"brand_guidelines": brand_guidelines}



def plan_node(state: AgentState):
    logger.info("Plan node started")
    plan = create_plan(state['messages'])
    
    return {"plan": plan}


def research_plan_node(state: AgentState):
    logger.info("Research plan node started")
    
    existing_content = state.get('content', [])
    research = research_for_plan(state['task'], existing_content)
    
    return {"research": research}


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


def reflection_node(state: AgentState):
    logger.info("Reflection node started")
    
    critique = reflect_on_draft(state['draft'])
    
    return {"critique": critique}


def research_critique_node(state: AgentState):
    logger.info("Research critique node started")
    
    existing_content = state.get('content', [])
    content = research_for_critique(state['critique'], existing_content)
    
    return {"content": content}


# def should_continue(state):
#     if state["revision_number"] > state.get("max_revisions", 2):
#         return END
#     return "reflect"


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
builder.add_node("reflect", reflection_node)
builder.add_node("research_plan", research_plan_node)
builder.add_node("research_critique", research_critique_node)

builder.set_entry_point("orchestrator")

builder.add_conditional_edges(
    "orchestrator",
    route_from_orchestrator,
    {"planner": "planner", "chatbot": "chatbot", "improve_draft": "improve_draft", "brand_guidelines": "brand_guidelines"}
)

builder.add_edge("chatbot", END)
builder.add_edge("improve_draft", END)
builder.add_edge("brand_guidelines", "planner")

# builder.add_conditional_edges(
#     "generate", 
#     should_continue, 
#     {END: END, "reflect": "reflect"}
# )


builder.add_edge("planner", "research_plan")
builder.add_edge("research_plan", "generate")

builder.add_edge("reflect", "research_critique")
builder.add_edge("research_critique", "generate")
builder.add_edge("generate", END)


graph = builder.compile(checkpointer=memory)


