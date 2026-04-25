"""
Prompts for the LLM Judge evaluation system.
Each criterion has its own prompt with only the relevant context exposed.
"""

from models import DebateState


# =============================================================================
# CRITERION-SPECIFIC SYSTEM PROMPTS
# =============================================================================

ARGUMENT_COHERENCE_SYSTEM = """You are an expert evaluator assessing a multi-agent debate conversation.

Your task is to evaluate the ARGUMENT COHERENCE of the entire discussion.

## CRITERION: Argument Coherence (1-5)
Evaluates logical consistency and reasoning flow across all participants.

- 1: Arguments are contradictory, illogical, or incoherent across participants
- 2: Arguments have significant logical gaps or inconsistencies
- 3: Arguments are mostly coherent with minor issues
- 4: Arguments are well-structured and logically consistent throughout
- 5: Arguments are exceptionally clear, logical, and build upon each other coherently

## OUTPUT FORMAT
You MUST respond with valid JSON in exactly this format:
{
    "score": <1-5>,
    "reasoning": "<brief explanation of the score>"
}

Respond ONLY with the JSON object, no additional text."""


IDENTITY_CONSISTENCY_SYSTEM = """You are an expert evaluator assessing a multi-agent debate conversation.

Your task is to evaluate the IDENTITY CONSISTENCY of all agents in the discussion.

## CRITERION: Identity Consistency (1-5)
Evaluates how well each agent aligns with their assigned role and personality traits throughout the conversation.

- 1: Agents completely ignore assigned roles/traits, behave contrary to character
- 2: Agents rarely reflect assigned traits, often break character
- 3: Agents are generally consistent with roles, occasional deviations
- 4: Strong alignment with assigned traits throughout discussion
- 5: Perfect embodiment of assigned roles and traits in every interaction

## OUTPUT FORMAT
You MUST respond with valid JSON in exactly this format:
{
    "score": <1-5>,
    "reasoning": "<brief explanation of the score>"
}

Respond ONLY with the JSON object, no additional text."""


RESPONSIVENESS_SYSTEM = """You are an expert evaluator assessing a multi-agent debate conversation.

Your task is to evaluate the RESPONSIVENESS of the discussion.

## CRITERION: Responsiveness (1-5)
Evaluates how well participants directly engage with each other's points.

- 1: Participants ignore each other entirely, only make standalone statements
- 2: Participants rarely acknowledge others, mostly talk past each other
- 3: Participants sometimes respond to others but often miss key points
- 4: Participants consistently engage with and address each other's arguments
- 5: Deep engagement with every relevant point, building constructive dialogue

## OUTPUT FORMAT
You MUST respond with valid JSON in exactly this format:
{
    "score": <1-5>,
    "reasoning": "<brief explanation of the score>"
}

Respond ONLY with the JSON object, no additional text."""


CONSENSUS_ALIGNMENT_SYSTEM = """You are an expert evaluator assessing a multi-agent debate conversation.

Your task is to evaluate the CONSENSUS ALIGNMENT between the discussion and final votes.

## CRITERION: Consensus Alignment (1-5)
Evaluates whether the final votes reflect the positions expressed during discussion.

- 1: Votes completely contradict stated positions during debate
- 2: Votes poorly reflect discussion, major inconsistencies
- 3: Votes somewhat align with discussion but with notable gaps
- 4: Votes logically follow from discussion contributions
- 5: Votes are a perfect synthesis of evolved positions through debate

## OUTPUT FORMAT
You MUST respond with valid JSON in exactly this format:
{
    "score": <1-5>,
    "reasoning": "<brief explanation of the score>"
}

Respond ONLY with the JSON object, no additional text."""


CONFLICT_AVOIDANCE_SYSTEM = """You are an expert evaluator assessing a multi-agent debate conversation.

Your task is to evaluate the CONFLICT AVOIDANCE / HEDGING patterns in the discussion.

## CRITERION: Conflict Avoidance / Hedging (1-5)
Evaluates how much participants avoid committing to positions or avoid constructive conflict.

- 1: Excessive hedging, no real positions taken, conflict completely avoided
- 2: Significant hedging, participants rarely commit to clear positions
- 3: Moderate hedging, some clear positions but frequent softening
- 4: Minimal hedging, participants mostly take clear stances
- 5: No inappropriate hedging, healthy debate with clear committed positions

Note: A HIGH score means participants engage constructively and take clear positions. A LOW score means excessive conflict avoidance.

## OUTPUT FORMAT
You MUST respond with valid JSON in exactly this format:
{
    "score": <1-5>,
    "reasoning": "<brief explanation of the score>"
}

Respond ONLY with the JSON object, no additional text."""


# =============================================================================
# FORMATTING HELPERS
# =============================================================================

def format_conversation(state: DebateState) -> str:
    """Format the full conversation for the prompt."""
    lines = []
    for msg in state.messages:
        lines.append(f"[{msg.name}]: {msg.content}")
    return "\n\n".join(lines)


def format_agent_profiles(state: DebateState) -> str:
    """Format all agent profiles with their traits"""
    profiles = []
    for agent_name, agent in state.agents.items():
        # Traits are dynamic dict, format all key-value pairs
        traits_str = ", ".join(
            f"{k}: {v}" for k, v in agent.traits.items()
        )
        profiles.append(
            f"**{agent.name}**\n"
            f"  Role: {agent.role_desc}\n"
            f"  Traits: {traits_str}"
        )
    return "\n\n".join(profiles)


def format_votes(state: DebateState, round: str = "final") -> str:
    """Format votes for a given round (defaults to final)"""
    
    round_votes = state.votes.get(round, {})
    lines = []
    
    for agent_name, v in round_votes.items():
        vote_str = v.get("vote", "") if isinstance(v, dict) else v
        reason_str = v.get("reason", "") if isinstance(v, dict) else ""
        lines.append(f"**{agent_name}**: {vote_str} — {reason_str}")
        
    return "\n\n".join(lines)


# =============================================================================
# USER PROMPT GENERATORS (per criterion)
# =============================================================================

def generate_argument_coherence_prompt(state: DebateState) -> str:
    """Generate prompt for Argument Coherence - only discussion."""
    return f"""## DEBATE TOPIC
{state.debate_topic}

## DISCUSSION
{format_conversation(state)}

---
Evaluate the argument coherence of this discussion. Respond with JSON only."""


def generate_identity_consistency_prompt(state: DebateState) -> str:
    """Generate prompt for Identity Consistency - discussion + agent traits."""
    return f"""## DEBATE TOPIC
{state.debate_topic}

## AGENT PROFILES
{format_agent_profiles(state)}

## DISCUSSION
{format_conversation(state)}

---
Evaluate how well each agent maintained their assigned identity. Respond with JSON only."""


def generate_responsiveness_prompt(state: DebateState) -> str:
    """Generate prompt for Responsiveness - only discussion."""
    return f"""## DEBATE TOPIC
{state.debate_topic}

## DISCUSSION
{format_conversation(state)}

---
Evaluate the responsiveness and engagement between participants. Respond with JSON only."""


def generate_consensus_alignment_prompt(state: DebateState) -> str:
    """Generate prompt for Consensus Alignment - discussion + votes."""
    return f"""## DEBATE TOPIC
{state.debate_topic}

## VOTING QUESTION
{state.voting_question}

## VOTING OPTIONS
{", ".join(state.voting_options)}

## DISCUSSION
{format_conversation(state)}

## FINAL VOTES
{format_votes(state)}

---
Evaluate how well the votes align with the discussion. Respond with JSON only."""


def generate_conflict_avoidance_prompt(state: DebateState) -> str:
    """Generate prompt for Conflict Avoidance - only discussion."""
    return f"""## DEBATE TOPIC
{state.debate_topic}

## DISCUSSION
{format_conversation(state)}

---
Evaluate the conflict avoidance and hedging patterns in this discussion. Respond with JSON only."""


# =============================================================================
# CRITERION REGISTRY
# =============================================================================

CRITERIA = {
    "argument_coherence": {
        "system_prompt": ARGUMENT_COHERENCE_SYSTEM,
        "user_prompt_fn": generate_argument_coherence_prompt,
    },
    "identity_consistency": {
        "system_prompt": IDENTITY_CONSISTENCY_SYSTEM,
        "user_prompt_fn": generate_identity_consistency_prompt,
    },
    "responsiveness": {
        "system_prompt": RESPONSIVENESS_SYSTEM,
        "user_prompt_fn": generate_responsiveness_prompt,
    },
    "consensus_alignment": {
        "system_prompt": CONSENSUS_ALIGNMENT_SYSTEM,
        "user_prompt_fn": generate_consensus_alignment_prompt,
    },
    "conflict_avoidance": {
        "system_prompt": CONFLICT_AVOIDANCE_SYSTEM,
        "user_prompt_fn": generate_conflict_avoidance_prompt,
    },
}
