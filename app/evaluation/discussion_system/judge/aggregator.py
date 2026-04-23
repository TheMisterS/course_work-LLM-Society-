"""
Metrics aggregation and output formatting..
"""

import csv
import json
from pathlib import Path
from datetime import datetime

from models import AggregatedMetrics, SubsessionMetrics


def save_as_csv(metrics: AggregatedMetrics, output_path: Path) -> None:
    """
    Save aggregated metrics to a CSV file.
    
    CSV columns (conversation-level):
    - session, subsession, debate_topic, num_agents, num_messages
    - argument_coherence, identity_consistency, responsiveness
    - consensus_alignment, conflict_avoidance, average
    - reasoning columns for each criterion
    
    Args:
        metrics: Aggregated metrics to save
        output_path: Path to output CSV file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = [
        "session",
        "subsession", 
        "debate_topic",
        "num_agents",
        "num_messages",
        "argument_coherence",
        "identity_consistency",
        "responsiveness",
        "consensus_alignment",
        "conflict_avoidance",
        "average",
        "argument_coherence_reasoning",
        "identity_consistency_reasoning",
        "responsiveness_reasoning",
        "consensus_alignment_reasoning",
        "conflict_avoidance_reasoning",
    ]
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for subsession in metrics.subsessions:
            writer.writerow({
                "session": subsession.session_name,
                "subsession": subsession.subsession_name,
                "debate_topic": subsession.debate_topic,
                "num_agents": subsession.num_agents,
                "num_messages": subsession.num_messages,
                "argument_coherence": subsession.scores.argument_coherence,
                "identity_consistency": subsession.scores.identity_consistency,
                "responsiveness": subsession.scores.responsiveness,
                "consensus_alignment": subsession.scores.consensus_alignment,
                "conflict_avoidance": subsession.scores.conflict_avoidance,
                "average": subsession.average_score,
                "argument_coherence_reasoning": subsession.scores.argument_coherence_reasoning,
                "identity_consistency_reasoning": subsession.scores.identity_consistency_reasoning,
                "responsiveness_reasoning": subsession.scores.responsiveness_reasoning,
                "consensus_alignment_reasoning": subsession.scores.consensus_alignment_reasoning,
                "conflict_avoidance_reasoning": subsession.scores.conflict_avoidance_reasoning,
            })
    
    print(f"Saved CSV to: {output_path}")


def save_as_json(metrics: AggregatedMetrics, output_path: Path) -> None:
    """
    Save aggregated metrics to a JSON file.
    
    Args:
        metrics: Aggregated metrics to save
        output_path: Path to output JSON file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to dict for JSON serialization
    data = {
        "generated_at": datetime.now().isoformat(),
        "total_subsessions": len(metrics.subsessions),
        "subsessions": []
    }
    
    for subsession in metrics.subsessions:
        subsession_data = {
            "session": subsession.session_name,
            "subsession": subsession.subsession_name,
            "debate_topic": subsession.debate_topic,
            "num_agents": subsession.num_agents,
            "num_messages": subsession.num_messages,
            "average_score": subsession.average_score,
            "scores": {
                "argument_coherence": {
                    "score": subsession.scores.argument_coherence,
                    "reasoning": subsession.scores.argument_coherence_reasoning,
                },
                "identity_consistency": {
                    "score": subsession.scores.identity_consistency,
                    "reasoning": subsession.scores.identity_consistency_reasoning,
                },
                "responsiveness": {
                    "score": subsession.scores.responsiveness,
                    "reasoning": subsession.scores.responsiveness_reasoning,
                },
                "consensus_alignment": {
                    "score": subsession.scores.consensus_alignment,
                    "reasoning": subsession.scores.consensus_alignment_reasoning,
                },
                "conflict_avoidance": {
                    "score": subsession.scores.conflict_avoidance,
                    "reasoning": subsession.scores.conflict_avoidance_reasoning,
                },
            }
        }
        
        data["subsessions"].append(subsession_data)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved JSON to: {output_path}")


def save_metrics(
    metrics: AggregatedMetrics, 
    output_path: Path, 
    format: str = "csv"
) -> None:
    """
    Save metrics in the specified format.
    
    Args:
        metrics: Aggregated metrics to save
        output_path: Path to output file
        format: Output format ("csv" or "json")
    """
    if format.lower() == "json":
        # Ensure .json extension
        if output_path.suffix != ".json":
            output_path = output_path.with_suffix(".json")
        save_as_json(metrics, output_path)
    else:
        # Default to CSV
        if output_path.suffix != ".csv":
            output_path = output_path.with_suffix(".csv")
        save_as_csv(metrics, output_path)


def generate_output_filename(format: str = "csv") -> str:
    """
    Generate a timestamped output filename.
    
    Args:
        format: Output format ("csv" or "json")
        
    Returns:
        Filename with timestamp
    """
    timestamp = datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
    extension = "json" if format.lower() == "json" else "csv"
    return f"judge_results_{timestamp}.{extension}"


def print_summary(metrics: AggregatedMetrics) -> None:
    """
    Print a summary of the evaluation results to console.
    
    Args:
        metrics: Aggregated metrics to summarize
    """
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    
    print(f"Subsessions evaluated: {len(metrics.subsessions)}")
    
    if metrics.subsessions:
        # Calculate overall averages per criterion
        all_scores = {
            "argument_coherence": [],
            "identity_consistency": [],
            "responsiveness": [],
            "consensus_alignment": [],
            "conflict_avoidance": [],
        }
        
        for subsession in metrics.subsessions:
            all_scores["argument_coherence"].append(subsession.scores.argument_coherence)
            all_scores["identity_consistency"].append(subsession.scores.identity_consistency)
            all_scores["responsiveness"].append(subsession.scores.responsiveness)
            all_scores["consensus_alignment"].append(subsession.scores.consensus_alignment)
            all_scores["conflict_avoidance"].append(subsession.scores.conflict_avoidance)
        
        print("\nAverages per criterion:")
        for criterion, scores in all_scores.items():
            avg = sum(scores) / len(scores) if scores else 0
            print(f"  {criterion}: {avg:.2f}")
        
        overall_avg = sum(s.average_score for s in metrics.subsessions) / len(metrics.subsessions)
        print(f"\nOverall average: {overall_avg:.2f}")
    
    print("=" * 60 + "\n")
