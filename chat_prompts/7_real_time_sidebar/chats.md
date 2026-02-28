Given these requirements and schema / api information, can you create a detailed list of user stories and their corresponding tasks that you will need to perform to achieve the requirements. Make the tasks granular, one task is one operation.

Requirements:

Feature 6: Real-Time Sidebar Chat

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

Schema / API Definitions:

Feature 6: Real-Time Sidebar Chat (WebSockets)

* **`WS /ws/chat/{session_id}`**
* **Connection Protocol:** The React frontend connects. If `session_id` is new, a new session is created.
* **Client Sends (JSON):** `{ "type": "user_message", "content": "How does the latest dividend yield affect this rating?" }`
* **Server Streams Back (JSON):** `{ "type": "ai_chunk", "content": "The " }`
`{ "type": "ai_chunk", "content": "dividend " }`
`{ "type": "ai_chunk", "content": "yield..." }`
* **Server Finalizes (JSON):**
`{ "type": "ai_complete", "full_message": "The dividend yield..." }`



---

Here is the granular, operation-by-operation breakdown of user stories and tasks for Feature 6 (Real-Time Sidebar Chat).

This phase connects the dynamic AI generation with a persistent frontend UI. Using WebSockets ensures the connection remains open, allowing the Gemini LLM to stream its reasoning token-by-token directly to the user's screen.

### User Story 1: WebSocket Connection Management (Backend)

**"As a backend developer, I need a robust WebSocket manager so that I can handle multiple concurrent user chat sessions without dropping connections or leaking memory."**

* **Task 1.1:** Create a `managers/websocket_manager.py` file in the backend.
* **Task 1.2:** Implement a `ConnectionManager` class containing an `active_connections: dict[str, WebSocket]` dictionary to track connected clients by their `session_id`.
* **Task 1.3:** Implement an async `connect(self, websocket: WebSocket, session_id: str)` method that calls `await websocket.accept()` and stores the socket in the dictionary.
* **Task 1.4:** Implement a `disconnect(self, session_id: str)` method that removes the socket from the dictionary.
* **Task 1.5:** Implement an async `send_personal_message(self, message: dict, session_id: str)` method that converts the dictionary to JSON and sends it via `websocket.send_json()`.

### User Story 2: FastAPI WebSocket Endpoint & Authentication

**"As a backend developer, I need a secure WebSocket endpoint so that the frontend can establish a bi-directional chat session tied to their authenticated account."**

* **Task 2.1:** Create a `routes/chat_routes.py` file and include it in the main FastAPI application.
* **Task 2.2:** Define the `@router.websocket("/ws/chat/{session_id}")` endpoint.
* **Task 2.3:** Implement authentication within the WebSocket route. Since browsers do not consistently send HttpOnly cookies during initial WebSocket handshakes, extract the JWT from a query parameter or an initial authentication frame, and verify it using the existing security utilities.
* **Task 2.4:** Call `manager.connect(websocket, session_id)` upon successful authentication.
* **Task 2.5:** Wrap the connection in a `try...except WebSocketDisconnect` block to gracefully handle client disconnections and call `manager.disconnect(session_id)`.

### User Story 3: LangGraph Chat Agent & Context Injection

**"As an AI agent, I need access to the user's conversation history and the details of the stock they are currently viewing so that I can provide highly relevant, contextual answers."**

* **Task 3.1:** Create a `workflows/chat_graph.py` file.
* **Task 3.2:** Define a LangGraph state containing the conversation history (a list of LangChain Message objects) and the current `context_ticker`.
* **Task 3.3:** Create a utility function to fetch the user's previous messages from the `chat_messages` PostgreSQL table using the `session_id` and format them into LangChain's `HumanMessage` and `AIMessage` objects.
* **Task 3.4:** Create a utility function to fetch the most recent analysis for the `context_ticker` from the `analysis_history` table to use as background context.
* **Task 3.5:** Configure the Gemini LLM node with streaming enabled (`streaming=True`).
* **Task 3.6:** Draft a system prompt that explicitly instructs the AI to ground its answers in the provided stock analysis context while maintaining a conversational tone.

### User Story 4: LLM Streaming Execution Loop

**"As a user, I want to see the AI's response streaming token-by-token so that I do not have to wait for the entire response to generate before reading."**

* **Task 4.1:** Inside the WebSocket route's `while True:` loop, wait for incoming messages using `await websocket.receive_json()`.
* **Task 4.2:** Parse the incoming payload ensuring it matches the `{ "type": "user_message", "content": "..." }` schema.
* **Task 4.3:** Save the user's raw message to the `chat_messages` PostgreSQL table.
* **Task 4.4:** Invoke the LangGraph chat workflow asynchronously using LangChain's `.astream_events()` or `.astream()` methods.
* **Task 4.5:** Iterate over the stream yields, packaging each chunk of text into the `{ "type": "ai_chunk", "content": "..." }` JSON format, and send it via the `ConnectionManager`.
* **Task 4.6:** Once the stream completes, package the final concatenated string into the `{ "type": "ai_complete", "full_message": "..." }` payload and send it.
* **Task 4.7:** Save the complete AI response to the `chat_messages` PostgreSQL table.

### User Story 5: Frontend State & WebSocket Client

**"As a frontend developer, I need a global chat state and WebSocket client so that the sidebar can persist without losing connection when the user navigates between dashboard views."**

* **Task 5.1:** Create a `chatStore.ts` using Zustand to hold state: `messages: array`, `isConnected: boolean`, `sessionId: string`, and `socket: WebSocket | null`.
* **Task 5.2:** Implement a `connectWebSocket` action that initializes the browser's native `WebSocket` API, attaching the JWT token (if using query param auth) to the connection string.
* **Task 5.3:** Set up the `socket.onmessage` event listener to parse incoming JSON.
* **Task 5.4:** Handle the `ai_chunk` event by locating the last message in the `messages` array (which represents the currently generating AI response) and appending the new text chunk to it.
* **Task 5.5:** Handle the `ai_complete` event by finalizing that message's state.
* **Task 5.6:** Implement a `sendMessage` action that stringifies a payload as `{ "type": "user_message", "content": "..." }`, calls `socket.send()`, and optimistically adds the user's message to the local store.

### User Story 6: Sidebar UI Component

**"As a user, I want a collapsible chat sidebar that stays open while I navigate, allowing me to easily ask questions about the stocks I am viewing."**

* **Task 6.1:** Create a `<SidebarChat />` component using shadcn/ui elements (such as a collapsible `Sheet` or a fixed side panel).
* **Task 6.2:** Map over the `messages` array from the Zustand store to render chat bubbles, applying distinct visual styles for User messages versus AI messages.
* **Task 6.3:** Implement a `useRef` auto-scroll mechanism that triggers whenever the `messages` array updates, ensuring the newest streaming chunks are always visible at the bottom of the container.
* **Task 6.4:** Add a text input field and a submit button at the bottom of the sidebar that triggers the `sendMessage` action.
* **Task 6.5:** Mount the `<SidebarChat />` component globally within your root `DashboardLayout.tsx` so it persists independently of the main page routing.

---

Would you like to move on to the final requirement, Feature 7 (Infrastructure as Code & CI/CD), to break down the Terraform steps and GitHub Actions pipeline needed to deploy this to Azure?

