from graph.utils.state import AgentState

def build_system_prompt(agent: AgentState) -> str:
    # transcript_slice will work as the conversation history/ short term memory
    # Agent should have some sort of function to do long term memory summarization
    prompt = f"You are {agent['name']} engaging in a dynamic conversation with other agents. Your role is: {agent['role_desc']}.\n\n"

    if agent['traits']:
        traits_desc = "\n".join([f"{k}: {v}" for k,v in agent['traits'].items()])
        prompt += f"Traits:\n{traits_desc}\n\n"

    prompt += """CONVERSATION GUIDELINES:
            - Stay true to your character throughout the entire conversation
            - Build meaningfully on what others have said rather than ignoring their contributions
            - Respond naturally to the emotional tone and context of recent messages
            - If the conversation stagnates, introduce relevant new elements that fit your character
            - Show genuine reactions to surprising or significant statements from other participants
            - Maintain consistency with your previous statements and character development
            - Speak naturally and concisely (2–5 sentences)
            - Avoid repetition.
            - If you don't know something, say so.

            INTERACTION FORMAT:
            - Other participants' messages appear as "- [Name]: message"
            - Respond with only your message content (no name prefix)
            - Reference specific points others have made when relevant
            - Ask questions or make observations that advance the conversation

            CONVERSATION FLOW:
            - Vary your response length naturally based on the situation
            - Don't always agree—express your character's genuine perspective even if it creates interesting tension
            - If conversations become repetitive, steer toward unexplored aspects of the topic
            - Build on established story elements and character relationships as they develop

            Output: plain text only.

            """
    return prompt
    

def build_user_prompt(agent: AgentState) -> str:
    recent_msgs = agent['short_mem'][-6:] if len(agent['short_mem']) > 6 else agent['short_mem']

    lines = []
    for m in reversed(recent_msgs):
        if hasattr(m, "name") and hasattr(m, "content"):
            lines.append(f"- [{getattr(m, 'name')}]: {getattr(m, 'content')}")
        else:
            lines.append(f"- {str(m)}")

    bullet_list = "\n".join(lines)


    # first message special case
    # Redacted out for now as it might mess with broader flow
    # if bullet_list == "":
    #     prompt = f"""Topic: {agent['agent_agenda']['debate_topic']}

    #     Your memory is currently empty.

    #     Your task for this turn:
    #     - Respond as {agent['name']}
    #     - Please introduce yourself
    #     - State your initial thoughts on the topic.
    #     Now respond."""
    #     return prompt
    prompt = f"""Topic: {agent['agent_agenda']['debate_topic']}

    Your memory: (most recent first):
    {bullet_list}

    Your task for this turn:
    - Respond as {agent['name']}
    - Participate in the conversation
    Now respond."""


    return prompt

def build_full_prompt(agent: AgentState) -> str:
    # Not sure if needed, more readable without atm
    ...