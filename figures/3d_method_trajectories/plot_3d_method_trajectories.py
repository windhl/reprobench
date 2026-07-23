"""Render the ReproBench four-panel 3D phase-trajectory figure.

For each CVE/model pair, select the run with the largest skill-consistent task
score (R1+...+R6); ties use the smallest run id. Normalize phases by rubric
maxima before averaging over CVEs. Cross-check the flat summary against every
evaluation JSON before rendering.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def find_project_root(script_path: Path) -> Path:
    """Find the outer workspace root from either maintained script copy."""
    summary_tail = Path("data/reprobench/eval/evaluation/evaluation_summary.txt")
    for candidate in (script_path.parent, *script_path.parents):
        if (candidate / summary_tail).is_file():
            return candidate
    raise FileNotFoundError(
        "Could not locate data/reprobench/eval/evaluation/evaluation_summary.txt "
        f"above {script_path}"
    )


ROOT = find_project_root(Path(__file__).resolve())
DEFAULT_EVAL_ROOT = ROOT / "data" / "reprobench" / "eval" / "evaluation"
DEFAULT_SUMMARY = DEFAULT_EVAL_ROOT / "evaluation_summary.txt"
DEFAULT_GROUNDTRUTH = ROOT / "data" / "reprobench" / "eval" / "repro_groundtruth"
DEFAULT_METADATA = ROOT / "figure" / "data" / "reprobench_cve_metadata.csv"
DEFAULT_OUTPUT_DIR = ROOT / "reprobench" / "figures" / "3d_method_trajectories"

MODELS = (
    "claude-sonnet-4-6",
    "deepseek-v4-flash-free",
    "glm-5.2",
    "gpt-5.5",
    "mimo-v2.5-free",
)
PLOT_MODELS = (
    "gpt-5.5",
    "deepseek-v4-flash-free",
    "claude-sonnet-4-6",
    "mimo-v2.5-free",
    "glm-5.2",
)
DISPLAY_NAMES = {
    "claude-sonnet-4-6": "Claude Sonnet 4.6",
    "deepseek-v4-flash-free": "DeepSeek V4 Flash",
    "glm-5.2": "GLM-5.2",
    "gpt-5.5": "GPT-5.5",
    "mimo-v2.5-free": "MiMo-V2.5",
}
LANE_LABELS = {
    "claude-sonnet-4-6": "Claude",
    "deepseek-v4-flash-free": "DeepSeek",
    "glm-5.2": "GLM",
    "gpt-5.5": "GPT",
    "mimo-v2.5-free": "MiMo",
}
COLORS = {
    "claude-sonnet-4-6": "#2A9D6F",
    "deepseek-v4-flash-free": "#E69F00",
    "glm-5.2": "#D45A87",
    "gpt-5.5": "#7657A6",
    "mimo-v2.5-free": "#3F7FBF",
}

PHASES = ("R1", "R2", "R3", "R4", "R5", "R6")
PHASE_LABELS = ("P1", "P2", "P3", "P4", "P5", "P6")
PHASE_MAX = np.array((15.0, 15.0, 15.0, 15.0, 20.0, 20.0))
PANEL_SPECS = (
    ("All CVEs", None),
    ("Buffer Overflow", "Buffer Overflow"),
    ("Command Injection", "Command Injection"),
    ("Authentication Bypass", "Authentication Bypass"),
)
WALL_ALPHA = 0.105

CLASS_MARKERS = {
    "Buffer Overflow": (
        "buffer overflow",
        "cwe-120",
        "cwe-121",
        "cwe-122",
        "cwe-787",
    ),
    "Command Injection": ("command injection", "os command", "cwe-77", "cwe-78"),
    "Authentication Bypass": (
        "authenticat",
        "unauthenticated",
        "access control",
        "cwe-284",
        "cwe-287",
        "cwe-288",
        "cwe-306",
        "cwe-798",
        "cwe-912",
    ),
}


@dataclass(frozen=True)
class RunRecord:
    cve: str
    model: str
    run: int
    plan: float
    phases: tuple[float, ...]
    reported_task: float
    reported_overall: float

    @property
    def phase_task(self) -> float:
        return float(sum(self.phases))


def parse_score_table(path: Path) -> list[RunRecord]:
    records: list[RunRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if len(fields) != 14 or not fields[0].startswith("CVE-"):
            continue
        if fields[1] not in MODELS or fields[2] not in {"1", "2", "3"}:
            continue
        try:
            numeric = [float(value) for value in fields[3:]]
        except ValueError:
            continue
        records.append(
            RunRecord(
                cve=fields[0],
                model=fields[1],
                run=int(fields[2]),
                plan=numeric[0],
                phases=tuple(numeric[2:8]),
                reported_task=numeric[8],
                reported_overall=numeric[10],
            )
        )
    if len(records) != 450:
        raise ValueError(f"Expected 450 score rows, found {len(records)} in {path}")
    keys = Counter((row.cve, row.model) for row in records)
    invalid = [key for key, count in keys.items() if count != 3]
    if len(keys) != 150 or invalid:
        raise ValueError(f"Expected 150 cells with three runs each; invalid={invalid}")
    return records


def read_metadata(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    metadata = {row["cve_id"]: row for row in rows}
    if len(rows) != 30 or len(metadata) != 30:
        raise ValueError(f"Expected 30 unique metadata rows, found {len(metadata)}")
    counts = Counter(row["vulnerability_class"] for row in rows)
    expected = {
        "Buffer Overflow": 10,
        "Command Injection": 10,
        "Authentication Bypass": 10,
    }
    if dict(counts) != expected:
        raise ValueError(f"Unexpected vulnerability-class balance: {dict(counts)}")
    return metadata


def _json_number(
    value: object, label: str, default: float | None = None
) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if default is not None:
        return float(default)
    raise ValueError(f"Expected numeric {label}, found {value!r}")


def validate_evaluation_jsons(
    eval_root: Path, records: list[RunRecord]
) -> tuple[int, list[str]]:
    """Cross-check the flat table against all skill-format evaluation JSONs."""
    record_map = {(row.cve, row.model, row.run): row for row in records}
    json_paths = sorted(eval_root.glob("CVE-*/*/[123]/evaluation-CVE-*.json"))
    if len(json_paths) != len(records):
        raise ValueError(
            f"Expected {len(records)} evaluation JSONs, found {len(json_paths)} in {eval_root}"
        )

    warnings: list[str] = []
    seen: set[tuple[str, str, int]] = set()
    for json_path in json_paths:
        relative = json_path.relative_to(eval_root)
        cve, model, run_text, _ = relative.parts
        key = (cve, model, int(run_text))
        if key not in record_map:
            raise ValueError(f"Evaluation JSON has no score-table row: {relative}")
        if key in seen:
            raise ValueError(f"Duplicate evaluation JSON for {key}")
        seen.add(key)

        with json_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        plan = data.get("plan_score", {})
        task = data.get("task_score", {})
        record = record_map[key]
        plan_total = _json_number(plan.get("total"), f"{key} plan total")
        defaulted_fields: list[str] = []
        if not isinstance(task.get("total"), (int, float)):
            defaulted_fields.append("Task")
        task_total = _json_number(task.get("total"), f"{key} task total", default=0.0)
        overall = _json_number(data.get("overall_score"), f"{key} overall score")

        if not np.isclose(plan_total, record.plan, atol=0.051):
            raise ValueError(f"{key}: JSON plan {plan_total} != summary {record.plan}")
        if not np.isclose(task_total, record.reported_task, atol=0.051):
            raise ValueError(
                f"{key}: JSON task {task_total} != summary {record.reported_task}"
            )
        if not np.isclose(overall, record.reported_overall, atol=0.051):
            raise ValueError(
                f"{key}: JSON overall {overall} != summary {record.reported_overall}"
            )

        phase_scores: list[float] = []
        for index, (phase_name, phase_max) in enumerate(
            zip(PHASES, PHASE_MAX, strict=True), start=1
        ):
            phase = task.get(f"Phase {index}", task.get(phase_name, {}))
            if not isinstance(phase, dict):
                phase = {}
            if not isinstance(phase.get("score"), (int, float)):
                defaulted_fields.append(phase_name)
            phase_score = _json_number(
                phase.get("score"), f"{key} {phase_name} score", default=0.0
            )
            if phase_score < 0 or phase_score > phase_max:
                raise ValueError(
                    f"{key}: {phase_name}={phase_score} outside 0..{phase_max}"
                )
            phase_scores.append(phase_score)
            item_scores = phase.get("item_scores", {})
            if not isinstance(item_scores, dict):
                raise ValueError(f"{key}: invalid {phase_name} item_scores")
            item_sum = sum(
                _json_number(item.get("score"), f"{key} {phase_name}/{item_name}", default=0.0)
                for item_name, item in item_scores.items()
                if isinstance(item, dict)
            )
            if not np.isclose(phase_score, item_sum, atol=0.01):
                warnings.append(
                    f"{cve} / {model} / run {run_text}: {phase_name} "
                    f"score={phase_score:.1f}, checklist sum={item_sum:.1f}"
                )

        if not np.allclose(phase_scores, record.phases, atol=0.051):
            raise ValueError(
                f"{key}: JSON phases {phase_scores} != summary {record.phases}"
            )
        phase_sum = float(sum(phase_scores))
        if not np.isclose(task_total, phase_sum, atol=0.01):
            default_note = (
                f"; skill-defaulted missing fields={','.join(defaulted_fields)}"
                if defaulted_fields
                else ""
            )
            warnings.append(
                f"{cve} / {model} / run {run_text}: reported Task={task_total:.1f}, "
                f"phase sum={phase_sum:.1f}{default_note}"
            )

        breakdown = data.get("weighted_score_breakdown", {})
        if isinstance(breakdown, dict):
            plan_weighted = _json_number(
                breakdown.get("plan_weighted_score"), f"{key} weighted plan"
            )
            task_weighted = _json_number(
                breakdown.get("task_weighted_score"), f"{key} weighted task"
            )
            if not np.isclose(overall, plan_weighted + task_weighted, atol=0.01):
                warnings.append(
                    f"{cve} / {model} / run {run_text}: Overall={overall:.1f}, "
                    f"weighted sum={plan_weighted + task_weighted:.1f}"
                )

    if seen != set(record_map):
        missing = sorted(set(record_map) - seen)
        raise ValueError(f"Score-table rows missing evaluation JSONs: {missing}")
    return len(json_paths), warnings


def validate_metadata_groundtruth(
    metadata: dict[str, dict[str, str]], groundtruth_root: Path
) -> int:
    """Confirm every panel label is supported by the local ground-truth dossier."""
    issues: list[str] = []
    for cve, row in metadata.items():
        info_path = groundtruth_root / cve / "info.txt"
        if not info_path.is_file():
            issues.append(f"{cve}: missing {info_path}")
            continue
        text = info_path.read_text(encoding="utf-8", errors="replace").lower()
        category = row["vulnerability_class"]
        markers = CLASS_MARKERS.get(category, ())
        if not markers or not any(marker in text for marker in markers):
            issues.append(f"{cve}: {category!r} is not supported by info.txt")
    if issues:
        raise ValueError("Ground-truth class validation failed: " + "; ".join(issues))
    return len(metadata)

def select_best_task_runs(records: list[RunRecord]) -> tuple[list[RunRecord], list[RunRecord]]:
    grouped: dict[tuple[str, str], list[RunRecord]] = defaultdict(list)
    for record in records:
        grouped[(record.cve, record.model)].append(record)

    selected: list[RunRecord] = []
    for group in grouped.values():
        # Draft policy: recompute Task as R1+...+R6, then use the smallest
        # run id as a deterministic tie breaker.
        selected.append(sorted(group, key=lambda row: (-row.phase_task, row.run))[0])
    selected.sort(key=lambda row: (row.cve, MODELS.index(row.model)))

    corrections = [
        record
        for record in records
        if not np.isclose(record.phase_task, record.reported_task, atol=1e-8)
    ]
    return selected, corrections


def aggregate_phase_scores(
    selected: list[RunRecord], metadata: dict[str, dict[str, str]]
) -> tuple[dict[str, dict[str, np.ndarray]], dict[str, int]]:
    selected_cves = {record.cve for record in selected}
    if selected_cves != set(metadata):
        missing = sorted(selected_cves - set(metadata))
        extra = sorted(set(metadata) - selected_cves)
        raise ValueError(f"Metadata/score CVEs differ; missing={missing}, extra={extra}")

    grouped: dict[tuple[str, str], list[np.ndarray]] = defaultdict(list)
    panel_sizes: dict[str, int] = {}
    for title, category in PANEL_SPECS:
        panel_cves = {
            cve
            for cve, row in metadata.items()
            if category is None or row["vulnerability_class"] == category
        }
        panel_sizes[title] = len(panel_cves)
        for record in selected:
            if record.cve in panel_cves:
                normalized = np.asarray(record.phases, dtype=float) / PHASE_MAX * 100.0
                grouped[(title, record.model)].append(normalized)

    aggregated: dict[str, dict[str, np.ndarray]] = {}
    for title, _ in PANEL_SPECS:
        aggregated[title] = {}
        for model in MODELS:
            rows = grouped[(title, model)]
            if len(rows) != panel_sizes[title]:
                raise ValueError(
                    f"{title}/{model}: expected {panel_sizes[title]} CVEs, found {len(rows)}"
                )
            aggregated[title][model] = np.mean(np.vstack(rows), axis=0)
    return aggregated, panel_sizes


def write_audit_outputs(
    output_dir: Path,
    selected: list[RunRecord],
    corrections: list[RunRecord],
    metadata: dict[str, dict[str, str]],
    aggregated: dict[str, dict[str, np.ndarray]],
    panel_sizes: dict[str, int],
    summary_path: Path,
    eval_root: Path,
    groundtruth_root: Path,
    evaluation_json_count: int,
    groundtruth_count: int,
    skill_warnings: list[str],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "selected_best_task_runs.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "cve_id",
                "vulnerability_class",
                "model",
                "selected_run",
                "reported_task",
                "recomputed_task",
                *PHASES,
            ]
        )
        for record in selected:
            writer.writerow(
                [
                    record.cve,
                    metadata[record.cve]["vulnerability_class"],
                    record.model,
                    record.run,
                    f"{record.reported_task:.1f}",
                    f"{record.phase_task:.1f}",
                    *(f"{value:.1f}" for value in record.phases),
                ]
            )

    with (output_dir / "aggregated_phase_scores.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(["panel", "n_cves", "model", "phase", "normalized_score_pct"])
        for title, _ in PANEL_SPECS:
            for model in MODELS:
                for phase, value in zip(PHASES, aggregated[title][model], strict=True):
                    writer.writerow([title, panel_sizes[title], model, phase, f"{value:.3f}"])

    category_counts = Counter(row["vulnerability_class"] for row in metadata.values())
    lines = [
        "REPROBENCH 3D PHASE-TRAJECTORY DATA AUDIT",
        "",
        "Scoring specification: reprobench/skills/reprobench-scoring/SKILL.md",
        f"Source summary: {summary_path.resolve().relative_to(ROOT).as_posix()}",
        f"Evaluation JSON root: {eval_root.resolve().relative_to(ROOT).as_posix()}",
        f"Ground-truth root: {groundtruth_root.resolve().relative_to(ROOT).as_posix()}",
        "",
        "Selection policy: maximize skill-consistent Task = R1+...+R6; ties use smallest run id.",
        f"Score-table rows parsed: {len(selected) * 3}",
        f"Evaluation JSON files checked and matched: {evaluation_json_count}",
        f"Selected CVE/model rows: {len(selected)}",
        f"Ground-truth class labels verified: {groundtruth_count}/{len(metadata)}",
        "Class counts: " + ", ".join(
            f"{key}={value}" for key, value in sorted(category_counts.items())
        ),
        f"Rows whose reported Task differs from R1+...+R6: {len(corrections)}",
    ]
    for record in corrections:
        lines.append(
            f"  {record.cve} / {record.model} / run {record.run}: "
            f"reported={record.reported_task:.1f}, recomputed={record.phase_task:.1f}"
        )
    lines.extend(["", f"Skill consistency warnings: {len(skill_warnings)}"])
    lines.extend(f"  {warning}" for warning in skill_warnings)
    lines.extend(
        [
            "",
            "Plotting correction policy:",
            "  Run selection uses the recomputed six-phase sum required by the scoring skill.",
            "  Plotted phase values always come from the six phase objects, not the reported Task field.",
        ]
    )
    (output_dir / "data_audit.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

def add_vertical_wall(ax, x: np.ndarray, y: float, z: np.ndarray, color: str) -> None:
    quads = [
        [
            (x[index], y, 0.0),
            (x[index + 1], y, 0.0),
            (x[index + 1], y, z[index + 1]),
            (x[index], y, z[index]),
        ]
        for index in range(len(x) - 1)
    ]
    ax.add_collection3d(
        Poly3DCollection(
            quads,
            facecolor=color,
            edgecolor="none",
            linewidth=0,
            alpha=WALL_ALPHA,
            zorder=1,
        )
    )


def style_3d_axis(ax, panel_index: int, title: str, n_cves: int) -> None:
    ax.set_xlim(0.75, 6.25)
    ax.set_ylim(0.35, 5.65)
    ax.set_zlim(0.0, 100.0)
    ax.set_xticks(np.arange(1, 7))
    ax.set_xticklabels(PHASE_LABELS)
    ax.set_yticks(np.arange(1, 6))
    ax.set_zticks((0, 25, 50, 75, 100))

    if panel_index == 0:
        ax.set_yticklabels([LANE_LABELS[model] for model in PLOT_MODELS])
        ax.set_ylabel("Model", labelpad=6)
        ax.set_zlabel("Normalized phase score (%)", labelpad=4)
    else:
        ax.set_yticklabels(("", "", "", "", ""))

    ax.set_xlabel("Reproduction Phase", labelpad=-1)
    ax.view_init(elev=23.5, azim=-59, roll=0)
    ax.set_proj_type("persp", focal_length=0.95)
    ax.set_box_aspect((1.38, 0.92, 0.98))

    pane = (1.0, 1.0, 1.0, 0.0)
    grid = {
        "color": (0.68, 0.68, 0.68, 0.50),
        "linewidth": 0.45,
        "linestyle": "-",
    }
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.set_pane_color(pane)
        axis._axinfo["grid"].update(grid)
        axis.line.set_color("#777777")
        axis.line.set_linewidth(0.65)

    ax.tick_params(axis="x", which="major", pad=-2, labelsize=7.5, colors="#555555")
    ax.tick_params(axis="y", which="major", pad=-1, labelsize=6.6, colors="#555555")
    ax.tick_params(axis="z", which="major", pad=0, labelsize=7.0, colors="#555555")
    ax.xaxis.label.set_color("#333333")
    ax.yaxis.label.set_color("#333333")
    ax.zaxis.label.set_color("#333333")
    ax.xaxis.label.set_size(8.1)
    ax.yaxis.label.set_size(8.0)
    ax.zaxis.label.set_size(8.0)
    ax.set_title(
        f"({chr(97 + panel_index)}) {title} (n={n_cves})",
        fontsize=9.5,
        pad=-1,
        color="#222222",
    )


def build_figure(
    aggregated: dict[str, dict[str, np.ndarray]], panel_sizes: dict[str, int]
):
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ("Arial", "DejaVu Sans"),
            "axes.linewidth": 0.65,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )

    fig = plt.figure(figsize=(15.4, 3.7), facecolor="white")
    axes = [
        fig.add_subplot(1, 4, index + 1, projection="3d", computed_zorder=False)
        for index in range(4)
    ]
    x = np.arange(1, 7, dtype=float)
    depths = {model: float(index + 1) for index, model in enumerate(PLOT_MODELS)}

    for panel_index, ((title, _), ax) in enumerate(zip(PANEL_SPECS, axes, strict=True)):
        for model in reversed(PLOT_MODELS):
            add_vertical_wall(ax, x, depths[model], aggregated[title][model], COLORS[model])
        for model in reversed(PLOT_MODELS):
            values = aggregated[title][model]
            ax.plot(
                x,
                np.full_like(x, depths[model]),
                values,
                color=COLORS[model],
                linewidth=1.85,
                marker="o",
                markersize=4.15,
                markerfacecolor=COLORS[model],
                markeredgecolor="white",
                markeredgewidth=0.52,
                solid_capstyle="round",
                zorder=10,
            )
        style_3d_axis(ax, panel_index, title, panel_sizes[title])

    handles = [
        Line2D(
            [0],
            [0],
            color=COLORS[model],
            marker="o",
            markersize=5.0,
            markeredgecolor="white",
            markeredgewidth=0.5,
            linewidth=1.9,
            label=DISPLAY_NAMES[model],
        )
        for model in PLOT_MODELS
    ]
    fig.legend(
        handles=handles,
        labels=[DISPLAY_NAMES[model] for model in PLOT_MODELS],
        loc="lower center",
        bbox_to_anchor=(0.5, 0.025),
        ncol=5,
        frameon=False,
        fontsize=8.9,
        handlelength=2.1,
        handletextpad=0.5,
        columnspacing=1.55,
    )
    fig.subplots_adjust(left=0.018, right=0.992, top=0.94, bottom=0.235, wspace=-0.075)
    return fig


def render(
    summary_path: Path,
    eval_root: Path,
    metadata_path: Path,
    groundtruth_root: Path,
    output_dir: Path,
    dpi: int,
) -> list[Path]:
    records = parse_score_table(summary_path)
    evaluation_json_count, skill_warnings = validate_evaluation_jsons(eval_root, records)
    metadata = read_metadata(metadata_path)
    groundtruth_count = validate_metadata_groundtruth(metadata, groundtruth_root)
    selected, corrections = select_best_task_runs(records)
    aggregated, panel_sizes = aggregate_phase_scores(selected, metadata)
    write_audit_outputs(
        output_dir,
        selected,
        corrections,
        metadata,
        aggregated,
        panel_sizes,
        summary_path,
        eval_root,
        groundtruth_root,
        evaluation_json_count,
        groundtruth_count,
        skill_warnings,
    )

    fig = build_figure(aggregated, panel_sizes)
    outputs = [
        output_dir / "four_panel_3d_trajectories.png",
        output_dir / "four_panel_3d_trajectories.pdf",
        output_dir / "four_panel_3d_trajectories.svg",
        output_dir / "preview.jpg",
    ]
    for output in outputs:
        kwargs = {"bbox_inches": "tight", "pad_inches": 0.04, "facecolor": "white"}
        if output.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            kwargs["dpi"] = 180 if output.suffix.lower() in {".jpg", ".jpeg"} else dpi
        fig.savefig(output, **kwargs)
        if output.suffix.lower() == ".svg":
            svg_text = output.read_text(encoding="utf-8")
            with output.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n")
    plt.close(fig)
    return outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--eval-root", type=Path, default=DEFAULT_EVAL_ROOT)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--groundtruth", type=Path, default=DEFAULT_GROUNDTRUTH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dpi", type=int, default=420)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    for path in render(
        args.summary,
        args.eval_root,
        args.metadata,
        args.groundtruth,
        args.output_dir,
        args.dpi,
    ):
        print(path)
