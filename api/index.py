"""Vercel serverless entrypoint (@vercel/python).

Exposes the FastAPI `app` from backend/. Vercel serves this file as a
serverless function; all /api/* traffic is rewritten here (see vercel.json).
Requires Postgres (e.g. Neon) + S3-compatible storage in production —
SQLite and local uploads do not survive serverless execution.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app  # noqa: F401  (Vercel looks for `app`)