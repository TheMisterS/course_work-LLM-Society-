from graph.utils.state import AgentState

def build_system_prompt(agent: AgentState) -> str:
    # transcript_slice will work as the conversation history/ short term memory
    # Agent should have some sort of function to do long term memory summarization
    prompt = f"You are {agent['name']}. Role: {agent['role_desc']}.\n\n"

    if agent['traits']:
        traits_desc = "\n".join([f"{k}: {v}" for k,v in agent['traits'].items()])
        prompt += f"Traits:\n{traits_desc}\n\n"

    prompt += """Goals: 
            *Do not restate your role or repeat previously stated facts unless adding something new.
            *Speak naturally and concisely (2–5 sentences)
            *Avoid repetition.
            *Do not invent facts.
            *Avoid formulaic openers like "As a researcher," or "As a supervisor," and closers like "In conclusion".

            Style: Casual conversation.
            Output: plain text only.

            """
    return prompt
    

def build_user_prompt(agent: AgentState) -> str:
    recent_msgs = agent['short_mem'][-6:] if len(agent['short_mem']) > 6 else agent['short_mem']
    bullet_list = "\n".join([f"• {msg}" for msg in reversed(recent_msgs)])

    prompt = f"""Topic: {agent['agent_agenda']['debate_topic']}

    Your memory: (most recent first):
    {bullet_list}

    Your task for this turn:
    - Respond as {agent['name']}
    - If you change or qualify your stance, state why briefly.
    - Optional: prefix crisp claims with "Fact:".

    Now respond."""
    return prompt

def build_full_prompt(agent: AgentState) -> str:
    # Not sure if needed, more readable without atm
    ...