"""
Resume Routes
-------------
POST /resume/upload — Accept a PDF or DOCX file, parse it, embed it,
                      and store metadata in JSON + FAISS.
"""

import logging
import traceback

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.db.json_store import JsonStore
from app.db.vector_db import vector_db
from app.services.embedding_service import embedding_service
from app.services.parser_service import parser_service
from app.utils.file_handler import is_valid_file

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and process a resume (PDF or DOCX).

    Processing pipeline:
      1. Validate file type
      2. Extract raw text  (PyMuPDF for PDF, python-docx for DOCX)
      3. Clean text
      4. Extract skills, experience, candidate name
      5. Generate embedding  (all-MiniLM-L6-v2)
      6. Store embedding → FAISS
      7. Store metadata  → resumes.json

    Returns:
        200  { "success": true,  "message": "..." }
        400  { "success": false, "message": "..." }   – bad file
        500  { "success": false, "message": "..." }   – unexpected error
    """
    # ── 1. Validate input ──────────────────────────────────────
    filename = file.filename or ""
    if not filename:
        return {"success": False, "message": "No file provided."}

    if not is_valid_file(filename):
        return {
            "success": False,
            "message": f"Unsupported file format. Please upload a PDF or DOCX file.",
        }

    try:
        content = await file.read()

        if not content:
            return {"success": False, "message": "Uploaded file is empty."}

        # ── 2. Extract text ────────────────────────────────────
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext == "pdf":
            raw_text = parser_service.extract_text_from_pdf(content)
        else:  # docx
            raw_text = parser_service.extract_text_from_docx(content)

        if not raw_text or not raw_text.strip():
            return {
                "success": False,
                "message": "Could not extract text from the file. The file may be scanned or image-based.",
            }

        # ── 3. Clean text ──────────────────────────────────────
        clean = parser_service.clean_text(raw_text)

        # ── 4. Extract metadata ────────────────────────────────
        skills = parser_service.extract_skills(clean)
        experience = parser_service.extract_experience(clean)
        candidate_name = parser_service.extract_candidate_name(raw_text)

        logger.info(
            f"Parsed '{filename}' → name='{candidate_name}', "
            f"skills={skills}, experience='{experience}'"
        )

        # ── 5. Generate embedding ──────────────────────────────
        embedding = embedding_service.get_embedding(clean)

        # ── 6. Store in FAISS ──────────────────────────────────
        faiss_id = vector_db.add(embedding)

        # ── 7. Store metadata in JSON ──────────────────────────
        resume_data = {
            "id": faiss_id,
            "filename": filename,
            "name": candidate_name,
            "skills": skills,
            "experience": experience,
            # Store the first 2000 chars — enough context, avoids huge JSON files
            "clean_text": clean[:2000],
        }
        JsonStore.add_resume(resume_data)

        return {
            "success": True,
            "message": f"Resume '{filename}' processed successfully.",
            "candidate_name": candidate_name,
            "skills_found": skills,
            "experience": experience,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing resume '{filename}': {e}")
        traceback.print_exc()
        return {"success": False, "message": "An unexpected error occurred while processing the resume."}
