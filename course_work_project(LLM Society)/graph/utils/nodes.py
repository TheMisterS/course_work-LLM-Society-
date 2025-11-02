
from typing import Any, Dict
from graph.utils.state import GraphState, Msg
from graph.utils.prompts import build_system_prompt, build_user_prompt
from configs.simulation_config import MODEL_USED_FOR_AGENTS, DEBATE_ROUND_COUNT
from graph.chain_factory import create_agent_chain

import logging
logger = logging.getLogger(__name__)

class Nodes:


    def supervisor(self, state: GraphState):
        logger.debug("***IN SUPERVISOR NODE***")

        supervisor_notes = [None]

        speakers_length = len(state["agents"])

        #retrieve next speaker (might need to randomize each phase)
        speaker = list(state["agents"].keys())[state["round"] % speakers_length]
        logger.debug(f"Supervisor selected next speaker: {speaker}")

        supervisor_notes = supervisor_notes +[f"Supervisor selects: {speaker} | phase={state['phase']} | round={state['round']}"]
        #(WIP) State shifting skeleton

        # if state["round"] == 5 and state["phase"] == "debate":
        #     phase = "role_shift"
        #     notes += ["Switching to role_shift."]
        # elif state["round"] == 7 and state["phase"] in ("debate","role_shift"):
        #     phase = "vote"
        #     notes += ["Switching to vote."]
        # else:
        #     phase = state["phase"]
        #return {"supervisor_notes": notes, "next_speaker": speaker, "phase": phase}

        return {"supervisor_notes": supervisor_notes, "next_speaker": speaker}


    def agent_speak(self, state: GraphState):
        logger.debug("***IN AGENT SPEAK NODE***")
         # Retrieve the agent state

        next_speaker = state.get("next_speaker", None)
        if not next_speaker:
            logger.error("No next speaker defined in state.")

        agent = state["agents"][next_speaker]

        current_sys_prompt = build_system_prompt(agent)
        current_user_prompt = build_user_prompt(agent)
        model = state["models"][MODEL_USED_FOR_AGENTS]

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
            if len(agent["short_mem"]) > 5: # limit short term memory (WIP, adjust via constant later)
                agent["short_mem"].pop(0)
            agent["short_mem"].append(last_message)

        return {"agents": state["agents"]}


    #increments round and goes back to supervisor
    def tick(self, state: GraphState) -> Dict[str, Any]:
        logger.debug("***IN TICK NODE***")
        new_round = state["round"] + 1

        if new_round >= DEBATE_ROUND_COUNT and state["phase"] == "debate":
            return {"round": new_round, "phase": "END"}

        return {"round": state["round"] + 1}
        ...

    #Add conditional edge after this node
    # def route_after_supervisor(state: graph_state) -> str:
    #     if state["phase"] == "role_shift":
    #         return "role_shift"
    #     if state["phase"] == "vote":
    #         return "vote"
    #     return "agent_speak"

    #Route after agent interaction, either end or to tick to increment round
    def router(self, state: GraphState) -> str:
        logger.debug("***IN ROUTER NODE***")
        ...

    #WIP for later
    def vote(self, state: GraphState) -> Dict[str, Any]:
        logger.debug("***IN VOTE NODE***")
        ...