# LLM Society — research discussion system enviroment

A LangGraph-based multi-agent discussion system. Personas are generated either via a RAG pipeline (web search → viewpoint extraction → synthesis) or a baseline (direct LLM generation). Agents discuss a configurable topic across multiple rounds, casting votes at the start, midpoint, and end.

## File Structure

- **`main.py`** — entry point; parses CLI args, runs persona generation, invokes the discussion graph
- **`run_batch.py`** — batch runner for executing multiple sessions and triggering evaluations
- **`smoke_test.py`** — step-by-step RAG pipeline smoke test (uncomment steps incrementally)
- **`logger.py`** — configures the root logger (console + file, coloured output)

- **`configs/`** — all runtime configuration
  - `simulation_config.py` — discussion topic, voting question/options, round count, memory settings
  - `models_config.py` — model profiles (RAG, baseline, discussion/voting) and `configure_model` factory
  - `rag_config.py` — RAG pipeline behaviour, Tavily settings, persona stance schema
  - `agent_config.py` — fallback static agent profiles and the default hardcoded persona (Rūta)
  - `system_config.py` — log level and log file path

- **`graph/`** — LangGraph discussion graph
  - `graph_factory.py` — builds and compiles the `StateGraph`; defines conditional routing logic
  - `chain_factory.py` — creates the LangChain prompt→model→parser chain used by all nodes
  - `utils/state.py` — core discussion data types
  - `utils/nodes.py` — all graph nodes: `supervisor`, `agent_speak`, `update_short_memory`, `update_long_memory`, `vote`
  - `utils/prompts.py` — prompt builders for discussion turns, voting, and memory summarisation

- **`rag/`** — RAG persona creation pipeline
  - `pipeline.py` — orchestrates the full pipeline
  - `query_planner.py` — **[step 1]** generates Tavily search queries from the discussion topic
  - `search_tool.py` — **[step 2]** executes queries via Tavily
  - `extractor.py` — **[step 3]** extracts stakeholder viewpoints from search results
  - `deduplicator.py` — **[step 4]** rule-based and optional LLM-based viewpoint deduplication
  - `stance_selector.py` — **[step 5]** selects viewpoints according to schema
  - `background_fetcher.py` — **[step 6]** enriches selected viewpoints with Wikipedia background
  - `persona_synthesis.py` — **[step 7]** synthesises final persona objects
  - `rag_logger.py` — RAG logger
  - `state.py` — core RAG data types 
  - `_llm.py` — shared LLM utilities

- **`baseline/`** — no-RAG persona generation
  - `pipeline.py` — generates personas from general LLM knowledge
  - `prompts.py` — system prompt and user message builder for baseline

- **`evaluation/`** — post-run analysis scripts (standalone, not imported by the simulation)
  - `votes/` — vote distribution, stance-vote alignment, vote change across rounds
  - `personas/` — persona similarity within and across sessions
  - `shared/` — shared loader, embedder, and config used by both evaluation modules

- **`utils/`** — general utilities
  - `result_formatting.py` — creates result folders, writes conversation/vote/memory logs, exports state JSON for evaluation to pickup
  - `config_formatting.py` — formats and saves a configuration snapshot per run
  - `time_and_dates.py` — `date_stamp` and `date_time_stamp` helpers

---

## Prerequisites

- Python 3.12+ (with venv available)
- An [OpenRouter](https://openrouter.ai) API key (or a local [Ollama](https://ollama.com) instance, has not been tested in a while)
- A [Tavily](https://tavily.com) API key (required for the RAG pipeline)

---

## Setup

1. **Clone the repository and enter the ./app directory.**

2. **Create and activate a virtual environment.**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # might differ based on enviroment, both Linux & Windows should work
   ```

3. **Install dependencies.**
   ```bash
   pip install -r requirements.txt # expect quite large dependencies due to cuda, 2gb<
   ```

4. **Configure environment variables.**
   ```bash
   cp .env.example .env
   ```
   Then open `.env` and fill in the secret values. \
   Don't forget you can also edit schemas in rag_config [WIP :)]

5. **Run a simulation.**
   ```bash
   # RAG mode (default)
   python main.py --mode rag

   # Baseline mode (no retrieval)
   python main.py --mode baseline

   # Generate personas only, skip the discussion
   python main.py --mode rag --personas-only

   # Run multiple sessions and evaluate automatically
   python run_batch.py --runs 3 --mode rag
   ```
Results are written to `results/session_<date>_<mode>/subsession_<timestamp>/`.

6. **(Optional) Run evaluations.** \
   The evaluation scripts are run from the project root and must be pointed at a results folder.\
    Each accepts either `--session` (evaluates all subsessions and aggregates) or `--subsession` (single run only). \

   **Vote evaluation example** — stance alignment, vote change across rounds, vote distribution:
   ```bash
   # whole session (aggregated)
   python evaluation/votes/main.py --session results/session_2025.05.20_rag
 
   # single subsession
   python evaluation/votes/main.py --subsession results/session_2025.05.20_rag/subsession_2025.05.17_12.00.00
   ```
   
 
   **Persona evaluation example** — intra-session similarity and cross-session consistency:
   ```bash
   # whole session
   python evaluation/personas/main.py --session results/session_2025.05.20_rag
 
   # single subsession (in-subsession metrics only)
   python evaluation/personas/main.py --subsession results/session_2025.05.20_rag/subsession_2025.05.17_12.00.00
   ```
 
   Results are saved to `eval/votes_metrics.json` and `eval/persona_metrics.json` inside the target folder.

---

