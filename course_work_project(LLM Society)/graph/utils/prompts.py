from typing import List
from graph.utils.state import AgentState

def generate_debate_system_prompt(agent: AgentState) -> str:
    # transcript_slice will work as the conversation history/ short term memory
    # Agent should have some sort of function to do long term memory summarization

    if agent['traits']:
        traits_desc = "\n".join([f"{k}: {v}" for k,v in agent['traits'].items()])

    return (
        f"You are {agent['name']} in a small group discussion.\n"
        f"Your role: {agent['role_desc']}.\n"
        f"{traits_desc}\n"
        "Speak like a real person in a live conversation:\n"
        "- Short, natural sentences.\n"
        "- Keep the tone casual; the others are your peers.\n"
        "- Let your reactions follow what feels natural for your personality.\n"
        "  For example, you might respond directly, change the angle, tell a small story,\n"
        "- It's okay to show emotions and be opinionated.\n"
        "  ask a question, or even go on a small tangent.\n"
        "- It's okay to show emotions and be opinionated.\n"
        "- If you don't know something, just admit it.\n"
        "- If you don't know something, you can say so or simply avoid that angle.\n"
        "Do NOT explain that you are an AI or mention any guidelines.\n"
        "Write only what you say in this turn as "
        f"{agent['name']}, nothing else."
    )
    

def generate_debate_user_prompt(agent: AgentState) -> str:
    recent_msgs = agent['short_mem'][-6:] if len(agent['short_mem']) > 6 else agent['short_mem']

    lines = []
    
    # format recent messages into bullet list (memory)
    for m in reversed(recent_msgs):
        if hasattr(m, "name") and hasattr(m, "content"):
            lines.append(f"- [{getattr(m, 'name')}]: {getattr(m, 'content')}")
        else:
            lines.append(f"- {str(m)}")

    short_memory_list = "\n".join(lines)


    # first message special case to reduce hallucination (detected based on empty memory)
    if not short_memory_list:
        return (
            f"Debate topic: {agent['agent_agenda']['debate_topic']}\n\n"
            f"You are the first to speak.\n"
            f"As {agent['name']}, start the conversation naturally: "
            "greet the others briefly and share your initial reaction to the topic.\n"
            "Keep it casual and true to your character, in 2–5 sentences.\n"
            f"Write only what {agent['name']} says."
        )
    else:
        return (
            f"Debate topic: {agent['agent_agenda']['debate_topic']}\n\n"
            "Recent conversation (most recent first):\n"
            f"{short_memory_list}\n\n"
            f"Now continue the conversation as {agent['name']}:\n"
            "Let your reply follow naturally from the situation and your personality.\n"
            "You can respond directly, shift the focus, tell a short anecdote, ask something,\n"
            "or even introduce a side thought, if that feels right to you.\n"
            "Keep it to roughly 2–5 sentences, sounding like a real person.\n"
            f"Write only what {agent['name']} says."
        )


def generate_voting_system_prompt(agent: AgentState) -> str:
    prompt = f"You are {agent['name']}. Your role is: {agent['role_desc']}.\n\n"
    
    if agent['traits']:
        traits_desc = "\n".join([f"{k}: {v}" for k,v in agent['traits'].items()])
        prompt += f"Traits:\n{traits_desc}\n\n"
    
    prompt += """VOTING GUIDELINES:
    - Review the debate that has taken place
    - Consider your character's values, traits, and perspective
    - Make a decision that aligns with your established character
    - Provide a brief justification for your vote (1-2 sentences)
    
    Output format:
    VOTE: [your choice]
    REASON: [brief justification]
    """
    return prompt


def generate_voting_user_prompt(agent: AgentState, voting_question: str, options: List[str]) -> str:
    # Include debate summary from long_mem for now, perhaps entertain other approaches later
    recent_msgs = agent['short_mem']
    
    debate_summary = "\n".join([
        f"- [{getattr(m, 'name', 'Unknown')}]: {getattr(m, 'content', str(m))}"
        for m in recent_msgs
    ])
    
    prompt = f"""Question: {voting_question}

    Available options:
    {chr(10).join([f"- {opt}" for opt in options])}

    Debate summary (most recent messages):
    {debate_summary}

    Based on the debate and your character, cast your vote."""
    
    return prompt