"""
RAG pipeline logger.

Writes one JSON file per pipeline stage into {subsession_path}/rag/
"""
import json
import logging
import os
from typing import List

from rag.state import GeneratedPersona, SearchResult, Viewpoint

logger = logging.getLogger(__name__)


class RagRunLogger:
    """Writes structured JSON logs for each RAG pipeline stage."""

    def __init__(self, subsession_path: str) -> None:
        """
        Initialise the logger and create the rag/ subfolder.

        Args:
            subsession_path: Path to the current session's subsession folder.
        """
        self._dir = os.path.join(subsession_path, "rag")
        os.makedirs(self._dir, exist_ok=True)
        self._query_iterations: list = []
        self._search_iterations: list = []
        self._all_viewpoints_raw: List[Viewpoint] = []
        self._all_raw_errors: list = []

    def _write(self, filename: str, data: dict) -> None:
        """Map data to a JSON file inside the rag/ folder."""
        path = os.path.join(self._dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("[rag_logger] saved %s", path)

    # Stage 1 — Query planner
    def log_queries(self, iteration: int, queries: List[str]) -> None:
        """
        Append this iteration's queries and overwrite 01_queries.json. Called once per search iteration
        """
        self._query_iterations.append({"iteration": iteration, "queries": queries})
        self._write("01_queries.json", {"iterations": self._query_iterations})

    # Stage 2 — Search results
    def log_search_results(self, iteration: int, results: List[SearchResult]) -> None:
        """
        Append this iteration's search results and overwrite 02_search_results.json.
        """
        self._search_iterations.append({"iteration": iteration, "total": len(results), "results": list(results)})
        self._write("02_search_results.json", {"iterations": self._search_iterations})

    # Stage 3 — Raw viewpoints (post-extraction)
    def log_viewpoints_raw(self, viewpoints: List[Viewpoint], errors: List[str]) -> None:
        """
        Accumulate extracted viewpoints and errors across iterations and overwrite 03_viewpoints_raw.json.
        """
        self._all_viewpoints_raw.extend(viewpoints)
        self._all_raw_errors.extend(errors)
        self._write(
            "03_viewpoints_raw.json",
            {
                "total": len(self._all_viewpoints_raw),
                "errors": list(self._all_raw_errors),
                "viewpoints": list(self._all_viewpoints_raw),
            },
        )

    # Stage 4 — Deduplicated viewpoints
    def log_viewpoints_deduped(
        self, before: int, after: int, viewpoints: List[Viewpoint]
    ) -> None:
        """Write 04_viewpoints_deduped.json with before/after counts."""
        self._write(
            "04_viewpoints_deduped.json",
            {"before": before, "after": after, "viewpoints": list(viewpoints)},
        )

    # Stage 5 — Stance-selected viewpoints
    def log_viewpoints_selected(self, viewpoints: List[Viewpoint]) -> None:
        """Write 05_viewpoints_selected.json with per-stance breakdown."""
        by_stance: dict[str, int] = {}
        for vp in viewpoints:
            stance = vp.get("stance", "unknown")
            by_stance[stance] = by_stance.get(stance, 0) + 1

        self._write(
            "05_viewpoints_selected.json",
            {"total": len(viewpoints), "by_stance": by_stance, "viewpoints": list(viewpoints)},
        )

    # Stage 6 — Enriched viewpoints (includes _enrichment_raw)
    def log_viewpoints_enriched(self, viewpoints: List[Viewpoint]) -> None:
        """
        Write 06_viewpoints_enriched.json.
        """
        self._write(
            "06_viewpoints_enriched.json",
            {"total": len(viewpoints), "viewpoints": list(viewpoints)},
        )

    # Stage 7 — Final personas
    def log_personas(self, personas: List[GeneratedPersona]) -> None:
        """Write 07_personas.json"""
        self._write(
            "07_personas.json",
            {"total": len(personas), "personas": list(personas)},
        )
