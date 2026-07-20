# ReproBench four-panel 3D phase trajectories

This directory contains the real-data ReproBench phase-trajectory figure.
It is generated from all 450 rows in
reprobench/data/evaluation_summary.txt and the provisional, source-linked
CVE class map in figure/data/reprobench_cve_metadata.csv.

## Aggregation policy

For each CVE/model pair, the script recomputes Task as P1+...+P6, selects
the run with the highest recomputed Task, and breaks ties using the smallest
run id. It then normalizes P1--P4 by 15 and P5--P6 by 20, and averages the
result over the CVEs in each panel.

Panels are All CVEs (n=30), Buffer Overflow (n=10), Command Injection
(n=10), and Authentication Bypass (n=10).

## Re-render

From the repository root:

    .\figure\tools\python311\python.exe .\figure\scripts\plot_3d_method_trajectories.py

## Audit artifacts

- aggregated_phase_scores.csv: every plotted point.
- selected_best_task_runs.csv: the 150 selected CVE/model rows.
- data_audit.txt: counts, temporary correction policy, and source warnings.
- four_panel_3d_trajectories.{png,pdf,svg}: publication outputs.

The CVE labels and three source-data inconsistencies are intentionally
documented as provisional so they can be manually verified before submission.
