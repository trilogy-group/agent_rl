from typing import Annotated
import os
from typing_extensions import TypedDict
from src.agent.llm import llm
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode, tools_condition
from src.agent.tools import search_tool_node, search_tool
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command, interrupt
from langchain_core.tools import tool, InjectedToolCallId
import uuid
import sqlite3



@tool
def human_assistance_tool(query: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> str:
    """Request assistance from a human."""
    print(f"************************************************")
    print(f"Human assistance requested: {query}")
    print(f"************************************************")
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


memory = SqliteSaver.from_conn_string("graph.db")
graph = graph_builder.compile(checkpointer=memory)
