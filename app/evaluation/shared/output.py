import csv
import json
import logging
from pathlib import Path

from models import AggregatedResults, SubsessionResult

logger = logging.getLogger(__name__)


def save_json(results: AggregatedResults, path: Path) -> None:
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results.to_dict(), f, indent=2, ensure_ascii=False)
        
    logger.info("saved JSON to: %s", path)


def save_csv(results: AggregatedResults, path: Path) -> None:

    path.parent.mkdir(parents=True, exist_ok=True)

    # collect all metric keys across subsessions so csv has consistent columns
    all_metric_keys = []
    for r in results.subsessions:
        for key in r.metrics:
            if key not in all_metric_keys:
                all_metric_keys.append(key)

    fieldnames = ["session", "subsession", "debate_topic"] + all_metric_keys

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in results.subsessions:
            row = {
                "session": r.session_name,
                "subsession": r.subsession_name,
                "debate_topic": r.debate_topic,
            }
            
            for key in all_metric_keys:
                row[key] = r.metrics.get(key, "")
            writer.writerow(row)

    logger.info("saved CSV to: %s", path)


def print_summary(results: AggregatedResults) -> None:
    logger.info("plane: %s | subsessions evaluated: %d", results.plane.upper(), len(results.subsessions))
    for r in results.subsessions:
        logger.info("  %s / %s", r.session_name, r.subsession_name)


def save_subsession_result(result: SubsessionResult, subsession_path: Path, plane: str) -> None:
    
    eval_dir = subsession_path / "eval"
    eval_dir.mkdir(parents=True, exist_ok=True)
    out_file = eval_dir / f"{plane}_metrics.json"
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result.metrics, f, indent=2, ensure_ascii=False)
        
    logger.info("saved %s metrics to: %s", plane, out_file)
