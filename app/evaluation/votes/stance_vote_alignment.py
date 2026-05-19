from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from loader import load_state, load_personas

STAGES = ["initial", "mid", "final"]

STANCE_EXPECTED_VOTES = {
    "support": ["For", "Strongly For"],
    "oppose":  ["Against", "Strongly Against"],
    "neutral": ["Neutral"],
}


def aggregate(subsession_metrics):
    if not subsession_metrics:
        raise ValueError("no subsession metrics to aggregate")

    result = {"num_subsessions": len(subsession_metrics)}
    
    for stage in STAGES:
        for key in [
            f"vote_alignment_{stage}_percentage",
            f"vote_alignment_{stage}_count",
            f"total_scoreable_{stage}_count",
        ]:
            values = [m[key] for m in subsession_metrics if isinstance(m.get(key), (int, float))]
            result[key] = round(sum(values) / len(values), 4) if values else None

    return result


def compute(subsession_path: Path) -> dict:
    state = load_state(subsession_path)
    votes: dict = state.get("votes", {})

    try:
        personas = load_personas(subsession_path)
    except FileNotFoundError:
        # no rag personas → can't compute alignment
        raise FileNotFoundError("personas not found, cannot compute vote alignment")


    # build stance map with persona name → stance (support/oppose/neutral)
    stance_map = {}
    for persona in personas:
        name = persona["name"]
        stance = persona.get("stance", "")
        stance_map[name] = stance

    result = {}
    for stage in STAGES:
        stage_votes = votes.get(stage)
        if stage_votes is None:
            result[f"vote_alignment_{stage}_percentage"] = None
            result[f"vote_alignment_{stage}_count"] = None
            result[f"total_scoreable_{stage}_count"] = None
            continue

        aligned = 0
        total = 0

        for agent_name, entry in stage_votes.items():
            stance = stance_map.get(agent_name, "")
            expected = STANCE_EXPECTED_VOTES.get(stance)

            # skip agents with mixed/unknown stance
            if expected is None:
                raise ValueError(f"agent {agent_name} has unknown stance '{stance}', cannot compute alignment for stage {stage}")

            total += 1
            
            # core matching operation
            if entry.get("vote") in expected:
                aligned += 1

        if total == 0:
            pct = None
        else:
            pct = round(aligned / total * 100, 1)

        result[f"vote_alignment_{stage}_percentage"] = pct
        result[f"vote_alignment_{stage}_count"] = aligned
        result[f"total_scoreable_{stage}_count"] = total

    return result
