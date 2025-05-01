"""
STEMnity AI Backend Server

This is the main FastAPI application entry point that sets up:
- API endpoints for the STEM tutoring service
- CORS middleware for frontend communication
- Configuration validation
- Router integration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import config
from app.api import chat as chat_router

# Initialize FastAPI with metadata
app = FastAPI(
    title="STEMnity AI Backend",
    description="API endpoints for the STEMnity AI STEM tutoring service.",
    version="0.1.0",
)

# --- CORS Configuration ---
# Security Note: In production, replace with specific origin URLs
# Development allows all origins for easy local testing
origins = [
    "http://localhost",
    "http://localhost:5173",  # Default Vite dev server port
    "http://127.0.0.1:5173",
    # TODO: Add your production frontend URL here
]

# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Configure specific HTTP methods in production
    allow_headers=["*"],  # Configure specific headers in production
)

# --- API Routes ---
@app.get("/")
async def read_root():
    """Health check endpoint to verify API is running."""
    return {"message": "Welcome to the STEMnity AI Backend"}

# Mount the chat router with /api prefix
app.include_router(
    chat_router.router,
    prefix="/api",
    tags=["Chat"]  # Groups chat endpoints in Swagger UI
)

# --- Configuration Validation ---
# Print startup configuration for debugging
print("\n=== STEMnity AI Backend Configuration ===")
print(f"Model ID: {config.GITHUB_MODEL_ID}")
print(f"GitHub PAT Status: {'Configured' if config.GITHUB_PAT else 'Missing - Check backend/.env'}")
print(f"API Documentation: http://localhost:8000/docs")
print(f"Chat API Endpoint: http://localhost:8000/api/chat")
print("=======================================\n")

# Development server configuration
if __name__ == "__main__":
    import uvicorn
    # Note: For development only. Use proper ASGI server in production.
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload for development
    ) 