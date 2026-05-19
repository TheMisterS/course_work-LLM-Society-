from pathlib import Path
import logging
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

TRANSITIONS = ["start_to_mid", "mid_to_end", "start_to_end"]


STAGES = ["initial", "mid", "final"]
logger = logging.getLogger(__name__)

def compute_vote_change(scores: dict, label: str, from_stage: str, to_stage: str) -> dict:

    score_differences = []
    for agent_scores in scores.values():
        a = agent_scores.get(from_stage)
        b = agent_scores.get(to_stage)

        # skip if either stage is missing
        if a is None or b is None:
            raise ValueError(f"agent missing score for {from_stage} or {to_stage}, cannot compute change for {label}")

        score_differences.append(b - a)

    if not score_differences:
        raise ValueError(f"no valid score differences for {label}, cannot compute change")


    # plain average
    n = len(score_differences)
    average = sum(score_differences) / n

    # average absolute change
    total_abs = 0
    for score_difference in score_differences:
        total_abs += abs(score_difference)
    average_abs = total_abs / n

    return {
        f"{label}_average_change": round(average, 4),
        f"{label}_average_abs_change": round(average_abs, 4),
    }

def aggregate(subsession_metrics: list[dict]) -> dict:
    if not subsession_metrics:
        raise ValueError("no subsession metrics to aggregate")

    result = {"num_subsessions": len(subsession_metrics)}
    for label in TRANSITIONS:
        for suffix in ["_average_change", "_average_abs_change"]:
            key = f"{label}{suffix}"
            values = [m[key] for m in subsession_metrics if isinstance(m.get(key), (int, float))]
            result[key] = round(sum(values) / len(values), 4) if values else None

    return result

def compute(subsession_path: Path) -> dict:
    state = load_state(subsession_path)
    votes: dict = state.get("votes", {})

    # collect numeric scores per agent per stage
    scores = {}

    # iterate over stages and all the agents within to gather numeric representations of all of the votes
    for stage in STAGES:
        stage_votes = votes.get(stage, {})
        for agent, entry in stage_votes.items():
            # initialize agent entry on initial stage
            if agent not in scores:
                scores[agent] = {}
                
            vote = entry.get("vote", "")
            scores[agent][stage] = VOTE_NUMERIC.get(vote)

    result = {}
    result.update(compute_vote_change(scores, "start_to_mid", "initial", "mid"))
    result.update(compute_vote_change(scores, "mid_to_end", "mid", "final"))
    result.update(compute_vote_change(scores, "start_to_end", "initial", "final"))

    return result
