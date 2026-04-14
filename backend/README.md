# AI Resume Screener & Job Matching System

A smart, AI-powered backend designed to match candidate resumes with job descriptions using Natural Language Processing (NLP) and Vector Search.

Built with **Python**, **FastAPI**, **Sentence-Transformers**, and **FAISS**. This project does *not* use a heavy relational or NoSQL database, making it extremely easy to run locally using simple JSON files for persistent storage.

## Features

- **Upload Resumes:** Parses PDF and DOCX files to extract text, skills, and experience length.
- **Smart Embeddings:** Converts extracted text into dense vectors using the HuggingFace `all-MiniLM-L6-v2` model.
- **Vector Search:** Uses FAISS (Facebook AI Similarity Search) to rapidly find resumes that semantically match a job description.
- **Job Management:** Store and manage job descriptions.
- **Explainable Matches:** Returns an easy-to-understand explanation of *why* a candidate is a good fit, based on keyword intersections and missing skills.

## Project Structure

```text
backend/
├── app/
│   ├── config/settings.py          # Centralized configuration (paths, models, matching rules)
│   ├── db/
│   │   ├── json_store.py           # Handles reading/writing to resumes.json and jobs.json
│   │   └── vector_db.py            # Manages the FAISS index for fast nearest-neighbor search
│   ├── routes/
│   │   ├── job.py                  # POST /job/add, GET /job/list
│   │   ├── match.py                # POST /match/run, GET /match/results
│   │   └── resume.py               # POST /resume/upload
│   ├── services/
│   │   ├── embedding_service.py    # HuggingFace model wrapper (sentence-transformers)
│   │   ├── matching_service.py     # Core matching logic, score calculation, explanations
│   │   └── parser_service.py       # Extract text and metadata (skills, experience) from files
│   ├── utils/
│   │   ├── file_handler.py         # Temporary file logic for document parsing
│   │   └── text_cleaner.py         # NLP text normalization and cleanup
│   └── main.py                     # FastAPI application entry point
├── data/                           # Storage directory (auto-created)
│   ├── resumes.json                # Metadata storage for uploaded resumes
│   ├── jobs.json                   # Storage for job postings
│   └── index.faiss                 # Binary vector index (FAISS)
├── requirements.txt                # Python dependencies
└── README.md                       # Project documentation
```

## Setup Instructions

### 1. Create a Virtual Environment
It's recommended to create a virtual environment to manage dependencies securely.
```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
Install all required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

> **Note:** The first time you run the application, it will download the `all-MiniLM-L6-v2` model from Hugging Face. This might take a minute depending on your internet connection.

### 3. Run the Server
Start the Uvicorn development server:
```bash
uvicorn app.main:app --reload
```
The server will be available at `http://localhost:8000`.

## API Endpoints

Once the server is running, you can explore the fully interactive API documentation and test endpoints directly from your browser by going to [http://localhost:8000/docs](http://localhost:8000/docs).

### Core Endpoints:

1. **`GET /`** - Health check and system stats.
2. **`POST /resume/upload`** - Upload a `.pdf` or `.docx` file. Extracts text, derives skills/experience, calculates the embedding, and saves it to the FAISS index and JSON store.
3. **`POST /job/add`** - Add a new job description with a title and full text.
4. **`GET /job/list`** - List all stored jobs.
5. **`POST /match/run`** - Find candidates. Pass either a raw `description` string or a valid `job_id`.
6. **`GET /match/results`** - Get the list of matched candidates from the latest run, fully scored (0-100) and ranked.

## Troubleshooting

- **FAISS Installation Issues:** If you face issues installing `faiss-cpu`, ensure your Python version is compatible (typically Python 3.9 - 3.12 works best).
- **Inaccurate Parsing:** Skill parsing relies on a keyword dictionary located in `parser_service.py`. If certain skills aren't being picked up, try adding them to the `SKILLS_BANK` list in that file.

---
*Created for the final year AI Project.*
