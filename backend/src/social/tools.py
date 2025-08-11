from dotenv import load_dotenv
from langchain_core.tools import tool  
from datetime import datetime
import os
import json
load_dotenv()

from tavily import TavilyClient
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)


@tool
def datetime_tool() -> str:
    """Returns the current datetime."""
    return datetime.now().isoformat()


@tool
def web_research_tool(query: str, max_results: int = 5) -> list[dict]:
    """Research current information on the web using Tavily search.
    
    Args:
        query: The search query/topic to research
        max_results: Maximum number of results to return (default 5)
    
    Returns:
        List of search results with title, content, and url
    """
    try:
        print(f"🔍 Researching: {query}")
        response = tavily.search(query=query, max_results=max_results, days=30)
        
        results = []
        for r in response.get('results', []):
            results.append({
                'title': r.get('title', ''),
                'content': r.get('content', ''),
                'url': r.get('url', ''),
                'published_date': r.get('published_date', '')
            })
        
        print(f"✅ Found {len(results)} research results")
        return results
        
    except Exception as e:
        print(f"❌ Research error: {e}")
        return [{"error": str(e)}]


@tool
def generate_tweet_tool(topic: str, style: str = "engaging", research_context: str = "") -> str:
    """Generate an engaging tweet based on topic and research context.
    
    Args:
        topic: The main topic/subject for the tweet
        style: The desired style (engaging, professional, humorous, etc.)
        research_context: Additional context from research to inform the tweet
    
    Returns:
        Generated tweet text
    """
    try:
        prompt = f"""
        Create an engaging tweet about: {topic}
        
        Style: {style}
        Research Context: {research_context}
        
        Requirements:
        - Keep under 280 characters
        - Use engaging hooks and compelling language
        - Include relevant hashtags (2-3 max)
        - Make it shareable and conversation-starting
        - Current and trending when possible
        
        Return only the tweet text, no quotes or explanations.
        """
        
        messages = [
            SystemMessage(content="You are an expert social media content creator specializing in viral, engaging tweets."),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        tweet = response.content.strip()
        
        print(f"🐦 Generated tweet: {tweet}")
        return tweet
        
    except Exception as e:
        print(f"❌ Tweet generation error: {e}")
        return f"Error generating tweet: {str(e)}"


@tool  
def generate_linkedin_post_tool(topic: str, style: str = "professional", research_context: str = "") -> str:
    """Generate a professional LinkedIn post based on topic and research context.
    
    Args:
        topic: The main topic/subject for the LinkedIn post
        style: The desired style (professional, thought leadership, storytelling, etc.)
        research_context: Additional context from research to inform the post
    
    Returns:
        Generated LinkedIn post text
    """
    try:
        prompt = f"""
        Create a compelling LinkedIn post about: {topic}
        
        Style: {style}
        Research Context: {research_context}
        
        Requirements:
        - 150-300 words ideal length
        - Professional yet engaging tone
        - Strong opening hook to grab attention
        - 2-3 key insights or main points  
        - Use line breaks for readability
        - Include a clear call to action
        - End with 3-5 relevant hashtags
        - Make it valuable for professional audience
        
        Structure:
        1. Attention-grabbing opening
        2. Key insights with supporting details
        3. Call to action or engagement prompt
        4. Relevant hashtags
        
        Return only the post text, no quotes or explanations.
        """
        
        messages = [
            SystemMessage(content="You are an expert LinkedIn content strategist who creates engaging professional posts that drive engagement and thought leadership."),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        post = response.content.strip()
        
        print(f"💼 Generated LinkedIn post: {post[:100]}...")
        return post
        
    except Exception as e:
        print(f"❌ LinkedIn post generation error: {e}")
        return f"Error generating LinkedIn post: {str(e)}"
