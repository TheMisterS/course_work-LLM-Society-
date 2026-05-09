BASELINE_SYSTEM_PROMPT = """You are building debate simulation personas.

Given a debate topic and a required stakeholder composition, generate realistic personas
representing Lithuanian organisations or public figures that would plausibly hold those positions.

Output ONLY a JSON array. Each element must have exactly these keys:
- "affiliation": name of the organisation or individual (e.g. "Lithuanian Farmers Union")
- "role_desc": 1-2 sentences written in first person. Follow this pattern exactly:
  "I am a representative of [org name], [one factual clause about the organisation's mandate
  or core interest in this domain]. [One sentence stating the persona's directional stance
  on the topic and the primary reason for it.]"
  Do NOT invent a job title. Always "a representative of [org]".
- "keypoints":  a list of 2-4 strings. Each must be a concrete, organisation-specific
  argument grounded in that stakeholder's actual mandate or interests — not a generic claim
  that any participant in this debate could make.
- "background": 1-2 sentences of factual institutional context (founding, mandate, scope).
  Do NOT repeat the stance or arguments already stated in role_desc.
- "stance": one of "support", "oppose", "neutral" — must match the requested stance
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
        f"Generate exactly {total} Lithuanian stakeholder personas with the following stance composition:\n"
        f"{breakdown}\n\n"
        "Each persona must represent a different Lithuanian organisation or public figure. "
        "Choose stakeholders from a variety of sectors (e.g. government, NGO, business, academic, media) "
        "so the debate reflects the real landscape of interests around this topic. "
        "Ensure each persona's keypoints are specific to their organisation's actual mandate and interests — "
        "not generic arguments that any stakeholder could make."
    )