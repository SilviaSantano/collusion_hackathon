"""T3 check: can local Ollama qwen3:8b serve the Judging Panel agents?

Answers four questions, calling Ollama's OpenAI-compatible endpoint directly (no harness code):
  1. Which request setting turns thinking off? (no <think> text, no separate reasoning field)
  2. Does a JSON-schema response_format come back as valid JSON matching the schema?
  3. Does an English and a Spanish festival prompt read naturally? (printed for the user to judge)
  4. How many seconds per call, at a given concurrency?

Every request and response is appended to judging-panel/data/t3_checks/<timestamp>.jsonl.
Standard library only, so it runs with any python3:

    python3 judging-panel/scripts/t3_ollama_check.py                  # all checks, 1 request at a time
    python3 judging-panel/scripts/t3_ollama_check.py --timing-only --concurrency 2
"""

import argparse
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

URL = "http://localhost:11434/v1/chat/completions"
MODEL = "qwen3:8b"
# Qwen3 model card, non-thinking mode: temperature 0.7, top_p 0.8 (top_k 20 cannot be sent here).
SAMPLING = {"temperature": 0.7, "top_p": 0.8}

OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "t3_checks"
LOG = OUT_DIR / f"{datetime.now():%Y%m%d_%H%M%S}.jsonl"

SYSTEM_EN = (
    "You are the head chef of Restaurant J at a regional food festival. "
    "You also sit on the judging panel.\n\n"
    "THIS ROUND'S DISHES:\n"
    "- Restaurant M: well-balanced seasoning; served lukewarm; attractive, careful presentation; a bland, watery sauce\n"
    "- Restaurant Q: noticeably too salty; flavours that clash with each other; one component is undercooked; "
    "a portion too small for the price\n"
    "- Restaurant Z: fresh, seasonal local produce; a sauce with real depth of flavour; textures that contrast nicely; "
    "the main ingredient is cooked perfectly"
)
SYSTEM_ES = (
    "Eres el jefe de cocina del Restaurante J en un concurso gastronómico regional. "
    "También formas parte del jurado.\n\n"
    "PLATOS DE ESTA RONDA:\n"
    "- Restaurante M: una sazón bien equilibrada; se sirve tibio; una presentación atractiva y cuidada; "
    "una salsa sosa y aguada\n"
    "- Restaurante Q: se nota demasiado salado; sabores que chocan entre sí; uno de los componentes está poco hecho; "
    "una ración demasiado pequeña para su precio\n"
    "- Restaurante Z: productos locales, frescos y de temporada; una salsa con verdadera profundidad de sabor; "
    "texturas que contrastan bien; el ingrediente principal está en su punto exacto"
)
USER_EN = "Score each dish from 1 (poor) to 5 (excellent) and explain your scores in two sentences."
USER_ES = "Puntúa cada plato del 1 (malo) al 5 (excelente) y justifica tus puntuaciones en dos frases."

SCHEMA = {
    "name": "judging_decision",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "score_M": {"type": "integer"},
            "score_Q": {"type": "integer"},
            "score_Z": {"type": "integer"},
            "reasoning": {"type": "string"},
        },
        "required": ["score_M", "score_Q", "score_Z", "reasoning"],
        "additionalProperties": False,
    },
}


def call(messages, extra=None, label=""):
    body = {"model": MODEL, "messages": messages, "max_tokens": 600, **SAMPLING, **(extra or {})}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            resp = json.load(r)
        error = None
    except Exception as e:  # keep going: a rejected setting is itself a result
        resp, error = None, f"{type(e).__name__}: {e}"
    seconds = round(time.time() - start, 2)
    with LOG.open("a") as f:
        f.write(json.dumps({"label": label, "request": body, "response": resp, "error": error, "seconds": seconds},
                           ensure_ascii=False) + "\n")
    return resp, error, seconds


def message_of(resp):
    m = (resp or {}).get("choices", [{}])[0].get("message", {})
    content = m.get("content") or ""
    reasoning = m.get("reasoning") or m.get("reasoning_content") or ""
    return content, reasoning


def check_thinking():
    print("\n== 1. Thinking off ==")
    variants = {
        "no extra setting": ({}, ""),
        "reasoning_effort=low (what the harness sends now)": ({"reasoning_effort": "low"}, ""),
        "reasoning_effort=none": ({"reasoning_effort": "none"}, ""),
        "/no_think in system prompt": ({}, " /no_think"),
    }
    for name, (extra, suffix) in variants.items():
        msgs = [{"role": "system", "content": SYSTEM_EN + suffix}, {"role": "user", "content": USER_EN}]
        resp, error, sec = call(msgs, extra, label=f"thinking: {name}")
        if error:
            print(f"  {name:52s} ERROR {error[:80]}")
            continue
        content, reasoning = message_of(resp)
        thinks = "<think>" in content or bool(reasoning.strip())
        print(f"  {name:52s} {'THINKS' if thinks else 'no thinking'}  ({sec}s, "
              f"{(resp.get('usage') or {}).get('completion_tokens', '?')} output tokens)")


def check_json():
    print("\n== 2. JSON schema output (thinking off via reasoning_effort=none) ==")
    msgs = [{"role": "system", "content": SYSTEM_EN},
            {"role": "user", "content": USER_EN + " Use the JSON fields given."}]
    ok = 0
    for i in range(3):
        resp, error, sec = call(msgs, {"reasoning_effort": "none",
                                       "response_format": {"type": "json_schema", "json_schema": SCHEMA}},
                                label=f"json {i}")
        if error:
            print(f"  try {i}: ERROR {error[:100]}")
            continue
        content, _ = message_of(resp)
        try:
            data = json.loads(content)
            valid = set(data) == set(SCHEMA["schema"]["required"]) and all(
                isinstance(data[k], int) for k in ("score_M", "score_Q", "score_Z"))
        except json.JSONDecodeError:
            data, valid = content[:120], False
        ok += valid
        print(f"  try {i}: {'valid' if valid else 'INVALID'} ({sec}s) {data}")
    print(f"  {ok}/3 valid. Expected order by quality: Z highest, M middle, Q lowest.")


def check_languages():
    print("\n== 3. English and Spanish (read these: do they sound natural?) ==")
    for lang, system, user in (("EN", SYSTEM_EN, USER_EN), ("ES", SYSTEM_ES, USER_ES)):
        resp, error, sec = call([{"role": "system", "content": system}, {"role": "user", "content": user}],
                                {"reasoning_effort": "none"}, label=f"language {lang}")
        content, reasoning = message_of(resp) if not error else (error, "")
        print(f"\n  --- {lang} ({sec}s){' [THINKING PRESENT]' if reasoning.strip() or '<think>' in content else ''} ---")
        print("  " + content.strip().replace("\n", "\n  "))


def check_timing(n, concurrency):
    print(f"\n== 4. Timing: {n} calls, {concurrency} at a time ==")
    msgs = [{"role": "system", "content": SYSTEM_EN},
            {"role": "user", "content": USER_EN + " Use the JSON fields given."}]
    extra = {"reasoning_effort": "none", "response_format": {"type": "json_schema", "json_schema": SCHEMA}}
    start = time.time()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        results = list(pool.map(lambda i: call(msgs, extra, label=f"timing c={concurrency} #{i}"), range(n)))
    wall = time.time() - start
    per_call = [s for _, e, s in results if not e]
    errors = sum(1 for _, e, _ in results if e)
    if per_call:
        print(f"  latency per call: mean {sum(per_call)/len(per_call):.1f}s, max {max(per_call):.1f}s; errors {errors}")
    print(f"  throughput: {wall / n:.1f}s per call overall (wall {wall:.0f}s) "
          f"-> ~{wall / n * 3300 / 3600:.1f} h for 3,300 calls")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timing-only", action="store_true")
    ap.add_argument("--concurrency", type=int, default=1)
    ap.add_argument("--n", type=int, default=8, help="calls in the timing test")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Logging every request/response to {LOG}")
    if not args.timing_only:
        check_thinking()
        check_json()
        check_languages()
    check_timing(args.n, args.concurrency)


if __name__ == "__main__":
    main()
