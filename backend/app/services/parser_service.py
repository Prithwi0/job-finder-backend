"""
Parser Service
--------------
Handles text extraction from PDF and DOCX files,
plus skills extraction and experience detection using regex/keyword matching.

Libraries used:
  - PyMuPDF (fitz)  → PDF text extraction
  - python-docx     → DOCX text extraction
"""

import re
import io
import logging

import fitz  # PyMuPDF
from docx import Document

from app.utils.text_cleaner import clean_text, normalize_for_matching
from app.utils.file_handler import temp_file

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# Skills keyword bank  (extend freely)
# ──────────────────────────────────────────────────────────────
SKILLS_BANK = [
    # Programming Languages
    "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#",
    "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R",
    "MATLAB", "Perl", "Bash", "Shell",

    # Web / Frontend
    "React", "Angular", "Vue", "Next.js", "HTML", "CSS",
    "Bootstrap", "Tailwind", "Redux", "GraphQL", "REST",

    # Backend / Frameworks
    "FastAPI", "Django", "Flask", "Node.js", "Express", "Spring Boot",
    "Laravel", "ASP.NET", "Spring",

    # Databases
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite",
    "Cassandra", "DynamoDB", "Firebase", "Elasticsearch",

    # Cloud / DevOps
    "AWS", "GCP", "Azure", "Docker", "Kubernetes", "CI/CD",
    "Jenkins", "Terraform", "Ansible", "Linux", "Git", "GitHub",
    "GitLab", "Nginx",

    # AI / ML / Data
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas",
    "NumPy", "Matplotlib", "Seaborn", "OpenCV", "BERT", "LLM",
    "LangChain", "FAISS", "Data Science", "Statistics",

    # Other
    "Agile", "Scrum", "Jira", "Figma", "Tableau", "Power BI",
    "Excel", "Communication", "Leadership", "Problem Solving",
]

# Pre-compute lowercase versions for fast case-insensitive matching
_SKILLS_LOWER = {s.lower(): s for s in SKILLS_BANK}


class ParserService:
    # ── Text Extraction ────────────────────────────────────────

    @staticmethod
    def extract_text_from_pdf(pdf_content: bytes) -> str:
        """Extract plain text from a PDF byte string using PyMuPDF."""
        try:
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            pages_text = [page.get_text() for page in doc]
            return "\n".join(pages_text)
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return ""

    @staticmethod
    def extract_text_from_docx(docx_content: bytes) -> str:
        """
        Extract plain text from a DOCX byte string using python-docx.
        Uses an in-memory BytesIO buffer — no temp file needed.
        """
        try:
            doc = Document(io.BytesIO(docx_content))
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return "\n".join(paragraphs)
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            return ""

    @staticmethod
    def clean_text(text: str) -> str:
        """Thin wrapper — delegates to text_cleaner utility."""
        return clean_text(text)

    # ── Skills Extraction ──────────────────────────────────────

    @staticmethod
    def extract_skills(text: str) -> list:
        """
        Keyword-based skill extraction.
        Compares lowercased text against SKILLS_BANK for O(1) lookup.
        Returns a sorted list of matched skill names (original casing).
        """
        normed = normalize_for_matching(text)
        # Word-boundary aware matching using regex
        matched = set()
        for lower_skill, original_skill in _SKILLS_LOWER.items():
            # Escape special regex characters (e.g. C++, C#, Next.js)
            pattern = re.escape(lower_skill)
            if re.search(rf'\b{pattern}\b', normed):
                matched.add(original_skill)
        return sorted(matched)

    # ── Experience Extraction ──────────────────────────────────

    @staticmethod
    def extract_experience(text: str) -> str:
        """
        Heuristic experience extraction.
        Tries to find statements like '3 years of experience' or '5+ yrs exp'.
        Returns the matched phrase, or a fallback message.
        """
        patterns = [
            r'(\d+)\+?\s*(years?|yrs?)[\s\-]*(of\s*)?(experience|exp)',
            r'(experience|exp)[:\s]+(\d+)\+?\s*(years?|yrs?)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()

        return "Experience not explicitly mentioned"

    # ── Name Extraction ────────────────────────────────────────

    @staticmethod
    def extract_candidate_name(text: str) -> str:
        """
        Best-effort candidate name extraction.
        Assumes the name appears on one of the first few lines of the resume.
        Falls back to 'Unknown Candidate'.
        """
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line in lines[:6]:
            # Heuristic: a name is 2-4 words, each capitalized, no digits
            words = line.split()
            if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
                if not any(char.isdigit() for char in line):
                    # Skip lines that look like section headers or emails
                    if "@" not in line and len(line) < 60:
                        return line
        return "Unknown Candidate"


parser_service = ParserService()
