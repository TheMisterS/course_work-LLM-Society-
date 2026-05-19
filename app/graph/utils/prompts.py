from typing import List
from graph.utils.state import AgentState

import logging
logger = logging.getLogger(__name__)


def format_messages_for_summary(messages: List) -> str:
    """Format a list of messages into a readable string for summarization."""
    lines = []
    for m in messages:
        if hasattr(m, "name") and hasattr(m, "content"):
            lines.append(f"[{getattr(m, 'name')}]: {getattr(m, 'content')}")
        elif isinstance(m, dict):
            lines.append(f"[{m.get('name', 'Unknown')}]: {m.get('content', str(m))}")
        else:
            lines.append(str(m))
    return "\n".join(lines)


def generate_initial_memory_summary_prompt(agent: AgentState, messages: List) -> dict:
    """
    Generate system and user prompts for creating the FIRST long-term memory summary.
    Returns dict with 'system_message' and 'user_message' keys.
    """
    logger.debug(f"Generating initial long term memory summary prompt for agent: {agent['name']}")
    
    formatted_messages = format_messages_for_summary(messages)
    
    system_message = (
        f"You are a memory summarizer for {agent['name']}.\n"
        f"Your task is to create a concise summary of a conversation from {agent['name']}'s perspective.\n\n"
        "Focus on:\n"
        "- Key points and arguments made by participants\n"
        "- Important reactions or positions taken\n"
        "- Any significant agreements or disagreements\n"
        f"- Information that would be valuable for {agent['name']} to remember later\n\n"
        "**Important Reminders:**\n"
        "- No preambles or introductory phrases\n"
        "- Summary must use 'I' statements and first-person perspective\n"
        "- Output is a single concise paragraph, 3-5 sentences\n\n"
        "**Output Format:**\n"
        f"A single paragraph, 3-5 sentences, in the first person as {agent['name']}. Do not include any introductory or explanatory text—start directly with the summary content."
    )
    
    user_message = (
        f"Summarize the following conversation for {agent['name']}'s long-term memory:\n\n"
        f"Conversation:\n{formatted_messages}\n\n"
        f"Create a concise summary that captures the key points and context."
    )
    
    return {"system_message": system_message, "user_message": user_message}


def generate_update_memory_summary_prompt(agent: AgentState, existing_summary: str, new_messages: List) -> dict:
    """
    Generate system and user prompts for updating an EXISTING long-term memory summary.
    The LLM will merge new conversation context into the existing summary.
    Returns dict with 'system_message' and 'user_message' keys.
    """
    logger.debug(f"Generating update memory summary prompt for agent: {agent['name']}")
    
    formatted_messages = format_messages_for_summary(new_messages)
    
    system_message = (
        f"You are a memory summarizer for {agent['name']}.\n"
        f"Your task is to update an existing conversation summary with new information.\n\n"
        "Guidelines:\n"
        "- Integrate new developments into the existing summary\n"
        "- Preserve important earlier context that remains relevant\n"
        "- Update or revise points if positions have changed\n"
        "- Keep the summary concise but comprehensive (4-6 sentences)\n\n"
        "**Important Reminders:**\n"
        "- Integrate new information smoothly into the summary\n"
        "- Retain earlier details only if still relevant\n"
        "- No preambles or update notes\n"
        "- Summary must use 'I' statements and first-person perspective\n"
        "- Output is a single concise paragraph, 4-6 sentences\n\n"
        "**Output Format:**\n"
        f"A single paragraph, 4-6 sentences, in the first person as {agent['name']}. Do not include any introductory or explanatory text—start directly with the summary content."
    )
    
    user_message = (
        f"Update {agent['name']}'s memory summary with the new conversation.\n\n"
        f"EXISTING SUMMARY:\n{existing_summary}\n\n"
        f"NEW CONVERSATION:\n{formatted_messages}\n\n"
        "Provide an updated summary that integrates the new information while preserving relevant earlier context."
    )
    
    return {"system_message": system_message, "user_message": user_message}


def format_long_memory_section(agent: AgentState) -> str:
    """
    Format the long-term memory section for inclusion in prompts.
    Returns empty string if long_mem is empty, otherwise returns formatted section.
    """
    if not agent.get('long_mem') or len(agent['long_mem']) == 0:
        logger.debug(f"No long-term memory for agent: {agent['name']}")
        return ""
    
    # Get the latest summary
    latest_summary = agent['long_mem'][-1]
    logger.debug(f"Including long-term memory for agent: {agent['name']} (total summaries: {len(agent['long_mem'])})")
    
    return (
        f"Long term memory (summary):\n"
        f"{latest_summary}\n\n"
    )


def generate_debate_system_prompt(agent: AgentState) -> str:
    # transcript_slice will work as the conversation history/ short term memory
    # Agent should have some sort of function to do long term memory summarization

    keypoints_desc = ""
    if agent.get('keypoints'):
        keypoints_desc = "Key beliefs:\n" + "\n".join(f"- {kp}" for kp in agent['keypoints']) + "\n\n"

    return (
        f"You are {agent['name']} in a small group discussion.\n"
        f"Your role: {agent['role_desc']}.\n\n"
        f"{keypoints_desc}"
        "Speak naturally and conversationally, as if you are interacting live with a group of peers.\n\n"
        "- Use short, casual sentences.\n"
        "- Let your tone be informal and relatable—these are your friends or colleagues.\n"
        "- React in a way that fits your personality: you may respond directly, shift topics, share a quick story, ask a question, or go off on a brief tangent.\n"
        "- Show genuine opinions and feelings; it's fine to express emotions or preferences.\n"
        "- If you don't know something, feel free to admit it or steer the conversation elsewhere.\n"
        "- Never refer to yourself as an AI or mention any instructions or rules.\n"
        "- Write ONLY your spoken turn—do not include descriptions, inner thoughts, or additional explanation.\n\n"
        "- Engage directly with what others argue — if they make a compelling point, "
        "acknowledge it honestly; if you disagree, push back with your reasoning.\n"
        "Response format:\n"
        "Write only what you would say out loud in your reply, as a single, natural-sounding statement or brief exchange.\n\n"
        "Example:\n\n"
        "**Input:** How was your weekend?\n\n"
        "**Output:** Pretty good, actually! I finally tried that new taco place down the street. Have you been?\n\n"
        "**(In real situations, responses should vary in length between a short sentence and a few lines, depending on context. Insert realistic, personality-driven phrasing as needed.)**\n\n"
        "---\n\n"
        "**Reminder:** Your main objective is to sound like a genuine, casual person in a live peer conversation—avoid any robotic or formal language, and do not reference guidelines. Respond freely and naturally in each turn.\n\n"
        f"Write only what you say in this turn as {agent['name']}, nothing else."
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
    
    # get long-term memory section
    long_memory_section = format_long_memory_section(agent)


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
            f"{long_memory_section}"
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
    
    if agent.get('keypoints'):
        prompt += "Key beliefs:\n" + "\n".join(f"- {kp}" for kp in agent['keypoints']) + "\n\n"

    prompt += """VOTING GUIDELINES:
    - Review the debate that has taken place
    - Consider your character's values and perspective
    - Make a decision that honestly reflects your current view after the debate
    — your position may have evolved from where you started
    - Provide a brief justification for your vote (1-2 sentences)
    
    Output format:
    VOTE: [your choice]
    REASON: [brief justification]
    """
    return prompt


def generate_voting_user_prompt(agent: AgentState, voting_question: str, options: List[str], prior_vote: dict = None) -> str:
    # Include debate summary from long_mem for now, perhaps entertain other approaches later
    recent_msgs = agent['short_mem']

    debate_summary = "\n".join([
        f"- [{getattr(m, 'name', 'Unknown')}]: {getattr(m, 'content', str(m))}"
        for m in recent_msgs
    ])

    # get long-term memory section for full context
    long_memory_section = format_long_memory_section(agent)

    # remind the agent of their previous vote so they can reflect on whether the debate changed their view
    prior_vote_section = ""
    if prior_vote:
        prior_vote_section = (
            f"\nIn your previous vote you reasoned: {prior_vote['reason']}\n"
            f"Reflect honestly on whether the discussion has shifted your perspective.\n"
            f"You are not bound to your previous position.\n"
        )

    if debate_summary.strip():
        context_section = f"Recent conversation summary:\n{debate_summary}"
    else:
        context_section = "No debate has taken place yet. Cast your vote based solely on your persona's prior beliefs and values."
    
    prompt = f"""Question: {voting_question}

    Available options:
    {chr(10).join([f"- {opt}" for opt in options])}

    Long term memory:
    {long_memory_section}

    {context_section}
    
    {prior_vote_section}
    Based on the discussion cast your vote."""

    return prompt