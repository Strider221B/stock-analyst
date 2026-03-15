# /backend/main.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from constants import APITags, AppConfig, CORSConfig, Environment
from routers.auth import router as auth_router

class AppCreator:
    def __init__(self):
        self._app = FastAPI(
            title=AppConfig.TITLE,
            description=AppConfig.DESCRIPTION,
            version=AppConfig.VERSION,
            # Disable Swagger docs in production dynamically
            docs_url="/docs" if settings.environment == Environment.DEVELOPMENT else None,
        )
        self._configure_cors()
        self._configure_routes()

    def _configure_cors(self):
        origins = [
            f"http://localhost:{settings.frontend_port}",
            "http://127.0.0.1",
            "http://localhost"
        ]
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=CORSConfig.ALLOWED_METHODS,
            allow_headers=CORSConfig.ALLOWED_HEADERS,
        )

    def _configure_routes(self):
        self._app.include_router(auth_router)

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
