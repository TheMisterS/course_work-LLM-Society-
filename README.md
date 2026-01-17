# LLM Society - Multi-Agent Debate Simulation

A  multi-agent debate simulation system where LLM-powered agents engage in structured debates, featuring short-term/long-term memory management, and automated evaluation using LLM-as-Judge methodology.

## Table of Contents

- [Overview](#overview)
- [Academic Documentation](#academic-documentation)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Judge System](#judge-system)
- [Results and Analysis](#results-and-analysis)
- [Requirements](#requirements)

##  Overview

This project simulates debates between multiple AI agents with distinct personalities and moral frameworks. Each agent maintains both short-term and long-term memory, enabling nuanced discussions that evolve over multiple rounds. The system includes an automated evaluation framework using LLM-as-Judge to assess debate quality across multiple criteria.

### Key Components

- **Multi-Agent Debate System**: Orchestrates debates between agents with configurable profiles and traits
- **Supervisor Node**: Manages debate flow, ensures rule compliance, and facilitates phase transitions
- **Memory Management**: Dual-layer memory system (short-term and long-term) with automatic summarization
- **Voting System**: Structured voting mechanism to capture agent positions
- **Evaluation Framework**: Automated quality assessment using LLM-as-Judge methodology

## Academic Documentation

This project includes comprehensive academic documentation:

- **[Course Work Document](course_work.pdf)** - Thereotical background, literature analysis, existing simulation system analysis.
- **[Course Work Project Document](course_work_project.pdf)** - Complete project specification, implementation details, and experimental results.

These documents provide in-depth coverage of the project's academic context, theoretical framework, experimental design, and analysis of results.

## Features

### Debate System (`app/`)

- **Configurable Agent Profiles**: Define agents with unique roles, traits, and moral frameworks
- **Dynamic Memory System**:
  - Short-term memory with configurable window size
  - Long-term memory with automatic summarization at intervals
  - Memory threshold-based updates
- **Flexible Debate Phases**:
  - Debate phase with multiple rounds
  - Role-shift capability for perspective changes
  - Voting phase with customizable questions and options
- **LangGraph Integration**: State management and workflow orchestration
- **Multiple Model Support**: Configure different LLMs for different roles (debate, voting, summarization)
- **Comprehensive Logging**: Detailed logging system for debugging and analysis
- **Result Persistence**: Automatic saving of debate results, state snapshots, and configuration

### Judge System (`judge/`)

- **Automated Evaluation**: LLM-based assessment of debate quality
- **Multiple Criteria**:
  - Coherence and logical flow
  - Relevance to topic
  - Argument quality and depth
  - Engagement and responsiveness
  - Memory utilization
- **Batch Processing**: Evaluate single subsessions, full sessions, or multiple sessions
- **Aggregated Metrics**: Statistical analysis across multiple debates
- **Flexible Output**: JSON, YAML, or plain text report formats
- **Configurable Models**: Use different LLMs for evaluation

## Project Structure

```
course_work_project(LLM Society)/
├── app/                          # Main debate simulation application
│   ├── main.py                   # Entry point for simulation
│   ├── logger.py                 # Logging configuration
│   ├── requirements.txt          # Python dependencies
│   ├── configs/                  # Configuration modules
│   │   ├── agent_config.py       # Agent profiles and traits
│   │   ├── models_config.py      # LLM model configurations
│   │   ├── simulation_config.py  # Debate parameters
│   │   └── system_config.py      # System-level settings
│   ├── graph/                    # LangGraph workflow
│   │   ├── graph_factory.py      # Graph construction and initialization
│   │   ├── chain_factory.py      # LLM chain configuration
│   │   └── utils/
│   │       ├── nodes.py          # Node implementations
│   │       ├── prompts.py        # Prompt templates
│   │       └── state.py          # State definitions
│   └── utils/                    # Utility functions
│       ├── config_formatting.py  # Configuration snapshot utilities
│       ├── result_formatting.py  # Result formatting and export
│       └── time_and_dates.py     # Timestamp utilities
│
├── judge/                        # Evaluation system
│   ├── main.py                   # Entry point for evaluation
│   ├── evaluator.py              # LLM judge implementation
│   ├── parser.py                 # State file parsing
│   ├── prompts.py                # Evaluation criteria prompts
│   ├── models.py                 # Data models for metrics
│   ├── aggregator.py             # Metrics aggregation
│   ├── cli.py                    # Command-line interface
│   ├── config.py                 # Judge configuration
│   └── requirements.txt          # Judge dependencies
│
└── results/                      # Output directory
    └── session_YYYY.MM.DD/       # Session-level results
        └── subsession_HH.MM.SS/  # Individual debate results
            ├── state.json        # Complete final state
            ├── config_snapshot.json
            └── messages.txt      # Human-readable conversation
```

## Installation

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- LLM models downloaded (e.g., `llama3.1:8b`)

### Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd course_work_project(LLM\ Society)
```

2. **Install dependencies for the debate system**:
```bash
cd app
pip install -r requirements.txt
```

3. **Install dependencies for the judge system**:
```bash
cd ../judge
pip install -r requirements.txt
```

4. **Configure environment variables**:
Create a `.env` file in the `app` directory:
```env
# Debate Configuration
DEBATE_TOPIC="The impact of artificial intelligence on society?"
DEBATE_ROUND_COUNT=10
MEMORY_WINDOW_SIZE=5

# Voting Configuration
VOTING_QUESTION="Based on the debate, what is your final position?"
VOTING_OPTIONS="Strongly For,For,Neutral,Against,Strongly Against"

# Model Configuration
OLLAMA_URL=http://localhost:11434
MODEL_1_MODEL=llama3.1:8b
MODEL_1_TEMPERATURE=0.9
MODEL_1_TOP_P=0.9
MODEL_1_TOP_K=40
MODEL_1_NUM_CTX=4096

MODEL_USED_FOR_DEBATE=model_1
MODEL_USED_FOR_VOTING=model_1
MODEL_USED_FOR_SUMMARIZATION=model_1

# Long-term Memory
LONG_MEMORY_ENABLED=true
LONG_MEMORY_UPDATE_INTERVAL=5
LONG_MEMORY_THRESHOLD_PERCENT=0.8
```

Create a `.env` file in the `judge` directory:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_TEMPERATURE=0.1
OLLAMA_NUM_CTX=8192
```

5. **Verify Ollama is running**:
```bash
ollama list
```

## Configuration

### Agent Configuration

Edit [`app/configs/agent_config.py`](app/configs/agent_config.py) to define agent profiles:

```python
AGENT_PROFILES = {
    "Agent_Name": {
        "role_desc": "Description of agent's role and perspective",
        "traits": {
            "rule_focus": "high|medium|low",
            "outcome_focus": "high|medium|low",
            "emotional_focus": "high|medium|low",
            "compromise_willingness": "high|medium|low"
        }
    }
}
```

### Simulation Parameters

Adjust debate parameters in [`app/configs/simulation_config.py`](app/configs/simulation_config.py):

- `DEBATE_ROUND_COUNT`: Number of debate rounds
- `MEMORY_WINDOW_SIZE`: Short-term memory capacity
- `LONG_MEMORY_UPDATE_INTERVAL`: Rounds between long-term memory updates
- `LONG_MEMORY_THRESHOLD_PERCENT`: Threshold for triggering memory summarization

### Model Configuration

Configure LLM parameters in [`app/configs/models_config.py`](app/configs/models_config.py):

- Model name
- Temperature, top_p, top_k
- Context window size
- Repeat penalty

## Usage

### Running a Debate Simulation

```bash
cd app
python main.py
```

This will:
1. Initialize agents with configured profiles
2. Run the debate for specified rounds
3. Trigger memory updates as configured
4. Conduct voting phase
5. Save results to `results/session_YYYY.MM.DD/subsession_HH.MM.SS/`

### Output Files

- `state.json`: Complete final state with all agent data
- `messages.txt`: Human-readable conversation transcript
- `config_snapshot.json`: Configuration used for this run
- `graph.png`: Visualization of the workflow graph

## Judge System

The judge system provides automated evaluation of debate quality using LLM-as-Judge methodology.

### Evaluation Criteria

- **Coherence**: Logical flow and consistency
- **Relevance**: Staying on topic
- **Argument Quality**: Depth and persuasiveness
- **Engagement**: Responsiveness to other agents
- **Memory Utilization**: Effective use of context

### Running Evaluations

**Evaluate a single subsession**:
```bash
cd judge
python main.py --subsession ../results/session_2025.11.16/subsession_10.30.45
```

**Evaluate an entire session**:
```bash
python main.py --session ../results/session_2025.11.16
```

**Evaluate all sessions**:
```bash
python main.py --sessions ../results --format json
```

### Command-Line Options

- `--subsession PATH`: Evaluate single subsession
- `--session PATH`: Evaluate all subsessions in a session
- `--sessions PATH`: Evaluate all sessions in a directory
- `--model NAME`: Specify Ollama model for evaluation
- `--temperature FLOAT`: Set model temperature (default: 0.1)
- `--format {json,yaml,text}`: Output format (default: text)
- `--output PATH`: Save results to file
- `--quiet`: Suppress progress messages

### Example Output

```
Subsession: subsession_10.30.45
  Coherence: 4.2 (0.5)
  Relevance: 4.5 (0.3)
  Argument Quality: 3.8 (0.6)
  Engagement: 4.0 (0.4)
  Memory Usage: 3.5 (0.7)
  Overall: 4.0

Session Average: 4.1
Standard Deviation: 0.3
```

##  Results and Analysis

Results are organized by session and subsession:

```
results/
└── session_2025.11.16/
    ├── subsession_10.30.45/
    │   ├── state.json
    │   ├── messages.txt
    │   └── config_snapshot.json
    └── subsession_14.22.13/
        └── ...
```