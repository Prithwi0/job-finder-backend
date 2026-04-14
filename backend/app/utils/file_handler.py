"""
File Handler Utility
--------------------
Handles uploaded file validation and temporary file operations.
Supports PDF and DOCX file types only.
"""

import os
import tempfile
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {"pdf", "docx"}


def get_file_extension(filename: str) -> str:
    """Returns lowercase file extension without the dot."""
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def is_valid_file(filename: str) -> bool:
    """
    Checks if uploaded file is a supported type (PDF or DOCX).
    Returns True if valid, False otherwise.
    """
    ext = get_file_extension(filename)
    return ext in ALLOWED_EXTENSIONS


@contextmanager
def temp_file(content: bytes, suffix: str):
    """
    Context manager that writes bytes to a temporary file,
    yields its path, then deletes it automatically — even on error.

    Usage:
        with temp_file(content, "pdf") as path:
            # use path here
    """
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        yield tmp_path
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception as e:
                logger.warning(f"Could not delete temp file {tmp_path}: {e}")


def save_temp_file(content: bytes, suffix: str) -> str:
    """
    Saves bytes content to a temporary file.
    Returns the path to the temp file.
    ⚠️  Caller is responsible for deleting — prefer using temp_file() context manager.
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}")
    try:
        tmp.write(content)
        tmp.flush()
        return tmp.name
    finally:
        tmp.close()


def delete_temp_file(path: str):
    """Safely deletes a temporary file. Logs a warning on failure."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logger.warning(f"Could not delete temp file {path}: {e}")
