from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import os

load_dotenv()

# Initialize the client with your API key
app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

def datetime_tool() -> str:
    """Returns the current datetime."""
    return datetime.now().isoformat()


def get_latest_news(keywords: list[str], limit: int = 5) -> pd.DataFrame:
    news = []

    print("Getting latest news for keywords: ", keywords)

    current_date = datetime.now().strftime("%Y-%m-%d")
    for keyword in keywords:
        search_results = app.search(
            query=f"site:news.google.com {keyword} {current_date}",
            limit=limit
        )

        news.extend(search_results.data)
    
    print("News ", news)
    
    return pd.DataFrame(news)
    

def scrape_website(url: str, maxAge: int = 3600000) -> str:
    """Loads the brand guidelines from a website."""
    return app.scrape_url(
        url, 
        formats=['markdown'],
        maxAge=maxAge  
    )

def extract_content_from_website(url: str, prompt: str) -> str:
    """Loads the brand guidelines from a website."""
    result = app.extract(
        urls=[url],
        prompt=prompt,
        schema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The main text content extracted from the website"
                },
                "colors": {
                    "type": "object",
                    "properties": {
                        "primary": {"type": "string"},
                        "secondary": {"type": "string"},
                        "tertiary": {"type": "string"},
                        "accent": {"type": "string"}
                    }
                },
                "fonts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "url": {"type": "string"}
                        }
                    }
                }
            }
        }
    )
    return result.data

def get_upcoming_events() -> dict:
    """Get the upcoming festivals in a country."""
    df = pd.read_csv("data/events-india.csv")
    print(df.head())

    today = datetime.now().strftime("%Y-%m-%d")
    upcoming_events = df[df['FullDate'] >= today][['FullDate', 'Event']]
    return upcoming_events.to_dict(orient="records")



if __name__ == "__main__":
    print(get_upcoming_events())