"""
AI Resume Screener — FastAPI Application Entry Point
----------------------------------------------------
Run with:
    cd backend
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Or directly:
    python -m app.main
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.routes import resume, job, match

# ── Logging Setup ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── FastAPI App ────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Production-ready backend for AI-powered resume screening and job matching. "
        "Upload resumes (PDF/DOCX), add job descriptions, and get ranked candidate lists."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.DEBUG,
)

# ── CORS Middleware ────────────────────────────────────────────
# Allow all origins for development. Restrict in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ─────────────────────────────────────────────────────
app.include_router(resume.router, prefix="/resume", tags=["Resume"])
app.include_router(job.router,    prefix="/job",    tags=["Job"])
app.include_router(match.router,  prefix="/match",  tags=["Matching"])


# ── Health Check ───────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def health_check():
    """Root health-check endpoint — confirms the server is running."""
    from app.db.vector_db import vector_db
    from app.db.json_store import JsonStore

    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "stats": {
            "resumes_stored": JsonStore.resume_count(),
            "jobs_stored": JsonStore.job_count(),
            "faiss_vectors": vector_db.total_vectors,
        },
    }


# ── Dev Server Entry ───────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )
