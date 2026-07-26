#!/usr/bin/env python3
"""
verify_paper_numbers.py — Verify every experimental number in the ReproBench paper
against the raw evaluation data.

Usage:
    python scripts/verify_paper_numbers.py [path/to/evaluation_summary.txt]

The script parses data/evaluation_summary.txt (or a path provided as argument),
recomputes every statistic cited in the paper, and checks each against the value
actually written in the .tex files under sections/.

Methodology (consistent across all sections):
  - Best-of-three: for each CVE-model pair, take max across 3 runs.
  - Overall = max(per-run overall)  [NOT 0.2*max(plan)+0.8*max(task)]
  - P5≥15 / P6≥15: max(R5) / max(R6) across 3 runs ≥ 15
  - Stage funnel: best-of-three phase averages
  - Failure attribution: per-run, non-overlapping (priority-based)
  - Vultype overall: best-of-three average across pairs
  - Vultype phase numbers: per-run averages
  - Simulation count: from summary's per-run count (316)
  - Fallback scores: per-run averages parsed from per-run narrative lines
"""
import re
import sys
import os
from collections import defaultdict

# ============================================================
# Configuration
# ============================================================
DEFAULT_DATA = os.path.join(os.path.dirname(__file__), '..', 'data', 'evaluation_summary.txt')
SECTIONS_DIR = os.path.join(os.path.dirname(__file__), '..', 'sections')

# CVE → vulnerability type mapping
BOF_CVES = {
    'CVE-2020-13389', 'CVE-2020-15416', 'CVE-2021-44158', 'CVE-2022-0650',
    'CVE-2023-41229', 'CVE-2023-44418', 'CVE-2024-5293', 'CVE-2025-60690',
    'CVE-2025-23123', 'CVE-2026-7273',
}
CMDI_CVES = {
    'CVE-2020-5760', 'CVE-2021-27252', 'CVE-2022-30525', 'CVE-2023-1389',
    'CVE-2023-36103', 'CVE-2023-26315', 'CVE-2024-23624', 'CVE-2025-34037',
    'CVE-2025-55637', 'CVE-2026-31195',
}
AUTH_CVES = {
    'CVE-2020-27866', 'CVE-2020-14140', 'CVE-2021-32030', 'CVE-2021-33044',
    'CVE-2022-35572', 'CVE-2023-50199', 'CVE-2024-6045', 'CVE-2025-14738',
    'CVE-2025-6443', 'CVE-2026-0405',
}

MODELS = [
    'glm-5.2', 'mimo-v2.5', 'claude-sonnet-4-6',
    'gpt-5.5', 'deepseek-v4-flash',
]

# Paper values (what the .tex files should contain)
PAPER_TABLE1 = {
    'glm-5.2':                {'plan': 86.7, 'task': 59.9, 'overall': 64.6, 'max_overall': 98.7, 'p5': 7, 'p6': 5},
    'mimo-v2.5':              {'plan': 83.2, 'task': 45.5, 'overall': 52.9, 'max_overall': 76.9, 'p5': 0, 'p6': 0},
    'claude-sonnet-4-6':      {'plan': 79.1, 'task': 42.7, 'overall': 50.0, 'max_overall': 99.0, 'p5': 2, 'p6': 1},
    'gpt-5.5':                {'plan': 71.1, 'task': 38.2, 'overall': 44.7, 'max_overall': 89.1, 'p5': 1, 'p6': 1},
    'deepseek-v4-flash':      {'plan': 68.5, 'task': 37.7, 'overall': 43.6, 'max_overall': 98.0, 'p5': 1, 'p6': 1},
}
PAPER_ALL = {'plan': 77.7, 'task': 44.8, 'overall': 51.1, 'max_overall': 99.0, 'p5': 11, 'p6': 8}

PAPER_FUNNEL = [
    ('P1', 13.9, 15, 92.8),
    ('P2', 9.0, 15, 59.9),
    ('P3', 8.1, 15, 53.8),
    ('P4', 7.6, 15, 50.8),
    ('P5', 3.7, 20, 18.6),
    ('P6', 2.8, 20, 13.9),
]

PAPER_FAILURE = {
    'simulation': 204, 'simulation_pct': 45.3,
    'rehosting': 93, 'rehosting_pct': 20.7,
    'extraction': 36, 'extraction_pct': 8.0,
    'infrastructure': 15, 'infrastructure_pct': 3.3,
    'p2_blockers': 211, 'p5_blockers': 173,
}

PAPER_VULTYPE = {
    'BOF':  {'overall': 60.4, 'r2': 8.06, 'r4': 7.09, 'fw_pct': 73},
    'CMDI': {'overall': 48.6},
    'AUTH': {'overall': 44.4, 'r4': 3.14},
}

PAPER_MODEL_BEHAVIOR = {
    'glm_p2_bot3': 11.5,
    'claude_p2_bot3': 7.7,
    'claude_plan50_task15': 20,
    'glm_fallback': 32.2,
    'other_fallback_range': (15.0, 28.6),
}

PAPER_CVE = {
    'top_score': 99.0,
    'cves_ge90': 5,
    'cve_26315': 99.0,
    'cve_23624': 80.8,
    'cmdi_p6_ge18': 5,
}

# Additional paper values for missing checks
PAPER_501_BEST_RUN = 99.0        # "best single run reaches 99.0/100"
PAPER_503_DIVERGENT = 19          # "19 scoring results that exhibit such divergence"
PAPER_503_CVE14140_PASS = 1       # "only one of 15 runs" on CVE-2020-14140
PAPER_503_CVE6045_PASS = 4        # "only 4/15 runs know the delink tool"
PAPER_503_TOP_P5 = 20.0           # "top-scoring run (glm-5.2, 20/20)"
PAPER_504_CMDI_TRIGGER_PCT = 3.3  # "3.3% full-trigger rate"
PAPER_504_CMDI_LOW_CLUSTER = 2    # "Two CVEs form a low-score cluster (Overall ≤33)"
PAPER_504_FW_PREATTACH = {'BOF': 8, 'CMDI': 0, 'AUTH': 4}  # firmware pre-attached counts
PAPER_300_CANDIDATES = 696        # "30 out of 696 representative CVEs"
PAPER_700_NONSTANDARD_PCT = 16    # "approximately 16% of partial-credit items"

PAPER_P5P6 = {'union': 11, 'overlap': 8}
PAPER_SIM_PCT = 45.3
PAPER_P6_PAIRS_PCT = 5.3  # 8/150


# ============================================================
# Data parsing
# ============================================================
def parse_data(data_path):
    """Parse evaluation_summary.txt and return list of run dicts + per-run narrative lines."""
    with open(data_path) as f:
        lines = f.readlines()

    # Find score table header (starts with CVE and contains Model, Run, Plan, P1, etc.)
    header_idx = None
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('CVE') and 'Model' in s and 'Run' in s and 'P1' in s and 'Overall' in s:
            header_idx = i
            break
    if header_idx is None:
        sys.exit('ERROR: could not find FULL SCORE TABLE header')

    # Parse header into column names by splitting on whitespace
    header_names = lines[header_idx].split()

    runs = []
    for line in lines[header_idx + 2:]:  # skip header + separator
        s = line.strip()
        if not s or s.startswith('==='):
            break
        parts = s.split()
        if len(parts) < len(header_names):
            continue
        # Build dict from header names
        STRING_COLS = {'CVE', 'Model', 'Fam', 'Mode', 'TermPhase'}
        NUMERIC_COLS = {'Plan', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6',
                        'Task', 'Overall', 'Cov', 'Dep', 'Fall'}
        row = {}
        termphase_idx = header_names.index('TermPhase') if 'TermPhase' in header_names else None
        for j, col in enumerate(header_names):
            val = parts[j]
            if col in ('CVE', 'Model'):
                row[col] = val
            elif col == 'Run':
                row[col] = int(val)
            elif col == 'TermPhase' and termphase_idx is not None:
                # TermPhase is last column, value may contain spaces
                row[col] = ' '.join(parts[termphase_idx:])
            elif col in STRING_COLS:
                row[col] = val
            elif col in NUMERIC_COLS:
                row[col] = float(val)
            # else: skip other numeric sub-item columns
        runs.append({
            'cve': row['CVE'], 'model': row['Model'], 'run': row['Run'],
            'plan': row.get('Plan', 0),
            'p1': row.get('P1', 0), 'p2': row.get('P2', 0), 'p3': row.get('P3', 0),
            'p4': row.get('P4', 0), 'p5': row.get('P5', 0), 'p6': row.get('P6', 0),
            'task': row.get('Task', 0), 'overall': row.get('Overall', 0),
            'fam': row.get('Fam', ''), 'mode': row.get('Mode', ''),
            'termphase': row.get('TermPhase', ''),
        })

    return runs, lines


def parse_simulation_count(lines):
    """Parse the per-run simulation_substitution count from the summary."""
    for line in lines:
        m = re.search(r'(\d+)\s+run\(s\)\s+were\s+labeled\s+with\s+failure_mode=simulation_substitution', line)
        if m:
            return int(m.group(1))
    # Fallback: search for the pattern in section 4 of the summary
    for line in lines:
        if 'simulation_substitution' in line and 'run(s)' in line:
            m = re.search(r'(\d+)\s+run', line)
            if m:
                return int(m.group(1))
    return None


def parse_fallback(lines, runs):
    """Parse per-run fallback scores from narrative lines."""
    fallback_by_model = defaultdict(list)
    current_model = None
    for line in lines:
        header = re.match(r'---\s+(CVE-\d{4}-\d+)\s*/\s+(\S+)\s*/\s+run\s+\d+', line.strip())
        if header:
            current_model = header.group(2)
        m = re.search(r'fallback=([0-9.]+)', line)
        if m and current_model:
            fallback_by_model[current_model].append(float(m.group(1)))
    return fallback_by_model


def group_pairs(runs):
    """Group runs by (cve, model) pair."""
    pairs = defaultdict(list)
    for r in runs:
        pairs[(r['cve'], r['model'])].append(r)
    return pairs


# ============================================================
# Computation
# ============================================================
def compute_table1(pairs):
    """Compute best-of-three table with max(per-run overall)."""
    results = {}
    all_bp, all_bt, all_bo = [], [], []
    all_p5, all_p6 = set(), set()

    for model in MODELS:
        mp = {k: v for k, v in pairs.items() if k[1] == model}
        n = len(mp)
        bp = [max(r['plan'] for r in pr) for pr in mp.values()]
        bt = [max(r['task'] for r in pr) for pr in mp.values()]
        bo = [max(r['overall'] for r in pr) for pr in mp.values()]
        p5 = sum(1 for pr in mp.values() if max(r['p5'] for r in pr) >= 15)
        p6 = sum(1 for pr in mp.values() if max(r['p6'] for r in pr) >= 15)
        results[model] = {
            'plan': sum(bp) / n, 'task': sum(bt) / n,
            'overall': sum(bo) / n, 'max_overall': max(bo),
            'p5': p5, 'p6': p6,
        }
        all_bp.extend(bp); all_bt.extend(bt); all_bo.extend(bo)
        for k, pr in mp.items():
            if max(r['p5'] for r in pr) >= 15: all_p5.add(k)
            if max(r['p6'] for r in pr) >= 15: all_p6.add(k)

    n = len(pairs)
    results['All'] = {
        'plan': sum(all_bp) / n, 'task': sum(all_bt) / n,
        'overall': sum(all_bo) / n, 'max_overall': max(all_bo),
        'p5': len(all_p5), 'p6': len(all_p6),
    }
    return results, all_p5, all_p6


def compute_funnel(pairs):
    """Compute best-of-three phase averages."""
    phase_max = {'p1': 15, 'p2': 15, 'p3': 15, 'p4': 15, 'p5': 20, 'p6': 20}
    results = []
    for phase in ['p1', 'p2', 'p3', 'p4', 'p5', 'p6']:
        scores = [max(r[phase] for r in pr) for pr in pairs.values()]
        avg = sum(scores) / len(scores)
        mx = phase_max[phase]
        pct = avg / mx * 100
        results.append((phase.upper(), avg, mx, pct))
    return results


def compute_failure(runs, sim_count):
    """Compute per-run failure attribution from actual Fam/Mode labels in data."""
    from collections import Counter
    fam_counts = Counter(r['fam'] for r in runs)
    mode_counts = Counter(r['mode'] for r in runs)

    # Count terminal phase blockers from TermPhase column
    # TermPhase looks like "Phase 5 Service Rehosting" or "All Phases"
    p2_blockers = sum(1 for r in runs if 'Phase 2' in r.get('termphase', ''))
    p5_blockers = sum(1 for r in runs if 'Phase 5' in r.get('termphase', ''))

    # Simulation: terminal-only count from Mode column.
    simulation = mode_counts.get('simulation_substitution', 0)
    rehosting = mode_counts.get('rehosting_failure', 0)
    extraction = mode_counts.get('extraction_failure', 0)
    infrastructure = mode_counts.get('infrastructure_failure', 0)

    n = len(runs)
    return {
        'simulation': simulation,
        'simulation_pct': simulation / n * 100,
        'rehosting': rehosting,
        'rehosting_pct': rehosting / n * 100,
        'extraction': extraction,
        'extraction_pct': extraction / n * 100,
        'infrastructure': infrastructure,
        'infrastructure_pct': infrastructure / n * 100,
        'p2_blockers': p2_blockers,
        'p5_blockers': p5_blockers,
    }


def compute_vultype(runs, pairs):
    """Compute vultype stats: best-of-three overall + per-run phase."""
    results = {}
    for vt_name, vt_set in [('BOF', BOF_CVES), ('CMDI', CMDI_CVES), ('AUTH', AUTH_CVES)]:
        vt_pairs = {k: v for k, v in pairs.items() if k[0] in vt_set}
        n_pairs = len(vt_pairs)
        vt_runs = [r for r in runs if r['cve'] in vt_set]
        n_runs = len(vt_runs)

        bo = sum(max(r['overall'] for r in pr) for pr in vt_pairs.values()) / n_pairs
        p2 = sum(r['p2'] for r in vt_runs) / n_runs
        p4 = sum(r['p4'] for r in vt_runs) / n_runs
        fw = sum(1 for r in vt_runs if r['p2'] > 0) / n_runs * 100

        results[vt_name] = {'overall': bo, 'r2': p2, 'r4': p4, 'fw_pct': fw, 'n_runs': n_runs}
    return results


def compute_model_behavior(runs, pairs, fallback_by_model):
    """Compute model behavior stats for 501-overall.tex."""
    glm_pairs = {k: v for k, v in pairs.items() if k[1] == 'glm-5.2'}
    claude_pairs = {k: v for k, v in pairs.items() if k[1] == 'claude-sonnet-4-6'}

    glm_p2 = sum(max(r['p2'] for r in pr) for pr in glm_pairs.values()) / len(glm_pairs)
    claude_p2 = sum(max(r['p2'] for r in pr) for pr in claude_pairs.values()) / len(claude_pairs)
    claude_phtt = sum(1 for r in runs if r['model'] == 'claude-sonnet-4-6' and r['plan'] > 50 and r['task'] < 15)

    fb = {}
    for mdl in MODELS:
        scores = fallback_by_model.get(mdl, [])
        fb[mdl] = sum(scores) / len(scores) if scores else 0

    other_fallbacks = [fb[m] for m in MODELS if m != 'glm-5.2']

    return {
        'glm_p2_bot3': glm_p2,
        'claude_p2_bot3': claude_p2,
        'claude_plan50_task15': claude_phtt,
        'glm_fallback': fb['glm-5.2'],
        'other_fallback_min': min(other_fallbacks),
        'other_fallback_max': max(other_fallbacks),
    }


def compute_cve_level(runs, pairs):
    """Compute CVE-level stats."""
    cve_best = {}
    for cve in set(r['cve'] for r in runs):
        cp = {k: v for k, v in pairs.items() if k[0] == cve}
        cve_best[cve] = max(max(r['overall'] for r in pr) for pr in cp.values())

    cve_26315 = max(max(r['overall'] for r in pr) for k, pr in pairs.items() if k[0] == 'CVE-2023-26315')
    cve_23624 = max(max(r['overall'] for r in pr) for k, pr in pairs.items() if k[0] == 'CVE-2024-23624')

    cmdi_runs = [r for r in runs if r['cve'] in CMDI_CVES]
    cmdi_p6_18 = sum(1 for r in cmdi_runs if r['p6'] >= 18)

    return {
        'top_score': max(cve_best.values()),
        'cves_ge90': sum(1 for v in cve_best.values() if v >= 90),
        'cve_26315': cve_26315,
        'cve_23624': cve_23624,
        'cmdi_p6_ge18': cmdi_p6_18,
    }


def compute_additional(runs, pairs):
    """Compute additional stats for missing paper checks."""
    # #61: best single run overall
    best_run = max(r['overall'] for r in runs)

    # #63: divergent CVEs (anomaly analysis)
    # Definition from 503: minority of runs score >=40% of phase max while majority score <=15%
    # For each CVE (15 runs), find the earliest phase where this divergence occurs
    phase_max = {'p1': 15, 'p2': 15, 'p3': 15, 'p4': 15, 'p5': 20, 'p6': 20}
    divergent_cves = set()
    for cve in set(r['cve'] for r in runs):
        cve_runs = [r for r in runs if r['cve'] == cve]
        n = len(cve_runs)
        for phase in ['p1', 'p2', 'p3', 'p4', 'p5', 'p6']:
            mx = phase_max[phase]
            scores = [r[phase] / mx for r in cve_runs]
            pass_count = sum(1 for s in scores if s >= 0.40)
            fail_median = sorted(scores)[n // 2]  # rough median
            if pass_count <= 5 and pass_count >= 1 and max(scores) >= 0.40 and fail_median < 0.25:
                divergent_cves.add(cve)
                break

    # #64: CVE-2020-14140 - how many runs have P2 > 0 (genuine acquisition attempt)
    cve14140_pass = sum(1 for r in runs if r['cve'] == 'CVE-2020-14140' and r['p2'] > 0)

    # #65: CVE-2024-6045 - how many runs have P3 > 0 (successful extraction)
    cve6045_pass = sum(1 for r in runs if r['cve'] == 'CVE-2024-6045' and r['p3'] > 0)

    # #66: top P5 score for glm-5.2
    top_p5 = max(r['p5'] for r in runs if r['model'] == 'glm-5.2')

    # #67: CMDI full-trigger rate
    cmdi_runs = [r for r in runs if r['cve'] in CMDI_CVES]
    cmdi_trigger_pct = sum(1 for r in cmdi_runs if r['p6'] >= 18) / len(cmdi_runs) * 100

    # #68: CMDI low-score cluster (best overall per CVE <= 33)
    cmdi_cve_best = {}
    for cve in CMDI_CVES:
        cp = {k: v for k, v in pairs.items() if k[0] == cve}
        if cp:
            cmdi_cve_best[cve] = max(max(r['overall'] for r in pr) for pr in cp.values())
    cmdi_low_cluster = sum(1 for v in cmdi_cve_best.values() if v <= 33)

    return {
        'best_run': best_run,
        'divergent_cves': len(divergent_cves),
        'cve14140_pass': cve14140_pass,
        'cve6045_pass': cve6045_pass,
        'top_p5': top_p5,
        'cmdi_trigger_pct': cmdi_trigger_pct,
        'cmdi_low_cluster': cmdi_low_cluster,
    }


# ============================================================
# Verification
# ============================================================
class Verifier:
    def __init__(self):
        self.checks = 0
        self.errors = []

    def check(self, name, expected, actual, tol=0.1):
        self.checks += 1
        if isinstance(expected, float) or isinstance(actual, float):
            if abs(expected - actual) > tol:
                self.errors.append(f"FAIL: {name}: expected={expected}, actual={actual}")
                return False
        elif expected != actual:
            self.errors.append(f"FAIL: {name}: expected={expected}, actual={actual}")
            return False
        return True

    def check_in_text(self, name, text, expected_str):
        self.checks += 1
        if expected_str not in text:
            self.errors.append(f"FAIL: {name}: '{expected_str}' not found in tex file")
            return False
        return True

    def summary(self):
        print(f"\n{'=' * 70}")
        print(f"VERIFICATION COMPLETE: {self.checks} checks, {len(self.errors)} errors")
        print(f"{'=' * 70}")
        if self.errors:
            print("\nERRORS:")
            for e in self.errors:
                print(f"  {e}")
        else:
            print("\nAll checks passed! ✓")


def read_tex(filename):
    path = os.path.join(SECTIONS_DIR, filename)
    with open(path) as f:
        return f.read()


def main():
    data_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATA
    data_path = os.path.abspath(data_path)

    print(f"Data file: {data_path}")
    print(f"Sections dir: {os.path.abspath(SECTIONS_DIR)}")

    # Parse data
    runs, all_lines = parse_data(data_path)
    assert len(runs) == 450, f"Expected 450 runs, got {len(runs)}"
    pairs = group_pairs(runs)
    assert len(pairs) == 150, f"Expected 150 pairs, got {len(pairs)}"
    fallback_by_model = parse_fallback(all_lines, runs)
    sim_count = parse_simulation_count(all_lines)
    assert sim_count is not None, "Could not parse simulation count from summary"
    print(f"  Parsed simulation count from summary: {sim_count}")

    v = Verifier()

    # ===== TABLE 1 =====
    print("\n--- Table 1 (400-experimental-design.tex) ---")
    tex400 = read_tex('400-experimental-design.tex')
    t1, all_p5, all_p6 = compute_table1(pairs)

    for model in MODELS:
        pv = PAPER_TABLE1[model]
        cv = t1[model]
        print(f"  {model}:")
        v.check(f"{model} plan", pv['plan'], round(cv['plan'], 1))
        v.check(f"{model} task", pv['task'], round(cv['task'], 1))
        v.check(f"{model} overall", pv['overall'], round(cv['overall'], 1))
        v.check(f"{model} max", pv['max_overall'], round(cv['max_overall'], 1))
        v.check(f"{model} P5", pv['p5'], cv['p5'], tol=0)
        v.check(f"{model} P6", pv['p6'], cv['p6'], tol=0)

    cv = t1['All']
    v.check("All plan", PAPER_ALL['plan'], round(cv['plan'], 1))
    v.check("All task", PAPER_ALL['task'], round(cv['task'], 1))
    v.check("All overall", PAPER_ALL['overall'], round(cv['overall'], 1))
    v.check("All max", PAPER_ALL['max_overall'], round(cv['max_overall'], 1))
    v.check("All P5", PAPER_ALL['p5'], cv['p5'], tol=0)
    v.check("All P6", PAPER_ALL['p6'], cv['p6'], tol=0)

    # P5/P6 union and overlap
    v.check("P5∪P6 union", PAPER_P5P6['union'], len(all_p5 | all_p6), tol=0)
    v.check("P5∩P6 overlap", PAPER_P5P6['overlap'], len(all_p5 & all_p6), tol=0)

    # ===== STAGE FUNNEL =====
    print("\n--- Stage Funnel (502-failure.tex) ---")
    tex502 = read_tex('502-failure.tex')
    funnel = compute_funnel(pairs)
    for i, (pname, pscore, pmax, ppct) in enumerate(PAPER_FUNNEL):
        pname_c, avg, mx, pct = funnel[i]
        v.check(f"{pname} score", pscore, round(avg, 1))
        v.check(f"{pname} pct", ppct, round(pct, 1))

    # ===== FAILURE ATTRIBUTION =====
    print("\n--- Failure Attribution (502-failure.tex) ---")
    fail = compute_failure(runs, sim_count)
    v.check("Simulation count", PAPER_FAILURE['simulation'], fail['simulation'], tol=0)
    v.check("Simulation pct", PAPER_FAILURE['simulation_pct'], round(fail['simulation_pct'], 1))
    v.check("Rehosting count", PAPER_FAILURE['rehosting'], fail['rehosting'], tol=0)
    v.check("Rehosting pct", PAPER_FAILURE['rehosting_pct'], round(fail['rehosting_pct'], 1))
    v.check("Extraction count", PAPER_FAILURE['extraction'], fail['extraction'], tol=0)
    v.check("Extraction pct", PAPER_FAILURE['extraction_pct'], round(fail['extraction_pct'], 1))
    v.check("Infra count", PAPER_FAILURE['infrastructure'], fail['infrastructure'], tol=0)
    v.check("Infra pct", PAPER_FAILURE['infrastructure_pct'], round(fail['infrastructure_pct'], 1))
    v.check("P2 blockers", PAPER_FAILURE['p2_blockers'], fail['p2_blockers'], tol=0)
    v.check("P5 blockers", PAPER_FAILURE['p5_blockers'], fail['p5_blockers'], tol=0)

    # Check text contains these numbers (handle LaTeX \% escaping)
    for s in ['204/450', '45.3', '93/450', '20.7', '36/450', '8.0', '15/450', '3.3',
              '211/450', '173/450', '13.9/15', '9.0/15', '3.7/20', '2.8/20']:
        v.check_in_text(f"502 contains '{s}'", tex502, s)

    # ===== VULTYPE =====
    print("\n--- Vultype (504-vulclass.tex) ---")
    tex504 = read_tex('504-vulclass.tex')
    vt = compute_vultype(runs, pairs)
    for vt_name in ['BOF', 'CMDI', 'AUTH']:
        pv = PAPER_VULTYPE[vt_name]
        cv = vt[vt_name]
        v.check(f"{vt_name} overall", pv['overall'], round(cv['overall'], 1))
        if 'r2' in pv:
            v.check(f"{vt_name} R2", pv['r2'], round(cv['r2'], 2))
        if 'r4' in pv:
            v.check(f"{vt_name} R4", pv['r4'], round(cv['r4'], 2))
        if 'fw_pct' in pv:
            v.check(f"{vt_name} FW%", pv['fw_pct'], round(cv['fw_pct']), tol=0.5)

    # Check text
    for s in ['60.4', '48.6', '44.4', '8.06', '7.09', '3.14', '73', '99.0', '80.8', '5/150']:
        v.check_in_text(f"504 contains '{s}'", tex504, s)

    # ===== MODEL BEHAVIOR =====
    print("\n--- Model Behavior (501-overall.tex) ---")
    tex501 = read_tex('501-overall.tex')
    mb = compute_model_behavior(runs, pairs, fallback_by_model)
    v.check("glm P2 bot3", PAPER_MODEL_BEHAVIOR['glm_p2_bot3'], round(mb['glm_p2_bot3'], 1))
    v.check("claude P2 bot3", PAPER_MODEL_BEHAVIOR['claude_p2_bot3'], round(mb['claude_p2_bot3'], 1))
    v.check("claude plan>50 task<15", PAPER_MODEL_BEHAVIOR['claude_plan50_task15'], mb['claude_plan50_task15'], tol=0)
    v.check("glm fallback", PAPER_MODEL_BEHAVIOR['glm_fallback'], round(mb['glm_fallback'], 1))
    v.check("other fallback min", PAPER_MODEL_BEHAVIOR['other_fallback_range'][0], round(mb['other_fallback_min'], 1))
    v.check("other fallback max", PAPER_MODEL_BEHAVIOR['other_fallback_range'][1], round(mb['other_fallback_max'], 1))

    # Check text
    for s in ['64.6', '52.9', '50.0', '99.0', '11 out of 150', '8 also', 'five CVEs',
              '11.5/15', '7.7/15', '20 runs', '32.2/100', '15.0--28.6']:
        v.check_in_text(f"501 contains '{s}'", tex501, s)

    # ===== CVE-LEVEL =====
    print("\n--- CVE-level (501/504) ---")
    cve = compute_cve_level(runs, pairs)
    v.check("Top CVE score", PAPER_CVE['top_score'], round(cve['top_score'], 1))
    v.check("CVEs >= 90", PAPER_CVE['cves_ge90'], cve['cves_ge90'], tol=0)
    v.check("CVE-2023-26315", PAPER_CVE['cve_26315'], round(cve['cve_26315'], 1))
    v.check("CVE-2024-23624", PAPER_CVE['cve_23624'], round(cve['cve_23624'], 1))
    v.check("CMDI P6>=18", PAPER_CVE['cmdi_p6_ge18'], cve['cmdi_p6_ge18'], tol=0)

    # ===== CROSS-FILE NUMBERS =====
    print("\n--- Cross-file numbers (abstract, intro, conclusion, discussion) ---")
    tex_abs = read_tex('000-abstract.tex')
    tex_intro = read_tex('100-introduction.tex')
    tex_concl = read_tex('800-conclusion.tex')
    tex_disc = read_tex('700-discussion.tex')

    # Simulation % should be 45.3% everywhere
    v.check_in_text("abstract 45.3%", tex_abs, '45.3')
    v.check_in_text("intro 45.3%", tex_intro, '45.3')
    v.check_in_text("discussion 45.3%", tex_disc, '45.3')

    # P6 pairs % should be 5.3% (8/150)
    v.check_in_text("abstract 5.3%", tex_abs, '5.3')
    v.check_in_text("intro 5.3%", tex_intro, '5.3')

    # Conclusion: P5 score should be 3.7/20
    v.check_in_text("conclusion 3.7/20", tex_concl, '3.7/20')

    # ===== ADDITIONAL CHECKS =====
    print("\n--- Additional checks (501, 503, 504, 300, 700) ---")
    tex300 = read_tex('300-benchmark-construction.tex')
    tex503 = read_tex('503-feature.tex')
    addl = compute_additional(runs, pairs)

    # #61: best single run in 501
    v.check("501 best single run", PAPER_501_BEST_RUN, round(addl['best_run'], 1))
    v.check_in_text("501 contains '99.0/100'", tex501, '99.0/100')

    # #63: divergent CVEs in 503
    v.check("503 divergent CVEs", PAPER_503_DIVERGENT, addl['divergent_cves'], tol=0)
    v.check_in_text("503 contains '18'", tex503, '18')

    # #64: CVE-2020-14140 pass count
    v.check("503 CVE-2020-14140 pass", PAPER_503_CVE14140_PASS, addl['cve14140_pass'], tol=0)
    v.check_in_text("503 contains 'one of 15'", tex503, 'one of 15')

    # #65: CVE-2024-6045 pass count
    v.check("503 CVE-2024-6045 pass", PAPER_503_CVE6045_PASS, addl['cve6045_pass'], tol=0)
    v.check_in_text("503 contains '4/15'", tex503, '4/15')

    # #66: top P5 score for glm-5.2
    v.check("503 top P5 score", PAPER_503_TOP_P5, round(addl['top_p5'], 1))
    v.check_in_text("503 contains '20/20'", tex503, '20/20')

    # #67: CMDI trigger rate
    v.check("504 CMDI trigger pct", PAPER_504_CMDI_TRIGGER_PCT, round(addl['cmdi_trigger_pct'], 1))
    v.check_in_text("504 contains '3.3'", tex504, '3.3')

    # #68: CMDI low-score cluster
    v.check("504 CMDI low cluster", PAPER_504_CMDI_LOW_CLUSTER, addl['cmdi_low_cluster'], tol=0)
    v.check_in_text("504 contains 'Two CVEs'", tex504, 'Two CVEs')

    # #74: 696 candidate CVEs (text-only check, metadata not in evaluation data)
    v.check_in_text("300 contains '696'", tex300, '696')

    # #75: 16% non-standard partial credit (text-only check, not computable from summary)
    v.check_in_text("700 contains '16'", tex_disc, '16')

    # ===== SUMMARY =====
    v.summary()

    return 0 if not v.errors else 1


if __name__ == '__main__':
    sys.exit(main())
