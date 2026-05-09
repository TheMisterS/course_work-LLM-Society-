import logging
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from embedder import embed, cosine_sim_matrix
from loader import load_personas

logger = logging.getLogger(__name__)

def compute(subsession_path: Path) -> dict:
    """Compute semantic similarity of persona affiliation/keypoints across personas in ONE subsession."""

    personas = load_personas(subsession_path)
    logger.info("loaded %d personas from %s", len(personas), subsession_path.name)

    # extract data from personas
    affiliations = [p["affiliation"] for p in personas]
    keypoints_per_persona = [p["keypoints"] for p in personas]

    # embed extracted data
    aff_vecs = embed(affiliations)
    kp_vecs_per_persona = [embed(kps) for kps in keypoints_per_persona]

    aff_scores: list[float] = []
    kp_scores: list[float] = []
    pairs: dict[str, dict] = {}

    for i in range(len(personas)):
        for j in range(i + 1, len(personas)):
            key = f"{affiliations[i]} vs {affiliations[j]}"

            aff_sim = round(float(cosine_sim_matrix(aff_vecs[i:i+1], aff_vecs[j:j+1])[0, 0]), 4)
            matrix = cosine_sim_matrix(kp_vecs_per_persona[i], kp_vecs_per_persona[j])
            kp_sim = round(float((matrix.max(axis=1).mean() + matrix.max(axis=0).mean()) / 2), 4)

            pairs[key] = {"aff_sim": aff_sim, "kp_sim": kp_sim}
            aff_scores.append(aff_sim)
            kp_scores.append(kp_sim)

    if aff_scores:
        average_aff = round(sum(aff_scores) / len(aff_scores), 4)
        min_aff = round(min(aff_scores), 4)
        max_aff = round(max(aff_scores), 4)
    else:
        average_aff = min_aff = max_aff = 0.0

    if kp_scores:
        average_kp = round(sum(kp_scores) / len(kp_scores), 4)
        min_kp = round(min(kp_scores), 4)
        max_kp = round(max(kp_scores), 4)
    else:
        average_kp = min_kp = max_kp = 0.0

    result = {
        "metric": "persona_similarity_in_subsession",
        "num_personas": len(personas),
        "average_pairwise_affiliation_sim": average_aff,
        "min_pairwise_affiliation_sim": min_aff,
        "max_pairwise_affiliation_sim": max_aff,
        "average_pairwise_keypoint_sim": average_kp,
        "min_pairwise_keypoint_sim": min_kp,
        "max_pairwise_keypoint_sim": max_kp,
        "pairs": pairs,
    }

    logger.info(
        "distinctiveness: affiliation similarity=%.4f keypoint similarity=%.4f (average pairwise)",
        average_aff, average_kp,
    )

    return result


def aggregate(subsession_metrics: list[dict]) -> dict:
    
    if not subsession_metrics:
        return {}

    num_subsessions = len(subsession_metrics)

    average_pairwise_affiliation_sim = round(
        sum(m["average_pairwise_affiliation_sim"] for m in subsession_metrics) / num_subsessions,
        4,
    )
    min_pairwise_affiliation_sim = round(
        sum(m["min_pairwise_affiliation_sim"] for m in subsession_metrics) / num_subsessions,
        4,
    )
    max_pairwise_affiliation_sim = round(
        sum(m["max_pairwise_affiliation_sim"] for m in subsession_metrics) / num_subsessions,
        4,
    )
    average_pairwise_keypoint_sim = round(
        sum(m["average_pairwise_keypoint_sim"] for m in subsession_metrics) / num_subsessions,
        4,
    )
    min_pairwise_keypoint_sim = round(
        sum(m["min_pairwise_keypoint_sim"] for m in subsession_metrics) / num_subsessions,
        4,
    )
    max_pairwise_keypoint_sim = round(
        sum(m["max_pairwise_keypoint_sim"] for m in subsession_metrics) / num_subsessions,
        4,
    )

    return {
        "metric": "persona_similarity_in_subsession_aggregate",
        "num_subsessions": num_subsessions,
        "average_pairwise_affiliation_sim": average_pairwise_affiliation_sim,
        "min_pairwise_affiliation_sim": min_pairwise_affiliation_sim,
        "max_pairwise_affiliation_sim": max_pairwise_affiliation_sim,
        "average_pairwise_keypoint_sim": average_pairwise_keypoint_sim,
        "min_pairwise_keypoint_sim": min_pairwise_keypoint_sim,
        "max_pairwise_keypoint_sim": max_pairwise_keypoint_sim,
    }
