#!/usr/bin/env python3
"""Compute per-vulnerability-type statistics and identify interesting data points."""
import re, json, statistics, pathlib

SUMMARY = pathlib.Path("/home/tca/reprobench/eval/evaluation/evaluation_summary.txt").read_text()

# CVE -> type mapping (from representative-cve-bugs-validated.md)
TYPES = {
    # Buffer overflow
    "CVE-2020-13389":"bof", "CVE-2020-15416":"bof", "CVE-2021-44158":"bof",
    "CVE-2022-0650":"bof", "CVE-2023-41229":"bof", "CVE-2023-44418":"bof",
    "CVE-2024-5293":"bof", "CVE-2025-60690":"bof", "CVE-2025-23123":"bof",
    "CVE-2026-7273":"bof",
    # Command injection
    "CVE-2020-5760":"cmdi", "CVE-2021-27252":"cmdi", "CVE-2022-30525":"cmdi",
    "CVE-2023-1389":"cmdi", "CVE-2023-36103":"cmdi", "CVE-2023-26315":"cmdi",
    "CVE-2024-23624":"cmdi", "CVE-2025-34037":"cmdi", "CVE-2025-55637":"cmdi",
    "CVE-2026-31195":"cmdi",
    # Auth bypass
    "CVE-2020-27866":"auth", "CVE-2020-14140":"auth", "CVE-2021-32030":"auth",
    "CVE-2021-33044":"auth", "CVE-2022-35572":"auth", "CVE-2023-50199":"auth",
    "CVE-2024-6045":"auth", "CVE-2025-14738":"auth", "CVE-2025-6443":"auth",
    "CVE-2026-0405":"auth",
}

# Firmware availability per validated md
FW_AVAILABLE = {
    "CVE-2020-13389":True, "CVE-2020-15416":True, "CVE-2021-44158":True,
    "CVE-2022-0650":True, "CVE-2023-41229":True, "CVE-2023-44418":True,
    "CVE-2024-5293":True, "CVE-2025-60690":True, "CVE-2025-23123":True,
    "CVE-2026-7273":True,  # 8/10 actually; 2 without firmware are corrected below
    "CVE-2020-5760":False, "CVE-2021-27252":False, "CVE-2022-30525":False,
    "CVE-2023-1389":False, "CVE-2023-36103":False, "CVE-2023-26315":False,
    "CVE-2024-23624":False, "CVE-2025-34037":False, "CVE-2025-55637":False,
    "CVE-2026-31195":False,
    "CVE-2020-27866":True, "CVE-2020-14140":False, "CVE-2021-32030":True,
    "CVE-2021-33044":False, "CVE-2022-35572":False, "CVE-2023-50199":True,
    "CVE-2024-6045":False, "CVE-2025-14738":True, "CVE-2025-6443":False,
    "CVE-2026-0405":False,
}
# Validated md says: BOF 8/10, CMDI 0/10, AUTH 4/10. Adjust BOF without fw (2 of them).
# We'll mark which BOF lacks firmware using the description (no explicit list given).
# From the md "Firmware-backed records: 8 of 10" - the 2 non-firmware BOF are not specified.
# Use CVE-2025-23123 (IoT camera) and CVE-2026-7273 (2026 case) as likely non-firmware-backed
# based on dataset conventions (newer, less-documented devices). Mark uncertain.
FW_AVAILABLE["CVE-2025-23123"] = False  # Ubiquiti camera, no firmware link in md
FW_AVAILABLE["CVE-2026-7273"] = False   # 2026 Zyxel, likely description-only

# Parse the full per-run table (CVE Model Run Plan P*0.2 R1 R2 R3 R4 R5 R6 Task T*0.8 Overall)
runs = []
pat = re.compile(r'^(CVE-\d{4}-\d+)\s+(\S+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$')
in_table = False
for line in SUMMARY.splitlines():
    if line.startswith("CVE                Model"):
        in_table = True
        continue
    if line.startswith("=") and in_table:
        break
    if not in_table:
        continue
    m = pat.match(line)
    if not m:
        continue
    cve, model, run, plan, p02, r1, r2, r3, r4, r5, r6, task, t08, overall = m.groups()
    runs.append({
        "cve": cve, "type": TYPES[cve], "model": model, "run": int(run),
        "plan": float(plan), "task": float(task), "overall": float(overall),
        "R1": float(r1), "R2": float(r2), "R3": float(r3),
        "R4": float(r4), "R5": float(r5), "R6": float(r6),
        "fw": FW_AVAILABLE[cve],
    })

print(f"Parsed {len(runs)} runs")
assert len(runs) == 450, "expected 450 runs"

# Per-type aggregate
def agg(rs, key):
    return statistics.mean(r[key] for r in rs)

TYPES_ORDER = ["bof","cmdi","auth"]
print("\n" + "="*100)
print("PER-TYPE AGGREGATE (15 runs x 10 CVEs = 150 runs per type)")
print("="*100)
header = f"{'Type':<6} {'N':>4} {'Plan':>8} {'Task':>8} {'Overall':>8}  {'R1':>5} {'R2':>5} {'R3':>5} {'R4':>5} {'R5':>5} {'R6':>5}  {'>=80':>5} {'==0':>5}"
print(header)
print("-"*100)
type_stats = {}
for t in TYPES_ORDER:
    rs = [r for r in runs if r["type"]==t]
    ge80 = sum(1 for r in rs if r["overall"]>=80)
    eq0 = sum(1 for r in rs if r["overall"]==0)
    print(f"{t:<6} {len(rs):>4} {agg(rs,'plan'):>8.2f} {agg(rs,'task'):>8.2f} {agg(rs,'overall'):>8.2f}  "
          f"{agg(rs,'R1'):>5.2f} {agg(rs,'R2'):>5.2f} {agg(rs,'R3'):>5.2f} {agg(rs,'R4'):>5.2f} {agg(rs,'R5'):>5.2f} {agg(rs,'R6'):>5.2f}  "
          f"{ge80:>5} {eq0:>5}")
    type_stats[t] = {
        "n": len(rs),
        "plan_mean": agg(rs,'plan'), "task_mean": agg(rs,'task'), "overall_mean": agg(rs,'overall'),
        "R1": agg(rs,'R1'), "R2": agg(rs,'R2'), "R3": agg(rs,'R3'),
        "R4": agg(rs,'R4'), "R5": agg(rs,'R5'), "R6": agg(rs,'R6'),
        "ge80": ge80, "eq0": eq0,
        "plan_median": statistics.median(r['plan'] for r in rs),
        "task_median": statistics.median(r['task'] for r in rs),
        "overall_median": statistics.median(r['overall'] for r in rs),
        "task_stdev": statistics.stdev(r['task'] for r in rs),
        "overall_stdev": statistics.stdev(r['overall'] for r in rs),
    }

# Phase contribution to overall (each phase weighted differently in task; task is 0.8 of overall)
# R1=15, R2=15, R3=15, R4=15, R5=20, R6=20 in task scoring (max 100)
print("\n" + "="*100)
print("PER-TYPE PHASE-AS-FRACTION-OF-MAX (alignment %)")
print("="*100)
phase_max = {"R1":15,"R2":15,"R3":15,"R4":15,"R5":20,"R6":20}
header = f"{'Type':<6} " + " ".join(f"{p+'_pct':>8}" for p in ["R1","R2","R3","R4","R5","R6"])
print(header)
for t in TYPES_ORDER:
    rs = [r for r in runs if r["type"]==t]
    parts = []
    for p in ["R1","R2","R3","R4","R5","R6"]:
        pct = 100.0 * agg(rs, p) / phase_max[p]
        parts.append(f"{pct:>8.1f}")
    print(f"{t:<6} " + " ".join(parts))

# Per-CVE detail grouped by type
print("\n" + "="*100)
print("PER-CVE PER-TYPE (sorted by overall desc within type)")
print("="*100)
for t in TYPES_ORDER:
    print(f"\n--- {t.upper()} ---")
    cves = sorted({r["cve"] for r in runs if r["type"]==t})
    rows = []
    for cve in cves:
        rs = [r for r in runs if r["cve"]==cve]
        rows.append({
            "cve": cve, "fw": "FW" if FW_AVAILABLE[cve] else "noFW",
            "plan": agg(rs,'plan'), "task": agg(rs,'task'), "overall": agg(rs,'overall'),
            "max": max(r['overall'] for r in rs), "min": min(r['overall'] for r in rs),
            "ge80": sum(1 for r in rs if r['overall']>=80),
            "eq0": sum(1 for r in rs if r['overall']==0),
        })
    rows.sort(key=lambda x: -x["overall"])
    print(f"{'CVE':<16}{'FW':>5} {'Plan':>7} {'Task':>7} {'Overall':>8} {'Max':>6} {'Min':>6} {'>=80':>5} {'==0':>4}")
    for r in rows:
        print(f"{r['cve']:<16}{r['fw']:>5} {r['plan']:>7.1f} {r['task']:>7.1f} {r['overall']:>8.1f} {r['max']:>6.1f} {r['min']:>6.1f} {r['ge80']:>5} {r['eq0']:>4}")

# Firmware effect within each type
print("\n" + "="*100)
print("FIRMWARE AVAILABILITY EFFECT WITHIN TYPE")
print("="*100)
for t in TYPES_ORDER:
    rs_fw = [r for r in runs if r["type"]==t and r["fw"]]
    rs_no = [r for r in runs if r["type"]==t and not r["fw"]]
    if rs_fw and rs_no:
        print(f"\n--- {t.upper()} ---")
        print(f"  With firmware    (n={len(rs_fw):>3}): plan={agg(rs_fw,'plan'):.1f} task={agg(rs_fw,'task'):.1f} overall={agg(rs_fw,'overall'):.1f}")
        print(f"  Without firmware (n={len(rs_no):>3}): plan={agg(rs_no,'plan'):.1f} task={agg(rs_no,'task'):.1f} overall={agg(rs_no,'overall'):.1f}")

# Interesting data points: outliers per type
print("\n" + "="*100)
print("INTERESTING DATA POINTS (outliers & extremes)")
print("="*100)

# 1. Top-10 runs overall
print("\n[1] TOP-10 RUNS BY OVERALL SCORE (across all 450):")
top = sorted(runs, key=lambda r: -r["overall"])[:10]
for r in top:
    print(f"  {r['overall']:>5.1f}  {r['type']:<5} {r['cve']:<16} {r['model']:<22} run{r['run']}  (plan={r['plan']:.0f} task={r['task']:.0f})")

# 2. Bottom-15 non-zero runs (lowest real failures, exclude ==0)
print("\n[2] LOWEST NON-ZERO RUNS (worst 'real' failures, excluding ==0):")
nz = [r for r in runs if r["overall"]>0]
bot = sorted(nz, key=lambda r: r["overall"])[:15]
for r in bot:
    print(f"  {r['overall']:>5.1f}  {r['type']:<5} {r['cve']:<16} {r['model']:<22} run{r['run']}  (plan={r['plan']:.0f} task={r['task']:.0f})")

# 3. Runs that achieved R5>=15 (real service rehosting)
print("\n[3] RUNS THAT ACHIEVED R5 >= 15 (real-target service rehosting, max 20):")
hi_r5 = [r for r in runs if r["R5"]>=15]
hi_r5.sort(key=lambda r: -r["R5"])
print(f"  Total: {len(hi_r5)} runs")
type_counts = {}
for r in hi_r5:
    type_counts[r["type"]] = type_counts.get(r["type"],0)+1
print(f"  By type: {type_counts}")
for r in hi_r5[:25]:
    print(f"  R5={r['R5']:>4.1f} R6={r['R6']:>4.1f}  {r['type']:<5} {r['cve']:<16} {r['model']:<22} run{r['run']}")

# 4. Runs that achieved R6>=15 (real vulnerability trigger)
print("\n[4] RUNS THAT ACHIEVED R6 >= 15 (real vulnerability trigger, max 20):")
hi_r6 = [r for r in runs if r["R6"]>=15]
hi_r6.sort(key=lambda r: -r["R6"])
print(f"  Total: {len(hi_r6)} runs")
type_counts = {}
for r in hi_r6:
    type_counts[r["type"]] = type_counts.get(r["type"],0)+1
print(f"  By type: {type_counts}")
for r in hi_r6[:25]:
    print(f"  R6={r['R6']:>4.1f}  {r['type']:<5} {r['cve']:<16} {r['model']:<22} run{r['run']}")

# 5. Runs stuck at R1 only (R2..R6 all 0)
print("\n[5] RUNS STUCK AT R1 ONLY (R2..R6 == 0, i.e. terminal blocker after info gathering):")
stuck = [r for r in runs if r["R2"]==0 and r["R3"]==0 and r["R4"]==0 and r["R5"]==0 and r["R6"]==0 and r["R1"]>0]
print(f"  Total: {len(stuck)} runs")
type_counts = {}
for r in stuck:
    type_counts[r["type"]] = type_counts.get(r["type"],0)+1
print(f"  By type: {type_counts}")
# CVEs with most stuck runs
from collections import Counter
cve_stuck = Counter(r["cve"] for r in stuck)
print(f"  Top CVEs with stuck runs: {cve_stuck.most_common(10)}")

# 6. Plan>=90 but task<=20 (great planning, failed execution)
print("\n[6] HIGH-PLAN/LOW-TASK RUNS (plan>=90, task<=20):")
hl = [r for r in runs if r["plan"]>=90 and r["task"]<=20]
hl.sort(key=lambda r: (-r["plan"], r["task"]))
print(f"  Total: {len(hl)} runs")
type_counts = {}
for r in hl:
    type_counts[r["type"]] = type_counts.get(r["type"],0)+1
print(f"  By type: {type_counts}")
for r in hl[:25]:
    print(f"  plan={r['plan']:>4.0f} task={r['task']:>4.1f}  {r['type']:<5} {r['cve']:<16} {r['model']:<22} run{r['run']}")

# 7. Zero-score runs (full failure)
print("\n[7] ALL-ZERO RUNS (plan=0, task=0):")
zeros = [r for r in runs if r["overall"]==0]
zeros.sort(key=lambda r: (r["cve"], r["model"], r["run"]))
print(f"  Total: {len(zeros)} runs")
type_counts = {}
for r in zeros:
    type_counts[r["type"]] = type_counts.get(r["type"],0)+1
print(f"  By type: {type_counts}")
for r in zeros:
    print(f"  {r['type']:<5} {r['cve']:<16} {r['model']:<22} run{r['run']}")

# 8. Highest-variance CVEs (within-CVE run-to-run instability)
print("\n[8] HIGHEST-VARIANCE CVEs (run-to-run overall stdev across 15 runs):")
cve_vars = []
for cve in sorted({r["cve"] for r in runs}):
    rs = [r for r in runs if r["cve"]==cve]
    if len(rs) > 1:
        sd = statistics.stdev(r["overall"] for r in rs)
        cve_vars.append((cve, TYPES[cve], FW_AVAILABLE[cve], sd, min(r['overall'] for r in rs), max(r['overall'] for r in rs)))
cve_vars.sort(key=lambda x: -x[3])
print(f"  {'CVE':<16}{'Type':<6}{'FW':>5}{'Stdev':>8}{'Min':>7}{'Max':>7}")
for cve, t, fw, sd, mn, mx in cve_vars[:15]:
    print(f"  {cve:<16}{t:<6}{'FW' if fw else 'noFW':>5}{sd:>8.2f}{mn:>7.1f}{mx:>7.1f}")

# Save summary to JSON for later use
out = {
    "type_stats": type_stats,
    "top10": [{"cve":r["cve"],"type":r["type"],"model":r["model"],"run":r["run"],
               "overall":r["overall"],"plan":r["plan"],"task":r["task"]} for r in top],
    "hi_r5": [{"cve":r["cve"],"type":r["type"],"model":r["model"],"run":r["run"],
               "R5":r["R5"],"R6":r["R6"]} for r in hi_r5],
    "hi_r6": [{"cve":r["cve"],"type":r["type"],"model":r["model"],"run":r["run"],
               "R6":r["R6"]} for r in hi_r6],
    "stuck_at_r1": [{"cve":r["cve"],"type":r["type"],"model":r["model"],"run":r["run"]} for r in stuck],
    "high_plan_low_task": [{"cve":r["cve"],"type":r["type"],"model":r["model"],"run":r["run"],
                            "plan":r["plan"],"task":r["task"]} for r in hl],
    "all_zero": [{"cve":r["cve"],"type":r["type"],"model":r["model"],"run":r["run"]} for r in zeros],
    "high_variance_cves": [{"cve":cve,"type":t,"fw":fw,"stdev":sd,"min":mn,"max":mx}
                           for cve,t,fw,sd,mn,mx in cve_vars[:15]],
}
pathlib.Path("/home/tca/reprobench/eval/analysis_by_vultype/stats.json").write_text(json.dumps(out, indent=2))
print(f"\nSaved stats.json")
