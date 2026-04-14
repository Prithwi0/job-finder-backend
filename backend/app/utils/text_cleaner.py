"""
Text Cleaner Utility
--------------------
Cleans raw text extracted from PDF/DOCX files.
Removes non-ASCII chars, special characters, collapses whitespace.
"""

import re


def clean_text(text: str) -> str:
    """
    Cleans raw resume/job text.
    Steps:
      1. Remove non-ASCII characters
      2. Keep only alphanumeric + common punctuation
      3. Collapse multiple spaces/newlines into a single space
      4. Strip leading/trailing whitespace
    """
    if not text:
        return ""

    # Remove non-ASCII characters
    text = text.encode("ascii", errors="ignore").decode("ascii")

    # Keep alphanumeric + useful punctuation
    text = re.sub(r"[^\w\s.,@\-/+#]", " ", text)

    # Collapse multiple whitespace/newlines into a single space
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_for_matching(text: str) -> str:
    """
    Lowercase + strip punctuation. Used only for skill comparison — not for storage.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s+#.]", "", text)
    return text.strip()
