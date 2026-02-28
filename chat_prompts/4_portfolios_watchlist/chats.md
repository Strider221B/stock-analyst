Given these requirements and schema / api information, can you create a detailed list of user stories and their corresponding tasks that you will need to perform to achieve the requirements. Make the tasks granular, one task is one operation.

Requirements:

Feature 3: Portfolio & Watchlist Dashboard

**Goal:** Allow users to manage the stocks and domains they want the AI to analyze, providing a clean UI to view their selected assets.

* **Requirements:**
* Create CRUD endpoints in FastAPI for users to add or remove stock tickers (e.g., adding US-listed tech stocks like GOOGL).
* Build a React dashboard displaying the user's active watchlist.
* Integrate a lightweight charting library (like Recharts) to display a basic historical price line graph for selected stocks on the dashboard.


* **Deliverables:**
| Component | Deliverable Description |
| :--- | :--- |
| **API Routes** | `GET /api/portfolio`, `POST /api/portfolio/add`, `DELETE /api/portfolio/{ticker}`. |
| **Frontend UI** | Main Dashboard view (`/dashboard`), a "Stock Card" component, and an "Add Ticker" modal. |

---

Schema / API Definitions:

Feature 3: Portfolios & Watchlists

* **`GET /api/portfolios`**
* **Response (200):** ```json
[
{
"id": "uuid",
"name": "US Tech",
"account_type": "INTERNATIONAL",
"items": [ {"ticker": "GOOGL"}, {"ticker": "MSFT"} ]
}
]
```

```




* **`POST /api/portfolios`**
* **Request:** `{ "name": "New Watchlist", "account_type": "DOMESTIC" }`
* **Response (201):** Returns the created portfolio object.


* **`POST /api/portfolios/{portfolio_id}/items`**
* **Request:** `{ "ticker": "GOOGL" }`
* **Response (201):** `{ "message": "Ticker added" }`

Here is the granular, operation-by-operation breakdown of user stories and tasks for Feature 3 (Portfolio & Watchlist Dashboard).

These tasks bridge the gap between your backend PostgreSQL database and the React UI, allowing you to establish logical separations for different investment types (like domestic trading accounts versus international employee equity/RSUs).

### User Story 1: Backend Portfolio Management Endpoints

**"As a backend developer, I need RESTful CRUD endpoints for portfolios and portfolio items so that users can create distinct watchlists and add/remove stock tickers."**

* **Task 1.1:** Create `portfolio_schemas.py` in the `/backend` directory. Define Pydantic models for `PortfolioCreate` (name, account_type), `PortfolioResponse` (id, name, account_type, items), and `PortfolioItemCreate` (ticker).
* **Task 1.2:** Create a `portfolio_routes.py` router file and include it in the main FastAPI application instance, applying the `get_current_user` dependency to protect all routes.
* **Task 1.3:** Implement the `POST /api/portfolios` endpoint. It should extract the user ID from the dependency, validate the `account_type` (e.g., ensuring it matches valid categories like 'DOMESTIC', 'INTERNATIONAL', or 'EMPLOYEE_EQUITY'), save the new portfolio to the database, and return a 201 status.
* **Task 1.4:** Implement the `GET /api/portfolios` endpoint. Query the database for all portfolios associated with the current user, eagerly loading the associated `portfolio_items` relationship, and return them as a nested JSON array.
* **Task 1.5:** Implement the `POST /api/portfolios/{portfolio_id}/items` endpoint. Verify the portfolio belongs to the user, validate the ticker format, insert the ticker into `portfolio_items`, and return a 201 status.
* **Task 1.6:** Implement a `DELETE /api/portfolios/{portfolio_id}/items/{ticker}` endpoint to allow users to remove a specific stock from a specific watchlist. Ensure it handles cases where the ticker doesn't exist gracefully (returning a 404).

### User Story 2: Historical Price Data Endpoint (For Charts)

**"As a backend developer, I need a lightweight endpoint that fetches recent historical prices so that the frontend dashboard can display sparkline charts for the saved tickers without running the full Gemini AI analysis."**

* **Task 2.1:** In `/backend/tools/finance_data.py`, create a `get_historical_prices(ticker: str, days: int = 30)` function using the `yfinance` library to fetch the closing prices for the last month.
* **Task 2.2:** Add a `GET /api/marketdata/{ticker}/history` endpoint in FastAPI that calls this function and returns an array of date-price pairs (e.g., `[{ "date": "2026-01-01", "price": 175.50 }, ...]`).
* **Task 2.3:** Implement simple Redis caching or in-memory LRU caching for this endpoint to prevent rate-limiting from Yahoo Finance if the user refreshes their dashboard frequently.

### User Story 3: Frontend State Management for Portfolios

**"As a frontend developer, I need to expand the global state store to handle portfolios so that the dashboard UI can efficiently render and update watchlists without unnecessary network requests."**

* **Task 3.1:** Create a `portfolioStore.ts` file using Zustand.
* **Task 3.2:** Define the state interface: `{ portfolios: Portfolio[], isLoading: boolean, error: string | null }`.
* **Task 3.3:** Implement a `fetchPortfolios` action that makes an Axios call to `GET /api/portfolios` and populates the store.
* **Task 3.4:** Implement a `createPortfolio` action that posts to `POST /api/portfolios` and appends the new portfolio to the local state upon success.
* **Task 3.5:** Implement an `addTickerToPortfolio` action that posts to `POST /api/portfolios/{portfolio_id}/items` and updates the nested items array in the local state.
* **Task 3.6:** Implement a `removeTicker` action that calls the DELETE endpoint and filters the removed ticker from the local state.

### User Story 4: Dashboard UI & Watchlist Layout

**"As a user, I want a clean dashboard where I can view my distinct portfolios, create new ones, and manage the stocks within them."**

* **Task 4.1:** Create a `Dashboard.tsx` view component. Implement a `useEffect` hook to call `fetchPortfolios` from the Zustand store on component mount.
* **Task 4.2:** Create a `CreatePortfolioModal.tsx` component using shadcn/ui Dialog and Form components. It should include a text input for the name and a select dropdown for the account type (Domestic, International, etc.).
* **Task 4.3:** Create an `AddTickerModal.tsx` component containing a text input for the stock symbol (e.g., adding "GOOGL" or "RELIANCE.NS").
* **Task 4.4:** Create a `PortfolioSection.tsx` component that maps over a single portfolio object and renders a grid layout for the stocks contained within it.
* **Task 4.5:** Assemble the Dashboard by rendering a "Create Watchlist" button and mapping over the user's portfolios, rendering a `PortfolioSection` for each.

### User Story 5: Stock Card & Chart Integration

**"As a user, I want to see a visual representation of a stock's recent performance on my dashboard so that I can gauge its trend at a glance."**

* **Task 5.1:** Install the charting library in the frontend (`npm install recharts`).
* **Task 5.2:** Create a `StockCard.tsx` component that accepts a `ticker` string as a prop.
* **Task 5.3:** Inside `StockCard.tsx`, implement a data-fetching hook (like SWR or React Query, or a simple `useEffect`) to call the `GET /api/marketdata/{ticker}/history` endpoint when the card mounts.
* **Task 5.4:** Implement a Recharts `<LineChart>` inside the card. Configure it to be a minimal "sparkline" (hide the X and Y axes, remove grid lines, and format the tooltip to show the date and price).
* **Task 5.5:** Add a "Remove" button (trash icon) to the top right of the `StockCard` that triggers the `removeTicker` Zustand action.
* **Task 5.6:** Add an "Analyze" button to the `StockCard` that will eventually route the user to the detailed Gemini analysis view (Feature 4).

---

Would you like to move on to detailing the tasks for Feature 4 (The Agentic AI Core with LangGraph and Gemini), or would you prefer to review the specific Recharts configuration for creating clean sparklines?

