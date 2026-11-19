from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a directory-only todo list for agent-based REPROBENCH scoring."
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path.cwd(),
        help="Base directory used for relative paths. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        required=True,
        help="Root directory containing repro_workspace-style CVE/model/run artifacts.",
    )
    parser.add_argument(
        "--trace-root",
        type=Path,
        required=True,
        help="Root directory containing repro_trace-style CVE/model/run traces.",
    )
    parser.add_argument(
        "--groundtruth-root",
        type=Path,
        required=True,
        help="Root directory containing repro_groundtruth-style CVE ground truth directories.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("evaluation"),
        help="Output directory for context files and agent_todo_list.json. Defaults to ./evaluation.",
    )
    return parser.parse_args()


def resolve(path: Path, base_dir: Path) -> Path:
    if path.is_absolute():
        return path
    return base_dir / path


def rel(path: Path, base_dir: Path) -> str:
    try:
        return str(path.resolve().relative_to(base_dir.resolve()))
    except ValueError:
        return str(path)


def collect_context(
    cve: str,
    model: str,
    run: str,
    workspace_root: Path,
    trace_root: Path,
    groundtruth_root: Path,
    base_dir: Path,
) -> dict:
    workspace_dir = workspace_root / cve / model / run
    trace_dir = trace_root / cve / model / run
    groundtruth_dir = groundtruth_root / cve

    return {
        "id": f"{cve}/{model}/{run}",
        "cve": cve,
        "model": model,
        "run": run,
        "directories": {
            "workspace": rel(workspace_dir, base_dir),
            "trace": rel(trace_dir, base_dir),
            "groundtruth": rel(groundtruth_dir, base_dir),
        },
        "exists": {
            "workspace": workspace_dir.exists(),
            "trace": trace_dir.exists(),
            "groundtruth": groundtruth_dir.exists(),
            "groundtruth_info": (groundtruth_dir / "info.txt").exists(),
        },
    }


def iter_runs(workspace_root: Path):
    for cve_dir in sorted(p for p in workspace_root.iterdir() if p.is_dir() and p.name.startswith("CVE-")):
        for model_dir in sorted(p for p in cve_dir.iterdir() if p.is_dir()):
            for run_dir in sorted(p for p in model_dir.iterdir() if p.is_dir()):
                yield cve_dir.name, model_dir.name, run_dir.name


def save_context(context: dict, context_root: Path) -> Path:
    out_dir = context_root / context["cve"] / context["model"] / context["run"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"context-{context['cve']}.json"
    out_path.write_text(json.dumps(context, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out_path


def todo_item(context: dict, context_path: Path, base_dir: Path) -> dict:
    return {
        "id": context["id"],
        "status": "pending",
        "task": "Evaluate this REPROBENCH run with the reprobench-scoring skill. Use the directories below to inspect artifacts directly.",
        "cve": context["cve"],
        "model": context["model"],
        "run": context["run"],
        "context_path": rel(context_path, base_dir),
        "directories": context["directories"],
        "expected_outputs": {
            "evaluation_json": f"evaluation/{context['cve']}/{context['model']}/{context['run']}/evaluation-{context['cve']}.json",
            "summary_txt": f"evaluation/{context['cve']}/{context['model']}/{context['run']}/summary-{context['cve']}.txt",
        },
    }


def main() -> None:
    args = parse_args()
    base_dir = args.base_dir.resolve()
    workspace_root = resolve(args.workspace_root, base_dir).resolve()
    trace_root = resolve(args.trace_root, base_dir).resolve()
    groundtruth_root = resolve(args.groundtruth_root, base_dir).resolve()
    output_root = resolve(args.output_root, base_dir).resolve()
    context_root = output_root / "context"
    todo_list_path = output_root / "agent_todo_list.json"

    output_root.mkdir(parents=True, exist_ok=True)
    context_root.mkdir(parents=True, exist_ok=True)

    todos = []
    for cve, model, run in iter_runs(workspace_root):
        context = collect_context(cve, model, run, workspace_root, trace_root, groundtruth_root, base_dir)
        context_path = save_context(context, context_root)
        todos.append(todo_item(context, context_path, base_dir))

    payload = {
        "description": "Todo list for agent-based REPROBENCH scoring. Each item points to one CVE/model/run and only records the relevant artifact directories.",
        "workspace_root": rel(workspace_root, base_dir),
        "trace_root": rel(trace_root, base_dir),
        "groundtruth_root": rel(groundtruth_root, base_dir),
        "context_root": rel(context_root, base_dir),
        "total_items": len(todos),
        "items": todos,
    }
    todo_list_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(todos)} context files to {context_root}")
    print(f"wrote todo list to {todo_list_path}")


if __name__ == "__main__":
    main()
