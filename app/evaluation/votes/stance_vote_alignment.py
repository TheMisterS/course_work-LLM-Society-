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


def compute(subsession_path: Path) -> dict:
    state = load_state(subsession_path)
    votes: dict = state.get("votes", {})

    try:
        personas = load_personas(subsession_path)
    except FileNotFoundError:
        # no rag personas → can't compute alignment
        empty_alignment = {}
        for stage in STAGES:
            key = f"alignment_{stage}_pct"
            empty_alignment[key] = None
        return empty_alignment

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
            result[f"alignment_{stage}_pct"] = None
            result[f"aligned_count_{stage}"] = None
            result[f"total_scoreable_{stage}"] = None
            continue

        aligned = 0
        total = 0

        for agent_name, entry in stage_votes.items():
            stance = stance_map.get(agent_name, "")
            expected = STANCE_EXPECTED_VOTES.get(stance)

            # skip agents with mixed/unknown stance
            if expected is None:
                continue

            total += 1
            if entry.get("vote") in expected:
                aligned += 1

        if total == 0:
            pct = None
        else:
            pct = round(aligned / total * 100, 1)

        result[f"alignment_{stage}_pct"] = pct
        result[f"aligned_count_{stage}"] = aligned
        result[f"total_scoreable_{stage}"] = total

    return result
