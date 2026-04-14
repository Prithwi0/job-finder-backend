"""
Configuration settings for the AI Resume Screener.
All paths, model names, and server config are defined here.
Edit this file to customize the behaviour of the application.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App Info ──────────────────────────────────────────────
    APP_NAME: str = "AI Resume Screener & Job Matching System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ── Storage Paths ─────────────────────────────────────────
    # BASE_DIR  →  backend/
    BASE_DIR: str = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    RESUMES_JSON: str = os.path.join(DATA_DIR, "resumes.json")
    JOBS_JSON: str = os.path.join(DATA_DIR, "jobs.json")
    FAISS_INDEX: str = os.path.join(DATA_DIR, "index.faiss")

    # ── Embedding Model ───────────────────────────────────────
    # Uses HuggingFace sentence-transformers (cached locally after first run)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384  # Fixed dimension for all-MiniLM-L6-v2

    # ── Matching ──────────────────────────────────────────────
    TOP_K_RESULTS: int = 5         # Maximum candidates returned per match query

    # ── Server ────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        case_sensitive = True


# Single global instance — import this everywhere else
settings = Settings()

# Ensure the data directory exists before anything tries to write to it
os.makedirs(settings.DATA_DIR, exist_ok=True)
