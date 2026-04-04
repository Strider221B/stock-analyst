# /backend/main.py
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from constants import APITags, AppConfig, CORSConfig, Environment
from routers.auth import router as auth_router
from routers.portfolio_routes import router as portfolio_router
from routers.marketdata_routes import router as marketdata_router

# Import the factory function we built for the agent
from workflows.stock_analysis_graph import create_stock_agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI application.
    Code before the yield runs on server startup.
    Code after the yield runs on server shutdown.
    """
    # Compile the LangGraph agent exactly once and attach it to the app state
    app.state.stock_agent = create_stock_agent()

    yield

    # Teardown logic goes here (e.g., closing manual connection pools if needed)

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
