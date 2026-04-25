
from typing import Any, Dict
from graph.utils.state import GraphState, Msg
from graph.utils.prompts import (
    generate_debate_system_prompt, 
    generate_debate_user_prompt, 
    generate_voting_system_prompt, 
    generate_voting_user_prompt,
    generate_initial_memory_summary_prompt,
    generate_update_memory_summary_prompt
)
from configs.simulation_config import (
    MEMORY_WINDOW_SIZE, 
    MODEL_USED_FOR_DEBATE, 
    DEBATE_ROUND_COUNT, 
    MODEL_USED_FOR_VOTING,
    LONG_MEMORY_UPDATE_INTERVAL,
    LONG_MEMORY_THRESHOLD_PERCENT,
    MODEL_USED_FOR_SUMMARIZATION
)
from graph.chain_factory import create_agent_chain

import logging
logger = logging.getLogger(__name__)


def _parse_vote_response(response: str) -> tuple[str, str]:
    """parse the VOTE and REASON values from voting- fall back to the raw response"""
    
    vote_choice = ""
    reason = ""

    for line in response.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("VOTE:"):
            vote_choice = stripped[len("VOTE:"):].strip()
        elif stripped.upper().startswith("REASON:"):
            reason = stripped[len("REASON:"):].strip()

    # if parsing failed, store the raw response
    if not vote_choice:
        vote_choice = response.strip()

    return vote_choice, reason


class Nodes:

    def supervisor(self, state: GraphState):
        logger.debug("***IN SUPERVISOR NODE***")

        supervisor_notes = []
        
        current_round = state["round"] + 1
        logger.debug(f"Incrementing round from {state['round']} to {current_round}")
        
        votes = state.get("votes", {})

        # initial vote before any agent speaks
        if current_round == 1 and "initial" not in votes:
            logger.debug("Triggering initial vote before debate starts.")
            supervisor_notes.append("Triggering initial vote (round 0).")
            return {"supervisor_notes": supervisor_notes, "phase": "vote", "round": current_round, "current_vote_label": "initial"}

        # mid-debate vote at the halfway point
        if current_round == DEBATE_ROUND_COUNT // 2 and "mid" not in votes:
            logger.debug(f"Triggering mid-debate vote at round {current_round}.")
            supervisor_notes.append(f"Triggering mid-debate vote at round {current_round}.")
            return {"supervisor_notes": supervisor_notes, "phase": "vote", "round": current_round, "current_vote_label": "mid"}

        # final vote after all debate rounds
        if current_round > DEBATE_ROUND_COUNT and "final" not in votes:
            logger.debug("Debate rounds complete. Transitioning to final vote.")
            supervisor_notes.append(f"Debate complete after {current_round - 1} rounds. Moving to final vote.")
            return {"supervisor_notes": supervisor_notes, "phase": "vote", "round": current_round, "current_vote_label": "final"}

        speakers_length = len(state["agents"])

        #retrieve next speaker (might need to randomize each phase)
        speaker = list(state["agents"].keys())[(current_round - 1) % speakers_length]
        logger.debug(f"Supervisor selected next speaker: {speaker}")

        supervisor_notes = supervisor_notes + [f"Supervisor selects: {speaker} | phase={state['phase']} | round={current_round}"]
        return {"supervisor_notes": supervisor_notes, "next_speaker": speaker, "round": current_round}


    def agent_speak(self, state: GraphState):
        logger.debug("***IN AGENT SPEAK NODE***")
         # Retrieve the agent state

        next_speaker = state.get("next_speaker", None)
        if not next_speaker:
            logger.error("No next speaker defined in state.")

        agent = state["agents"][next_speaker]

        current_sys_prompt = generate_debate_system_prompt(agent)
        current_user_prompt = generate_debate_user_prompt(agent)
        model = state["models"][MODEL_USED_FOR_DEBATE]

        chain = create_agent_chain(model)
        response = chain.invoke({
            "system_message": current_sys_prompt,
            "user_message": current_user_prompt
        })

        message = Msg(
            role="agent",
            name=next_speaker,
            content=response
        )

        return {"messages": [message], "next_speaker": next_speaker}
        

    def update_short_memory(self, state: GraphState):
        logger.debug("***IN UPDATE SHORT MEMORY NODE***")
         # Update the agent's memories
        last_message = state["messages"][-1]

        # not good practise to update state directly, but left as is for PoC

        for agent in state["agents"].values():
            if len(agent["short_mem"]) >= MEMORY_WINDOW_SIZE: # limit short term memory (WIP, adjust via constant later)
                agent["short_mem"].pop(0)
            agent["short_mem"].append(last_message)

        return {"agents": state["agents"]}
    
    
    def update_long_memory(self, state: GraphState):
        logger.debug("***IN UPDATE LONG MEMORY NODE***")
        
        current_round = state["round"]
        
        # check if it's time to update long memory based on interval
        if current_round % LONG_MEMORY_UPDATE_INTERVAL != 0:
            logger.debug(f"Skipping long memory update: round {current_round} not at interval {LONG_MEMORY_UPDATE_INTERVAL}")
            return {"agents": state["agents"]}
        
        logger.debug(f"Long memory update triggered at round {current_round}")
        
        # calculate threshold for short memory
        threshold = int(MEMORY_WINDOW_SIZE * LONG_MEMORY_THRESHOLD_PERCENT)
        logger.debug(f"Short memory threshold: {threshold} (MEMORY_WINDOW_SIZE={MEMORY_WINDOW_SIZE}, THRESHOLD_PERCENT={LONG_MEMORY_THRESHOLD_PERCENT})")
        
        model = state["models"][MODEL_USED_FOR_SUMMARIZATION]
        chain = create_agent_chain(model)
        
        for agent_name, agent in state["agents"].items():
            short_mem_length = len(agent["short_mem"])
            
            # check if short memory meets threshold
            if short_mem_length < threshold:
                logger.debug(f"Agent '{agent_name}': short_mem ({short_mem_length}) below threshold ({threshold}), skipping")
                continue
            
            logger.debug(f"Agent '{agent_name}': short_mem ({short_mem_length}) meets threshold ({threshold}), processing")
            
            # Get messages to summarize (all current short_mem)
            messages_to_summarize = agent["short_mem"]
            
            # Check if this is initial summary or update
            if not agent["long_mem"] or len(agent["long_mem"]) == 0:
                logger.debug(f"Agent '{agent_name}': Creating initial long-term memory summary")
                prompt_data = generate_initial_memory_summary_prompt(agent, messages_to_summarize)
            else:
                # Get the latest existing summary for update
                existing_summary = agent["long_mem"][-1]
                logger.debug(f"Agent '{agent_name}': Updating existing summary (total summaries: {len(agent['long_mem'])})")
                prompt_data = generate_update_memory_summary_prompt(agent, existing_summary, messages_to_summarize)
            
            # Invoke LLM for summarization
            try:
                summary = chain.invoke({
                    "system_message": prompt_data["system_message"],
                    "user_message": prompt_data["user_message"]
                })
                
                # Append new summary to long_mem (store all summaries)
                agent["long_mem"].append(summary)
                logger.debug(f"Agent '{agent_name}': Successfully stored summary (total summaries: {len(agent['long_mem'])})")
                logger.debug(f"Agent '{agent_name}': Summary content: {summary[:100]}..." if len(summary) > 100 else f"Agent '{agent_name}': Summary content: {summary}")
                
            except Exception as e:
                logger.error(f"Agent '{agent_name}': Failed to generate summary: {e}")
                continue
        
        return {"agents": state["agents"]}


    def vote(self, state: GraphState) -> Dict[str, Any]:
        # voting node invokes every agent so they all cast their vote in one pass
        logger.debug("***IN VOTE NODE***")

        vote_label = state.get("current_vote_label", "final")
        voting_options = state["voting_options"]
        voting_question = state["voting_question"]
        all_votes = dict(state.get("votes", {}))
        round_votes = {}

        for agent_name, agent_state in state["agents"].items():
            # for mid/final votes, pass back what this agent voted previously so they can reflect on it
            prior_vote = None
            if vote_label == "mid" and "initial" in all_votes:
                prior_vote = all_votes["initial"].get(agent_name)
            elif vote_label == "final" and "mid" in all_votes:
                prior_vote = all_votes["mid"].get(agent_name)
            elif vote_label == "final" and "initial" in all_votes:
                prior_vote = all_votes["initial"].get(agent_name)

            current_sys_prompt = generate_voting_system_prompt(agent_state)
            current_user_prompt = generate_voting_user_prompt(agent_state, voting_question, voting_options, prior_vote)
            model = state["models"][MODEL_USED_FOR_VOTING]

            chain = create_agent_chain(model)

            response = chain.invoke({
                "system_message": current_sys_prompt,
                "user_message": current_user_prompt
            })

            vote_choice, reason = _parse_vote_response(response)
            round_votes[agent_name] = {"vote": vote_choice, "reason": reason}

        # merge this round's votes into the existing votes dict under the correct label
        all_votes[vote_label] = round_votes

        logger.debug(f"Vote phase '{vote_label}' complete.")
        return {"votes": all_votes, "phase": "debate", "current_vote_label": None}
            
            
            
            
            