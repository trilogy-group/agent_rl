from typing import Annotated
import os
from typing_extensions import TypedDict
from llm import llm
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from IPython.display import Image, display
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode, tools_condition
from tools import search_tool_node, search_tool
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command, interrupt
from langchain_core.tools import tool
import sqlite3

# Enable LangSmith tracing (optional)
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT"] = "agent-rl-debug"
# Uncomment and add your LangSmith API key if you have one:
# os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-api-key"


@tool
def human_assistance_tool(query: str) -> str:
    """Request assistance from a human."""
    print(f"Human assistance requested: {query}")
    return interrupt({"query": query})


class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)


tools = [search_tool, human_assistance_tool]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}
    

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")


memory = SqliteSaver(sqlite3.connect("graph.db", check_same_thread=False))
graph = graph_builder.compile(checkpointer=memory)
try:
    with open("graph_mermaid.png", "wb") as f:
        f.write(graph.get_graph().draw_mermaid_png())
except Exception:
    # This requires some extra dependencies and is optional
    pass


def stream_graph_updates(user_input: str):
    events = graph.stream({"messages": [{"role": "user", "content": user_input}]}, config={"configurable": {"thread_id": "1"}})
    for event in events:
        for node_name, value in event.items():
            if "messages" in value and value["messages"]:
                last_message = value["messages"][-1]
                
                if node_name == "chatbot":
                    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                        print(f"🔍 Searching...")
                    else:
                        print(f"Assistant: {last_message.content}")
                elif node_name == "tools":
                    print(f"🔍 Search completed")


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except KeyboardInterrupt:
        print("\nGoodbye!")
        break
    except Exception as e:
        print(f"Error: {e}")
        break




