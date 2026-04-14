"""
Matching Service
----------------
Core business logic for the AI resume-job matching system.

Steps:
  1. Embed the job description (or load an existing job)
  2. Search FAISS for the most similar resume embeddings
  3. Retrieve resume metadata from JSON store
  4. Calculate match score (0–100) clamped from cosine similarity
  5. Identify matched / missing skills
  6. Generate a human-readable explanation string
  7. Return ranked results list
"""

import logging
from typing import List, Dict, Any, Optional

from app.db.json_store import JsonStore
from app.db.vector_db import vector_db
from app.services.embedding_service import embedding_service
from app.services.parser_service import parser_service
from app.config.settings import settings

logger = logging.getLogger(__name__)


def _build_explanation(
    matched_skills: List[str],
    missing_skills: List[str],
    score: int,
    experience: str,
) -> str:
    """
    Generate a plain-English explanation string for a candidate match.
    No LLM is needed — purely rule-based logic.
    """
    parts = []

    if score >= 80:
        parts.append("Excellent overall match.")
    elif score >= 60:
        parts.append("Good match with relevant background.")
    elif score >= 40:
        parts.append("Moderate match — some alignment found.")
    else:
        parts.append("Weak match — limited alignment with job requirements.")

    if matched_skills:
        skills_str = ", ".join(matched_skills[:5])
        parts.append(f"Matching skills: {skills_str}.")
    else:
        parts.append("No direct skill keywords overlap found.")

    if missing_skills:
        missing_str = ", ".join(missing_skills[:3])
        parts.append(f"Skills to develop: {missing_str}.")

    if experience and experience != "Experience not explicitly mentioned":
        parts.append(f"Experience noted: {experience}.")

    return " ".join(parts)


class MatchingService:

    @staticmethod
    def run_match(
        job_description: Optional[str] = None,
        job_id: int = -1,
        top_k: int = None,
    ) -> List[Dict[str, Any]]:
        """
        Run a full matching pass and return ranked candidates.

        Priority:
          - If job_description is provided, use it directly.
          - Else if job_id >= 0, look up the stored job.
          - Otherwise return empty list.

        Returns a list of dicts, sorted by descending match score.
        """
        top_k = top_k or settings.TOP_K_RESULTS

        # ── 1. Resolve job text ────────────────────────────────
        if job_description and job_description.strip():
            text_to_match = job_description.strip()
        elif job_id >= 0:
            job = JsonStore.get_job_by_id(job_id)
            if not job:
                logger.warning(f"Job ID {job_id} not found.")
                return []
            text_to_match = job.get("description", "")
        else:
            logger.warning("run_match called with no job description or valid job_id.")
            return []

        if not text_to_match:
            return []

        # ── 2. Embed the job description ───────────────────────
        query_embedding = embedding_service.get_embedding(text_to_match)

        # ── 3. FAISS nearest-neighbour search ──────────────────
        distances, indices = vector_db.search(query_embedding, top_k)

        if len(indices) == 0:
            logger.info("FAISS returned no results (index may be empty).")
            return []

        # ── 4. Load resume metadata ────────────────────────────
        resumes = JsonStore.get_resumes()
        job_skills = parser_service.extract_skills(text_to_match)

        results = []
        for dist, idx in zip(distances, indices):
            if idx == -1 or idx >= len(resumes):
                continue

            resume = resumes[idx]

            # ── 5. Calculate score ─────────────────────────────
            # FAISS inner-product after L2-norm == cosine similarity ∈ [-1, 1].
            # We clamp & scale to [0, 100].
            raw_score = float(dist)
            score = int(max(0.0, min(1.0, raw_score)) * 100)

            # ── 6. Skill diff ──────────────────────────────────
            resume_skills = resume.get("skills", [])
            matched_skills = sorted(set(resume_skills) & set(job_skills))
            missing_skills = sorted(set(job_skills) - set(resume_skills))
            experience = resume.get("experience", "")

            # ── 7. Explanation ─────────────────────────────────
            explanation = _build_explanation(matched_skills, missing_skills, score, experience)

            results.append({
                "name": resume.get("name", resume.get("filename", "Unknown")),
                "filename": resume.get("filename", ""),
                "score": score,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "explanation": explanation,
                "experience": experience,
            })

        # Sort by descending score
        results.sort(key=lambda x: x["score"], reverse=True)
        logger.info(f"Match complete — {len(results)} candidates returned.")
        return results


matching_service = MatchingService()
