from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import os
from dotenv import load_dotenv

load_dotenv()

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chatbot(state: State):
    llm = ChatOpenAI(model="gpt-4o-mini")
    return {"messages": [llm.invoke(state["messages"])]}

def create_agent():
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    
    return graph_builder.compile()

if __name__ == "__main__":
    agent = create_agent()
    
    # Test the agent
    result = agent.invoke({
        "messages": [HumanMessage(content="Hello! What can you help me with?")]
    })
    
    print("Agent response:", result["messages"][-1].content)