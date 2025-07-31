"""
Working Plan and Execute Agent with LangGraph
"""
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from datetime import datetime

# Import tools
from src.social.tools import (
    web_research_tool,
    generate_tweet_tool,
    generate_linkedin_post_tool
)

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# State
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Tools
tools = [web_research_tool, generate_tweet_tool, generate_linkedin_post_tool]
tool_node = ToolNode(tools)

# Agent node - single node that both plans and executes
def agent(state: State):
    """Single agent that handles both planning and execution"""
    
    messages = state["messages"]
    
    # Check if we just completed tool calls and need to provide final answer
    if len(messages) > 2 and hasattr(messages[-1], 'name'):  # Last message is a tool result
        # We just got tool results, provide final answer
        prompt = f"""Today is {datetime.now().strftime('%Y-%m-%d')}.
You are a social media content creation agent.

Based on the tool results above, provide the final answer to the user's request.
If you generated content, show it clearly.
Be concise and helpful."""
        
        full_messages = [SystemMessage(content=prompt)] + messages
        response = llm.invoke(full_messages)
        return {"messages": [response]}
    
    else:
        # Initial planning and tool calling
        prompt = f"""Today is {datetime.now().strftime('%Y-%m-%d')}.
You are a social media content creation agent.

You have these tools:
- web_research_tool(query): Research current information
- generate_tweet_tool(topic, style, research_context): Create tweets
- generate_linkedin_post_tool(topic, style, research_context): Create LinkedIn posts

Approach:
1. If the user asks for content, first research the topic
2. Then generate the requested content using the research

Execute the user's request using the appropriate tools."""
        
        # Create agent with tools
        agent_with_tools = llm.bind_tools(tools)
        
        # Add system message to the conversation
        full_messages = [SystemMessage(content=prompt)] + messages
        
        # Get response
        response = agent_with_tools.invoke(full_messages)
        
        return {"messages": [response]}

# Create graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("agent", agent)
workflow.add_node("tools", tool_node)

# Set entry point
workflow.set_entry_point("agent")

# Add edges
def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    
    # If LLM makes a tool call, route to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    # Otherwise end
    return END

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)

# After tools, always go back to agent
workflow.add_edge("tools", "agent")

# Compile
app = workflow.compile()

# Helper function to run
def run_agent(user_input: str):
    """Run the agent with user input"""
    print(f"\n🚀 Running agent with: {user_input}")
    print("-" * 50)
    
    result = app.invoke({
        "messages": [HumanMessage(content=user_input)]
    })
    
    # Get the final response - it's the last AIMessage with content
    final_response = None
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
            final_response = msg.content
            break
    
    # Print the final answer prominently
    if final_response:
        print("\n✨ FINAL ANSWER:")
        print("=" * 50)
        print(final_response)
        print("=" * 50)
    else:
        print("\n❌ No final response generated")
    
    # Debug info (optional)
    print("\n📊 Full Conversation:")
    print("-" * 50)
    for i, msg in enumerate(result["messages"]):
        if isinstance(msg, HumanMessage):
            print(f"{i}. 👤 User: {msg.content}")
        elif isinstance(msg, AIMessage):
            if msg.content:
                print(f"{i}. 🤖 Agent: {msg.content[:100]}...")
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    print(f"   └─ 🔧 Calling: {tc['name']}")
        elif hasattr(msg, 'name'):  # ToolMessage
            content_preview = str(msg.content)[:100] + "..." if len(str(msg.content)) > 100 else str(msg.content)
            print(f"{i}. 📦 Tool Result ({msg.name}): {content_preview}")
    
    return result

# Test function
def test():
    """Test the agent"""
    # Test cases
    test_cases = [
        "Create a tweet about AI trends",
        "Write a LinkedIn post about remote work benefits",
        "Generate a tweet about climate change solutions"
    ]
    
    for test in test_cases:
        print("\n" + "="*60)
        run_agent(test)
        print("="*60)

if __name__ == "__main__":
    # Run a simple test
    run_agent("Create a tweet about the benefits of Python programming")