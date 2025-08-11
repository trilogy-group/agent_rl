from dotenv import load_dotenv
from langchain_core.tools import tool
from src.agent.marketing.utils import scrape_website, get_upcoming_events, get_latest_news
from datetime import datetime
import pandas as pd
import os
import json
load_dotenv()

from openai import OpenAI

llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@tool
def datetime_tool() -> str:
    """Returns the current datetime."""
    return datetime.now().isoformat()


@tool
def load_brand_guidelines_from_website(url: str) -> str:
    """Loads the brand guidelines from a website."""
    try:
        content = scrape_website(url)

        print(f"Scraped website content: {content}")

        prompt = f"""
        You are a marketing expert.
        From the website content below, extract the brand guidelines from the website if they are explicitly stated.
        If they are not explicitly stated, you need to infer or suggest the brand guidelines from the website.
        The brand guidelines should include the following:
        - Brand values
        - Brand mission
        - Brand vision
        - Brand personality
        - Brand tone of voice
        - Brand style
        - Brand colors
        - Brand fonts

        Return a markdown document with the brand guidelines.

        ### Website Content
        {content}
        """

        response = llm.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
            ]
        )

        print(response.choices[0].message.content)

        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in load_brand_guidelines_from_website: {e}")
        return f"Error loading brand guidelines: {str(e)}"

    
@tool
def get_upcoming_events_tool() -> list[dict]:
    """Get the upcoming events."""
    try:
        result = get_upcoming_events()
        print(f"get_upcoming_events returned: {result[:1]}")
        return result
    except Exception as e:
        print(f"Error in get_upcoming_events_tool: {e}")
        return {"error": str(e), "events": []}


@tool
def get_latest_news_for_brand(user_query: str, brand_guidelines: str, limit: int = 2) -> list[dict]:
    """Fetches recent news articles based on the brand guidelines.
    
    Params:
    - user_query: The user query.
    - brand_guidelines: The brand guidelines.
    - limit: The number of news articles to fetch.
    """

    print("Getting latest news for user query: ", user_query)
    print("Getting latest news for brand guidelines: ", brand_guidelines)

    prompt = f"""
    You are a marketing expert. For the following user query and brand guidelines, return a list of 2 keywords that are relevant to the brand, and highly relevant for searching news articles. Think categories.
    ### User Query
    {user_query}

    ### Brand Guidelines
    {brand_guidelines}

    The keywords should be very specific. Examples: 
    If the brand is OpenAI, return Artificial Intelligence, ChatGPT etc. Do not just return "Technology".
    If the brand is Nike, return "Sports", "Athleisure", "Fitness" etc. Do not just return "Clothing".    

    Return only a json object with list of keywords, no other text with the format.
    {{
        "keywords": ["keyword1", "keyword2"]
    }}
    """

    print("Prompt: ", prompt)
    

    response = llm.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
        ],
        response_format={"type": "json_object"}
    )
    
    print("Response: ", response.choices[0].message.content)

    data = json.loads(response.choices[0].message.content)

    print("Getting latest news: ", data["keywords"])

    news = get_latest_news(data["keywords"], limit)

    print("News: ")
    print(news.head())

    return news.to_dict(orient="records")

@tool
def generate_brand_campaign_ideas(brand_guidelines: str, news: list[dict] = [], upcoming_events: list[dict] = []) -> str:
    """Generates brand campaign ideas based on the brand guidelines, news and upcoming events. Always use this tool to generate campaign ideas."""

    prompt = {
        "today_date": datetime.now().strftime("%Y-%m-%d"),
        "role": "You are a marketing expert",
        "brand_guidelines": brand_guidelines,
        "news": news,
        "upcoming_events": upcoming_events,
        "task": "Generate a list of 5 campaign ideas based on the news and upcoming events",
        "response_format": """the output should be a JSON object with the following format:
        {{
            "campaign_ideas": ["campaign_idea1","campaign_idea2"...]
        }}"""
    }

    content = f"""json```{json.dumps(prompt)}```"""
    print("Prompt: ", content)


    response = llm.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": content},
        ],
        response_format={"type": "json_object"}
    )

    print("Response: ", response.choices[0].message.content)

    data = json.loads(response.choices[0].message.content)

    print("Campaign ideas: ", data["campaign_ideas"])

    return data["campaign_ideas"]
    
    
@tool  
def generate_tweets(user_query: str, brand_guidelines: str, news: list[dict], upcoming_events: list[dict], limit: int = 5) -> str:
    """Generates tweets based on the brand guidelines and recent news/events. Call this after getting news and events."""



    # This tool should be called after get_latest_news_for_brand and get_upcoming_events_tool
    # The LLM will have that context from previous tool calls in the conversation
    
    prompt = {
        "today_date": datetime.now().strftime("%Y-%m-%d"),
        "role": "You are a social media content creation expert",
        "brand_guidelines": brand_guidelines,
        "news": news,
        "upcoming_events": upcoming_events,
        "user_query": user_query,
        "task": f"Generate a list of {limit} tweets based on the brand guidelines and user query. Use any relevant news and events information from the conversation context. Create relevant, engaging tweets that align with the brand guidelines. Return as JSON with format: {{\"tweets\": [\"tweet1\", \"tweet2\", \"tweet3\"]}}"
    }

    content = f"""{json.dumps(prompt)}"""
    print("Prompt: ", content)

    response = llm.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": content},
        ],
        response_format={"type": "json_object"}
    )

    print("Response: ", response.choices[0].message.content)

    data = json.loads(response.choices[0].message.content)

    print("Tweets: ", data["tweets"])
    return data["tweets"]
