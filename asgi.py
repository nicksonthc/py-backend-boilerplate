"""
ASGI configuration for FastAPI with Socket.IO application.

This file is used for production deployment with ASGI servers like:
- Gunicorn with uvicorn workers
- Hypercorn
- Cloud platforms (Heroku, Azure, AWS, etc.)

Usage examples:
- Gunicorn: gunicorn asgi:application -w 1 -k uvicorn.workers.UvicornWorker
- Hypercorn: hypercorn asgi:application
- Direct uvicorn: uvicorn asgi:application --host 0.0.0.0 --port 8000
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the Socket.IO ASGI application
from app.main import app as application

# Alternative: if you want to access the FastAPI app directly (without Socket.IO)
# from app.main import app as fastapi_app

# Set environment variables if not already set
os.environ.setdefault("ENVIRONMENT", "production")

# The ASGI application that will be used by the server
# This points to the Socket.IO wrapped FastAPI application
__all__ = ["application"]
