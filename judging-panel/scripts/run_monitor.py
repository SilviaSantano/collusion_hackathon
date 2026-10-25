"""Run a Gemini monitor over the monitor views (T9).

One call per (game, view, monitor): the prompt in monitor/prompt_en.md followed by the view text. The
monitor returns a 0-10 suspicion score for each of the 6 pairs plus one sentence. Every response is saved
to data/monitor_outputs/<model>/<condition>/game_<g>_<view>.json and never requested again (cache), so
the script can be stopped and resumed, and spread over days for free-tier limits.

    python3 judging-panel/scripts/run_monitor.py weak --split dev --dry-run    # list calls, no requests
    python3 judging-panel/scripts/run_monitor.py weak --split dev              # tune the prompt on dev only
    python3 judging-panel/scripts/run_monitor.py weak --split test             # after freezing the prompt
    python3 judging-panel/scripts/run_monitor.py strong --split test --views V2 V4 --conditions C0 C1

Reads GEMINI_API_KEY from the repo-root compute.env (never printed or saved). Standard library only.
"""

import argparse
import hashlib
import json
import sys
import time
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

PANEL = Path(__file__).resolve().parents[1]
ROOT = PANEL.parent
CONFIG = PANEL / "config" / "conditions.toml"
PROMPT = PANEL / "monitor" / "prompt_en.md"
VIEWS = PANEL / "data" / "views"
OUT = PANEL / "data" / "monitor_outputs"
PAIRS = ["J-M", "J-Q", "J-Z", "M-Q", "M-Z", "Q-Z"]
API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "scores": {"type": "OBJECT", "properties": {p: {"type": "INTEGER"} for p in PAIRS}, "required": PAIRS},
        "reasoning": {"type": "STRING"},
    },
    "required": ["scores", "reasoning"],
}


def api_key():
    for line in (ROOT / "compute.env").read_text().splitlines():
        if line.strip().startswith("GEMINI_API_KEY="):
            key = line.split("=", 1)[1].strip().strip("'\"")
            if key:
                return key
    sys.exit("GEMINI_API_KEY is not set in compute.env")


def call_gemini(model, prompt, temperature, key, max_tries=6):
    body = json.dumps({
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "responseMimeType": "application/json",
                             "responseSchema": SCHEMA},
    }).encode()
    for attempt in range(1, max_tries + 1):
        req = urllib.request.Request(API.format(model=model), data=body, method="POST",
                                     headers={"Content-Type": "application/json", "x-goog-api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 503) and attempt < max_tries:
                wait = 30 * attempt if e.code == 429 else 5 * attempt
                print(f"    HTTP {e.code}, retry {attempt}/{max_tries - 1} in {wait}s", flush=True)
                time.sleep(wait)
                continue
            raise RuntimeError(f"HTTP {e.code}: {detail}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < max_tries:
                time.sleep(5 * attempt)
                continue
            raise RuntimeError(f"network error: {e}") from None


def parse(response):
    """(scores dict with all 6 pairs as ints 0-10, reasoning) or (None, None) if unusable."""
    try:
        parts = response["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        data = json.loads(text)
        scores = {p: max(0, min(10, int(data["scores"][p]))) for p in PAIRS}
        return scores, str(data.get("reasoning", ""))
    except (KeyError, IndexError, ValueError, TypeError):
        return None, None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("monitor", choices=["weak", "strong"])
    ap.add_argument("--split", choices=["dev", "test", "all"], default="dev")
    ap.add_argument("--conditions", nargs="*", help="default: all conditions in the config")
    ap.add_argument("--views", nargs="*", default=["V1", "V2", "V3", "V4"])
    ap.add_argument("--dry-run", action="store_true", help="list the calls that would be made, then stop")
    args = ap.parse_args()

    cfg = tomllib.loads(CONFIG.read_text())
    model = cfg["monitors"][args.monitor]
    temperature = cfg["monitors"]["temperature"]
    template = PROMPT.read_text()
    prompt_hash = hashlib.sha256(template.encode()).hexdigest()[:12]
    dev_games = cfg["schedule"]["dev_games"]
    conditions = args.conditions or list(cfg["conditions"])

    tasks = []
    for cond in conditions:
        for g in range(cfg["conditions"][cond]["games"]):
            split = "dev" if g < dev_games else "test"
            if args.split != "all" and split != args.split:
                continue
            for view in args.views:
                src = VIEWS / cond / f"game_{g}" / f"{view}.txt"
                dest = OUT / model / cond / f"game_{g}_{view}.json"
                if not src.exists():
                    sys.exit(f"missing view {src}; run build_views.py first")
                if not dest.exists():
                    tasks.append((cond, g, split, view, src, dest))

    print(f"monitor {args.monitor} = {model}, temperature {temperature}, prompt {prompt_hash}; "
          f"{len(tasks)} calls to make ({args.split} split)")
    if args.dry_run or not tasks:
        for t in tasks[:12]:
            print(f"  {t[0]} game {t[1]} ({t[2]}) {t[3]}")
        return

    key = api_key()
    for i, (cond, g, split, view, src, dest) in enumerate(tasks, 1):
        prompt = template.rstrip() + "\n\n" + src.read_text()
        start = time.time()
        try:
            response = call_gemini(model, prompt, temperature, key)
        except RuntimeError as e:
            print(f"STOPPED at {cond} game {g} {view}: {e}\nRe-run the same command later to continue "
                  f"({i - 1}/{len(tasks)} saved).")
            sys.exit(1)
        scores, reasoning = parse(response)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps({
            "condition": cond, "game": g, "split": split, "view": view, "monitor": args.monitor,
            "model": model, "temperature": temperature, "prompt_sha256_12": prompt_hash,
            "time": time.strftime("%Y-%m-%dT%H:%M:%S"), "seconds": round(time.time() - start, 1),
            "scores": scores, "reasoning": reasoning, "_parse_ok": scores is not None,
            "usage": response.get("usageMetadata"), "response": response,
        }, ensure_ascii=False, indent=1))
        print(f"  [{i}/{len(tasks)}] {cond} game {g} {view}: "
              f"{'ok' if scores else 'PARSE FAILED'} {scores or ''}", flush=True)
        time.sleep(cfg["monitors"]["min_interval_s"])


if __name__ == "__main__":
    main()
