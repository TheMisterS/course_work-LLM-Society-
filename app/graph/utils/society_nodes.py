
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

class SocietyNodes:

    def supervisor(self, state: GraphState):
        logger.debug("***IN SUPERVISOR NODE***")

        supervisor_notes = []
        
        current_round = state["round"] + 1
        logger.debug(f"Incrementing round from {state['round']} to {current_round}")
        
        # Check if we should transition to voting phase
        if current_round > DEBATE_ROUND_COUNT and state["phase"] == "debate":
            logger.debug("Debate rounds complete. Transitioning to vote phase.")
            supervisor_notes.append(f"Debate complete after {current_round - 1} rounds. Moving to voting phase.")
            return {"supervisor_notes": supervisor_notes, "phase": "vote", "round": current_round}

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
        print(response)

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
            if len(agent["short_mem"]) > MEMORY_WINDOW_SIZE: # limit short term memory (WIP, adjust via constant later)
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



    #Route after agent interaction, either end or to tick to increment round
    def router(self, state: GraphState) -> str:
        logger.debug("***IN ROUTER NODE***")
        ...

    def vote(self, state: GraphState) -> Dict[str, Any]:
        # Voting node is designed so that each agent votes, thus all of the agents are invoked here
        logger.debug("***IN VOTE NODE***")
        
        voting_options = state["voting_options"]
        voting_question = state["voting_question"]
        votes = {}
        
        for agent_name, agent_state in state["agents"].items():
            
            current_sys_prompt = generate_voting_system_prompt(agent_state)
            current_user_prompt = generate_voting_user_prompt(agent_state, voting_question, voting_options)
            model = state["models"][MODEL_USED_FOR_VOTING]
            
            chain = create_agent_chain(model)
            
            response = chain.invoke({
                "system_message": current_sys_prompt,
                "user_message": current_user_prompt
            })
            
            votes[agent_name] = response
            
            print(response)
            print("----------------------------------------------------\n")
        
        logger.debug("Vote phase complete.")
        return {"votes": votes, "phase": "END"}
            
            
            
            
            