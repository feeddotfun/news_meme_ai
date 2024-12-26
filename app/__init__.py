from fastapi import FastAPI
from app.api.routes import router
from app.api.middleware import setup_middleware

def create_app() -> FastAPI:
    """Create and configure a FastAPI application."""
    app = FastAPI(
        title="Feed.fun API",
        description="API for Feed.fun - Where News Meets Memes in the World of Crypto",
        version="1.0.0",
        docs_url=None,  # Disable Swagger UI for production
        redoc_url=None  # Disable ReDoc for production
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Include routers
    app.include_router(router, prefix="/api/v1")
    
    return app