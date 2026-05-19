import json
import logging
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from embedder import embed, cosine_sim_matrix
from loader import discover_subsessions, load_personas

logger = logging.getLogger(__name__)

def compute(session_path: Path, output_path: Path | None = None) -> dict:
    """Compute semantic similarity of persona affiliation/keypoints across personas in ALL subsessions."""

    subsessions = discover_subsessions(session_path)
    logger.info("found %d subsessions in %s", len(subsessions), session_path.name)

    if len(subsessions) < 2:
        raise ValueError(f"stability requires at least 2 subsessions, found {len(subsessions)}")

    runs = []
    for sub in subsessions:
        personas = load_personas(sub)
        
        # Extract data from personas
        affiliations = [p["affiliation"] for p in personas]
        keypoints = [kp for p in personas for kp in p["keypoints"]]
        
        # Embed extracted data
        aff_vecs = embed(affiliations)
        kp_vecs = embed(keypoints)
        
        runs.append({"subsession": sub.name, "aff_vecs": aff_vecs, "kp_vecs": kp_vecs})
        logger.info("loaded %d personas from %s", len(personas), sub.name)

    per_pair_aff: dict[str, float] = {}
    per_pair_kp: dict[str, float] = {}
    all_aff: list[float] = []
    all_kp: list[float] = []

    # BertScore-like approach: for each run pair, compute cosine similarity matrix and average max sims in both directions
    for i in range(len(runs)):
        for j in range(i + 1, len(runs)):
            key = f"{runs[i]['subsession']} vs {runs[j]['subsession']}"

            aff_matrix = cosine_sim_matrix(runs[i]["aff_vecs"], runs[j]["aff_vecs"])
            aff_sim = round(float((aff_matrix.max(axis=1).mean() + aff_matrix.max(axis=0).mean()) / 2), 4)

            kp_matrix = cosine_sim_matrix(runs[i]["kp_vecs"], runs[j]["kp_vecs"])
            kp_sim = round(float((kp_matrix.max(axis=1).mean() + kp_matrix.max(axis=0).mean()) / 2), 4)

            per_pair_aff[key] = aff_sim
            per_pair_kp[key] = kp_sim

            all_aff.append(aff_sim)
            all_kp.append(kp_sim)

    average_aff = round(sum(all_aff) / len(all_aff), 4) if all_aff else 0.0
    average_kp = round(sum(all_kp) / len(all_kp), 4) if all_kp else 0.0

    result = {
        "metric": "persona_similarity_across_sessions",
        "session": session_path.name,
        "num_runs": len(runs),
        "average_affiliation_sim": average_aff,
        "average_keypoint_sim": average_kp,
        "per_pair_affiliation_sim": per_pair_aff,
        "per_pair_keypoint_sim": per_pair_kp,
    }

    logger.info(
        "stability: affiliation similarity=%.4f keypoint similarity=%.4f in %d runs",
        average_aff, average_kp, len(runs),
    )

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        logger.info("saved stability results to: %s", output_path)

    return result


def aggregate(session_results: list[dict]) -> dict:

    if not session_results:
        return {}

    average_aff = round(sum(r["average_affiliation_sim"] for r in session_results) / len(session_results), 4)
    average_kp = round(sum(r["average_keypoint_sim"] for r in session_results) / len(session_results), 4)

    return {
        "metric": "persona_similarity_across_sessions_aggregate",
        "num_sessions": len(session_results),
        "sessions": [r["session"] for r in session_results],
        "average_affiliation_sim": average_aff,
        "average_keypoint_sim": average_kp,
        "per_session": {
            r["session"]: {
                "average_affiliation_sim": r["average_affiliation_sim"],
                "average_keypoint_sim": r["average_keypoint_sim"],
            }
            for r in session_results
        },
    }
