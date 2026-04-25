import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from config import KEYPOINT_COVERAGE_THRESHOLD
from embedder import embed, pairwise_cosine
from loader import load_personas

logger = logging.getLogger(__name__)

def compute(subsession_path: Path) -> dict:
    """Compute pairwise semantic distinctiveness across personas in one subsession."""

    personas = load_personas(subsession_path)
    logger.info("loaded %d personas from %s", len(personas), subsession_path.name)

    texts = []
    affiliations = []
    for p in personas:
        texts.append(" ".join(p["keypoints"]))
        affiliations.append(p["affiliation"])

    vectors = embed(texts)
    sim_matrix = pairwise_cosine(vectors)

    pairs = {}
    scores = []

    for i in range(len(affiliations)):
        for j in range(i + 1, len(affiliations)):
            score = round(float(sim_matrix[i, j]), 4)
            key = f"{affiliations[i]} vs {affiliations[j]}"
            pairs[key] = score
            scores.append(score)

    if scores:
        mean_sim = round(sum(scores) / len(scores), 4)
        min_sim = round(min(scores), 4)
        max_sim = round(max(scores), 4)
    else:
        mean_sim = min_sim = max_sim = 0.0

    result = {
        "metric": "persona_distinctiveness",
        "num_personas": len(personas),
        "mean_pairwise_similarity": mean_sim,
        "min_pairwise_similarity": min_sim,
        "max_pairwise_similarity": max_sim,
        "pairs": pairs,
    }

    logger.info("mean pairwise similarity: %.4f (min=%.4f max=%.4f)", mean_sim, min_sim, max_sim)

    return result
