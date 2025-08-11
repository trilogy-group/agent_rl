from typing import Annotated
from typing_extensions import TypedDict
from src.agent.llm import llm
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import ToolMessage, SystemMessage, AIMessage, HumanMessage
from langgraph.prebuilt import ToolNode, tools_condition
from src.agent.marketing.tools import (
    load_brand_guidelines_from_website,
    datetime_tool,
    get_latest_news_for_brand,
    get_upcoming_events_tool,
    generate_brand_campaign_ideas,
    generate_tweets
)
from langgraph.checkpoint.sqlite import SqliteSaver
from datetime import datetime

# -----------------------
# State schema
# -----------------------
class State(TypedDict):
    messages: Annotated[list, add_messages]   # only messages use add_messages
    brand_guidelines: str
    latest_news: list[dict]                   # plain, no Annotated
    upcoming_events: list[dict]
    user_query: str
    tweets: list[str]

builder = StateGraph(State)

SYSTEM_PROMPT = f"""
Today is {datetime.now().strftime('%Y-%m-%d')}.
You are an expert marketing strategist and brand consultant.

You have access to special tools for brand strategy work. 
Use them whenever appropriate:
- For brand guidelines → use load_brand_guidelines_from_website
- For current events → use get_latest_news_for_brand and get_upcoming_events_tool
- For campaign ideas → use generate_brand_campaign_ideas
- For tweet creation → always use generate_tweets (never draft tweets manually)

When the user asks for tweets:
1. First, make sure you have the latest news and upcoming events.
2. Then call generate_tweets with that information.
3. Return only the output from the generate_tweets tool.
"""

tools = [
    datetime_tool,
    load_brand_guidelines_from_website,
    get_latest_news_for_brand,
    get_upcoming_events_tool,
    generate_brand_campaign_ideas,
    generate_tweets
]
# llm_tools = llm.bind_tools(tools)

# -----------------------
# Debug tracer
# -----------------------
def trace_node(name):
    def wrapper(fn):
        def inner(state):
            print(f"🚀 Entering node: {name}")
            print("STATE:", {k: v for k, v in state.items() if k != "messages"})
            return fn(state)
        return inner
    return wrapper

# -----------------------
# Chatbot node
# -----------------------
@trace_node("chatbot")
def chatbot_node(state: State) -> dict: 
    msgs = state.get('messages', [])

    # Lock user query once
    if not state.get("user_query"):
        last_user = next((m for m in reversed(msgs) if isinstance(m, HumanMessage)), None)
        user_q = last_user.content if last_user else ""
    else:
        user_q = state["user_query"]

    # System prompt used internally, not added to state
    input_msgs = [SystemMessage(content=SYSTEM_PROMPT)] + msgs

    assistant_msg = llm.invoke(input_msgs)

    return {
        **state,
        'messages': msgs + [assistant_msg],  # only user-facing msgs + AI response
        'user_query': user_q
    }

builder.add_node('chatbot', chatbot_node)

# -----------------------
# Fetch latest news
# -----------------------
@trace_node("fetch_news")
def fetch_news_node(state: State) -> dict:
    news = []
    if state.get('user_query'):
        news = get_latest_news_for_brand.invoke({
            'user_query': state['user_query'],
            'brand_guidelines': state.get('brand_guidelines', ''),
            'limit': 3,
        })
    return {'latest_news': news}

builder.add_node('fetch_news', fetch_news_node)

# -----------------------
# Fetch upcoming events
# -----------------------
@trace_node("fetch_events")
def fetch_events_node(state: State) -> dict:
    events = get_upcoming_events_tool.invoke({})
    return {'upcoming_events': events}

builder.add_node('fetch_events', fetch_events_node)

# -----------------------
# Generate tweets
# -----------------------
@trace_node("generate_tweets")
def generate_tweets_node(state: State) -> dict:
    tweets = generate_tweets.invoke({
        'user_query': state.get('user_query', ''),
        'brand_guidelines': state.get('brand_guidelines', ''),
        'news': state.get('latest_news', []),
        'upcoming_events': state.get('upcoming_events', []),
        'limit': 5,
    })
    return {'tweets': tweets}

builder.add_node('generate_tweets', generate_tweets_node)

# -----------------------
# Tool fallback
# -----------------------
builder.add_node('tools', ToolNode(tools=tools))

# -----------------------
# End node
# -----------------------
@trace_node("end")
def end_node(state: State) -> dict:
    return state

builder.add_node('end', end_node)

# -----------------------
# Routing logic
# -----------------------
def should_fetch(state: State):
    uq = (state.get('user_query') or "").lower()
    print("🧐 should_fetch evaluating:", uq)
    if "tweet" in uq:
        if not state.get('latest_news'):
            return 'fetch_news'
        if not state.get('upcoming_events'):
            return 'fetch_events'
        return 'generate_tweets'
    return 'chatbot'

builder.add_edge(START, 'chatbot')

# -----------------------
# Conditional edges
# -----------------------


builder.add_conditional_edges(
    'chatbot',
    should_fetch,
)

builder.add_conditional_edges(
    'fetch_news',
    should_fetch,
)
builder.add_conditional_edges(
    'fetch_events',
    should_fetch,
)

builder.add_conditional_edges(
    'generate_tweets',
    should_fetch,
)

builder.add_edge('fetch_news', 'chatbot')
builder.add_edge('fetch_events', 'chatbot')
builder.add_edge('generate_tweets', 'chatbot')

builder.add_edge('chatbot', END)

# -----------------------
# Persist graph
# -----------------------
memory = SqliteSaver.from_conn_string('graph.db')
graph = builder.compile(checkpointer=memory)
