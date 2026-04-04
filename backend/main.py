# /backend/main.py
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from constants import APITags, AppConfig, CORSConfig, Environment
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from routers.auth import router as auth_router
from routers.portfolio_routes import router as portfolio_router
from routers.marketdata_routes import router as marketdata_router

# Import the factory function we built for the agent
from workflows.stock_analysis_graph import create_stock_agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application."""

    # --- PHASE 1: DDL SETUP (Admin Privileges) ---
    # Use the admin URL to create the LangGraph tables.
    # Note: Ensure 'admin_database_url' is defined in your config.py Settings class!
    admin_dsn = settings.get_admin_database_url().replace("+psycopg2", "").replace("+psycopg", "")

    # We only need this pool for a split second, so max_size=2 is plenty
    async with AsyncConnectionPool(conninfo=admin_dsn,
                                   min_size=1,
                                   max_size=2,
                                   kwargs={"autocommit": True, "prepare_threshold": 0}) as admin_pool:
        setup_checkpointer = AsyncPostgresSaver(admin_pool)
        # This creates the tables using the admin role
        await setup_checkpointer.setup()

    # admin_pool automatically closes here. Schema is now ready!

    # --- PHASE 2: RUNTIME (Restricted API Privileges) ---
    # Now we switch to the safe API user for everyday operation
    api_dsn = settings.get_database_url().replace("+psycopg2", "").replace("+psycopg", "")

    async with AsyncConnectionPool(conninfo=api_dsn,
                                   min_size=1,
                                   max_size=settings.pool_size,
                                   kwargs={"autocommit": True, "prepare_threshold": 0}) as pool:
        # Pass the restricted pool into the checkpointer
        runtime_checkpointer = AsyncPostgresSaver(pool)

        # Compile the agent and attach it to the app state
        app.state.stock_agent = create_stock_agent(checkpointer=runtime_checkpointer)

        # Yield control back to FastAPI. The API pool stays open while the server runs.
        yield

class AppCreator:
    def __init__(self):
        self._app = FastAPI(
            title=AppConfig.TITLE,
            description=AppConfig.DESCRIPTION,
            version=AppConfig.VERSION,
            # Disable Swagger docs in production dynamically
            docs_url="/docs" if settings.environment == Environment.DEVELOPMENT else None,
            # Attach the lifespan manager here!
            lifespan=lifespan,
        )
        self._configure_cors()
        self._configure_routes()

    def _configure_cors(self):
        origins = [
            f"http://localhost:{settings.frontend_port}",
            f"http://127.0.0.1:{settings.frontend_port}",
            "http://127.0.0.1",
            "http://localhost"
        ]

        # If production, you might want to add your actual domain from settings
        if settings.environment == Environment.PRODUCTION and hasattr(settings, 'domain'):
            origins.append(f"https://{settings.domain}")

        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=CORSConfig.ALLOWED_METHODS,
            allow_headers=CORSConfig.ALLOWED_HEADERS,
        )

    def _configure_routes(self):
        self._app.include_router(auth_router)
        self._app.include_router(portfolio_router)
        self._app.include_router(marketdata_router)

        @self._app.get(f"{AppConfig.API_PREFIX}/health", tags=[APITags.SYSTEM])
        async def health_check():
            return {
                "status": "healthy",
                "environment": settings.environment
            }

    def get_app(self) -> FastAPI:
        return self._app

app_creator = AppCreator()
app = app_creator.get_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=(settings.environment == Environment.DEVELOPMENT),
        workers=(4 if settings.environment == Environment.PRODUCTION else None)
    )
