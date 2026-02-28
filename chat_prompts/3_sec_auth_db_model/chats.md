Given these requirements and schema / api information, can you create a detailed list of user stories and their corresponding tasks that you will need to perform to achieve the requirements. Make the tasks granular, one task is one operation.

Requirements:

Feature 2: Secure Authentication & Database Modeling

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

Schema / API Definitions:

API Contracts (FastAPI & React)

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

Here is the granular, operation-by-operation breakdown of user stories and tasks for Feature 2 (Secure Authentication & Database Modeling).

These are structured to be directly imported into your project management tool, keeping the backend security and frontend state management tightly aligned.

### User Story 1: Backend Security Utilities

**"As a backend developer, I need utilities for hashing passwords and generating secure JWTs so that user credentials remain safe and sessions can be verified without database lookups."**

* **Task 1.1:** Install required security packages in the `/backend` directory (`pip install passlib[bcrypt] pyjwt`).
* **Task 1.2:** Create a `security.py` utility file in the backend.
* **Task 1.3:** Implement a `get_password_hash(password: str) -> str` function using bcrypt.
* **Task 1.4:** Implement a `verify_password(plain_password: str, hashed_password: str) -> bool` function.
* **Task 1.5:** Implement a `create_access_token(data: dict) -> str` function using PyJWT, pulling a secret key and expiration time from environment variables.
* **Task 1.6:** Implement a `verify_access_token(token: str) -> dict` function that decodes the JWT and raises a credentials exception if invalid or expired.

### User Story 2: FastAPI Authentication Endpoints

**"As a backend developer, I want RESTful endpoints for registration, login, and logout that utilize HttpOnly cookies so that the frontend can authenticate securely against XSS attacks."**

* **Task 2.1:** Create a `schemas.py` file to define Pydantic models for `UserCreate` (email, password), `UserLogin` (email, password), and `UserResponse` (id, email).
* **Task 2.2:** Create an `auth.py` router file and include it in the main FastAPI application instance.
* **Task 2.3:** Implement the `POST /api/auth/register` route to validate input, hash the password, save the new user to the PostgreSQL database, and return a 201 status.
* **Task 2.4:** Implement the `POST /api/auth/login` route to verify the user's email and password against the database.
* **Task 2.5:** Update the `login` route to generate a JWT and attach it to the response object using `response.set_cookie(key="access_token", value=token, httponly=True, secure=True, samesite="lax")`.
* **Task 2.6:** Implement the `POST /api/auth/logout` route that returns a response object with `response.delete_cookie(key="access_token")`.
* **Task 2.7:** Create a database seed script to test the portfolio models by creating mock portfolios with different `account_type` values (e.g., testing both 'DOMESTIC' and 'INTERNATIONAL' data constraints).

### User Story 3: FastAPI Route Protection Dependency

**"As a backend developer, I need a reusable dependency to protect specific API routes so that only authenticated users with valid cookies can access their portfolio and chat data."**

* **Task 3.1:** Create a `dependencies.py` file in the backend.
* **Task 3.2:** Implement a `get_current_user` FastAPI dependency that extracts the `access_token` directly from the incoming request cookies.
* **Task 3.3:** Configure the dependency to pass the token to `verify_access_token`, fetch the corresponding user from the database, and return the User object.
* **Task 3.4:** Add error handling inside the dependency to throw a `401 Unauthorized` HTTP exception if the cookie is missing, invalid, or the user no longer exists.

### User Story 4: Frontend State Management & API Configuration

**"As a frontend developer, I need a global state store and a configured HTTP client so that the React app knows if a user is logged in and automatically sends credentials with every request."**

* **Task 4.1:** Install state management and routing libraries in the `/frontend` directory (`npm install zustand react-router-dom axios`).
* **Task 4.2:** Create an `api.ts` utility file and configure an Axios instance with `withCredentials: true` so that the browser automatically includes the HttpOnly cookie on all requests to the backend.
* **Task 4.3:** Create an `authStore.ts` file using Zustand (or Context) with the state interface: `{ isAuthenticated: boolean, user: User | null }`.
* **Task 4.4:** Implement a `login` action in the store that calls the Axios `POST /api/auth/login` endpoint and updates the state upon success.
* **Task 4.5:** Implement a `logout` action in the store that calls the Axios `POST /api/auth/logout` endpoint and clears the state.
* **Task 4.6:** Implement a `checkAuth` action that silently pings a protected backend route on initial app load to verify if a valid session cookie already exists.

### User Story 5: Frontend Authentication UI & Routing

**"As a user, I want secure login and registration pages, and I expect to be redirected if I try to access the dashboard without being logged in."**

* **Task 5.1:** Create a `LoginForm.tsx` component using shadcn/ui form elements, handling local input state and displaying error messages for invalid credentials.
* **Task 5.2:** Create a `RegisterForm.tsx` component with password confirmation validation.
* **Task 5.3:** Create an `AuthLayout.tsx` component to wrap the login and registration pages with a clean, centered UI design.
* **Task 5.4:** Create a `ProtectedRoute.tsx` wrapper component that checks the `isAuthenticated` state from the store; if false, it redirects the user to the `/login` route using React Router's `Maps`.
* **Task 5.5:** Configure `App.tsx` (or your main router file) to define the `/login` and `/register` public routes, and wrap the `/dashboard` route inside the `ProtectedRoute` component.

---

Would you like to move directly into defining the tasks for Feature 3 (Portfolio & Watchlist Dashboard), or would you prefer me to write out the Python code for the `get_current_user` FastAPI dependency since that handles the critical cookie extraction?
