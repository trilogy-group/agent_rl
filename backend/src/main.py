from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage
from agent import create_agent

app = FastAPI(title="Agent RL Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
agent = create_agent()

class ChatMessage(BaseModel):
    content: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
async def root():
    return {"message": "Agent RL Backend is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    try:
        result = agent.invoke({
            "messages": [HumanMessage(content=message.content)]
        })
        
        response_content = result["messages"][-1].content
        return ChatResponse(response=response_content)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)