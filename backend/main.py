from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import config
from app.api import chat as chat_router

app = FastAPI(
    title="STEMnity AI Backend",
    description="API endpoints for the STEMnity agent.",
    version="0.1.0",
   
)

# --- CORS Middleware --- 
# Adjust origins as needed for your frontend setup
# Allows all origins for development, restrict in production!
origins = [
    "http://localhost",
    "http://localhost:5173", # Default Vite dev port
    "http://127.0.0.1:5173",
    # Add your deployed frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)


# --- Placeholder Root Endpoint --- 
@app.get("/")
async def read_root():
    return {"message": "Welcome to the STEMnity AI Backend"}

# --- Include Routers --- 
# Placeholder: Include your API routers here
# Include the chat router with a prefix
app.include_router(chat_router.router, prefix="/api", tags=["Chat"]) # Add tags for Swagger UI

print(f"--- Backend Config ---")
print(f"Model ID: {config.GITHUB_MODEL_ID}")
print(f"GitHub PAT Loaded: {'Yes' if config.GITHUB_PAT else 'NO! - Check backend/.env'}")
print(f"----------------------")
print("Chat API endpoint available at /api/chat")

# If running directly using `python main.py` (for simple testing)
# Use `uvicorn main:app --reload --host 0.0.0.0 --port 8000` for development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 