from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Union


class ResponseType(str, Enum):
    SCALE       = "scale"       # numeric range, e.g. 0–10
    LIKERT      = "likert"      # ordered labelled options
    CATEGORICAL = "categorical" # named options, no implied order
    NUMERIC     = "numeric"     # raw number (age, minutes, count)


@dataclass
class Question:
    key:           str # variable or short identifier
    text:          str # full question text shown to model
    response_type: ResponseType
    options:       Dict[int, str] = field(default_factory=dict)  # code → label (likert/categorical)
    scale_min:     Optional[int]  = None
    scale_max:     Optional[int]  = None
    scale_labels:  Dict[int, str] = field(default_factory=dict)  # endpoint labels


@dataclass
class Persona:
    """
    A respondent built from any survey source.
    attributes: variable name → decoded value (int, float, or str)
    answers:    question key  → raw coded value from the survey (ground truth)
    source_id:  trace back to original row / respondent id
    """
    attributes: Dict[str, Union[int, float, str]] = field(default_factory=dict)
    answers:    Dict[str, Union[int, float, str]] = field(default_factory=dict)
    source_id:  Optional[str] = None