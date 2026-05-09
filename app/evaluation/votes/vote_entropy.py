import math
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from loader import load_state

STAGES = ["initial", "mid", "final"]

# 5 options so max entropy = log2(5) ≈ 2.322
_MAX_ENTROPY = math.log2(5)


def _entropy(votes: list[str]) -> float:

    if not votes:
        raise ValueError("no votes provided, cannot compute entropy")

    
    counts: dict[str, int] = {}
    
    # count how often each vote appears.
    for v in votes:
        counts[v] = counts.get(v, 0) + 1

    # Shannon entropy: H = -sum(p * log2(p)) across vote categories.
    n = len(votes)
    h = 0.0
    for c in counts.values():
        # category count to probability.
        p = c / n
        h -= p * math.log2(p)

    # Normalize
    return h / _MAX_ENTROPY


def aggregate(subsession_metrics: list[dict]) -> dict:

    if not subsession_metrics:
        raise ValueError("no subsession metrics to aggregate")

    result = {"num_subsessions": len(subsession_metrics)}
    for stage in STAGES:
        key = f"entropy_{stage}"
        values = [m[key] for m in subsession_metrics if isinstance(m.get(key), float)]
        result[key] = round(sum(values) / len(values), 4) if values else None

    return result


def compute(subsession_path: Path) -> dict:
    state = load_state(subsession_path)
    votes: dict = state.get("votes", {})

    result = {}
    for stage in STAGES:
        stage_votes = votes.get(stage)
        if stage_votes is None:
            result[f"entropy_{stage}"] = None
            continue

        vote_values = [entry["vote"] for entry in stage_votes.values() if "vote" in entry]
        if not vote_values:
            raise ValueError(f"no votes found for stage {stage}, cannot compute entropy")
        else:
            result[f"entropy_{stage}"] = round(_entropy(vote_values), 4)

    return result
