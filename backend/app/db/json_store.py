"""
JSON Store — File-based storage for resumes and jobs.
-----------------------------------------------------
No database used. Data is persisted in JSON files under the /data directory.
  - resumes.json : stores resume metadata (skills, experience, name, etc.)
  - jobs.json    : stores job descriptions and their embeddings (omitted)
"""

import json
import logging
import os
from typing import Any, Dict, List

from app.config.settings import settings

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# Low-level helpers
# ──────────────────────────────────────────────────────────────

def load_json(file_path: str) -> List[Dict[str, Any]]:
    """Load JSON array from file. Returns empty list if file is missing or corrupt."""
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Failed to load JSON from {file_path}: {e}")
        return []


def save_json(file_path: str, data: List[Dict[str, Any]]):
    """Save list of dicts as pretty-printed JSON to file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def append_to_json(file_path: str, item: Dict[str, Any]):
    """Load existing data, append new item, and save back."""
    data = load_json(file_path)
    data.append(item)
    save_json(file_path, data)


# ──────────────────────────────────────────────────────────────
# JsonStore — high-level interface
# ──────────────────────────────────────────────────────────────

class JsonStore:
    """
    Simple file-based storage using JSON.
    All methods are static — no instance needed.
    """

    # ── Resumes ──────────────────────────────────────────────

    @staticmethod
    def get_resumes() -> List[Dict[str, Any]]:
        """Return all stored resumes."""
        return load_json(settings.RESUMES_JSON)

    @staticmethod
    def add_resume(resume: Dict[str, Any]):
        """
        Append a resume entry to resumes.json.
        Expected fields: id, filename, name, skills, experience, clean_text
        """
        append_to_json(settings.RESUMES_JSON, resume)
        logger.info(f"Resume stored: {resume.get('filename', 'unknown')} (id={resume.get('id')})")

    @staticmethod
    def get_resume_by_id(resume_id: int) -> Dict[str, Any]:
        """Fetch a resume by its FAISS index ID. Returns empty dict if not found."""
        for r in load_json(settings.RESUMES_JSON):
            if r.get("id") == resume_id:
                return r
        return {}

    @staticmethod
    def resume_count() -> int:
        """Total number of resumes stored."""
        return len(load_json(settings.RESUMES_JSON))

    # ── Jobs ──────────────────────────────────────────────────

    @staticmethod
    def get_jobs() -> List[Dict[str, Any]]:
        """Return all stored job descriptions."""
        return load_json(settings.JOBS_JSON)

    @staticmethod
    def add_job(job: Dict[str, Any]):
        """Append a job entry to jobs.json."""
        append_to_json(settings.JOBS_JSON, job)
        logger.info(f"Job stored with ID: {job.get('id')}")

    @staticmethod
    def get_job_by_id(job_id: int) -> Dict[str, Any]:
        """Fetch a job by its integer ID. Returns empty dict if not found."""
        jobs = load_json(settings.JOBS_JSON)
        if 0 <= job_id < len(jobs):
            return jobs[job_id]
        return {}

    @staticmethod
    def job_count() -> int:
        """Total number of jobs stored."""
        return len(load_json(settings.JOBS_JSON))
