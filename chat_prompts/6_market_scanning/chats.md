Given these requirements and schema / api information, can you create a detailed list of user stories and their corresponding tasks that you will need to perform to achieve the requirements. Make the tasks granular, one task is one operation.

Requirements:

Feature 5: High-Potential Market Scanning

**Goal:** Implement a feature allowing users to search entire sectors or domains for high-potential short-term or long-term gains.

* **Requirements:**
* Create a backend service that pulls a list of tickers within a user-specified sector.
* Implement a batch-processing LangGraph workflow that runs lightweight analysis on multiple tickers concurrently.
* Build a frontend interface where users select a sector from a dropdown and trigger the scan, displaying the top 5 results ranked by Gemini's confidence score.


* **Deliverables:**
| Component | Deliverable Description |
| :--- | :--- |
| **API Route** | `POST /api/scan/sector` accepting a domain string and timeframe (short/long). |
| **Frontend UI** | A "Sector Scan" dedicated page or tab with loading skeletons while the batch process runs. |

---

Schema / API Definitions:

Feature 5: High-Potential Market Scanning

* **`POST /api/scan/sector`**
* **Request:** `{ "sector": "Technology", "timeframe": "short_term" }`
* **Response (200):**
```json
{
  "scan_id": "uuid",
  "results": [
    { "ticker": "NVDA", "confidence_score": 92, "summary": "Strong momentum..." },
    { "ticker": "AMD", "confidence_score": 88, "summary": "Undervalued relative to peers..." }
  ]
}

```

Here is the granular, operation-by-operation breakdown of user stories and tasks for Feature 5 (High-Potential Market Scanning).

This feature introduces concurrency. Because analyzing multiple stocks sequentially would cause the API request to time out, we need to design the LangGraph workflow to process the tickers in parallel using an asynchronous "Map-Reduce" or batch-processing pattern.

### User Story 1: Sector Ticker Retrieval Tool

**"As a backend developer, I need a service to fetch a list of top tickers within a specific sector so that the AI knows which stocks to scan."**

* **Task 1.1:** Create a `tools/sector_data.py` file in the `/backend` directory.
* **Task 1.2:** Implement a `get_tickers_by_sector(sector: str, limit: int = 15) -> list[str]` function.
* **Task 1.3:** Configure this function to map standard sector strings (e.g., "Technology", "Healthcare", "Finance") to valid API queries (using a free screener API like Finviz, or predefined static lists if a free API is unavailable).
* **Task 1.4:** Add error handling to return an empty list or a default fallback list if the sector is unrecognized or the upstream data source fails.

### User Story 2: Lightweight Batch Agent Workflow

**"As an AI agent, I need a streamlined version of my analysis workflow that can be run concurrently so that I can evaluate multiple stocks quickly without hitting API rate limits or timing out."**

* **Task 2.1:** Create a `workflows/batch_scan_graph.py` file.
* **Task 2.2:** Define a `LightweightAgentState` TypedDict containing `ticker` (str), `summary_data` (dict), and `scan_result` (dict).
* **Task 2.3:** Implement a `fetch_summary_data_node` that uses `yfinance` to pull *only* the current price, 1-year target estimate, and recommendation mean (skipping the Playwright news scraping to save time).
* **Task 2.4:** Define a new Pydantic schema `ScanOutput` with `confidence_score` (int) and `summary` (str, max 2 sentences).
* **Task 2.5:** Implement an `evaluate_potential_node` that binds `ScanOutput` to Gemini. The prompt must instruct Gemini to assess the summary data against the user's requested `timeframe` (short-term vs. long-term) and output the score.
* **Task 2.6:** Construct and compile the `LightweightStateGraph` (START $\rightarrow$ fetch_summary $\rightarrow$ evaluate_potential $\rightarrow$ END).
* **Task 2.7:** Create an asynchronous wrapper function `run_batch_scan(tickers: list[str], timeframe: str)` that utilizes `asyncio.gather` (or LangChain's `.abatch()` method) to execute the lightweight graph on all tickers concurrently.
* **Task 2.8:** Add a sorting mechanism within `run_batch_scan` to filter out failures, rank the successful results by `confidence_score` descending, and slice the top 5.

### User Story 3: FastAPI Sector Scan Endpoint

**"As a frontend application, I need an endpoint to submit my scan criteria and receive the ranked top 5 results."**

* **Task 3.1:** Create `scan_schemas.py` and define a Pydantic model `ScanRequest` (sector: str, timeframe: Literal['short_term', 'long_term']).
* **Task 3.2:** Define a Pydantic model `ScanResponse` matching the required JSON schema (scan_id, list of results).
* **Task 3.3:** Open `routes/analysis_routes.py` and add the `POST /api/scan/sector` endpoint, protected by the `get_current_user` dependency.
* **Task 3.4:** Inside the route handler, call the `get_tickers_by_sector` tool.
* **Task 3.5:** Pass the resulting list of tickers and the requested timeframe to the `run_batch_scan` asynchronous wrapper.
* **Task 3.6:** Generate a unique UUID for the `scan_id`, format the returned top 5 results into the `ScanResponse` schema, and return the 200 OK response.

### User Story 4: Frontend UI & State Management for Scanning

**"As a user, I want a dedicated UI to select a market sector, initiate a scan, and see visual feedback while the system analyzes the market."**

* **Task 4.1:** In the frontend, create a new Zustand store or expand an existing one to include: `scanResults: array`, `isScanning: boolean`, and `scanError: string | null`.
* **Task 4.2:** Implement an async action `triggerSectorScan(sector, timeframe)` that sets `isScanning` to true, makes the POST request to `/api/scan/sector`, updates `scanResults` on success, and sets `isScanning` to false.
* **Task 4.3:** Create a `SectorScan.tsx` page/component.
* **Task 4.4:** Integrate shadcn/ui form elements: a `<Select>` dropdown for the Sector (e.g., Technology, Energy, Finance) and a `<Select>` dropdown for the Timeframe (Short Term, Long Term).
* **Task 4.5:** Add a "Run Scan" `<Button>` that triggers the Zustand action. Disable this button while `isScanning` is true.
* **Task 4.6:** Create a `ScanResultSkeleton.tsx` component using shadcn/ui `<Skeleton>` to display pulsing placeholder cards.
* **Task 4.7:** Conditionally render a list of `ScanResultSkeleton` components (e.g., 5 of them) when `isScanning` is true.
* **Task 4.8:** Conditionally render the actual `scanResults` mapping over the array to display the Ticker, Confidence Score (perhaps as a colored badge), and the AI-generated Summary when `isScanning` is false and results exist.
* **Task 4.9:** Add an "Add to Watchlist" button on each result card that dispatches the `addTickerToPortfolio` action from Feature 3.

---

Would you like to move on to Feature 6 (Real-Time Sidebar Chat) to map out how we will implement WebSockets and conversational memory, or would you prefer to review the specific `asyncio.gather` Python code needed for Task 2.7?

