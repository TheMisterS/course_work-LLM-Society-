import os
from dotenv import load_dotenv

from data.datasets.ess_11_lt import load_questions, load_personas

load_dotenv(dotenv_path=os.environ.get("APP_ENV_FILE", ".env"))

# ---- Load structured data from datasets, validated indicates human validation and changes path for where dataset is located ----
INDIVIDUAL_QUESTION_OBJECTS = load_questions(validated=True)   # List[Question]
INDIVIDUAL_PERSONAS         = load_personas(validated=True)    # List[Persona]

# Index of the persona to use in single-persona mode (0-based)
PERSONA_INDEX = int(os.environ.get("PERSONA_INDEX", "0"))

# Convenience accessors (backwards-compatible with existing code)
INDIVIDUAL_PERSONA   = INDIVIDUAL_PERSONAS[PERSONA_INDEX]
INDIVIDUAL_PROFILE   = {
    "demographics": {k: str(v) for k, v in INDIVIDUAL_PERSONA.attributes.items()}
}
INDIVIDUAL_QUESTIONS = [q.text for q in INDIVIDUAL_QUESTION_OBJECTS]

MODEL_USED_FOR_INDIVIDUAL = os.environ.get("MODEL_USED_FOR_INDIVIDUAL", "model_1")

INDIVIDUAL_ANSWER_MODE = os.environ.get("INDIVIDUAL_ANSWER_MODE", "structured").strip().lower()
if INDIVIDUAL_ANSWER_MODE not in {"free_form", "structured"}:
    raise ValueError(
        "INDIVIDUAL_ANSWER_MODE must be one of: 'free_form', 'structured'"
    )
