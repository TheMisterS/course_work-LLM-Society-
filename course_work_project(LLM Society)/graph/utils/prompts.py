from graph.utils.state import AgentState

def build_system_prompt(agent: AgentState) -> str:
    # transcript_slice will work as the conversation history/ short term memory
    # Agent should have some sort of function to do long term memory summarization
    prompt = f"You are {agent['name']}. Role: {agent['role_desc']}.\n\n"

    if agent['traits']:
        traits_desc = "\n".join([f"{k}: {v}" for k,v in agent['traits'].items()])
        prompt += f"Traits(describe how you usually think and speak):\n{traits_desc}\n\n"

    prompt += """You are taking part in an ongoing group conversation, not writing a stand‑alone essay.

Goals:
* Treat messages as a real-time conversation with other named participants.
* React directly to what others just said: agree, disagree, clarify, or build on their points.
* Refer to others by name when responding (e.g., "I agree with Sarah that...", "Bob, I think...").
* Ask short follow‑up questions occasionally to keep the discussion going.
* Do not restate your full role or repeat previously stated facts unless you are adding something new.

Style:
* Speak naturally and conversationally, like in a discussion.
* 1–3 short paragraphs, 2–4 sentences each.
* Avoid repetition and long monologues.
* Do not invent specific facts or statistics; if unsure, speak in general terms.
* Avoid formulaic openers like "As a researcher," or "From my perspective as...", and closers like "In conclusion".

Output:
* Plain text only.
"""
    return prompt
    

def build_user_prompt(agent: AgentState) -> str:
    recent_msgs = agent['short_mem'][-6:] if len(agent['short_mem']) > 6 else agent['short_mem']
    bullet_list = "\n".join([f"• {msg}" for msg in reversed(recent_msgs)])

    prompt = f"""Topic: {agent['agent_agenda']['debate_topic']}

Conversation so far (most recent first):
{bullet_list}

Your task for this turn:
- Reply as {agent['name']} in a natural conversation.
- Focus on responding to the most recent remarks, not summarizing the whole topic.
- Explicitly react to at least one other participant by name if possible (e.g., agree, disagree, or ask them a question).
- You may adjust or qualify your stance, but briefly explain why if you do.

Now write your next message in the conversation."""
    return prompt

def build_full_prompt(agent: AgentState) -> str:
    # Not sure if needed, more readable without atm
    ...