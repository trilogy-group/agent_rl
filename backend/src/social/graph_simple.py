from typing import Annotated, List, Dict
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from datetime import datetime
import json

# Import tools
from src.social.tools import (
    web_research_tool,
    generate_tweet_tool,
    generate_linkedin_post_tool
)

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# State definition
class State(TypedDict):
    messages: Annotated[list, add_messages]
    plan: str
    research_results: str

# Create graph
builder = StateGraph(State)

# Tools list
tools = [web_research_tool, generate_tweet_tool, generate_linkedin_post_tool]

# Planner node
def planner(state: State):
    """Creates a simple plan based on user request"""
    messages = state["messages"]
    
    # Get the user's request
    user_request = messages[-1].content if messages else ""
    
    planner_prompt = f"""Today is {datetime.now().strftime('%Y-%m-%d')}.
You are a social media content planner.

Based on this request: {user_request}

Create a simple step-by-step plan. Format your response as:
1. [First step]
2. [Second step]
3. [Third step]

Keep it simple and actionable."""
    
    response = llm.invoke([SystemMessage(content=planner_prompt)])
    
    return {
        "messages": [response],
        "plan": response.content
    }

# Executor node
def executor(state: State):
    """Executes the plan using available tools"""
    plan = state.get("plan", "")
    messages = state["messages"]
    
    executor_prompt = f"""Today is {datetime.now().strftime('%Y-%m-%d')}.
You are a social media content executor.

Available tools:
- web_research_tool: Research current information
- generate_tweet_tool: Create tweets
- generate_linkedin_post_tool: Create LinkedIn posts

Plan to execute:
{plan}

Previous research results:
{state.get('research_results', 'No research yet')}

Execute the plan step by step using the available tools."""
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)
    
    response = llm_with_tools.invoke([
        SystemMessage(content=executor_prompt),
        HumanMessage(content="Execute the plan now.")
    ])
    
    return {"messages": [response]}

# Tool handler node
def handle_tools(state: State):
    """Handle tool execution results"""
    messages = state["messages"]
    
    # Check if last message had tool calls
    last_message = messages[-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        # If it was a research tool, store results
        for tool_call in last_message.tool_calls:
            if tool_call['name'] == 'web_research_tool':
                # This will be updated when tool executes
                pass
    
    return state

# Add nodes
builder.add_node("planner", planner)
builder.add_node("executor", executor)
builder.add_node("tools", ToolNode(tools))

# Routing function
def should_continue(state: State):
    """Determine next step"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the last message has tool calls, execute tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    # Otherwise end
    return END

# Add edges
builder.add_edge(START, "planner")
builder.add_edge("planner", "executor")
builder.add_conditional_edges(
    "executor",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)
builder.add_edge("tools", "executor")

# Compile graph
graph = builder.compile()

# Test function
def test_agent():
    """Test the agent with a simple request"""
    result = graph.invoke({
        "messages": [HumanMessage(content="Create a tweet about AI trends")]
    })
    
    print("\n=== FINAL RESULT ===")
    for msg in result["messages"]:
        print(f"\n{msg.__class__.__name__}: {msg.content[:200]}...")
    
    return result

if __name__ == "__main__":
    test_agent()