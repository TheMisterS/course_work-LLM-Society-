
from typing import Any, Dict
from graph.utils.state import GraphState, Msg
from graph.utils.prompts import generate_debate_system_prompt, generate_debate_user_prompt, generate_voting_system_prompt, generate_voting_user_prompt
from configs.simulation_config import MEMORY_WINDOW_SIZE, MODEL_USED_FOR_DEBATE, DEBATE_ROUND_COUNT, MODEL_USED_FOR_VOTING
from graph.chain_factory import create_agent_chain

import logging
logger = logging.getLogger(__name__)

class Nodes:


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
        

    def update_memory(self, state: GraphState):
        logger.debug("***IN UPDATE MEMORY NODE***")
         # Update the agent's memories
        last_message = state["messages"][-1]

        # not good practise to update state directly, but left as is for PoC

        for agent in state["agents"].values():
            if len(agent["short_mem"]) > MEMORY_WINDOW_SIZE: # limit short term memory (WIP, adjust via constant later)
                agent["short_mem"].pop(0)
            agent["short_mem"].append(last_message)

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
            
            
            
            
            