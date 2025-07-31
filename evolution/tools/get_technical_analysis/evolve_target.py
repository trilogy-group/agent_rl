"""
Tool: get_technical_analysis
Extracted from: tools.py

Function get_technical_analysis
"""

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


if __name__ == "__main__":
    # Test the tool here
    # result = get_technical_analysis(...)
    pass
