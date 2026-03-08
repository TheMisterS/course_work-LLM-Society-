"""
ESS Round 11 – Lithuania: parse the codebook HTML + raw CSV into
``questions.json`` and ``personas.csv``.

Run from the ``app/`` directory:
    python -m data.datasets.ess_11_lt.parser
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd
from bs4 import BeautifulSoup, Tag

from data.types import Question, ResponseType
from data.datasets.ess_11_lt.field_config import (
    CODEBOOK_HTML,
    RAW_CSV,
    OUTPUT_DIR,
    PERSONA_FIELDS,
    QUESTION_FIELDS,
    SOURCE_ID_COLUMN,
)

# **********************************************************************************
# 1.  Codebook HTML parser
# **********************************************************************************

def _is_missing(label: str) -> bool:
    return label.rstrip().endswith("*")


def _parse_int(text: str) -> Optional[int]:
    text = text.strip()
    try:
        return int(text)
    except ValueError:
        return None


def _best_question_text(meta_strings: List[str], label: str) -> str:
    """Pick the most informative question text from the meta-strings.

    Parsing order:
    1.  The longest meta-string that is NOT just a CARD/READ OUT instruction.
    2.  The variable label from the first <div> after <h3>.
    """
    candidates: list[str] = []
    skip_prefixes = ("CARD", "READ OUT", "ASK ALL", "CODE", "INTERVIEWER")
    for s in meta_strings:
        stripped = s.strip()
        if not stripped:
            continue
        # skip pure instructions
        first_line = stripped.split("\n")[0].strip()
        if any(first_line.upper().startswith(p) for p in skip_prefixes):
            continue
        candidates.append(stripped)

    if candidates:
        return max(candidates, key=len)
    return label


def parse_codebook(
    html_path: Path,
    wanted: Set[str],
) -> Dict[str, Dict[str, Any]]:
    """Parse the ESS codebook HTML and return metadata for *wanted* variables.

    Returns ``{var_name: {label, question_text, values, missing_codes}}``.
    """
    with open(html_path, encoding="utf-8") as fh:
        soup = BeautifulSoup(fh, "html.parser")

    result: Dict[str, Dict[str, Any]] = {}

    for h3 in soup.find_all("h3"):
        var_name = h3.get("id")
        if var_name is None or var_name not in wanted:
            continue

        container: Tag = h3.parent  # the wrapping <div> of wanted variable

        # label
        label_div = h3.find_next_sibling("div")
        label = label_div.get_text(strip=True) if label_div else var_name

        # meta-strings (question wording, cards, instructions)
        meta_strings: list[str] = [
            div.get_text(strip=True)
            for div in container.find_all("div", class_="variable-meta-string")
        ]

        # question values
        values: Dict[int, str] = {}
        missing_codes: Set[int] = set()
        tbody = container.find("tbody", class_="codelist")
        if tbody:
            for tr in tbody.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) < 2:
                    continue
                code = _parse_int(tds[0].get_text())
                cat_label = tds[1].get_text(strip=True)
                if code is None:
                    continue
                if _is_missing(cat_label): # mark missing codes that indicate Not Applicable, Don't Know, Refused, etc.
                    missing_codes.add(code)
                else:
                    values[code] = cat_label

        question_text = _best_question_text(meta_strings, label)

        result[var_name] = {
            "label": label,
            "question_text": question_text,
            "values": values,           # code → label (non-missing)
            "missing_codes": missing_codes,
        }

    return result


# **********************************************************************************
# 2.  Derive Question objects from codebook metadata
# **********************************************************************************

def _infer_response_type(
    values: Dict[int, str],
) -> Tuple[ResponseType, Dict[int, str], Optional[int], Optional[int], Dict[int, str]]:
    """Infer response type, options dict, and scale bounds from parsed codebook answer value labels.

    Returns (response_type, options, scale_min, scale_max, scale_labels).
    """
    if not values:
        return ResponseType.NUMERIC, {}, None, None, {}

    codes = sorted(values.keys())
    lo, hi = codes[0], codes[-1]

    # 0-10 scale: endpoints have text labels, middle values are just numbers
    if lo == 0 and hi == 10 and len(codes) == 11:
        scale_labels: Dict[int, str] = {}
        for code, lbl in values.items():
            # endpoint or any label that isn't just the number itself
            if lbl != str(code):
                scale_labels[code] = lbl
        return ResponseType.SCALE, {}, 0, 10, scale_labels

    # otherwise treat as likert (every value has a text label)
    return ResponseType.LIKERT, dict(values), None, None, {}


def build_questions(
    codebook: Dict[str, Dict[str, Any]],
    question_fields: List[str],
) -> List[Question]:
    """Build a list of ``Question`` dataclass instances from parsed codebook metadata."""
    questions: list[Question] = []
    for key in question_fields:
        if key not in codebook:
            print(f"[WARN] question field '{key}' not found in codebook – skipped")
            continue
        meta = codebook[key]
        rtype, options, smin, smax, slabels = _infer_response_type(meta["values"])
        questions.append(
            Question(
                key=key,
                text=meta["question_text"],
                response_type=rtype,
                options=options,
                scale_min=smin,
                scale_max=smax,
                scale_labels=slabels,
            )
        )
    return questions


def write_questions_json(questions: List[Question], out_path: Path) -> None:
    """Serialise Question dataclass list to JSON."""
    records: list[dict] = []
    for q in questions:
        d = asdict(q)
        d["response_type"] = q.response_type.value
        d["options"] = {str(k): v for k, v in q.options.items()}
        d["scale_labels"] = {str(k): v for k, v in q.scale_labels.items()}
        records.append(d)
    out_path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(records)} questions → {out_path}")


# **********************************************************************************
# 3.  Build personas.csv from the raw data + codebook
# **********************************************************************************

def _build_decoder(
    var_meta: Optional[Dict[str, Any]],
) -> Optional[Dict[int, str]]:
    """Build a code → label mapping for ``pd.Series.map()``, or None for
    variables without coded categories (e.g. continuous age)."""
    if var_meta is None or not var_meta["values"]:
        return None
    return dict(var_meta["values"])

def write_personas_csv(
    raw_csv_path: Path,
    codebook: Dict[str, Dict[str, Any]],
    persona_fields: List[str],
    source_id_col: str,
    out_path: Path,
) -> None:
    """Read the raw ESS CSV, decode persona fields, and write personas.csv."""
    keep_cols = [source_id_col] + persona_fields
    df = pd.read_csv(raw_csv_path, usecols=keep_cols, encoding="utf-8")
    df = df.rename(columns={source_id_col: "source_id"})

    for field in persona_fields:
        meta = codebook.get(field)
        if meta is None:
            continue

        # replace missing codes with NaN
        if meta["missing_codes"]:
            df[field] = df[field].replace(
                {code: pd.NA for code in meta["missing_codes"]}
            )

        # decode coded categories to human-readable labels, missing codes will stay NaN
        decoder = _build_decoder(meta)
        if decoder:
            df[field] = df[field].map(decoder).fillna(df[field])

    # reorder columns: source_id first, then persona fields
    df = df[["source_id"] + persona_fields]
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Wrote {len(df)} personas → {out_path}")


def write_answers_csv(
    raw_csv_path: Path,
    codebook: Dict[str, Dict[str, Any]],
    question_fields: List[str],
    source_id_col: str,
    out_path: Path,
) -> None:
    """Extract each respondent's raw coded answers to the question fields.

    Values are kept as raw survey codes (int) so downstream code can
    compare, decode, or aggregate however it needs.
    Missing / sentinel codes are replaced with NaN.
    """
    keep_cols = [source_id_col] + question_fields
    df = pd.read_csv(raw_csv_path, usecols=keep_cols, encoding="utf-8")
    df = df.rename(columns={source_id_col: "source_id"})

    for field in question_fields:
        meta = codebook.get(field)
        if meta is None:
            continue
        if meta["missing_codes"]:
            df[field] = df[field].replace(
                {code: pd.NA for code in meta["missing_codes"]}
            )

    df = df[["source_id"] + question_fields]
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Wrote {len(df)} answer rows → {out_path}")


# **********************************************************************************
# 4.  Main entry-point
# **********************************************************************************

def main() -> None:
    wanted = set(PERSONA_FIELDS) | set(QUESTION_FIELDS)
    print(f"Parsing codebook for {len(wanted)} variables …")
    codebook = parse_codebook(CODEBOOK_HTML, wanted)
    print(f"  → found {len(codebook)} variable definitions")

    missing = wanted - set(codebook)
    if missing:
        print(f"  [WARN] variables not found in codebook: {sorted(missing)}")

    # questions.json
    questions = build_questions(codebook, QUESTION_FIELDS)
    write_questions_json(questions, OUTPUT_DIR / "questions.json")

    # personas.csv
    write_personas_csv(
        RAW_CSV,
        codebook,
        PERSONA_FIELDS,
        SOURCE_ID_COLUMN,
        OUTPUT_DIR / "personas.csv",
    )

    # answers.csv
    write_answers_csv(
        RAW_CSV,
        codebook,
        QUESTION_FIELDS,
        SOURCE_ID_COLUMN,
        OUTPUT_DIR / "answers.csv",
    )

if __name__ == "__main__":
    main()
