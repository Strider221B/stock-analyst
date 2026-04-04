# /backend/workflows/stock_analysis_graph.py
import logging
from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from tools.finance_data import get_historical_prices
from tools.news_scraper import scrape_yahoo_finance_news

logger = logging.getLogger(__name__)

# 1. Define the State Schema
class AgentState(TypedDict):
    """The shared memory space for the LangGraph workflow."""
    ticker: str
    market_data: list[dict]
    news_data: str
    final_analysis: dict[str, Any]

# 2. Define the Nodes
async def fetch_market_data_node(state: AgentState):
    """Fetches 30 days of historical prices."""
    ticker = state["ticker"]
    logger.info(f"LangGraph: Fetching market data for {ticker}")
    try:
        prices = get_historical_prices(ticker, days=30)
        return {"market_data": prices}
    except Exception as e:
        logger.error(f"Market data fetch failed for {ticker}: {e}")
        # Graceful degradation: Pass error to state so the LLM knows data is missing
        return {"market_data": [{"error": f"Failed to fetch market data: {str(e)}"}]}

async def fetch_news_node(state: AgentState):
    """Scrapes top headlines using the async Playwright tool."""
    ticker = state["ticker"]
    logger.info(f"LangGraph: Fetching news for {ticker}")
    try:
        news_json = await scrape_yahoo_finance_news(ticker)
        return {"news_data": news_json}
    except Exception as e:
        logger.error(f"News fetch failed for {ticker}: {e}")
        # Graceful degradation: Return error as a JSON string
        return {"news_data": f'{{"error": "Failed to fetch news: {str(e)}"}}'}

async def generate_thesis_node(state: AgentState):
    """Placeholder for the GenAI analysis node."""
    logger.info(f"LangGraph: Generating thesis for {state['ticker']}")

    # We will inject the Gemini model here in the next step
    placeholder_analysis = {
        "status": "pending",
        "message": "LLM thesis generation coming next.",
        "data_points_collected": len(state.get("market_data", [])),
        "news_preview": state.get("news_data", "")[:100]
    }

    return {"final_analysis": placeholder_analysis}

# 3. Initialize and Route the Graph
workflow = StateGraph(AgentState)

workflow.add_node("fetch_market_data", fetch_market_data_node)
workflow.add_node("fetch_news", fetch_news_node)
workflow.add_node("generate_thesis", generate_thesis_node)

# Parallel execution (Fan-out)
workflow.add_edge(START, "fetch_market_data")
workflow.add_edge(START, "fetch_news")

# Parallel execution (Fan-in)
# LangGraph natively waits for both incoming edges to resolve before proceeding
workflow.add_edge("fetch_market_data", "generate_thesis")
workflow.add_edge("fetch_news", "generate_thesis")

# Terminate
workflow.add_edge("generate_thesis", END)

# 4. Add Checkpointer and Compile
memory = MemorySaver()
stock_agent_app = workflow.compile(checkpointer=memory)

# 5. Local Testing Block
if __name__ == "__main__":
    import asyncio

    async def test_run():
        initial_state = {"ticker": "AAPL"}
        # IMPORTANT: Checkpointers require a thread_id to isolate memory states
        config = {"configurable": {"thread_id": "test_run_001"}}

        result = await stock_agent_app.ainvoke(initial_state, config=config)

        print("\n--- Final State ---")
        print("Market Data Length:", len(result.get("market_data", [])))
        print("News Preview:", result.get("news_data", "")[:100])
        print("Analysis:", result.get("final_analysis"))

    asyncio.run(test_run())
