from fastapi import FastAPI
from contextlib import asynccontextmanager

from database import connect_to_mongo, close_mongo_connection
from middleware.cors import setup_cors
from config import get_settings

# Import routers
from routers import complaints, status, departments, map, analytics

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    print("🚀 Starting Smart Problem Resolver API...")
    await connect_to_mongo()
    print("✓ Application ready!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    await close_mongo_connection()
    print("✓ Shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for Smart Local Problem Resolver - A citizen complaint management platform",
    lifespan=lifespan
)

# Setup CORS
setup_cors(app)

# Include routers
app.include_router(complaints.router)
app.include_router(status.router)
app.include_router(departments.router)
app.include_router(map.router)
app.include_router(analytics.router)


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to Smart Problem Resolver API",
        "version": settings.app_version,
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
