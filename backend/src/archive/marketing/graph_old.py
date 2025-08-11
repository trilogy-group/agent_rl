from typing import Annotated
import os
from typing_extensions import TypedDict
from src.agent.llm import llm
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode, tools_condition
from src.agent.marketing.tools import load_brand_guidelines_from_website, datetime_tool, get_latest_news_for_brand, get_upcoming_events_tool, generate_brand_campaign_ideas, generate_tweets
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command, interrupt
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages import SystemMessage
from langchain_core.messages import AIMessage
import uuid
import sqlite3
from datetime import datetime




@tool
def human_assistance_tool(query: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> str:
    """Request assistance from a human."""
    print(f"************************************************")
    print(f"Human assistance requested: {query}")
    print(f"************************************************")
    return interrupt({"query": query})


class State(TypedDict):
    messages: Annotated[list, add_messages]
    brand_guidelines: str
    latest_news: list[dict]
    upcoming_events: list[dict]
    user_query: str

graph_builder = StateGraph(State)


MARKETING_SYSTEM_PROMPT = f"""
Today is {datetime.now().strftime("%Y-%m-%d")}.
You are an expert marketing strategist and brand consultant with deep expertise in:

- Brand strategy and positioning
- Campaign development and execution  
- Market trend analysis and insights
- Content marketing and storytelling
- Digital marketing and social media strategy
- Event marketing and experiential campaigns
- Consumer psychology and behavior
- Data-driven marketing optimization

You excel at creating innovative, results-driven marketing campaigns that align perfectly with brand values while capitalizing on current events, market trends, and consumer insights. You always provide actionable, creative, and strategically sound marketing recommendations.

When helping with marketing tasks, you:
1. Analyze brand guidelines thoroughly
2. Consider current market trends and news
3. Identify relevant upcoming events and opportunities
4. Create campaigns that resonate with target audiences. When ideating, use the generate_brand_campaign_ideas tool to generate campaign ideas.
5. Ensure all recommendations align with brand values and voice.
6. When generating tweets, use the generate_tweets tool to generate tweets."""

tools = [datetime_tool, load_brand_guidelines_from_website, human_assistance_tool, get_latest_news_for_brand, get_upcoming_events_tool, generate_brand_campaign_ideas, generate_tweets]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    # Add system prompt as the first message if not already present
    messages = state["messages"]
    
    # Check if first message is a system message
    if not messages or not isinstance(messages[0], SystemMessage):
        system_message = SystemMessage(content=MARKETING_SYSTEM_PROMPT)
        messages = [system_message] + messages
    
    return {"messages": [llm_with_tools.invoke(messages)]}

def fetch_news_node(state: State):
    """Fetch latest news and update state"""
    if not state.get("brand_guidelines") or not state.get("user_query"):
        return {"latest_news": []}
    
    news = get_latest_news_for_brand.invoke({
        "user_query": state["user_query"], 
        "brand_guidelines": state["brand_guidelines"], 
        "limit": 3
    })
    return {"latest_news": news}

def fetch_events_node(state: State):
    """Fetch upcoming events and update state"""
    events = get_upcoming_events_tool.invoke({})
    return {"upcoming_events": events}

def generate_tweets_with_state(state: State):
    """Generate tweets using state data"""
    if not state.get("brand_guidelines"):
        
        return {"messages": [AIMessage(content="No brand guidelines available for tweet generation")]}
    
    # Use the modified generate_tweets tool that works with state data
    tweets = generate_tweets(
        user_query=state.get("user_query", ""),
        brand_guidelines=state["brand_guidelines"],
        news=state.get("latest_news", []),
        upcoming_events=state.get("upcoming_events", []),
        limit=5
    )
    
    
    return {"messages": [AIMessage(content=f"Generated tweets: {tweets}")]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("fetch_news", fetch_news_node)
graph_builder.add_node("fetch_events", fetch_events_node)
graph_builder.add_node("generate_tweets", generate_tweets_with_state)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

def should_fetch_data(state: State):
    """Determine if we need to fetch news and events data"""
    messages = state.get("messages", [])
    if not messages:
        return "chatbot"
    
    last_message = messages[-1].content.lower() if messages else ""
    
    # Check if user is asking for tweets and we don't have the required data
    if ("tweet" in last_message or "social media" in last_message) and not state.get("latest_news"):
        return "fetch_news"
    
    return "chatbot"

def after_fetch_news(state: State):
    """After fetching news, decide next step"""
    last_message = state.get("messages", [])[-1].content.lower() if state.get("messages") else ""
    
    if "tweet" in last_message or "social media" in last_message:
        return "fetch_events"
    
    return "chatbot"

def after_fetch_events(state: State):
    """After fetching events, decide next step"""
    last_message = state.get("messages", [])[-1].content.lower() if state.get("messages") else ""
    
    if "tweet" in last_message or "social media" in last_message:
        return "generate_tweets"
    
    return "chatbot"

# Add conditional routing from start
graph_builder.add_conditional_edges(
    START,
    should_fetch_data,
    {
        "fetch_news": "fetch_news",
        "chatbot": "chatbot"
    }
)

# Add routing after fetch_news
graph_builder.add_conditional_edges(
    "fetch_news",
    after_fetch_news,
    {
        "fetch_events": "fetch_events",
        "chatbot": "chatbot"
    }
)

# Add routing after fetch_events
graph_builder.add_conditional_edges(
    "fetch_events",
    after_fetch_events,
    {
        "generate_tweets": "generate_tweets",
        "chatbot": "chatbot"
    }
)

# After generating tweets, go to chatbot
graph_builder.add_edge("generate_tweets", "chatbot")

# Original chatbot flow
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")


memory = SqliteSaver.from_conn_string("graph.db")
graph = graph_builder.compile(checkpointer=memory)
