# ReproBench four-panel 3D phase trajectories

This directory contains the publication outputs for the ReproBench phase-trajectory figure.

## Source of truth

The plotted scores come from the updated summary committed to the inner
`reprobench` repository:

- `reprobench/data/evaluation_summary.txt`: the 450-run published score table
  used for run selection and every plotted phase value.
- `data/reprobench/eval/repro_groundtruth/CVE-*/info.txt`: workspace-level local
  ground-truth dossiers used only to verify the three vulnerability classes.
- `figure/data/reprobench_cve_metadata.csv`: the workspace-level balanced
  30-CVE panel map, cross-checked against the local dossiers.

The scoring contract is `reprobench/skills/reprobench-scoring/SKILL.md`.

## Aggregation policy

For each CVE/model pair, the script recomputes skill-consistent Task as
`R1+...+R6`, selects the highest-scoring run, and breaks ties using the smallest
run id. It normalizes R1--R4 by 15 and R5--R6 by 20 before averaging over CVEs.

Panels are All CVEs (n=30), Buffer Overflow (n=10), Command Injection (n=10),
and Authentication Bypass (n=10).

Before rendering, the script checks that the inner summary contains exactly
450 rows and 150 CVE/model cells with three runs each. It recomputes Task from
the six phase totals and verifies every class label against the corresponding
local ground-truth dossier. The outer workspace's older evaluation JSON set is
deliberately not used to validate the updated inner summary.

## Re-render

From the workspace root:

    .\figure\tools\python311\python.exe .\figure\scripts\plot_3d_method_trajectories.py

The default output directory is this directory:
`reprobench/figures/3d_method_trajectories`.

## Audit artifacts

- `FIGURE_EXPLANATION.md`: figure meaning, data provenance, aggregation, and interpretation guidance.
- `aggregated_phase_scores.csv`: every plotted point.
- `selected_best_task_runs.csv`: the 150 selected CVE/model rows.
- `data_audit.txt`: source paths, counts, selection policy, and consistency warnings.
- `four_panel_3d_trajectories.{png,pdf,svg}` and `preview.jpg`: publication outputs.
