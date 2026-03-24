"""
FastAPI application entry point.
Initializes the app, configures middleware, creates database tables, and mounts routers.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
from app.api.endpoints import router as api_router

# Create SQLite database tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Prompt Corrector API",
    description="A commercial-grade intent and spelling corrector microservice for AI Agents.",
    version="1.0.0",
)

# Configure CORS to allow cross-origin requests from any Agent UI (e.g., React frontends)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the API routes under the /api/v1 prefix
app.include_router(api_router, prefix="/api/v1", tags=["corrector"])

if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
