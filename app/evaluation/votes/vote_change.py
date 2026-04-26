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

STAGES = ["initial", "mid", "final"]

# helper to map vote to numeric score
def _score(vote_entry: dict) -> int | None:
    vote = vote_entry.get("vote", "")
    return VOTE_NUMERIC.get(vote)


def _add_change_metrics(
    result: dict,
    scores: dict[str, dict[str, int | None]],
    label: str,
    from_stage: str,
    to_stage: str,
) -> None:
    deltas = []
    for agent_scores in scores.values():
        a = agent_scores.get(from_stage)
        b = agent_scores.get(to_stage)
        
        # skip if either stage is missing
        if a is None or b is None:
            continue
        
        deltas.append(b - a)

    if not deltas:
        result[f"{label}_mean_change"] = None
        result[f"{label}_mean_abs_change"] = None
        result[f"{label}_std_change"] = None
        return

    n = len(deltas)
    mean = sum(deltas) / n
    total_abs = 0
    for delta in deltas:
        total_abs += abs(delta)
    mean_abs = total_abs / n

    squared_diff_sum = 0
    for delta in deltas:
        squared_diff_sum += (delta - mean) ** 2
    variance = squared_diff_sum / n
    std = variance ** 0.5

    result[f"{label}_mean_change"] = round(mean, 4)
    result[f"{label}_mean_abs_change"] = round(mean_abs, 4)
    result[f"{label}_std_change"] = round(std, 4)


def compute(subsession_path: Path) -> dict:
    state = load_state(subsession_path)
    votes: dict = state.get("votes", {})

    # collect numeric scores per agent per stage
    scores: dict[str, dict[str, int | None]] = {}
    for stage in STAGES:
        stage_votes = votes.get(stage, {})
        for agent, entry in stage_votes.items():
            if agent not in scores:
                scores[agent] = {}
            scores[agent][stage] = _score(entry)

    result = {}

    _add_change_metrics(result, scores, "start_to_mid", "initial", "mid")
    _add_change_metrics(result, scores, "mid_to_end", "mid", "final")
    _add_change_metrics(result, scores, "start_to_end", "initial", "final")

    return result
