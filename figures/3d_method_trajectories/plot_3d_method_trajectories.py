"""Render the ReproBench four-panel 3D phase-trajectory figure.

For each CVE/model pair, select the run with the largest recomputed task score
(P1+...+P6); ties use the smallest run id. Normalize phases by rubric maxima
before averaging over CVEs.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SUMMARY = ROOT / "reprobench" / "data" / "evaluation_summary.txt"
DEFAULT_METADATA = ROOT / "figure" / "data" / "reprobench_cve_metadata.csv"
DEFAULT_OUTPUT_DIR = ROOT / "figure" / "results" / "3d_method_trajectories"

MODELS = (
    "claude-sonnet-4-6",
    "deepseek-v4-flash-free",
    "glm-5.2",
    "gpt-5.5",
    "mimo-v2.5-free",
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

PHASES = ("P1", "P2", "P3", "P4", "P5", "P6")
PHASE_MAX = np.array((15.0, 15.0, 15.0, 15.0, 20.0, 20.0))
PANEL_SPECS = (
    ("All CVEs", None),
    ("Buffer Overflow", "Buffer Overflow"),
    ("Command Injection", "Command Injection"),
    ("Authentication Bypass", "Authentication Bypass"),
)
WALL_ALPHA = 0.105


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


def select_best_task_runs(records: list[RunRecord]) -> tuple[list[RunRecord], list[RunRecord]]:
    grouped: dict[tuple[str, str], list[RunRecord]] = defaultdict(list)
    for record in records:
        grouped[(record.cve, record.model)].append(record)

    selected: list[RunRecord] = []
    for group in grouped.values():
        # Draft policy: recompute Task as P1+...+P6, then use the smallest
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
        "Selection policy: maximize recomputed Task = P1+...+P6; ties use smallest run id.",
        f"Parsed runs: {len(selected) * 3}",
        f"Selected CVE/model rows: {len(selected)}",
        f"Metadata CVEs: {len(metadata)}",
        "Class counts: " + ", ".join(
            f"{key}={value}" for key, value in sorted(category_counts.items())
        ),
        f"Rows whose reported Task differs from P1+...+P6: {len(corrections)}",
    ]
    for record in corrections:
        lines.append(
            f"  {record.cve} / {record.model} / run {record.run}: "
            f"reported={record.reported_task:.1f}, recomputed={record.phase_task:.1f}"
        )
    lines.extend(
        [
            "",
            "Known source warning not resolvable from the flat table:",
            "  CVE-2023-26315 / deepseek-v4-flash-free / run 2: R4 differs from checklist-item sum.",
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
    ax.set_xticklabels(PHASES)
    ax.set_yticks(np.arange(1, 6))
    ax.set_zticks((0, 25, 50, 75, 100))

    if panel_index == 0:
        ax.set_yticklabels([LANE_LABELS[model] for model in MODELS])
        ax.set_ylabel("Model", labelpad=6)
        ax.set_zlabel("Normalized phase score (%)", labelpad=4)
    else:
        ax.set_yticklabels(("", "", "", "", ""))

    ax.set_xlabel("Pipeline phase", labelpad=-1)
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
    depths = {model: float(index + 1) for index, model in enumerate(MODELS)}

    for panel_index, ((title, _), ax) in enumerate(zip(PANEL_SPECS, axes, strict=True)):
        for model in reversed(MODELS):
            add_vertical_wall(ax, x, depths[model], aggregated[title][model], COLORS[model])
        for model in reversed(MODELS):
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
        for model in MODELS
    ]
    fig.legend(
        handles=handles,
        labels=[DISPLAY_NAMES[model] for model in MODELS],
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
    metadata_path: Path,
    output_dir: Path,
    dpi: int,
) -> list[Path]:
    records = parse_score_table(summary_path)
    metadata = read_metadata(metadata_path)
    selected, corrections = select_best_task_runs(records)
    aggregated, panel_sizes = aggregate_phase_scores(selected, metadata)
    write_audit_outputs(output_dir, selected, corrections, metadata, aggregated, panel_sizes)

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
    plt.close(fig)
    return outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dpi", type=int, default=420)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    for path in render(args.summary, args.metadata, args.output_dir, args.dpi):
        print(path)
