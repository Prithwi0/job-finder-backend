"""
Job Routes
----------
POST /job/add  — Add a job description; store in jobs.json with embedding.
GET  /job/list — List all stored jobs.
"""

import logging

from fastapi import APIRouter, Body
from pydantic import BaseModel, field_validator

from app.db.json_store import JsonStore
from app.services.embedding_service import embedding_service
from app.services.parser_service import parser_service

logger = logging.getLogger(__name__)

router = APIRouter()


class JobDescription(BaseModel):
    title: str = "Untitled Position"
    description: str

    @field_validator("description")
    @classmethod
    def description_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Job description cannot be empty.")
        return v.strip()


@router.post("/add")
async def add_job(job: JobDescription = Body(...)):
    """
    Add a new job description.

    Stores:
      - Job text + title in jobs.json
      - Pre-extracts skills for later comparison (cached at store time)

    Returns:
        200  { "success": true,  "job_id": <int>, "skills_found": [...] }
        500  { "success": false, "message": "..." }
    """
    try:
        # Extract skills from the job description (for preview, not matching)
        job_skills = parser_service.extract_skills(job.description)

        job_data = {
            "id": JsonStore.job_count(),   # Use count as sequential ID
            "title": job.title,
            "description": job.description,
            "skills": job_skills,          # Pre-cached job skills
        }
        JsonStore.add_job(job_data)

        logger.info(f"Job '{job.title}' added with ID={job_data['id']}, skills={job_skills}")

        return {
            "success": True,
            "message": f"Job description '{job.title}' added successfully.",
            "job_id": job_data["id"],
            "skills_found": job_skills,
        }

    except ValueError as e:
        return {"success": False, "message": str(e)}
    except Exception as e:
        logger.error(f"Error adding job: {e}")
        return {"success": False, "message": "An unexpected error occurred while saving the job."}


@router.get("/list")
async def list_jobs():
    """
    Return all stored job descriptions.

    Returns:
        List of job objects  [{ id, title, description, skills }, ...]
        Empty list if no jobs have been added.
    """
    try:
        jobs = JsonStore.get_jobs()
        return {
            "success": True,
            "total": len(jobs),
            "jobs": [
                {"id": j.get("id"), "title": j.get("title"), "skills": j.get("skills", [])}
                for j in jobs
            ],
        }
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        return {"success": False, "message": "Could not retrieve jobs."}
