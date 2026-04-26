BASELINE_SYSTEM_PROMPT = """You are building debate simulation personas.

Given a debate topic and an exact stakeholder composition (stances and counts), generate
realistic stakeholder personas representing organisations or public figures that would
plausibly hold those positions.

Output ONLY a JSON array. Each element must have exactly these keys:
- "affiliation": name of the organisation or individual being represented (e.g. "Lithuanian Farmers Union")
- "role_desc": 1-2 sentences written in first person. Follow this pattern exactly:
  "I am a representative of [org name], [one factual clause about the organisation's mandate
  or core interest in this domain]. [One sentence stating the persona's directional stance
  on the topic and the primary reason for it.]"
  Do NOT invent a job title or describe a fictional career. Always "a representative of [org]".
- "keypoints": a list of exactly 3 strings, each a distinct argument or belief this stakeholder holds
- "background": 1-2 sentences of factual institutional context based on your general knowledge
- "stance": one of "support", "oppose", "neutral" — must match the requested stance for this persona
- "sources": always exactly ["general knowledge"]

No markdown fences. No explanation. Output only the JSON array."""


def build_baseline_user_message(topic: str, stance_schema: dict, min_viewpoints: int) -> str:
    # build per-stance breakdown the same way the rag pipeline selects viewpoints
    breakdown_lines = []
    for stance, count in stance_schema.items():
        if count > 0:
            breakdown_lines.append(f"- {count} stakeholder(s) with stance: {stance}")
    breakdown = "\n".join(breakdown_lines)

    total = sum(stance_schema.values())

    return (
        f"Debate topic: {topic}\n\n"
        f"Generate exactly the following stakeholder composition (minimum {min_viewpoints} viewpoints per candidate):\n"
        f"{breakdown}\n\n"
        f"Total personas to generate: {total}\n\n"
        f"Base all personas on your general knowledge of this topic."
        f"Choose distinct organisations or public figures that plausibly hold each requested stance."
        f"Ensure personas are clearly differentiated from each other."
    )
