from firecrawl import FirecrawlApp
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from evolution.decorators import evolve

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

import os

load_dotenv()

# Initialize the client with your API key
app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

@tool
def datetime_tool() -> str:
    """Returns the current datetime."""
    return datetime.now().isoformat()


@tool
def search_tool(query: str) -> list:
    """Searches the web using the Firecrawl API and returns the top 5 results.

    Args:
        query: The search query string.

    Returns:
        A list containing the search results data.
    """
    print("Called search tool with query: ", query)
    search_result = app.search(query, limit=5)
    return search_result.data

search_tool_node = ToolNode([search_tool])



@tool
def get_basic_stock_info(ticker: str) -> pd.DataFrame:
    """Retrieves basic information about a single stock.
    For more information, you can perform technical analysis, assess stock risk or perform fundamental analysis.
    
    Params:
    - ticker: The stock ticker symbol.
    """
    print("Called get_basic_stock_info with ticker: ", ticker)
    stock = yf.Ticker(ticker)
    info = stock.info
    
    basic_info = pd.DataFrame({
        'Name': [info.get('longName', 'N/A')],
        'Sector': [info.get('sector', 'N/A')],
        'Industry': [info.get('industry', 'N/A')],
        'Market Cap': [info.get('marketCap', 'N/A')],
        'Current Price': [info.get('currentPrice', 'N/A')],
        '52 Week High': [info.get('fiftyTwoWeekHigh', 'N/A')],
        '52 Week Low': [info.get('fiftyTwoWeekLow', 'N/A')],
        'Average Volume': [info.get('averageVolume', 'N/A')]
    })
    return basic_info

@tool
def get_fundamental_analysis(ticker: str, period: str = '1y') -> pd.DataFrame:
    """
    Performs fundamental analysis on a given stock for a specific period.
    
    Params:
    - ticker: The stock ticker symbol.
    - period: The period to consider for historical data (default is 1 year) (available time-periods: ["1y", "2y", "5y", "10y", "ytd", "max"]).
    
    Returns: 
    - DataFrame with fundamental metrics.
    """
    print("Called get_fundamental_analysis with ticker: ", ticker)
    stock = yf.Ticker(ticker)
    
    # Fetch historical data for the given period
    history = stock.history(period=period)
    
    # Fetch latest available financial info
    info = stock.info
    
    fundamental_analysis = pd.DataFrame({
        'PE Ratio': [info.get('trailingPE', 'N/A')],
        'Forward PE': [info.get('forwardPE', 'N/A')],
        'PEG Ratio': [info.get('pegRatio', 'N/A')],
        'Price to Book': [info.get('priceToBook', 'N/A')],
        'Dividend Yield': [info.get('dividendYield', 'N/A')],
        'EPS (TTM)': [info.get('trailingEps', 'N/A')],
        'Revenue Growth': [info.get('revenueGrowth', 'N/A')],
        'Profit Margin': [info.get('profitMargins', 'N/A')],
        'Free Cash Flow': [info.get('freeCashflow', 'N/A')],
        'Debt to Equity': [info.get('debtToEquity', 'N/A')],
        'Return on Equity': [info.get('returnOnEquity', 'N/A')],
        'Operating Margin': [info.get('operatingMargins', 'N/A')],
        'Quick Ratio': [info.get('quickRatio', 'N/A')],
        'Current Ratio': [info.get('currentRatio', 'N/A')],
        'Earnings Growth': [info.get('earningsGrowth', 'N/A')],
        'Stock Price Avg (Period)': [history['Close'].mean()],
        'Stock Price Max (Period)': [history['Close'].max()],
        'Stock Price Min (Period)': [history['Close'].min()]
    })
    
    return fundamental_analysis

@tool
def get_stock_risk_assessment(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Performs a risk assessment on a given stock.
    
    Params:
    - ticker: The stock ticker symbol.
    - period: The time period for historical data (default: "1y").
    """
    print("Called get_stock_risk_assessment with ticker: ", ticker)
    stock = yf.Ticker(ticker)
    history = stock.history(period=period)
    
    # Calculate daily returns
    returns = history['Close'].pct_change().dropna()
    
    # Calculate risk metrics
    volatility = returns.std() * np.sqrt(252)  # Annualized volatility
    beta = calculate_beta(returns, '^GSPC', period)  # Beta relative to S&P 500
    var_95 = np.percentile(returns, 5)  # 95% Value at Risk
    max_drawdown = calculate_max_drawdown(history['Close'])
    
    risk_assessment = pd.DataFrame({
        'Annualized Volatility': [volatility],
        'Beta': [beta],
        'Value at Risk (95%)': [var_95],
        'Maximum Drawdown': [max_drawdown],
        'Sharpe Ratio': [calculate_sharpe_ratio(returns)],
        'Sortino Ratio': [calculate_sortino_ratio(returns)]
    })
    
    return risk_assessment

def calculate_beta(stock_returns, market_ticker, period):
    market = yf.Ticker(market_ticker)
    market_history = market.history(period=period)
    market_returns = market_history['Close'].pct_change().dropna()
    
    # Align the dates of stock and market returns
    aligned_returns = pd.concat([stock_returns, market_returns], axis=1).dropna()
    
    covariance = aligned_returns.cov().iloc[0, 1]
    market_variance = market_returns.var()
    
    return covariance / market_variance

def calculate_max_drawdown(prices):
    peak = prices.cummax()
    drawdown = (prices - peak) / peak
    return drawdown.min()

def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    excess_returns = returns - risk_free_rate/252
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

def calculate_sortino_ratio(returns, risk_free_rate=0.02, target_return=0):
    excess_returns = returns - risk_free_rate/252
    downside_returns = excess_returns[excess_returns < target_return]
    downside_deviation = np.sqrt(np.mean(downside_returns**2))
    return np.sqrt(252) * excess_returns.mean() / downside_deviation

@evolve()
@tool
def get_technical_analysis(ticker: str, period: str = "1mo") -> pd.DataFrame:
    """Perform technical analysis on a given stock.
    
    Params:
    - ticker: The stock ticker symbol.
    - period: The time period for historical data (available time-periods: ["1d", "5d", "1mo", "3mo", "6mo"]).
    """
    print("Called get_technical_analysis with ticker: ", ticker)
    stock = yf.Ticker(ticker)
    history = stock.history(period=period)
    
    # Calculate indicators
    history['SMA_50'] = history['Close'].rolling(window=50).mean()
    history['SMA_200'] = history['Close'].rolling(window=200).mean()
    history['RSI'] = calculate_rsi(history['Close'])
    history['MACD'], history['Signal'] = calculate_macd(history['Close'])
    
    latest = history.iloc[-1]
    
    analysis = pd.DataFrame({
        'Indicator': [
            'Current Price',
            '50-day SMA',
            '200-day SMA',
            'RSI (14-day)',
            'MACD',
            'MACD Signal',
            'Trend',
            'MACD Signal',
            'RSI Signal'
        ],
        'Value': [
            f'${latest["Close"]:.2f}',
            f'${latest["SMA_50"]:.2f}',
            f'${latest["SMA_200"]:.2f}',
            f'{latest["RSI"]:.2f}',
            f'{latest["MACD"]:.2f}',
            f'{latest["Signal"]:.2f}',
            analyze_trend(latest),
            analyze_macd(latest),
            analyze_rsi(latest)
        ]
    })
    
    return analysis

@tool
def get_stock_news(ticker: str, limit: int = 10) -> pd.DataFrame:
    """Fetches recent news articles related to a specific stock.
    
    Params:
    - ticker: The stock ticker symbol.
    - limit: The number of news articles to fetch.
    """
    print("Called get_stock_news with ticker: ", ticker)
    stock = yf.Ticker(ticker)
    news = stock.news[:limit]
    
    news_data = []
    for article in news:
        news_entry = {
            "Title": article['title'],
            "Publisher": article['publisher'],
            "Published": datetime.fromtimestamp(article['providerPublishTime']).strftime('%Y-%m-%d %H:%M:%S'),
            "Link": article['link']
        }
        news_data.append(news_entry)
    
    return pd.DataFrame(news_data)

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(series, short_window=12, long_window=26, signal_window=9):
    short_ema = series.ewm(span=short_window, adjust=False).mean()
    long_ema = series.ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal


def analyze_trend(latest):
    if latest['Close'] > latest['SMA_50'] > latest['SMA_200']:
        return "Bullish"
    elif latest['Close'] < latest['SMA_50'] < latest['SMA_200']:
        return "Bearish"
    else:
        return "Neutral"

def analyze_macd(latest):
    if latest['MACD'] > latest['Signal']:
        return "Bullish"
    else:
        return "Bearish"

def analyze_rsi(latest):
    if latest['RSI'] > 70:
        return "Overbought"
    elif latest['RSI'] < 30:
        return "Oversold"
    else:
        return "Neutral"

def analyze_bollinger_bands(latest):
    if latest['Close'] > latest['BB_Upper']:
        return "Price above upper band (potential overbought)"
    elif latest['Close'] < latest['BB_Lower']:
        return "Price below lower band (potential oversold)"
    else:
        return "Price within bands"

def format_number(value):
    if value != 'N/A':
        return f'${value:,.2f}'
    else:
        return 'N/A'

def interpret_pe_ratio(trailing_pe):
    if trailing_pe < 15:
        return "Undervalued"
    elif trailing_pe > 30:
        return "Overvalued"
    else:
        return "Neutral"

def interpret_price_to_book(price_to_book):
    if price_to_book < 1:
        return "Undervalued"
    elif price_to_book > 3:
        return "Overvalued"
    else:
        return "Neutral"