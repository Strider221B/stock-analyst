## Prompt 1

I want to build an app in python backend and react front end for stock analysis and buy/sell suggestions based on latest news and technical analysis. For stock related information I want to start of by using yahoo finance first. The UI will allow user to log in, register stocks, provide in-depth analysis by using information from yahoo stocks and news and processed by Gemini. So Gemini will have access to free tools that it may need to perform its analysis, like data from yahoo finance, playwright etc. Use framework like langgraph but you may choose any other framework that may be better suited for this. The app will also search for stocks which have a large potential gains in the short and long term. The app will ask the user to  select companies and or domains in which they want to perform the search. It will also have a sidebar chat which will be connected to Gemini for discussing more on the recommendations. The app will be finally hosted on Azure and the deployment will happen via terraform.

Given these requirements, can you come up with the steps that are required to build an app like this. Start with basic - like let's start with the high level design and the individual components.

This sounds like a fantastic and highly capable project. Combining traditional financial data with an LLM's reasoning capabilities via an agentic framework like LangGraph is exactly the right approach for a modern stock analysis tool.

FastAPI is highly recommended for the Python backend because of its native asynchronous support, which is critical when running LLM calls, web scraping (Playwright), and web sockets (for your sidebar chat).

Here is a breakdown of the High-Level Design (HLD) and the foundational steps to bring this application to life.

### 1. High-Level Design (HLD): The Core Components

To keep the system modular, scalable, and easy to deploy on Azure, we should divide it into four main pillars:

* **The Frontend (Client Layer):**
* **Framework:** React (bootstrapped with Vite for speed).
* **State & Routing:** React Router for navigation, and Context API or Zustand for state management (user sessions, current stock being viewed).
* **UI Components:** A library like Tailwind CSS + shadcn/ui for clean, dashboard-style aesthetics.
* **Real-time Communication:** WebSockets or Server-Sent Events (SSE) to handle the streaming responses for the Gemini sidebar chat.


* **The Backend (API Layer):**
* **Framework:** Python with FastAPI. It’s fast, modern, and handles the asynchronous operations required by LangGraph and Playwright beautifully.
* **Authentication:** JWT (JSON Web Tokens) for secure user login.
* **Database:** PostgreSQL (hosted on Azure) to store user credentials, registered stocks (watchlists), and chat history.


* **The AI & Agent Layer (The "Brain"):**
* **Orchestrator:** LangGraph. This is perfect because stock analysis is often cyclical (fetch data $\rightarrow$ check if sufficient $\rightarrow$ scrape news if needed $\rightarrow$ analyze).
* **LLM:** Google Gemini API. It handles the reasoning, parsing of news sentiment, and generating buy/sell suggestions based on your rules.
* **Tools:** * `yfinance` for historical data, current prices, and technical indicators.
* `Playwright` for scraping dynamic financial news sites or specific domain searches.




* **Infrastructure & Deployment (Azure + Terraform):**
* **Hosting:** Azure Container Apps or Azure App Service for both the React frontend and FastAPI backend.
* **Database:** Azure Database for PostgreSQL.
* **IaC:** Terraform to provision the resource groups, database, App Services, and securely inject environment variables (like your Gemini API key).



---

### 2. Step-by-Step Development Plan

Building this requires a phased approach so you can test the AI reasoning before dealing with complex UI or deployment infrastructure.

#### Phase 1: Foundation & Data Modeling

1. **Repository Setup:** Create a monorepo or two separate repositories (frontend/backend).
2. **Database Design:** Outline your schemas. You will need tables for `Users`, `Portfolios` (the stocks/domains they registered), and `ChatSessions`.
3. **Basic Backend:** Stand up a skeleton FastAPI app with basic CRUD routes for users and portfolios. Implement JWT authentication.
4. **Basic Frontend:** Set up the React app with a login screen and a simple dashboard that fetches the user's saved stocks.

#### Phase 2: The Agentic Core (LangGraph + Gemini)

*This is the most critical phase where the actual value of your app is created.*

1. **Tool Creation:** Write Python functions to fetch data. Create a `get_stock_data(ticker)` using `yfinance` and a `scrape_latest_news(ticker, domain)` using Playwright.
2. **Graph Construction:** Build your LangGraph workflow.
* *Node 1:* Fetch financial metrics (e.g., analyzing tech stocks like Google, pulling P/E ratio, moving averages).
* *Node 2:* Fetch current news.
* *Node 3 (Gemini):* Synthesize the data and output a structured JSON response with a "Buy/Hold/Sell" rating, a confidence score, and a short thesis.


3. **Search Logic:** Implement the feature where users can scan specific domains/sectors for high-potential gains by combining sector-wide APIs with Gemini's filtering.

#### Phase 3: UI Integration

1. **Dashboard UI:** Build the views where users can register stocks and trigger the "In-Depth Analysis".
2. **Data Visualization:** Integrate a charting library (like Recharts or Lightweight Charts) to display the `yfinance` historical data alongside the Gemini-generated analysis.

#### Phase 4: The Sidebar Chat

1. **WebSocket Setup:** Create a WebSocket endpoint in FastAPI to handle real-time chat.
2. **Contextual Memory:** Configure LangChain/LangGraph memory so the Gemini chat agent knows what stock the user is currently looking at on their screen.
3. **React Sidebar:** Build a persistent sidebar component that sends messages to the WebSocket and streams Gemini's response back to the user.

#### Phase 5: Infrastructure as Code & Deployment

1. **Dockerization:** Write Dockerfiles for both the React frontend (usually served via Nginx) and the FastAPI backend.
2. **Terraform:** Write the `.tf` files to define your Azure Resource Group, PostgreSQL server, and Azure Container Apps/App Service.
3. **Deployment:** Run your Terraform apply, push your containers to Azure Container Registry, and launch the app.

---

Would you like me to sketch out the specific database schema for this, or would you prefer to dive straight into designing the LangGraph nodes for the stock analysis workflow?

## Prompt 2
Can you add 2 additional things to this - the entire app should run locally and will be tested locally before finally being pushed to Azure. Also, on Azure we want to have 2 separate environment - test and prod.

These are excellent additions. Ensuring the application runs entirely locally guarantees a tight developer feedback loop without incurring cloud costs, and establishing distinct `test` and `prod` environments is a fundamental best practice for reliable software delivery.

Here is how we integrate these requirements into the architecture and development plan.

### 1. Enabling Seamless Local Development

To run the entire stack locally and mimic the eventual Azure environment as closely as possible, we will use **Docker Compose**.

* **The `docker-compose.yml` file:** This will orchestrate your entire local setup with a single command (`docker-compose up`). It will define three primary services:
1. **Frontend Service:** Your React/Vite app with hot-reloading enabled.
2. **Backend Service:** Your FastAPI/Python app. We will configure it to mount your local code directory so changes reflect instantly without rebuilding the container.
3. **Database Service:** A local PostgreSQL container.


* **Environment Variables:** You will use a local `.env` file (which is strictly ignored by git) to securely store your Gemini API key, local database credentials, and Playwright configuration.
* **Local Playwright:** The FastAPI Dockerfile will need a step to install Playwright's browser binaries so the scraping tools work seamlessly inside the local container.

### 2. Architecting Test and Prod on Azure via Terraform

To manage two distinct environments without duplicating your infrastructure code, we will make your Terraform configuration modular.

* **Terraform Workspaces or Variable Files:** Instead of hardcoding Azure resource names, your Terraform scripts will use variables. You will have a `test.tfvars` file and a `prod.tfvars` file.
* **Azure Isolation:** * **Test Environment:** Deployed into a dedicated Azure Resource Group (e.g., `rg-stockapp-test`). It will use smaller, cheaper compute instances (Azure Container Apps/App Service) and a basic PostgreSQL tier. This is where you verify your Gemini prompts and LangGraph flows work with actual Azure networking.
* **Prod Environment:** Deployed into a separate Resource Group (e.g., `rg-stockapp-prod`). This ensures absolute isolation. If you accidentally drop a database table in `test`, `prod` remains untouched. It will use production-grade compute and database tiers.


* **CI/CD Pipeline (e.g., GitHub Actions):** You will set up a pipeline that automates this flow:
* Merging code to the `main` branch automatically builds the Docker images, runs Terraform with `test.tfvars`, and deploys to the Test environment.
* After manual verification, a manual trigger promotes those exact same Docker images to the Prod environment using `prod.tfvars`.



### 3. Updated Step-by-Step Plan

Here is how these requirements modify our previous development phases:

* **Phase 1: Foundation & Local Containerization**
* Set up React and FastAPI.
* **NEW:** Write the `Dockerfile` for each and a `docker-compose.yml` to spin up both along with a local PostgreSQL container. Ensure everything runs via `localhost`.


* **Phase 2 & 3: Agent Core & UI Integration**
* Build the LangGraph agents, integrate Gemini and yfinance, and build the UI.
* *All testing happens locally in the Docker Compose environment.*


* **Phase 4: Infrastructure as Code (Terraform)**
* Write the Terraform configuration (`.tf` files).
* **NEW:** Parameterize the Terraform code. Create `test.tfvars` (cheaper resources) and `prod.tfvars` (production resources).


* **Phase 5: CI/CD Pipeline & Deployment**
* **NEW:** Create a GitHub Actions workflow (or Azure DevOps pipeline).
* Configure it to deploy to the Azure `test` environment on every code merge.
* Add a manual approval gate to deploy to the Azure `prod` environment.



---

Would you like to start by drafting the `docker-compose.yml` file to get your local environment stubbed out, or would you prefer to look at how we should structure the Terraform directories for the test and prod environments?


## Prompt 3
Can you start with high level uml diagrams highlighting the design of the system? What are the different components and how they interact

Here are the high-level UML diagrams representing the logical architecture and the interaction flow of your system. To make these easy to read and integrate into your documentation, I have used Mermaid.js syntax, which generates standard UML diagrams.

### 1. Component Diagram: System Architecture

This diagram illustrates the structural design of the system, showing the distinct modules and how they connect.

```mermaid
flowchart TB
    subgraph Client [Frontend - React UI]
        Dashboard[Dashboard & Charts]
        ChatUI[Sidebar Chat UI]
    end

    subgraph Server [Backend - FastAPI]
        Auth[Auth & User Routes]
        DataRoutes[Stock/Portfolio Routes]
        WS_Manager[WebSocket Manager]

        subgraph AI_Layer [Agentic Layer]
            LangGraph[LangGraph Orchestrator]
        end
    end

    subgraph Database [Storage]
        DB[(PostgreSQL)]
    end

    subgraph External [External Tools & APIs]
        Gemini[Google Gemini API]
        YFinance[yfinance]
        Playwright[Playwright / News Scraper]
    end

    %% Connections
    Dashboard <-->|HTTP/REST| Auth
    Dashboard <-->|HTTP/REST| DataRoutes
    ChatUI <-->|WebSockets| WS_Manager

    Auth <--> DB
    DataRoutes <--> DB

    DataRoutes --> LangGraph
    WS_Manager <--> LangGraph

    LangGraph <--> Gemini
    LangGraph <--> YFinance
    LangGraph <--> Playwright

```

**Key Interactions:**

* **Frontend to Backend:** The React app uses standard HTTP REST calls for CRUD operations (registering stocks, logging in) and a persistent WebSocket connection for the Gemini sidebar chat.
* **Backend to Database:** FastAPI handles reading and writing user profiles, saved stock lists, and historical chat logs to PostgreSQL.
* **Backend to Agent:** When a user requests an analysis or sends a chat message, FastAPI hands the request off to the LangGraph Orchestrator.
* **Agent to External World:** LangGraph determines the execution path. It calls `yfinance` for quantitative data, triggers Playwright to scrape qualitative news, and feeds all that context to the Gemini API for synthesis.

---

### 2. Sequence Diagram: In-Depth Stock Analysis Flow

This diagram traces the step-by-step execution path when a user requests an analysis for a specific stock or sector.

```mermaid
sequenceDiagram
    actor User
    participant React as React Frontend
    participant Fast as FastAPI Backend
    participant Graph as LangGraph Orchestrator
    participant Tools as yfinance & Playwright
    participant Gemini as Gemini API
    participant DB as PostgreSQL

    User->>React: Clicks "Analyze Stock"
    React->>Fast: POST /api/analyze {ticker}
    Fast->>Graph: Trigger Analysis Workflow

    rect rgb(240, 240, 240)
        Note over Graph,Gemini: Agentic Loop Execution
        Graph->>Tools: Fetch historical data & technicals (yfinance)
        Tools-->>Graph: Return market data
        Graph->>Tools: Scrape latest news for ticker (Playwright)
        Tools-->>Graph: Return scraped news text
        Graph->>Gemini: Prompt: Analyze market data + news
        Gemini-->>Graph: Return structured JSON (Buy/Sell/Hold, Thesis)
    end

    Graph-->>Fast: Return Final Analysis
    Fast->>DB: Save analysis to user history
    Fast-->>React: 200 OK (JSON Response)
    React-->>User: Render Charts and AI Insights

```

**Key Takeaways from the Flow:**

1. **Asynchronous Nature:** The Agentic Loop block can take a few seconds (fetching data, scraping, waiting for the LLM). FastAPI's asynchronous nature (`async def`) ensures the server doesn't block other users while this happens.
2. **Stateless Agent, Stateful Backend:** LangGraph performs the heavy lifting and reasoning, but the FastAPI backend is responsible for taking the final output and persisting it to PostgreSQL before sending it back to the client.

---

### 3. Deployment Context (Local vs. Azure)

While not a standard UML diagram, it is important to map how these components sit in your environments:

* **Locally:** The React App, FastAPI App, and PostgreSQL DB all run in separate Docker containers managed by `docker-compose`. They communicate over a custom Docker bridge network.
* **On Azure (Test/Prod):** The Docker containers for React and FastAPI are pushed to an Azure Container Registry and hosted on Azure Container Apps. PostgreSQL is hosted on Azure Database for PostgreSQL (Flexible Server). Terraform manages the networking (VNet, subnets) that allows them to communicate securely.

Would you like to move on to defining the specific API endpoints (REST routes and WebSocket channels) between the React frontend and FastAPI backend, or would you prefer to start designing the database schema?

## Prompt 4

Can you create detailed requirements for this project which breaks down the different features, the deliverables for each feature that can be used in the subsequent steps? Make the individual feature requirements detailed enough so that I can take the individual features and start developing.

Here is a detailed breakdown of the requirements and deliverables for each feature. This structure is designed so you can take any individual feature block and immediately begin coding its components.

### Feature 1: Local Development & Foundation Setup

**Goal:** Establish the monorepo structure, initialize the core frameworks, and ensure the entire stack runs seamlessly on a local machine via Docker Compose.

* **Requirements:**
* Initialize a Vite + React + TypeScript frontend with Tailwind CSS and shadcn/ui.
* Initialize a FastAPI + Python backend with environment variable management.
* Set up a local PostgreSQL database instance.
* Configure Docker Compose to network the frontend, backend, and database together locally with hot-reloading enabled for development.


* **Deliverables:**
| Component | Deliverable Description |
| :--- | :--- |
| **Repository** | A standard monorepo folder structure (`/frontend`, `/backend`, `/infrastructure`). |
| **Docker** | `Dockerfile.dev` for both frontend and backend; a root `docker-compose.yml` file. |
| **Config Files** | `vite.config.ts` (proxying API requests to backend), `requirements.txt` / `pyproject.toml`, and a local `.env.example`. |

---

### Feature 2: Secure Authentication & Database Modeling

**Goal:** Create a secure user login system and define the foundational database schemas required to support user sessions and portfolio tracking.

* **Requirements:**
* Implement user registration and login endpoints in FastAPI.
* Implement JWT-based authentication using **HttpOnly, Secure cookies** to prevent XSS attacks.
* Design SQLAlchemy models for `Users`, `Portfolios` (capable of differentiating between domestic brokerage accounts and international holdings), and `ChatSessions`.
* Build the frontend React UI for Login/Registration, utilizing React Context or Zustand to manage the global authentication state.


* **Deliverables:**
| Component | Deliverable Description |
| :--- | :--- |
| **Database** | Alembic migration scripts defining the `users`, `portfolios`, and `chat_history` tables. |
| **API Routes** | `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/logout`. |
| **Frontend UI** | Authentication pages (`/login`, `/register`) and protected route wrappers in React Router. |

---

### Feature 3: Portfolio & Watchlist Dashboard

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

### Feature 4: The Agentic AI Core (LangGraph + Gemini)

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

### Feature 5: High-Potential Market Scanning

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

### Feature 6: Real-Time Sidebar Chat

**Goal:** Provide an interactive sidebar where the user can discuss the current stock analysis with Gemini in real-time.

* **Requirements:**
* Set up a FastAPI WebSocket endpoint (`/ws/chat/{session_id}`) to handle persistent, bi-directional communication.
* Configure LangChain/LangGraph memory to inject the context of the currently viewed stock analysis into the chat agent's prompt.
* Build a persistent React sidebar component that connects to the WebSocket and handles the streaming text chunks from Gemini.


* **Deliverables:**
| Component | Deliverable Description |
| :--- | :--- |
| **WebSocket** | `managers/websocket_manager.py` to handle active connections and broadcasting. |
| **AI Memory** | Integration of PostgreSQL-backed chat history into the Gemini chat node. |
| **Frontend UI** | A collapsible `<SidebarChat />` component globally accessible across the dashboard. |

---

### Feature 7: Infrastructure as Code & CI/CD

**Goal:** Automate the deployment process to Azure, maintaining strict isolation between the Test and Production environments.

* **Requirements:**
* Write Terraform configuration files utilizing variables to provision distinct Azure Resource Groups, Azure Container Apps, and Azure Database for PostgreSQL servers.
* Create a GitHub Actions workflow that builds the Docker images and pushes them to an Azure Container Registry (ACR).
* Configure the CI/CD pipeline to automatically apply Terraform and deploy to the `Test` environment on merge to `main`, with a manual approval step required to deploy to `Prod`.


* **Deliverables:**
| Component | Deliverable Description |
| :--- | :--- |
| **Terraform** | `main.tf`, `variables.tf`, `test.tfvars`, and `prod.tfvars`. |
| **CI/CD** | `.github/workflows/deploy.yml` defining the build, test-deploy, and prod-deploy jobs. |

---

Would you like me to generate the exact folder structure and the initial `docker-compose.yml` file to get Feature 1 started immediately?

## Prompt 5

Given these features, can you first come up with all the required database schemas and api contracts between the components - from feature 1 to 7?

This is the perfect next step. Defining the database schemas and API contracts upfront ensures that both your React frontend and FastAPI backend are speaking the exact same language before you write any component logic.

Here is the blueprint for your data layer and API communication.

### 1. Database Schemas (PostgreSQL)

To support the features—while allowing flexibility for different types of investment strategies, such as separating domestic trading from international brokerage accounts or tracking employee equity (RSUs)—we need a normalized relational structure.

#### `users`

Stores authentication and basic profile data.
| Column | Type | Constraints / Notes |
| :--- | :--- | :--- |
| `id` | UUID | Primary Key, default `uuid4()` |
| `email` | VARCHAR(255) | Unique, Not Null, Indexed |
| `password_hash` | VARCHAR(255) | Not Null (Argon2 or bcrypt) |
| `created_at` | TIMESTAMP | Default `now()` |

#### `portfolios`

Allows users to group their tracked stocks logically (e.g., "Tech Dividend Reinvestment", "Domestic Holdings").
| Column | Type | Constraints / Notes |
| :--- | :--- | :--- |
| `id` | UUID | Primary Key |
| `user_id` | UUID | Foreign Key -> `users.id`, On Delete Cascade |
| `name` | VARCHAR(100) | Not Null |
| `account_type` | VARCHAR(50) | e.g., 'DOMESTIC', 'INTERNATIONAL', 'EMPLOYEE_EQUITY' |
| `created_at` | TIMESTAMP | Default `now()` |

#### `portfolio_items`

The specific tickers associated with a portfolio.
| Column | Type | Constraints / Notes |
| :--- | :--- | :--- |
| `id` | UUID | Primary Key |
| `portfolio_id` | UUID | Foreign Key -> `portfolios.id`, On Delete Cascade |
| `ticker` | VARCHAR(20) | Not Null (e.g., 'GOOGL', 'RELIANCE.NS') |
| `added_at` | TIMESTAMP | Default `now()` |

#### `analysis_history`

Caches the Gemini analysis so users can review past AI recommendations without triggering new API calls.
| Column | Type | Constraints / Notes |
| :--- | :--- | :--- |
| `id` | UUID | Primary Key |
| `user_id` | UUID | Foreign Key -> `users.id` |
| `ticker` | VARCHAR(20) | Not Null |
| `rating` | VARCHAR(20) | 'BUY', 'HOLD', 'SELL' |
| `confidence` | INTEGER | 0 to 100 |
| `thesis` | TEXT | The detailed markdown thesis generated by Gemini |
| `created_at` | TIMESTAMP | Default `now()` |

#### `chat_sessions` & `chat_messages`

Stores the conversational memory for the WebSocket sidebar.
| Table | Column | Type | Constraints / Notes |
| :--- | :--- | :--- | :--- |
| **`chat_sessions`** | `id` | UUID | Primary Key |
| | `user_id` | UUID | Foreign Key -> `users.id` |
| | `context_ticker`| VARCHAR(20) | Nullable (If chat is tied to a specific stock) |
| **`chat_messages`** | `id` | UUID | Primary Key |
| | `session_id` | UUID | Foreign Key -> `chat_sessions.id` |
| | `sender_type` | VARCHAR(10) | 'USER' or 'AI' |
| | `content` | TEXT | The message body |
| | `created_at` | TIMESTAMP | Default `now()` |

---

### 2. API Contracts (FastAPI & React)

These represent the RESTful endpoints and WebSocket channels. All REST endpoints (except registration/login) will require the `HttpOnly` JWT cookie for authorization.

#### Feature 2: Authentication

* **`POST /api/auth/register`**
* **Request:** `{ "email": "user@example.com", "password": "securepassword123" }`
* **Response (201):** `{ "message": "User created successfully" }` (Sets `HttpOnly` cookie).


* **`POST /api/auth/login`**
* **Request:** `{ "email": "user@example.com", "password": "securepassword123" }`
* **Response (200):** `{ "user": { "id": "...", "email": "..." } }` (Sets `HttpOnly` cookie).


* **`POST /api/auth/logout`**
* **Response (200):** `{ "message": "Logged out" }` (Clears `HttpOnly` cookie).



#### Feature 3: Portfolios & Watchlists

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



#### Feature 4: Agentic AI Core (In-Depth Analysis)

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





#### Feature 5: High-Potential Market Scanning

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





#### Feature 6: Real-Time Sidebar Chat (WebSockets)

* **`WS /ws/chat/{session_id}`**
* **Connection Protocol:** The React frontend connects. If `session_id` is new, a new session is created.
* **Client Sends (JSON):** `{ "type": "user_message", "content": "How does the latest dividend yield affect this rating?" }`
* **Server Streams Back (JSON):** `{ "type": "ai_chunk", "content": "The " }`
`{ "type": "ai_chunk", "content": "dividend " }`
`{ "type": "ai_chunk", "content": "yield..." }`
* **Server Finalizes (JSON):**
`{ "type": "ai_complete", "full_message": "The dividend yield..." }`



---

Would you like me to write the actual SQLAlchemy Python models for these database schemas so you can drop them right into your backend repository?


