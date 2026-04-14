"""
Embedding Service
-----------------
Wraps the HuggingFace sentence-transformers model to produce
dense vector embeddings from text.

Model: all-MiniLM-L6-v2
  - 384-dimensional output
  - Fast, lightweight, excellent for semantic similarity tasks
  - Downloaded and cached by sentence-transformers on first use
"""

import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config.settings import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully.")

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Encode a text string into a dense embedding vector.

        Returns:
            np.ndarray of shape (1, 384) with dtype float32
            — the extra batch dimension is required by FAISS.
        """
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text.")
        embedding = self.model.encode(text, convert_to_numpy=True)
        # Cast to float32 (FAISS requirement) and add batch dimension
        return np.expand_dims(embedding.astype(np.float32), axis=0)


# Single global instance — model is loaded once at startup
embedding_service = EmbeddingService()
