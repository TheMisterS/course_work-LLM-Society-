import os
from dotenv import load_dotenv

# redundant, but left as a safeguard
load_dotenv()

# Tavily search
TAVILY_API_KEY      = os.environ.get("TAVILY_API_KEY", "")
TAVILY_MAX_RESULTS  = int(os.environ.get("TAVILY_MAX_RESULTS", 5))
TAVILY_SEARCH_DEPTH = os.environ.get("TAVILY_SEARCH_DEPTH", "advanced")

# Optional comma-separated domain whitelist, e.g. "wikipedia.org,reuters.com"
# Leave unset or empty to fall back to a Lithuania-focused default list.
raw_include_domains = os.environ.get("TAVILY_INCLUDE_DOMAINS", "")

LITHUANIAN_DOMAINS = [
    "lrs.lt",
    "lrv.lt",
    "delfi.lt",
    "lrytas.lt",
    "15min.lt",
    "vz.lt",
    "bernardinai.lt",
    "lrt.lt",
    "vu.lt",
    "ktu.lt",
]

if raw_include_domains.strip():
    parsed_domains = []

    for part in raw_include_domains.split(","):
        domain = part.strip()
        if domain:
            parsed_domains.append(domain)

    TAVILY_INCLUDE_DOMAINS = parsed_domains
else:
    TAVILY_INCLUDE_DOMAINS = LITHUANIAN_DOMAINS

# Pipeline behaviour
RAG_QUERY_COUNT    = int(os.environ.get("RAG_QUERY_COUNT", 4))     # Tavily queries generated per iteration
RAG_MAX_ITERATIONS = int(os.environ.get("RAG_MAX_ITERATIONS", 2))  # Hard cap on search-extract loops
RAG_MIN_VIEWPOINTS = int(os.environ.get("RAG_MIN_VIEWPOINTS", 5))  # Early-exit threshold: stop looping once this many viewpoints are found
RAG_DEDUP_USE_LLM  = os.environ.get("RAG_DEDUP_USE_LLM", "false").lower() == "true"  # LLM Dedup

# how many stakeholders with each stance to include in the final agent composition
# possible stances are "support", "oppose", "neutral", "mixed"
# [WIPWIPWIPWIP] This never made it into .env, thus it should be configured directly in this file
PERSONA_STANCE_SCHEMA = {
    "support": 2,
    "oppose":  1
}
SYNTHESIS_MAX_RETRIES = int(os.environ.get("SYNTHESIS_MAX_RETRIES", 3))

# Domain list for background_fetcher searches.
raw_background_domains = os.environ.get("BACKGROUND_FETCHER_INCLUDE_DOMAINS", "")
BACKGROUND_FETCHER_DEFAULT_DOMAINS = [
    "wikipedia.org",
    "en.wikipedia.org",
    "lt.wikipedia.org",
]

if raw_background_domains.strip():
    parsed_background_domains = []

    for part in raw_background_domains.split(","):
        domain = part.strip()
        if domain:
            parsed_background_domains.append(domain)

    BACKGROUND_FETCHER_INCLUDE_DOMAINS = parsed_background_domains
else:
    BACKGROUND_FETCHER_INCLUDE_DOMAINS = BACKGROUND_FETCHER_DEFAULT_DOMAINS
