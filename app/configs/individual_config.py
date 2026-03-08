import os
from dotenv import load_dotenv

load_dotenv()

# Single persona to be interviewed
INDIVIDUAL_PROFILE = {
    "demographics": {
        "nationality": "Lithuanian",
        "sex": "Male",
        "education": "Not finished secondary school"
    }
}

# Questions asked during the interview (in order)
INDIVIDUAL_QUESTIONS = [
    "A man should earn more than his wife or partner.",
    "In public places (e.g., cafes, shopping centers, gas stations, movie theaters), toilets must be adapted for people with disabilities."
]

MODEL_USED_FOR_INDIVIDUAL = os.environ.get("MODEL_USED_FOR_INDIVIDUAL", "model_1")
