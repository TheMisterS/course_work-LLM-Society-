from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from loader import load_state

VOTE_NUMERIC = {
    "Strongly For":     2,
    "For":              1,
    "Neutral":          0,
    "Against":         -1,
    "Strongly Against": -2,
}

VOTE_OPTIONS = ["Strongly For", "For", "Neutral", "Against", "Strongly Against"]
STAGES = ["initial", "mid", "final"]


def compute(subsession_path: Path) -> dict:
    """Compute vote distribution and average position for each stage in a subsession."""
    state = load_state(subsession_path)
    votes: dict = state.get("votes", {})

    result = {}
    for stage in STAGES:
        stage_votes = votes.get(stage)
        if stage_votes is None:
            result[f"average_position_{stage}"] = None
            result[f"distribution_{stage}"] = None
            continue

        vote_labels = [entry["vote"] for entry in stage_votes.values() if "vote" in entry]
        if not vote_labels:
            result[f"average_position_{stage}"] = None
            result[f"distribution_{stage}"] = None
            continue

        numeric = [VOTE_NUMERIC[v] for v in vote_labels if v in VOTE_NUMERIC]
        result[f"average_position_{stage}"] = round(sum(numeric) / len(numeric), 4) if numeric else None
        result[f"distribution_{stage}"] = {opt: vote_labels.count(opt) for opt in VOTE_OPTIONS}

    return result


def aggregate(subsession_metrics: list[dict]) -> dict:
    if not subsession_metrics:
        raise ValueError("no subsession metrics to aggregate")

    result = {"num_subsessions": len(subsession_metrics)}

    for stage in STAGES:
        pos_key = f"average_position_{stage}"
        values = [m[pos_key] for m in subsession_metrics if isinstance(m.get(pos_key), (int, float))]
        result[pos_key] = round(sum(values) / len(values), 4) if values else None

        dist_key = f"distribution_{stage}"
        dists = [m[dist_key] for m in subsession_metrics if isinstance(m.get(dist_key), dict)]
        if dists:
            result[dist_key] = {
                opt: round(sum(d.get(opt, 0) for d in dists) / len(dists), 4)
                for opt in VOTE_OPTIONS
            }
        else:
            result[dist_key] = None

    return result
