import os
import requests
from openai import OpenAI
from tavily import TavilyClient

# 1. Plug in your API keys (Replace these with your actual keys)
FMP_API_KEY = "YOUR_FMP_API_KEY"
TAVILY_API_KEY = "YOUR_TAVILY_API_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# Initialize our free search and low-cost AI brain
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
ai_client = OpenAI(api_key=OPENAI_API_KEY)

# 2. Define our low-cost tools
def get_stock_price(ticker):
    """Fetches real-time stock price cleanly from FMP without using web search."""
    url = f"https://financialmodelingprep.com/api/v3/quote/{ticker.upper()}?apikey={FMP_API_KEY}"
    try:
        data = requests.get(url).json()
        if data:
            return f"Price for {ticker}: ${data[0]['price']}. Change: {data[0]['changesPercentage']}%"
        return "Stock not found."
    except Exception:
        return "Could not fetch data from FMP."

def search_stock_news(ticker):
    """Uses Tavily's free tier to find recent news headlines instead of expensive Exa loops."""
    query = f"Latest financial news for {ticker} stock"
    response = tavily_client.search(query=query, max_results=3)
    
    # Extract just the title and snippet to save tokens
    news_summary = ""
    for result in response['results']:
        news_summary += f"- Title: {result['title']}\n  Summary: {result['snippet']}\n"
    return news_summary

# 3. The Core Logic (A deterministic hybrid function)
def run_stock_report(ticker):
    print(f"🔄 Gathering data for {ticker.upper()}...")
    
    # Step A: Get structured numbers directly from FMP (Costs $0 in LLM tokens)
    price_data = get_stock_price(ticker)
    
    # Step B: Get recent news context from Tavily (Costs $0 on Free Tier)
    news_data = search_stock_news(ticker)
    
    # Step C: Hand the clean, pre-filtered data to a cheap LLM to summarize
    prompt = f"""
    You are a helpful financial assistant. Synthesize the following data into a clean summary.
    
    STOCK PRICE DATA:
    {price_data}
    
    RECENT NEWS:
    {news_data}
    """
    
    print("🧠 Summarizing with cheap LLM...")
    response = ai_client.chat.completions.create(
        model="gpt-4o-mini", # Extremely cheap model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    return response.choices[0].message.content

# 4. Run the program
if __name__ == "__main__":
    ticker_to_search = input("Enter a stock ticker (e.g., AAPL): ")
    report = run_stock_report(ticker_to_search)
    print("\n--- FINAL REPORT ---")
    print(report)
