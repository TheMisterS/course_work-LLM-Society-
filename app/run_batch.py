"""
Batch runner for easier execution of multiple sessions and evaluations, required for research.
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def run_simulation(mode: str, run_index: int, total: int, personas_only: bool = False,
                   persona_file: str = None, append_default_persona: bool = False):
    
    label = "persona generation" if personas_only else "simulation"
    
    print(f"[{run_index}/{total}] Starting {mode} {label}...")
    
    cmd = [sys.executable, "main.py", "--mode", mode]
    
    if personas_only:
        cmd.append("--personas-only")
    if persona_file:
        cmd += ["--persona-file", persona_file]
    if append_default_persona:
        cmd.append("--append-default-persona")
        
    result = subprocess.run(cmd, cwd=SCRIPT_DIR)
    
    if result.returncode != 0:
        print(f"  [WARN] Run {run_index} ({mode}) exited with code {result.returncode}")
    else:
        print(f"  [OK] Run {run_index} ({mode}) complete.")


def run_eval(eval_script: str, session_path: Path):
    
    print(f"  Running {eval_script} on {session_path.name}...")
    result = subprocess.run(
        [sys.executable, eval_script, "--session", str(session_path)],
        cwd=SCRIPT_DIR,
    )
    if result.returncode != 0:
        print(f"  [WARN] Eval {eval_script} exited with code {result.returncode}")
    else:
        print(f"  [OK] Eval {eval_script} complete.")


def main():
    parser = argparse.ArgumentParser(description="Run N simulation sessions per mode, then evaluate.")
    parser.add_argument("--runs", type=int, required=True, help="Number of runs per mode")
    parser.add_argument("--mode", choices=["rag", "baseline"], default=None,
                        help="Mode to run (default: both rag and baseline)")
    parser.add_argument("--personas-only", action="store_true",
                        help="Only generate personas and run persona evaluation — skip discussion and vote eval")
    parser.add_argument("--debate-only", action="store_true",
                        help="Skip persona generation; use --persona-file for all runs. Runs vote eval only.")
    parser.add_argument("--persona-file", type=str, default=None, metavar="PATH",
                        help="Path to a 07_personas.json to use for all runs (required with --debate-only)")
    parser.add_argument("--append-default-persona", action="store_true", default=False,
                        help="Append the hardcoded default persona (Rūta) to the generated persona list.")
    args = parser.parse_args()

    if args.debate_only and not args.persona_file:
        parser.error("--debate-only requires --persona-file")

    modes = [args.mode] if args.mode else ["rag", "baseline"]
    total = args.runs * len(modes)
    counter = 0

    today = datetime.now().strftime("%Y.%m.%d")
    folder_mode = {"rag": "rag", "baseline": "no_rag"}
    session_paths = {
        mode: SCRIPT_DIR / "results" / f"session_{today}_{folder_mode[mode]}"
        for mode in modes
    }

    for mode in modes:
        for _ in range(args.runs):
            counter += 1
            run_simulation(mode,
                           counter,
                           total,
                           personas_only=args.personas_only,
                           persona_file=args.persona_file,
                           append_default_persona=args.append_default_persona)

    print(f"\nBatch complete: {counter}/{total} runs finished.")
    print("\nRunning evaluations...")

    for mode in modes:
        session_path = session_paths[mode]
        if not session_path.exists():
            print(f"  [SKIP] Session folder not found for {mode}: {session_path}")
            continue

        print(f"\n[{mode}] Evaluating {session_path.name}")
        
        if not args.debate_only:
            run_eval("evaluation/personas/main.py", session_path)
        if not args.personas_only:
            run_eval("evaluation/votes/main.py", session_path)

    print("\nAll evaluations complete.")

if __name__ == "__main__":
    main()
