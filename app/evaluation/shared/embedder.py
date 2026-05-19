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

def cosine_sim_matrix(vecs_a: np.ndarray, vecs_b: np.ndarray) -> np.ndarray:
    """Cosine similarity between every row of vecs_a and every row of vecs_b. Returns (N, M)."""
    norms_a = np.linalg.norm(vecs_a, axis=1, keepdims=True)
    norms_b = np.linalg.norm(vecs_b, axis=1, keepdims=True)
    norms_a = np.where(norms_a == 0, 1e-10, norms_a)
    norms_b = np.where(norms_b == 0, 1e-10, norms_b)
    return np.dot(vecs_a / norms_a, (vecs_b / norms_b).T)
