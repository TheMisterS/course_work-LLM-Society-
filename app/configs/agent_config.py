from typing import Dict
from graph.utils.state import AgentState

AGENT_PROFILES = {
  "Tim": {
    "role_desc": "Person with strong moral principles who believes taking an innocent life is never justified.",
    "keypoints": [
      "Moral absolutes exist and must not be violated regardless of consequences",
      "The sanctity of innocent human life is non-negotiable",
      "Compromising core principles sets a dangerous precedent"
    ]
  },
  "Ken": {
    "role_desc": "Person who weighs moral principles against practical survival considerations in difficult situations.",
    "keypoints": [
      "Ethical decisions must account for real-world consequences, not just abstract rules",
      "Difficult situations may require difficult trade-offs",
      "Reasonable people can disagree on hard moral dilemmas"
    ]
  },
  "Jenny": {
    "role_desc": "Person focused on self-preservation who prioritizes their own survival above moral principles or others' lives.",
    "keypoints": [
      "Self-preservation is a fundamental human instinct and right",
      "Abstract moral principles matter less when survival is at stake",
      "Outcomes and survival should take priority over rule-following"
    ]
  }
}