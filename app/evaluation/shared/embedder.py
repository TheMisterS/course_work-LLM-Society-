import numpy as np
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL

_model = None

def get_model() -> SentenceTransformer:
    """Return cached model instance, loading on first call."""
    
    global _model
    
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed(texts: list[str]) -> np.ndarray:
    """Embed a list of strings. Returns (N, 768) array."""
    
    model = get_model()
    return model.encode(texts, convert_to_numpy=True)


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two 1D vectors."""
    
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return float(np.dot(a, b) / (norm_a * norm_b))


def pairwise_cosine(matrix: np.ndarray) -> np.ndarray:
    """Compute pairwise cosine similarity for rows of matrix. Returns (N, N) symmetric matrix."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    
    # avoid division by zero
    norms = np.where(norms == 0, 1e-10, norms)
    
    normalised = matrix / norms
    return np.dot(normalised, normalised.T)
