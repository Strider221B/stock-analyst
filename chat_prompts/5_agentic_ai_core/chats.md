Given these requirements and schema / api information, can you create a detailed list of user stories and their corresponding tasks that you will need to perform to achieve the requirements. Make the tasks granular, one task is one operation.

Requirements:

The Agentic AI Core (LangGraph + Gemini)

**Goal:** Build the backend reasoning engine that fetches quantitative data, scrapes qualitative news, and synthesizes a final recommendation.

* **Requirements:**
* Develop a `yfinance` Python tool to fetch current prices, P/E ratios, and moving averages.
* Develop a `Playwright` Python tool to scrape the latest headlines and sentiment from financial news sites.
* Construct a LangGraph `StateGraph` with nodes for: *Fetch Market Data*, *Fetch News*, and *Generate Thesis*.
* Engineer the Gemini system prompt to output a strict JSON schema containing a "Buy/Hold/Sell" rating, a confidence score (0-100), and a structured thesis (e.g., evaluating the strategic value of reinvesting RSU dividend yields into specific equities).


* **Deliverables:**
| Component | Deliverable Description |
| :--- | :--- |
| **AI Tools** | `tools/finance_data.py` and `tools/news_scraper.py`. |
| **LangGraph** | `workflows/stock_analysis_graph.py` defining the nodes, edges, and state schema. |
| **API Route** | `POST /api/analyze/{ticker}` which triggers the LangGraph workflow and returns the JSON result. |

---

Schema / API Definitions:

Feature 4: Agentic AI Core (In-Depth Analysis)

* **`POST /api/analyze/{ticker}`**
* **Description:** Triggers the LangGraph workflow.
* **Response (200):**
```json
{
  "ticker": "GOOGL",
  "rating": "BUY",
  "confidence_score": 85,
  "current_price": 175.32,
  "thesis": "## AI Analysis\nBased on recent Q4 earnings and the deployment of new AI models..."
}

```

Here is the granular, operation-by-operation breakdown of user stories and tasks for Feature 4 (The Agentic AI Core).

This phase is where the core logic of the application resides. By decoupling the data gathering tools from the reasoning engine, you ensure the AI has clean, reliable context before it generates a thesis.

### User Story 1: Quantitative Data Tool (`yfinance`)

**"As an AI agent, I need a reliable tool to fetch real-time and historical quantitative data so that I can evaluate a stock's technical performance and valuation."**

* **Task 1.1:** Install the `yfinance` library in the `/backend` directory.
* **Task 1.2:** Create a `tools/finance_data.py` file.
* **Task 1.3:** Implement a `get_technical_indicators(ticker: str) -> dict` function that instantiates a `yf.Ticker` object.
* **Task 1.4:** Extract the current stock price, 50-day moving average, 200-day moving average, and trading volume.
* **Task 1.5:** Extract fundamental valuation metrics like the Trailing P/E, Forward P/E, and dividend yield (crucial for evaluating reinvestment strategies).
* **Task 1.6:** Add error handling to return a structured error dictionary if a ticker is invalid or delisted, preventing the LangGraph workflow from crashing.

### User Story 2: Qualitative News Scraper Tool (`Playwright`)

**"As an AI agent, I need to scrape current financial news headlines and articles so that I can assess market sentiment and recent business developments."**

* **Task 2.1:** Install Playwright and its Python dependencies (`pip install playwright` and run `playwright install chromium`).
* **Task 2.2:** Create a `tools/news_scraper.py` file.
* **Task 2.3:** Implement an asynchronous `scrape_yahoo_finance_news(ticker: str) -> str` function using Playwright's async API to launch a headless Chromium instance.
* **Task 2.4:** Write DOM selectors to navigate to `finance.yahoo.com/quote/{ticker}/news` (or an equivalent financial news aggregator) and bypass any initial cookie consent popups.
* **Task 2.5:** Extract the top 5 most recent headlines and their corresponding subtext/summary paragraphs.
* **Task 2.6:** Format the scraped headlines and summaries into a clean, combined text string or JSON array optimized for LLM token consumption.

### User Story 3: LangGraph State and Workflow Construction

**"As a backend developer, I want to orchestrate the data fetching and reasoning steps into a LangGraph state machine so that the execution flow is predictable, debuggable, and extensible."**

* **Task 3.1:** Install LangGraph and the Google GenAI LangChain integrations (`pip install langgraph langchain-google-genai`).
* **Task 3.2:** Create a `workflows/stock_analysis_graph.py` file.
* **Task 3.3:** Define a `TypedDict` class named `AgentState` containing the keys: `ticker` (str), `market_data` (dict), `news_data` (str), and `final_analysis` (dict).
* **Task 3.4:** Create a `fetch_market_data_node(state: AgentState)` function that calls the `yfinance` tool and returns the updated `market_data` state dictionary.
* **Task 3.5:** Create a `fetch_news_node(state: AgentState)` function that calls the Playwright scraper tool and returns the updated `news_data` state dictionary.
* **Task 3.6:** Initialize a `StateGraph(AgentState)` object. Add the market data, news, and (placeholder) analysis nodes.
* **Task 3.7:** Define the directed edges to dictate the flow: `START` $\rightarrow$ `fetch_market_data_node` $\rightarrow$ `fetch_news_node` $\rightarrow$ `generate_thesis_node` $\rightarrow$ `END`.
* **Task 3.8:** Compile the LangGraph instance so it is ready to be invoked.

### User Story 4: Gemini Prompt Engineering and JSON Structured Output

**"As an AI agent, I need a strictly defined system prompt and structured output schema so that my financial analysis is consistently formatted for the frontend React application."**

* **Task 4.1:** Inside `workflows/stock_analysis_graph.py`, initialize the `ChatGoogleGenerativeAI` model using the Gemini API key from the environment variables.
* **Task 4.2:** Define a Pydantic model (`AnalysisOutput`) mirroring the required JSON schema: `rating` (Literal['BUY', 'HOLD', 'SELL']), `confidence_score` (int), `current_price` (float), and `thesis` (str).
* **Task 4.3:** Bind the Pydantic model to the Gemini LLM using `.with_structured_output(AnalysisOutput)`.
* **Task 4.4:** Draft the system prompt. Instruct the model to act as an expert equity researcher, emphasizing specific strategic evaluations (such as the viability of reinvesting corporate RSU dividends into the analyzed asset).
* **Task 4.5:** Create the `generate_thesis_node(state: AgentState)` function. Combine the system prompt, `state["market_data"]`, and `state["news_data"]` into a single LangChain `HumanMessage`.
* **Task 4.6:** Invoke the structured LLM within the node and map the output to the `final_analysis` state key.

### User Story 5: FastAPI Endpoint Integration and History Caching

**"As a frontend application, I need a single REST API endpoint to trigger the full analysis workflow and receive the finalized JSON payload."**

* **Task 5.1:** Open the `routes/analysis_routes.py` file and include the `get_current_user` dependency.
* **Task 5.2:** Implement the `POST /api/analyze/{ticker}` endpoint.
* **Task 5.3:** Inside the route handler, instantiate the compiled LangGraph workflow and invoke it asynchronously with the initial state `{"ticker": ticker}`.
* **Task 5.4:** Extract the `final_analysis` dictionary from the completed LangGraph state.
* **Task 5.5:** Insert a new record into the `analysis_history` PostgreSQL table (from Feature 2) to cache the user ID, ticker, rating, confidence score, and markdown thesis.
* **Task 5.6:** Return the structured dictionary as a standard 200 OK JSON response to the client.

---

Would you like to move on to Feature 5 (High-Potential Market Scanning) to see how we modify this graph to run lightweight batch analyses on multiple tickers concurrently?

