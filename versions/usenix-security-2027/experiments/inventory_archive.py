#!/usr/bin/env python3
"""Inventory historical files and labels without scoring or executing artifacts.

Counts describe archived annotations and directory availability, not validated
reproduction outcomes. Raw source files are never modified.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def directory_state(path):
    if not path.is_dir():
        return "missing"
    return "nonempty" if next(path.iterdir(), None) is not None else "empty"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    counts = Counter()
    by_model = {}
    for path in sorted((args.archive / "evaluation").glob("CVE-*/*/[123]/evaluation-CVE-*.json")):
        cve, model, run, _ = path.relative_to(args.archive / "evaluation").parts
        data = json.loads(path.read_text())
        failures = [f for f in data.get("failure_analysis", []) if isinstance(f, dict)]
        terminal = [f for f in failures if f.get("terminal") is True]
        simulation = [f for f in failures if f.get("failure_mode") == "simulation_substitution"]
        items = data.get("task_score", {}).get("Phase 6", {}).get("item_scores", {})
        candidate = all(items.get(k, {}).get("score", 0) > 0 for k in (
            "poc_execution_against_real_target", "vulnerability_specific_trigger_evidence"))
        trace = directory_state(args.archive / "repro_trace" / cve / model / run)
        workspace = directory_state(args.archive / "repro_workspace" / cve / model / run)
        row = {
            "cve": cve, "model": model, "run": int(run),
            "annotation_file": str(path.relative_to(args.archive)),
            "annotation_sha256": digest(path),
            "trace_directory": trace, "workspace_directory": workspace,
            "historical_trigger_candidate": candidate,
            "historical_any_simulation_label": bool(simulation),
            "historical_any_terminal_simulation_label": any(f.get("terminal") is True for f in simulation),
            "historical_terminal_entry_count": len(terminal),
        }
        rows.append(row)
        counts["runs"] += 1
        counts["trace_" + trace] += 1
        counts["workspace_" + workspace] += 1
        counts["trigger_candidates"] += candidate
        counts["any_simulation_label"] += bool(simulation)
        counts["any_terminal_simulation_label"] += row["historical_any_terminal_simulation_label"]
        counts["multiple_terminal_entries"] += len(terminal) > 1
        by_model.setdefault(model, Counter())
        by_model[model]["runs"] += 1
        by_model[model]["trigger_candidates"] += candidate
    counts["cves"] = len({r["cve"] for r in rows})
    counts["model_labels"] = len(by_model)
    counts["candidate_cves"] = len({r["cve"] for r in rows if r["historical_trigger_candidate"]})
    counts["candidate_cve_model_pairs"] = len({(r["cve"], r["model"]) for r in rows if r["historical_trigger_candidate"]})
    result = {
        "status": "Historical annotation inventory; not human-validated outcomes or behavior coding.",
        "counting_rule": "Match evaluation/CVE-*/*/[123]/evaluation-CVE-*.json; keep exact model labels.",
        "summary": dict(counts), "by_model": {m: dict(c) for m, c in sorted(by_model.items())},
        "runs": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"summary": result["summary"], "by_model": result["by_model"]}, indent=2))


if __name__ == "__main__":
    main()
