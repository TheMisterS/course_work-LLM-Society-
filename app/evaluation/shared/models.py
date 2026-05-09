from dataclasses import dataclass, field


@dataclass
class SubsessionResult:
    session_name: str
    subsession_name: str
    debate_topic: str
    plane: str  # "rag" | "debate" | "votes"
    metrics: dict


@dataclass
class AggregatedResults:
    plane: str # "rag" | "debate" | "votes"
    subsessions: list = field(default_factory=list)

    def add(self, result: SubsessionResult) -> None:
        self.subsessions.append(result)

    def to_dict(self) -> dict:
        return {
            "plane": self.plane,
            "total_subsessions": len(self.subsessions),
            "subsessions": [
                {
                    "session": r.session_name,
                    "subsession": r.subsession_name,
                    "debate_topic": r.debate_topic,
                    "metrics": r.metrics,
                }
                for r in self.subsessions
            ],
        }
