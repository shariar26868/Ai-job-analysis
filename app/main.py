from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.api.routes import router
from app.services.database_service import database_service

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered electrical quote estimation system using OpenAI",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.debug else "An error occurred"
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print(f"🚀 {settings.app_name} v{settings.app_version} starting...")
    print(f"📊 Debug mode: {settings.debug}")
    print(f"🔑 OpenAI API configured: {'Yes' if settings.openai_api_key else 'No'}")
    print(f"🌐 CORS origins: {', '.join(settings.cors_origins)}")
    print(f"💰 Pricing API: {settings.pricing_api_url}")
    
    # Connect to MongoDB
    try:
        await database_service.connect()
        print("✅ Database connection established")
    except Exception as e:
        print(f"⚠️ Database connection failed: {str(e)}")
        print("   Running in degraded mode - quote persistence unavailable")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print(f"🛑 {settings.app_name} shutting down...")
    await database_service.disconnect()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
