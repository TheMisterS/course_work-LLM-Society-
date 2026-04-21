"""
Pydantic data models for the Judge system.
Evaluates the whole conversation, not per-agent.
"""

from typing import Optional
from pydantic import BaseModel, Field


# =============================================================================
# Input Models (parsed from state JSON)
# =============================================================================

class Message(BaseModel):
    """A single message in the conversation."""
    role: str
    name: str
    content: str


class AgentData(BaseModel):
    """Agent information extracted from state."""
    name: str
    role_desc: str
    traits: dict[str, str] = Field(default_factory=dict)  # Dynamic key-value pairs
    long_mem: list[str] = Field(default_factory=list)
    short_mem: list[Message] = Field(default_factory=list)
    agent_agenda: dict = Field(default_factory=dict)


class DebateState(BaseModel):
    """Parsed debate state from JSON file."""
    messages: list[Message]
    agents: dict[str, AgentData]
    votes: dict[str, str]
    voting_options: list[str]
    voting_question: str
    agenda: dict
    round: int
    phase: str
    
    @property
    def debate_topic(self) -> str:
        """Extract debate topic from agenda."""
        return self.agenda.get("debate_topic", "Unknown topic")
    
    def get_agent_messages(self, agent_name: str) -> list[Message]:
        """Get all messages from a specific agent."""
        return [m for m in self.messages if m.name == agent_name]
    
    def get_agent_vote(self, agent_name: str) -> Optional[str]:
        """Get the vote of a specific agent."""
        return self.votes.get(agent_name)


# =============================================================================
# Output Models (conversation-level evaluation)
# =============================================================================

class CriterionResult(BaseModel):
    """Result for a single criterion evaluation."""
    criterion: str
    score: int = Field(ge=1, le=5)
    reasoning: str = ""


class ConversationScores(BaseModel):
    """Scores for each evaluation criterion (1-5 scale) for the whole conversation."""
    argument_coherence: int = Field(ge=1, le=5, description="Logical consistency, reasoning flow")
    identity_consistency: int = Field(ge=1, le=5, description="Alignment with assigned traits")
    responsiveness: int = Field(ge=1, le=5, description="Direct engagement with others")
    consensus_alignment: int = Field(ge=1, le=5, description="Does the vote reflect discussion?")
    conflict_avoidance: int = Field(ge=1, le=5, description="How much agents avoid committing or avoid conflict")
    
    # Reasoning for each criterion
    argument_coherence_reasoning: str = ""
    identity_consistency_reasoning: str = ""
    responsiveness_reasoning: str = ""
    consensus_alignment_reasoning: str = ""
    conflict_avoidance_reasoning: str = ""
    
    @property
    def average(self) -> float:
        """Calculate average score across all criteria."""
        return round(
            (self.argument_coherence + 
             self.identity_consistency + 
             self.responsiveness + 
             self.consensus_alignment + 
             self.conflict_avoidance) / 5, 
            2
        )


class SubsessionMetrics(BaseModel):
    """Metrics for a single subsession evaluation (conversation-level)."""
    session_name: str
    subsession_name: str
    debate_topic: str
    num_agents: int
    num_messages: int
    scores: ConversationScores
    
    @property
    def average_score(self) -> float:
        """Get average score."""
        return self.scores.average


class AggregatedMetrics(BaseModel):
    """Aggregated metrics across multiple subsessions."""
    subsessions: list[SubsessionMetrics] = Field(default_factory=list)
    
    def add_subsession(self, metrics: SubsessionMetrics) -> None:
        """Add subsession metrics to the aggregation."""
        self.subsessions.append(metrics)
