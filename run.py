#!/usr/bin/env python3
"""
WireQuote AI Backend - Application Entry Point
Run this file to start the server
"""
import uvicorn
from app.config import settings

if __name__ == "__main__":
    print("=" * 60)
    print(f"🔌 {settings.app_name} v{settings.app_version}")
    print("=" * 60)
    print(f"📍 Server: http://{settings.host}:{settings.port}")
    print(f"📚 API Docs: http://{settings.host}:{settings.port}/docs")
    print(f"🔧 Debug mode: {settings.debug}")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )