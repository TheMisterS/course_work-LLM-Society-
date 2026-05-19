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
            result[f"per_agent_{stage}"] = None
            continue

        numeric = [VOTE_NUMERIC[v] for v in vote_labels if v in VOTE_NUMERIC]
        result[f"average_position_{stage}"] = round(sum(numeric) / len(numeric), 4) if numeric else None
        result[f"distribution_{stage}"] = {opt: vote_labels.count(opt) for opt in VOTE_OPTIONS}
        result[f"per_agent_{stage}"] = {
            agent: entry["vote"]
            for agent, entry in stage_votes.items()
            if "vote" in entry
        }

    return result

def aggregate(subsession_metrics: list[dict]) -> dict:
    if not subsession_metrics:
        raise ValueError("no subsession metrics to aggregate")

    result = {"num_subsessions": len(subsession_metrics)}

    # agregate average group position
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
            
    # aggregate each agents distributions
    for stage in STAGES:
        per_agent_dicts = [
            m[f"per_agent_{stage}"]
            for m in subsession_metrics
            if isinstance(m.get(f"per_agent_{stage}"), dict)
        ]
        
        if not per_agent_dicts:
            result[f"per_agent_distribution_{stage}"] = None
            continue
        else:
            agent_dist: dict = {}    
        
        for per_agent in per_agent_dicts:
            for name, vote in per_agent.items():
                if name not in agent_dist:
                    agent_dist[name] = {opt: 0 for opt in VOTE_OPTIONS}
                    agent_dist[name]["count"] = 0
                    agent_dist[name]["_numeric_sum"] = 0              
                    
                if vote in VOTE_OPTIONS:
                    agent_dist[name][vote] += 1
                    agent_dist[name]["count"] += 1
                    agent_dist[name]["_numeric_sum"] += VOTE_NUMERIC[vote]
                else:
                    raise ValueError(f"unknown vote '{vote}' for agent '{name}' in stage '{stage}', cannot aggregate distribution")

        # alculate the final average position for each agent based on their totals 
        for name, dist in agent_dist.items():
            n = dist.pop("_numeric_sum")
            c = dist["count"]
            dist["average_position"] = round(n / c, 4) if c else None

        result[f"per_agent_distribution_{stage}"] = agent_dist

    return result
