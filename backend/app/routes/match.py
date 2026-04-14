"""
Match Routes
------------
POST /match/run     — Run a matching pass for a job description or stored job.
GET  /match/results — Return the results from the most recent match run.
"""

import logging
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Body
from pydantic import BaseModel

from app.services.matching_service import matching_service
from app.config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# ── In-memory cache for the last match results ─────────────────
# Simple approach suitable for single-user / development use.
# For multi-user production, replace with a session-keyed cache or DB.
_last_results: List[Dict[str, Any]] = []


class MatchRequest(BaseModel):
    description: Optional[str] = None   # Provide a raw JD text directly
    job_id: Optional[int] = -1          # OR reference a stored job by ID
    top_k: Optional[int] = None         # How many candidates to return


@router.post("/run")
async def run_match(request: MatchRequest = Body(...)):
    """
    Run an AI matching pass.

    Provide either:
      - `description`: raw job description text, OR
      - `job_id`: integer ID of a previously stored job (/job/add)

    Returns ranked list of matching candidates with scores, skills, and explanations.
    """
    global _last_results

    if not request.description and (request.job_id is None or request.job_id < 0):
        return {
            "success": False,
            "message": "Provide either a 'description' string or a valid 'job_id'.",
        }

    try:
        results = matching_service.run_match(
            job_description=request.description,
            job_id=request.job_id if request.job_id is not None else -1,
            top_k=request.top_k or settings.TOP_K_RESULTS,
        )

        _last_results = results

        if not results:
            return {
                "success": True,
                "message": "No matching resumes found. Upload some resumes first.",
                "results": [],
            }

        return {
            "success": True,
            "total_matched": len(results),
            "results": results,
        }

    except Exception as e:
        logger.error(f"Error during match run: {e}")
        return {"success": False, "message": "An unexpected error occurred during matching."}


@router.get("/results")
async def get_results():
    """
    Retrieve the results from the most recent /match/run call.

    Returns:
        List of ranked candidate objects, or empty list if none available.

    Response format (per candidate):
    {
        "name":           "Jane Doe",
        "filename":       "jane_doe_cv.pdf",
        "score":          87,
        "matched_skills": ["Python", "Machine Learning"],
        "missing_skills": ["AWS"],
        "explanation":    "Excellent overall match. Matching skills: Python, ML...",
        "experience":     "3 years of experience"
    }
    """
    if not _last_results:
        return {
            "success": True,
            "message": "No match has been run yet. Call POST /match/run first.",
            "results": [],
        }
    return {
        "success": True,
        "total_matched": len(_last_results),
        "results": _last_results,
    }
