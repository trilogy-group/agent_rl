"""
Simple Plan and Execute Agent for Social Media Content
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from datetime import datetime
import json

# Import our tools
from src.social.tools import (
    web_research_tool,
    generate_tweet_tool, 
    generate_linkedin_post_tool
)

class SimplePlanExecuteAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        self.tools = {
            "web_research_tool": web_research_tool,
            "generate_tweet_tool": generate_tweet_tool,
            "generate_linkedin_post_tool": generate_linkedin_post_tool
        }
    
    def plan(self, user_request: str) -> dict:
        """Create a simple execution plan"""
        prompt = f"""Today is {datetime.now().strftime('%Y-%m-%d')}.
        
User request: {user_request}

Create a simple plan with these tools:
- web_research_tool: Research current information
- generate_tweet_tool: Create tweets  
- generate_linkedin_post_tool: Create LinkedIn posts

Return a JSON plan:
{{
    "goal": "what we're trying to achieve",
    "steps": [
        {{"tool": "tool_name", "input": "what to input"}}
    ]
}}

Return ONLY the JSON, no other text."""
        
        response = self.llm.invoke([SystemMessage(content=prompt)])
        
        try:
            return json.loads(response.content)
        except:
            # Fallback plan
            return {
                "goal": user_request,
                "steps": [
                    {"tool": "web_research_tool", "input": user_request},
                    {"tool": "generate_tweet_tool", "input": user_request}
                ]
            }
    
    def execute(self, user_request: str):
        """Plan and execute the request"""
        print(f"📋 Planning for: {user_request}")
        
        # Create plan
        plan = self.plan(user_request)
        print(f"✅ Plan created: {plan['goal']}")
        print(f"📝 Steps: {len(plan['steps'])}")
        
        # Execute plan
        results = []
        context = ""
        
        for i, step in enumerate(plan['steps']):
            print(f"\n🔄 Step {i+1}: {step['tool']}")
            
            tool_name = step['tool']
            tool_input = step['input']
            
            # Add context from previous steps
            if context and tool_name in ['generate_tweet_tool', 'generate_linkedin_post_tool']:
                tool_input = f"{tool_input}\n\nContext from research:\n{context}"
            
            try:
                # Execute tool
                if tool_name == "web_research_tool":
                    result = self.tools[tool_name].invoke({"query": tool_input})
                    # Store research context
                    context = json.dumps(result[:2]) if isinstance(result, list) else str(result)
                elif tool_name == "generate_tweet_tool":
                    result = self.tools[tool_name].invoke({
                        "topic": tool_input,
                        "style": "engaging",
                        "research_context": context
                    })
                elif tool_name == "generate_linkedin_post_tool":
                    result = self.tools[tool_name].invoke({
                        "topic": tool_input,
                        "style": "professional", 
                        "research_context": context
                    })
                else:
                    result = f"Unknown tool: {tool_name}"
                
                results.append({
                    "step": i+1,
                    "tool": tool_name,
                    "result": result
                })
                
                print(f"✅ Completed: {tool_name}")
                
            except Exception as e:
                print(f"❌ Error in {tool_name}: {str(e)}")
                results.append({
                    "step": i+1,
                    "tool": tool_name,
                    "error": str(e)
                })
        
        return {
            "plan": plan,
            "results": results
        }

# Test the agent
def test_simple_agent():
    agent = SimplePlanExecuteAgent()
    
    # Test request
    request = "Create a tweet about the latest AI trends"
    
    print("="*50)
    print("SIMPLE PLAN AND EXECUTE AGENT")
    print("="*50)
    
    result = agent.execute(request)
    
    print("\n" + "="*50)
    print("FINAL RESULTS")
    print("="*50)
    
    for r in result['results']:
        print(f"\nStep {r['step']} - {r['tool']}:")
        if 'result' in r:
            print(r['result'][:500] + "..." if len(str(r['result'])) > 500 else r['result'])
        else:
            print(f"Error: {r['error']}")

if __name__ == "__main__":
    test_simple_agent()