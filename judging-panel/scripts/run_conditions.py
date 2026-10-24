"""Run the Judging Panel conditions defined in config/conditions.toml (T6).

Each game is one harness run (1 trial, 4 rounds). Finished games are copied to
judging-panel/data/runs/<condition>/game_<g>.json (+ _calls.jsonl and .log), and a game whose copy
already exists is skipped, so the script can be stopped and restarted at any time.

    python3 judging-panel/scripts/run_conditions.py --dry-run               # list every planned game
    python3 judging-panel/scripts/run_conditions.py C0 C1 --parallel 3      # run these conditions
    python3 judging-panel/scripts/run_conditions.py C1 --games 0 1           # only some game indices

Needs Ollama running (OLLAMA_CONTEXT_LENGTH=8192 OLLAMA_NUM_PARALLEL=4 ollama serve) and the
compute.env lines LLM_BASE_URL, LLM_API_KEY, REASONING_EFFORT=none, TOP_P=0.8.
"""

import argparse
import json
import random
import shutil
import subprocess
import sys
import time
import tomllib
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations
from pathlib import Path

PANEL = Path(__file__).resolve().parents[1]
HARNESS = PANEL.parent / "llm-trust-breaking"
CONFIG = PANEL / "config" / "conditions.toml"
RUNS = PANEL / "data" / "runs"
AGENT_NAMES = ["J", "M", "Q", "Z"]  # what the harness picks for --agents 4 (fixed-seed shuffle)
CALLS_PER_ROUND = 16                # 4 plan + 4 announce + 4 final + 4 reflection
PAIR_CALLS_PER_ROUND = 2            # private messages


def pair_schedule(seed):
    pairs = list(combinations(AGENT_NAMES, 2))
    random.Random(seed).shuffle(pairs)
    return pairs


def planned_games(cfg, conditions, only_games=None):
    pairs = pair_schedule(cfg["schedule"]["pair_seed"])
    for cond in conditions:
        c = cfg["conditions"][cond]
        for g in range(c["games"]):
            if only_games is not None and g not in only_games:
                continue
            yield {
                "condition": cond,
                "game": g,
                "seed": g,
                "language": c["language"],
                "pair": pairs[g % len(pairs)] if c["secret_pair"] else None,
                "auditor_notice": c["auditor_notice"],
                "split": "dev" if g < cfg["schedule"]["dev_games"] else "test",
            }


def out_path(game):
    return RUNS / game["condition"] / f"game_{game['game']}.json"


def command(cfg, game):
    suffix = f"{game['condition']}_g{game['game']}"
    cmd = ["uv", "run", "python", "experiments/run_endogenous.py",
           "--game", "judging", "--agents", str(cfg["game"]["agents"]), "--trials", "1",
           "--rounds", str(cfg["game"]["rounds"]), "--model", cfg["model"]["name"],
           "--temperature", str(cfg["model"]["temperature"]), *cfg["game"]["flags"],
           "--language", game["language"], "--game-seed", str(game["seed"]),
           "--condition", game["condition"], "--run-suffix", suffix]
    if game["pair"]:
        cmd += ["--secret-pair", ",".join(game["pair"])]
    if game["auditor_notice"]:
        cmd += ["--auditor-notice"]
    result = HARNESS / "outputs" / "experiments" / "judging" / f"{cfg['game']['agents']}agents" / \
        f"{cfg['model']['name'].replace('/', '_').replace(':', '_')}_endogenous_{suffix}.json"
    return cmd, result


def run_game(cfg, game):
    cmd, result = command(cfg, game)
    dest = out_path(game)
    dest.parent.mkdir(parents=True, exist_ok=True)
    log = dest.with_suffix(".log")
    start = time.time()
    with open(log, "w") as f:
        code = subprocess.run(cmd, cwd=HARNESS, stdout=f, stderr=subprocess.STDOUT).returncode
    minutes = (time.time() - start) / 60
    label = f"{game['condition']} game {game['game']}"
    if code != 0 or not result.exists():
        return f"FAILED  {label} after {minutes:.1f} min (exit {code}); see {log}"
    shutil.copy(result, dest)
    calls = result.with_name(result.stem + "_calls.jsonl")
    if calls.exists():
        shutil.copy(calls, dest.with_name(dest.stem + "_calls.jsonl"))
    data = json.loads(dest.read_text())
    errors = sum(t["_parse_errors"] for r in data["rounds"] for t in r["trials"])
    return f"done    {label} in {minutes:.1f} min, parse errors {errors}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("conditions", nargs="*", help="conditions to run (default: all, in config order)")
    ap.add_argument("--games", type=int, nargs="*", help="only these game indices")
    ap.add_argument("--parallel", type=int, default=3, help="games run at the same time (default 3)")
    ap.add_argument("--dry-run", action="store_true", help="list the planned games and exit")
    args = ap.parse_args()

    cfg = tomllib.loads(CONFIG.read_text())
    conditions = args.conditions or list(cfg["conditions"])
    unknown = [c for c in conditions if c not in cfg["conditions"]]
    if unknown:
        sys.exit(f"unknown condition(s) {unknown}; choose from {list(cfg['conditions'])}")
    games = list(planned_games(cfg, conditions, set(args.games) if args.games is not None else None))
    todo = [g for g in games if not out_path(g).exists()]

    rounds = cfg["game"]["rounds"]
    calls = sum(rounds * (CALLS_PER_ROUND + (PAIR_CALLS_PER_ROUND if g["pair"] else 0)) for g in todo)
    print(f"{'cond':6} {'game':>4} {'seed':>4} {'lang':4} {'pair':5} {'notice':6} {'split':5} status")
    for g in games:
        print(f"{g['condition']:6} {g['game']:>4} {g['seed']:>4} {g['language']:4} "
              f"{'-'.join(g['pair']) if g['pair'] else '-':5} {'yes' if g['auditor_notice'] else 'no':6} "
              f"{g['split']:5} {'done' if g not in todo else 'to run'}")
    print(f"\n{len(games)} games planned, {len(todo)} to run, about {calls} calls "
          f"(~{calls * 3.9 / 3600:.1f} h at 3.9 s per call)")
    if args.dry_run or not todo:
        return

    start = time.time()
    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        for line in pool.map(lambda g: run_game(cfg, g), todo):
            print(line, flush=True)
    print(f"\nfinished {len(todo)} games in {(time.time() - start) / 3600:.2f} h")


if __name__ == "__main__":
    main()
