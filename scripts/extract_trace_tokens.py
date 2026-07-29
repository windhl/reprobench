#!/usr/bin/env python3
"""
extract_trace_tokens.py — Extract token/cost/time usage from session trace JSON files.

Walks the repro_trace/ directory, parses every session_messages.json (plus metadata.json
for elapsed time), and aggregates per-run / per-model statistics.

Token semantics (verified across all 5 models by summing and comparing to `total`):
    total    = input + output + reasoning + cache.read + cache.write
    input    = non-cached input tokens (the "new" prompt tokens each turn)
    output   = generated output tokens
    reasoning= thinking/reasoning tokens (non-zero for deepseek/gpt/mimo)
    cache.read  = cached input tokens (conversation history re-read from cache)
    cache.write = input tokens written to cache for the first time

The "real" input a model processes each turn = input + cache.read + cache.write.
The "real" output = output + reasoning.
The `total` field already equals their sum, so we use it directly.

Cost and time are taken from the trace files as-is (already correct in prior work).

Outputs:
  - data/trace_token_extraction.json   : per-run raw numbers (machine-readable)
  - data/trace_token_summary.md        : per-model aggregate table (human-readable)
  - stdout                             : the aggregate table for quick inspection
"""
import json
import os
import sys
from collections import defaultdict, OrderedDict

# ============================================================
# Configuration
# ============================================================
TRACE_BASE = os.environ.get(
    "REPRO_TRACE",
    "/home/tca/reprobench/eval/repro_trace",
)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")

# Canonical model order (matches the paper)
MODELS = [
    "claude-sonnet-4-6",
    "deepseek-v4-flash",
    "glm-5.2",
    "gpt-5.5",
    "mimo-v2.5",
]


# ============================================================
# Per-run extraction
# ============================================================
def extract_run(session_path, metadata_path):
    """Extract token/cost counts for one run from session_messages.json + metadata.json.

    Returns an OrderedDict with per-run totals, or None if the trace is unreadable.
    """
    try:
        with open(session_path) as f:
            msgs = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None

    elapsed = None
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path) as f:
                meta = json.load(f)
            elapsed = meta.get("elapsed_seconds")
        except (OSError, json.JSONDecodeError):
            pass

    run = OrderedDict([
        ("assistant_msgs", 0),
        ("input", 0),            # tokens.input  (non-cached)
        ("output", 0),           # tokens.output
        ("reasoning", 0),        # tokens.reasoning
        ("cache_read", 0),       # tokens.cache.read
        ("cache_write", 0),      # tokens.cache.write
        ("total", 0),            # tokens.total  (verified = input+output+reasoning+cache.read+cache.write)
        ("cost", 0.0),           # info.cost
        ("elapsed_seconds", elapsed),
    ])

    for m in msgs:
        if not isinstance(m, dict):
            continue
        info = m.get("info", {})
        if info.get("role") != "assistant":
            continue

        run["assistant_msgs"] += 1

        tokens = info.get("tokens") or {}
        run["input"] += tokens.get("input", 0) or 0
        run["output"] += tokens.get("output", 0) or 0
        run["reasoning"] += tokens.get("reasoning", 0) or 0
        cache = tokens.get("cache") or {}
        run["cache_read"] += cache.get("read", 0) if isinstance(cache, dict) else 0
        run["cache_write"] += cache.get("write", 0) if isinstance(cache, dict) else 0
        run["total"] += tokens.get("total", 0) or 0

        cost = info.get("cost", 0)
        if isinstance(cost, (int, float)):
            run["cost"] += cost

    return run


# ============================================================
# Directory walk
# ============================================================
def walk_traces(trace_base):
    """Yield (cve, model, run_num, session_path, metadata_path) for every run dir."""
    for cve in sorted(os.listdir(trace_base)):
        cve_path = os.path.join(trace_base, cve)
        if not os.path.isdir(cve_path):
            continue
        for model_dir in sorted(os.listdir(cve_path)):
            model_path = os.path.join(cve_path, model_dir)
            if not os.path.isdir(model_path):
                continue
            for run_dir in sorted(os.listdir(model_path)):
                run_path = os.path.join(model_path, run_dir)
                if not os.path.isdir(run_path):
                    continue
                session_path = os.path.join(run_path, "session_messages.json")
                if not os.path.exists(session_path):
                    continue
                # Normalise model name: strip "-free" suffix used by some dirs.
                model = model_dir.replace("-free", "")
                try:
                    run_num = int(run_dir)
                except ValueError:
                    run_num = run_dir
                metadata_path = os.path.join(run_path, "metadata.json")
                yield cve, model, run_num, session_path, metadata_path


# ============================================================
# Aggregation
# ============================================================
def aggregate(per_runs):
    """Compute per-model aggregates from a list of per-run dicts."""
    fields = [
        "input", "output", "reasoning",
        "cache_read", "cache_write", "total",
        "cost", "elapsed_seconds", "assistant_msgs",
    ]
    agg = {}
    for f in fields:
        vals = [r[f] for r in per_runs if r.get(f) is not None]
        if not vals:
            agg[f] = {"sum": 0, "avg": 0, "min": 0, "max": 0}
            continue
        agg[f] = {
            "sum": sum(vals),
            "avg": sum(vals) / len(vals),
            "min": min(vals),
            "max": max(vals),
        }
    agg["runs"] = len(per_runs)
    # Derived: effective input (input + cache_read + cache_write) and
    # effective output (output + reasoning), for sanity check.
    agg["eff_input"] = {
        "sum": agg["input"]["sum"] + agg["cache_read"]["sum"] + agg["cache_write"]["sum"],
        "avg": (agg["input"]["avg"] + agg["cache_read"]["avg"] + agg["cache_write"]["avg"]),
    }
    agg["eff_output"] = {
        "sum": agg["output"]["sum"] + agg["reasoning"]["sum"],
        "avg": (agg["output"]["avg"] + agg["reasoning"]["avg"]),
    }
    return agg


def fmt_int(n):
    return f"{int(round(n)):,}"


def fmt_float(n, d=2):
    return f"{n:.{d}f}"


# ============================================================
# Main
# ============================================================
def main():
    if not os.path.isdir(TRACE_BASE):
        sys.exit(f"ERROR: trace base not found: {TRACE_BASE}")

    # ---- Extract all runs ----
    all_runs = []          # list of (cve, model, run_num, run_dict)
    by_model = defaultdict(list)

    for cve, model, run_num, sp, mp in walk_traces(TRACE_BASE):
        run = extract_run(sp, mp)
        if run is None:
            continue
        run["cve"] = cve
        run["model"] = model
        run["run"] = run_num
        all_runs.append(OrderedDict([
            ("cve", cve), ("model", model), ("run", run_num),
            ("assistant_msgs", run["assistant_msgs"]),
            ("input", run["input"]),
            ("output", run["output"]),
            ("reasoning", run["reasoning"]),
            ("cache_read", run["cache_read"]),
            ("cache_write", run["cache_write"]),
            ("total", run["total"]),
            ("cost", round(run["cost"], 6)),
            ("elapsed_seconds", run["elapsed_seconds"]),
        ]))
        by_model[model].append(run)

    print(f"Extracted {len(all_runs)} runs from {TRACE_BASE}\n")

    # ---- Per-model aggregation ----
    model_agg = OrderedDict()
    for model in MODELS:
        if model in by_model:
            model_agg[model] = aggregate(by_model[model])
    # Overall
    model_agg["Overall"] = aggregate(all_runs)

    # ---- Print table ----
    # Columns: Model | Runs | AvgInput | AvgOutput | AvgTotal | AvgCost | AvgTime
    #          + cache breakdown (AvgCacheRead, AvgCacheWrite, AvgReasoning)
    header = (
        f"{'Model':<22} {'Runs':>5} "
        f"{'AvgInput':>12} {'AvgOutput':>10} {'AvgTotal':>12} "
        f"{'AvgCost':>8} {'AvgTime':>8} "
        f"{'AvgCacheR':>12} {'AvgCacheW':>10} {'AvgReason':>10} {'AvgMsgs':>7}"
    )
    print("=" * len(header))
    print("PER-MODEL AGGREGATE (correct token extraction)")
    print("=" * len(header))
    print(header)
    print("-" * len(header))
    for model, a in model_agg.items():
        print(
            f"{model:<22} {a['runs']:>5} "
            f"{fmt_int(a['input']['avg'] + a['cache_read']['avg'] + a['cache_write']['avg']):>12} "
            f"{fmt_int(a['output']['avg'] + a['reasoning']['avg']):>10} "
            f"{fmt_int(a['total']['avg']):>12} "
            f"{fmt_float(a['cost']['avg']):>8} "
            f"{fmt_int(a['elapsed_seconds']['avg']):>8} "
            f"{fmt_int(a['cache_read']['avg']):>12} "
            f"{fmt_int(a['cache_write']['avg']):>10} "
            f"{fmt_int(a['reasoning']['avg']):>10} "
            f"{fmt_int(a['assistant_msgs']['avg']):>7}"
        )

    # ---- Verification block ----
    print("\n" + "=" * len(header))
    print("VERIFICATION: total == input + output + reasoning + cache.read + cache.write")
    print("=" * len(header))
    for model, a in model_agg.items():
        computed = (
            a["input"]["sum"] + a["output"]["sum"] + a["reasoning"]["sum"]
            + a["cache_read"]["sum"] + a["cache_write"]["sum"]
        )
        actual = a["total"]["sum"]
        match = computed == actual
        print(f"  {model:<22} computed={fmt_int(computed):>15}  actual={fmt_int(actual):>15}  {'OK' if match else 'MISMATCH'}")

    # ---- Grand totals ----
    print("\n" + "=" * len(header))
    print("GRAND TOTALS")
    print("=" * len(header))
    ov = model_agg["Overall"]
    print(f"  Total runs with trace:   {ov['runs']}")
    print(f"  Total tokens:            {fmt_int(ov['total']['sum'])}")
    print(f"  Total cost:              ${fmt_float(ov['cost']['sum'])}")
    print(f"  Total elapsed time:      {fmt_int(ov['elapsed_seconds']['sum'])}s "
          f"({ov['elapsed_seconds']['sum']/3600:.1f}h)")
    print(f"  Avg tokens per run:      {fmt_int(ov['total']['avg'])}")
    print(f"  Avg cost per run:        ${fmt_float(ov['cost']['avg'])}")
    print(f"  Avg time per run:        {fmt_int(ov['elapsed_seconds']['avg'])}s "
          f"({ov['elapsed_seconds']['avg']/60:.1f}min)")

    # ---- Save JSON ----
    os.makedirs(DATA_DIR, exist_ok=True)
    out_json = os.path.join(DATA_DIR, "trace_token_extraction.json")
    output = OrderedDict()
    output["_meta"] = OrderedDict([
        ("trace_base", TRACE_BASE),
        ("total_runs", len(all_runs)),
        ("description", "Per-run token/cost/time extraction from session_messages.json"),
        ("token_formula", "total = input + output + reasoning + cache.read + cache.write"),
        ("real_input", "input + cache.read + cache.write"),
        ("real_output", "output + reasoning"),
    ])
    output["per_model"] = model_agg
    output["per_run"] = all_runs
    with open(out_json, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved per-run + per-model data: {out_json}")

    # ---- Save markdown summary ----
    out_md = os.path.join(DATA_DIR, "trace_token_summary.md")
    with open(out_md, "w") as f:
        f.write("# Trace Token Extraction Summary\n\n")
        f.write(f"Extracted from `{TRACE_BASE}` — {len(all_runs)} runs.\n\n")
        f.write("Token formula: `total = input + output + reasoning + cache.read + cache.write`\n\n")
        f.write("## Per-Model Aggregate\n\n")
        f.write("| Model | Runs | Avg Input | Avg Output | Avg Total | Avg Cost ($) | Avg Time (s) |\n")
        f.write("|-------|-----:|----------:|-----------:|----------:|-------------:|-------------:|\n")
        for model, a in model_agg.items():
            f.write(
                f"| {model} | {a['runs']} "
                f"| {fmt_int(a['input']['avg'] + a['cache_read']['avg'] + a['cache_write']['avg'])} "
                f"| {fmt_int(a['output']['avg'] + a['reasoning']['avg'])} "
                f"| {fmt_int(a['total']['avg'])} "
                f"| {fmt_float(a['cost']['avg'])} "
                f"| {fmt_int(a['elapsed_seconds']['avg'])} |\n"
            )
        f.write("\n## Cache Token Breakdown\n\n")
        f.write("| Model | Avg Cache Read | Avg Cache Write | Avg Reasoning | Avg Assistant Msgs |\n")
        f.write("|-------|---------------:|----------------:|--------------:|-------------------:|\n")
        for model, a in model_agg.items():
            f.write(
                f"| {model} "
                f"| {fmt_int(a['cache_read']['avg'])} "
                f"| {fmt_int(a['cache_write']['avg'])} "
                f"| {fmt_int(a['reasoning']['avg'])} "
                f"| {fmt_int(a['assistant_msgs']['avg'])} |\n"
            )
        f.write("\n## Grand Totals\n\n")
        ov = model_agg["Overall"]
        f.write(f"- Total runs with trace: {ov['runs']}\n")
        f.write(f"- Total tokens: {fmt_int(ov['total']['sum'])}\n")
        f.write(f"- Total cost: ${fmt_float(ov['cost']['sum'])}\n")
        f.write(f"- Total elapsed time: {fmt_int(ov['elapsed_seconds']['sum'])}s ({ov['elapsed_seconds']['sum']/3600:.1f}h)\n")
    print(f"Saved markdown summary: {out_md}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
