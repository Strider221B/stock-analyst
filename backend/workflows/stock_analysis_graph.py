# /backend/workflows/stock_analysis_graph.py
import asyncio
import json
import logging
import operator
from typing import Annotated, Any, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from tools.finance_data import get_historical_prices
from tools.news_scraper import scrape_yahoo_finance_news

logger = logging.getLogger(__name__)

# [Warning 1 Fixed] Added explicit 'errors' channel
class AgentState(TypedDict):
    """The shared memory space for the LangGraph workflow."""
    ticker: str
    market_data: list[dict]
    news_data: str
    final_analysis: dict[str, Any]
    errors: Annotated[list[str], operator.add]

# [Critical 1 Fixed] True parallel execution via asyncio.gather
async def fetch_all_data_node(state: AgentState):
    """Fetches market data and news concurrently."""
    ticker = state["ticker"]
    logger.info(f"LangGraph: Fetching all data concurrently for {ticker}")

    errors = state.get("errors", [])

    # Internal helpers to catch errors without breaking the gather
    async def safe_fetch_market():
        try:
            # [Warning 2 Fixed] Offload sync yfinance call to a thread
            res = await asyncio.to_thread(get_historical_prices, ticker, 30)
            return res, None
        except Exception as e:
            logger.error(f"Market data fetch failed for {ticker}: {e}")
            return [], f"Market data failed: {str(e)}"

    async def safe_fetch_news():
        try:
            res = await scrape_yahoo_finance_news(ticker)
            return res, None
        except Exception as e:
            logger.error(f"News fetch failed for {ticker}: {e}")
            # [Warning 3 Fixed] json.dumps instead of fragile f-string interpolation
            err_json = json.dumps([{"error": f"Failed to fetch news: {str(e)}"}])
            return err_json, f"News fetch failed: {str(e)}"

    # Execute both I/O bounds tasks at the exact same time
    (market_res, market_err), (news_res, news_err) = await asyncio.gather(
        safe_fetch_market(),
        safe_fetch_news()
    )

    if market_err: errors.append(market_err)
    if news_err: errors.append(news_err)

    return {
        "market_data": market_res,
        "news_data": news_res,
        "errors": errors
    }

async def generate_thesis_node(state: AgentState):
    """Placeholder for the GenAI analysis node."""
    # [Suggestion 1 Fixed] Explicit warning for incomplete implementation
    logger.warning("generate_thesis_node is a placeholder — LLM not yet integrated.")
    logger.info(f"LangGraph: Generating thesis for {state['ticker']}")

    placeholder_analysis = {
        "status": "pending",
        "message": "LLM thesis generation coming next.",
        "data_points_collected": len(state.get("market_data", [])),
        "errors_encountered": len(state.get("errors", []))
    }

    return {"final_analysis": placeholder_analysis}

# [Critical 2 Fixed] Factory function prevents module-level side effects
def create_stock_agent(checkpointer=None):
    """Factory function to build and compile the graph safely."""
    workflow = StateGraph(AgentState)

    workflow.add_node("fetch_all_data", fetch_all_data_node)
    workflow.add_node("generate_thesis", generate_thesis_node)

    # Simplified sequential edge routing
    workflow.add_edge(START, "fetch_all_data")
    workflow.add_edge("fetch_all_data", "generate_thesis")
    workflow.add_edge("generate_thesis", END)

    return workflow.compile(checkpointer=checkpointer or MemorySaver())

# Expose a default instance for FastAPI imports
stock_agent_app = create_stock_agent()

if __name__ == "__main__":
    async def test_run():
        # Initialize the errors list to avoid NoneType issues
        initial_state = {"ticker": "AAPL", "errors": []}
        config = {"configurable": {"thread_id": "test_run_001"}}

        # [Suggestion 2 Fixed] Try/except wrapper for the test runner
        try:
            result = await stock_agent_app.ainvoke(initial_state, config=config)

            print("\n--- Final State ---")
            print("Market Data Points:", len(result.get("market_data", [])))
            print("News Preview:", result.get("news_data", "")[:100])
            print("Errors:", result.get("errors", []))
            print("Analysis:", result.get("final_analysis"))
        except Exception as e:
            print(f"\n❌ Graph Execution Catastrophically Failed: {e}")

    asyncio.run(test_run())
