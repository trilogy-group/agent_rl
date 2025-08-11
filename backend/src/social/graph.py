import json
from typing import Annotated
from typing_extensions import TypedDict
from src.agent.llm import llm
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import ToolMessage, SystemMessage, AIMessage, HumanMessage
from langgraph.prebuilt import ToolNode, tools_condition
from src.social.tools import (
    datetime_tool,
    web_research_tool,
    generate_tweet_tool,
    generate_linkedin_post_tool
)
from langgraph.checkpoint.sqlite import SqliteSaver
from datetime import datetime

# -----------------------
# State schema
# -----------------------
class State(TypedDict):
    messages: Annotated[list, add_messages]   # only messages use add_messages
    user_query: str
    execution_plan: dict                      # plan with steps and reasoning  
    research_results: list[dict]              # web research results
    generated_content: dict                   # tweets, linkedin posts, etc.
    current_step: int                         # track execution progress
    completed_steps: list[str]                # completed step names

builder = StateGraph(State)

def get_planner_prompt():
    return f"""
Today is {datetime.now().strftime('%Y-%m-%d')}.
You are an expert social media strategist and content planner.

Your role is to analyze user requests and create detailed execution plans for social media content creation.

Available capabilities:
- Web research using Tavily (current news, trends, data)
- Generate tweets (engaging, platform-optimized)  
- Generate LinkedIn posts (professional, thought leadership)

Create a structured execution plan with:
1. **Objective**: Clear goal based on user request
2. **Steps**: Ordered list of actions needed (use tools: web_research_tool, generate_tweet_tool, generate_linkedin_post_tool)
3. **Research Topics**: What information to gather
4. **Content Strategy**: Type and approach for content creation
5. **Success Criteria**: How to measure if objective is met

CRITICAL: You MUST respond with ONLY valid JSON. No explanations, no markdown, no additional text.

Required JSON format:
{{
    "objective": "Clear description of what we're trying to achieve",
    "steps": [
        {{"name": "research_topic", "action": "Research current information about the topic", "tool": "web_research_tool"}},
        {{"name": "generate_content", "action": "Create social media content", "tool": "generate_tweet_tool"}}
    ],
    "research_topics": ["specific topic 1", "specific topic 2"],
    "content_strategy": "detailed approach and style guidance",
    "success_criteria": "measurable outcomes"
}}

Respond with ONLY the JSON object above. No other text.
"""

def get_executor_prompt():
    return f"""
Today is {datetime.now().strftime('%Y-%m-%d')}.
You are an expert social media content executor.

You have access to these tools:
- web_research_tool: Research current information using Tavily
- generate_tweet_tool: Create engaging tweets  
- generate_linkedin_post_tool: Create professional LinkedIn posts

Follow the execution plan step by step. Use the appropriate tools for each step.
Focus on creating high-quality, engaging content based on current research and trends.
"""

tools = [
    datetime_tool,
    web_research_tool,
    generate_tweet_tool,
    generate_linkedin_post_tool
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
# Planner node
# -----------------------
@trace_node("planner")
def planner_node(state: State) -> dict:
    msgs = state.get('messages', [])
    
    # Get user query from messages
    if not state.get("user_query"):
        last_user = next((m for m in reversed(msgs) if isinstance(m, HumanMessage)), None)
        user_q = last_user.content if last_user else ""
    else:
        user_q = state["user_query"]
    
    # Create planning message
    planning_msg = HumanMessage(content=f"Create an execution plan for: {user_q}")
    input_msgs = [SystemMessage(content=get_planner_prompt()), planning_msg]
    
    response = llm.invoke(input_msgs)
    
    # Parse the plan with robust JSON extraction
    def extract_json_from_response(text: str) -> dict:
        """Extract JSON from LLM response with fallback handling"""
        try:
            # First try direct parsing
            return json.loads(text.strip())
        except json.JSONDecodeError:
            try:
                # Try to find JSON within the text
                import re
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
            
            # Return fallback plan
            print(f"❌ Failed to parse plan from response: {text[:200]}...")
            return {
                "objective": user_q,
                "steps": [
                    {"name": "research", "action": "Research the topic", "tool": "web_research_tool"},
                    {"name": "generate_content", "action": "Generate social media content", "tool": "generate_tweet_tool"}
                ],
                "research_topics": [user_q],
                "content_strategy": "Create engaging content based on research",
                "success_criteria": "High-quality content generated successfully"
            }
    
    plan = extract_json_from_response(response.content)
    print(f"✅ Execution plan created: {plan['objective']}")
    
    return {
        **state,
        'user_query': user_q,
        'execution_plan': plan,
        'current_step': 0,
        'completed_steps': [],
        'research_results': [],
        'generated_content': {},
        'messages': msgs + [AIMessage(content=f"I've created an execution plan to {plan['objective']}. Let me execute it step by step.")]
    }

builder.add_node('planner', planner_node)

# -----------------------
# Executor node
# -----------------------
@trace_node("executor")
def executor_node(state: State) -> dict:
    msgs = state.get('messages', [])
    plan = state.get('execution_plan', {})
    current_step = state.get('current_step', 0)
    completed_steps = state.get('completed_steps', [])
    user_q = state.get('user_query', '')
    
    # Check if we have steps to execute
    steps = plan.get('steps', [])
    if current_step >= len(steps):
        # All steps completed
        return {
            **state,
            'messages': msgs + [AIMessage(content="All steps in the execution plan have been completed successfully!")]
        }
    
    # Get current step
    step = steps[current_step]
    step_name = step.get('name', f'step_{current_step}')
    step_action = step.get('action', '')
    tool_name = step.get('tool', '')
    
    # Check if this step was just completed (last message is a tool result)
    messages = state.get('messages', [])
    if messages and isinstance(messages[-1], ToolMessage):
        # Store tool results
        tool_result = messages[-1]
        if 'web_research_tool' in str(tool_result.name):
            # Store research results
            research_results = state.get('research_results', [])
            try:
                # Parse the tool result content
                if isinstance(tool_result.content, str):
                    result_data = json.loads(tool_result.content)
                else:
                    result_data = tool_result.content
                research_results.extend(result_data if isinstance(result_data, list) else [result_data])
                state['research_results'] = research_results
                print(f"📚 Stored {len(result_data)} research results")
            except:
                pass
        
        # This step was just completed, move to next
        print(f"✅ Completed step: {step_name}")
        new_completed_steps = completed_steps + [step_name]
        new_current_step = current_step + 1
        
        # Check if there are more steps
        if new_current_step >= len(steps):
            # Generate final summary
            summary = f"""
✅ All tasks completed successfully!

Objective: {plan.get('objective', '')}
Completed Steps: {', '.join(new_completed_steps)}

Results are shown above. The plan has been executed successfully.
"""
            return {
                **state,
                'current_step': new_current_step,
                'completed_steps': new_completed_steps,
                'messages': msgs + [AIMessage(content=summary)]
            }
        else:
            # Continue to next step
            return {
                **state,
                'current_step': new_current_step,
                'completed_steps': new_completed_steps
            }
    
    # Execute current step
    print(f"🔄 Executing step {current_step + 1}/{len(steps)}: {step_name}")
    
    # Build context with previous results
    research_context = ""
    if state.get('research_results'):
        research_context = f"\n\nPrevious research results:\n{json.dumps(state.get('research_results', []), indent=2)}"
    
    # Create specific instruction for this step
    if tool_name == "web_research_tool":
        instruction = f"Use the web_research_tool to research: {', '.join(plan.get('research_topics', [user_q]))}"
    elif tool_name == "generate_tweet_tool":
        instruction = f"Use the generate_tweet_tool to create a tweet about {plan.get('objective', user_q)}. Style: {plan.get('content_strategy', 'engaging')}{research_context}"
    elif tool_name == "generate_linkedin_post_tool":
        instruction = f"Use the generate_linkedin_post_tool to create a LinkedIn post about {plan.get('objective', user_q)}. Style: {plan.get('content_strategy', 'professional')}{research_context}"
    else:
        instruction = f"Execute: {step_action} using {tool_name}"
    
    executor_msg = HumanMessage(content=instruction)
    input_msgs = [SystemMessage(content=get_executor_prompt()), executor_msg]
    
    # Use tool-enabled LLM
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(input_msgs)
    
    # Don't update step counter here - wait for tool completion
    return {
        **state,
        'messages': msgs + [response]
    }

builder.add_node('executor', executor_node)

# -----------------------
# Tool node for handling tool calls
# -----------------------
builder.add_node('tools', ToolNode(tools=tools))

# -----------------------
# Routing logic
# -----------------------
def should_continue(state: State):
    """Determine if we should continue execution or end"""
    plan = state.get('execution_plan', {})
    current_step = state.get('current_step', 0)
    steps = plan.get('steps', [])
    
    # Check if all steps are completed
    if current_step >= len(steps):
        return END
    
    # Check if the last message has tool calls
    messages = state.get('messages', [])
    if messages and hasattr(messages[-1], 'tool_calls') and messages[-1].tool_calls:
        return 'tools'
    
    # Continue with next step
    return 'executor'

def should_continue_after_tools(state: State):
    """Continue execution after tool calls"""
    # Store tool results and move to next step
    messages = state.get('messages', [])
    if messages and len(messages) >= 2:
        # Get the last tool message result
        last_msg = messages[-1]
        if isinstance(last_msg, ToolMessage):
            # Extract research results if it's from web_research_tool
            if 'web_research_tool' in str(last_msg):
                research_results = state.get('research_results', [])
                research_results.append(last_msg.content)
                state['research_results'] = research_results
    
    return 'executor'

# -----------------------
# Graph edges
# -----------------------
builder.add_edge(START, 'planner')
builder.add_edge('planner', 'executor')

builder.add_conditional_edges(
    'executor',
    should_continue,
    {
        'tools': 'tools',
        'executor': 'executor',
        END: END
    }
)

builder.add_conditional_edges(
    'tools',
    should_continue_after_tools,
    {
        'executor': 'executor'
    }
)

# -----------------------
# Persist graph
# -----------------------
memory = SqliteSaver.from_conn_string('graph.db')
graph = builder.compile(checkpointer=memory)
