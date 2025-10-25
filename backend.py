"""
Refactored backend for the Personal Assistant application using modular structure.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api_routes import api_router
from config import config


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Personal Assistant API",
        version="1.0.0",
        description="A modular personal assistant with screen capture, OCR, and AI capabilities"
    )
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Include API routes
    app.include_router(api_router.get_router())
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
