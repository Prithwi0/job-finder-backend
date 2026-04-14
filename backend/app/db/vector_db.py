"""
Vector Database (FAISS)
-----------------------
Wraps Facebook AI Similarity Search (FAISS) for fast nearest-neighbour
search over resume embeddings.

Index type: IndexFlatIP  (Inner Product / Cosine similarity after L2-norm)
Dimension:  384          (all-MiniLM-L6-v2 output size)

The index is persisted to disk after every write so that state
survives server restarts.
"""

import logging
import os

import faiss
import numpy as np

from app.config.settings import settings

logger = logging.getLogger(__name__)


class VectorDB:
    def __init__(self):
        self.dimension = settings.EMBEDDING_DIMENSION
        self._load_or_create_index()

    # ── Index Lifecycle ────────────────────────────────────────

    def _load_or_create_index(self):
        if os.path.exists(settings.FAISS_INDEX):
            self.index = faiss.read_index(settings.FAISS_INDEX)
            logger.info(
                f"FAISS index loaded from disk — {self.index.ntotal} vectors present."
            )
        else:
            # IndexFlatIP: exact inner-product search.
            # After L2 normalisation, inner product == cosine similarity.
            self.index = faiss.IndexFlatIP(self.dimension)
            logger.info("New FAISS index created (IndexFlatIP).")

    def save(self):
        """Persist index to disk."""
        faiss.write_index(self.index, settings.FAISS_INDEX)
        logger.debug(f"FAISS index saved — total vectors: {self.index.ntotal}")

    # ── Write ──────────────────────────────────────────────────

    def add(self, vector: np.ndarray) -> int:
        """
        Normalise and add a (1, 384) float32 vector to the index.
        Returns the 0-based integer ID assigned to this vector.
        """
        vec = vector.astype(np.float32).copy()
        faiss.normalize_L2(vec)
        self.index.add(vec)
        self.save()
        assigned_id = self.index.ntotal - 1
        logger.info(f"Resume embedding added at FAISS index ID: {assigned_id}")
        return assigned_id

    # ── Read ───────────────────────────────────────────────────

    def search(self, query_vector: np.ndarray, top_k: int = 5):
        """
        Find the top_k most similar vectors to the query.

        Returns:
            distances (np.ndarray): cosine similarity scores in [0, 1]
            indices   (np.ndarray): FAISS internal IDs of matched vectors

        Note: reduces top_k to available vectors to avoid FAISS errors.
        """
        if self.index.ntotal == 0:
            return np.array([]), np.array([])

        k = min(top_k, self.index.ntotal)
        vec = query_vector.astype(np.float32).copy()
        faiss.normalize_L2(vec)
        distances, indices = self.index.search(vec, k)
        return distances[0], indices[0]

    @property
    def total_vectors(self) -> int:
        """Total number of vectors stored in the index."""
        return self.index.ntotal


# Global singleton — shared across routes and services
vector_db = VectorDB()
