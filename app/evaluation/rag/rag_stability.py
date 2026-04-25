import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from embedder import embed, cosine_sim
from loader import discover_subsessions, load_personas

logger = logging.getLogger(__name__)


def _jaccard(set_a: set, set_b: set) -> float:
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)


def compute(session_path: Path, output_path: Path | None = None) -> dict:
    """Compute cross-run stability for all subsessions in a session."""

    subsessions = discover_subsessions(session_path)
    logger.info("found %d subsessions in %s", len(subsessions), session_path.name)

    if len(subsessions) < 2:
        raise ValueError(f"stability requires at least 2 subsessions, found {len(subsessions)}")

    # load personas per run
    runs = []
    for sub in subsessions:
        personas = load_personas(sub)
        runs.append({"subsession": sub.name, "personas": personas})
        logger.info("loaded %d personas from %s", len(personas), sub.name)

    # jaccard overlap of affiliation sets per pair
    # affiliation is the stable real-world identity; names are static assignments and must not be used
    jaccard_scores = {}
    all_jaccard = []

    for i in range(len(runs)):
        for j in range(i + 1, len(runs)):
            affiliations_i = set(p["affiliation"] for p in runs[i]["personas"])
            affiliations_j = set(p["affiliation"] for p in runs[j]["personas"])
            score = round(_jaccard(affiliations_i, affiliations_j), 4)
            key = f"{runs[i]['subsession']} vs {runs[j]['subsession']}"
            jaccard_scores[key] = score
            all_jaccard.append(score)

    mean_jaccard = round(sum(all_jaccard) / len(all_jaccard), 4) if all_jaccard else 0.0

    # cross-run argument similarity for affiliations appearing in more than one run
    affiliation_to_runs: dict[str, list[list[str]]] = {}
    for run in runs:
        for p in run["personas"]:
            affiliation = p["affiliation"]
            if affiliation not in affiliation_to_runs:
                affiliation_to_runs[affiliation] = []
            affiliation_to_runs[affiliation].append(p["keypoints"])

    per_stakeholder = {}
    all_cross_run = []

    for affiliation, keypoint_lists in affiliation_to_runs.items():
        if len(keypoint_lists) < 2:
            continue

        texts = [" ".join(kps) for kps in keypoint_lists]
        vectors = embed(texts)

        pair_scores = []
        for i in range(len(vectors)):
            for j in range(i + 1, len(vectors)):
                score = cosine_sim(vectors[i], vectors[j])
                pair_scores.append(score)

        mean_score = round(sum(pair_scores) / len(pair_scores), 4) if pair_scores else 0.0
        per_stakeholder[affiliation] = mean_score
        all_cross_run.append(mean_score)

    mean_cross_run = round(sum(all_cross_run) / len(all_cross_run), 4) if all_cross_run else 0.0

    per_run_sets = [sorted(p["affiliation"] for p in run["personas"]) for run in runs]

    result = {
        "metric": "rag_stability",
        "session": session_path.name,
        "num_runs": len(runs),
        "mean_jaccard_stakeholder_overlap": mean_jaccard,
        "per_pair_jaccard": jaccard_scores,
        "mean_cross_run_argument_similarity": mean_cross_run,
        "per_stakeholder_cross_run_similarity": per_stakeholder,
        "per_run_stakeholder_sets": per_run_sets,
    }

    logger.info(
        "stability: jaccard=%.4f cross_run_sim=%.4f over %d runs",
        mean_jaccard, mean_cross_run, len(runs),
    )

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info("saved stability results to: %s", output_path)

    return result
