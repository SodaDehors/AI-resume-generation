"""WSGI entry point for production deployment (Gunicorn).

Usage:
    gunicorn wsgi:app -w 2 -b 127.0.0.1:8000
"""

import os
from dotenv import load_dotenv

# Load .env before app creation
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from app import create_app
from config import ProductionConfig

app = create_app(ProductionConfig)
