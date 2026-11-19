#!/usr/bin/env python3
"""Build an independent paper copy into build/<version>/ without changing its sources."""

import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "aaai-2027": ("main", "appendix_standalone", "ReproducibilityChecklist"),
    "arxiv": ("main",),
    "usenix-security-2027": ("usenixsecurity2027",),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", choices=TARGETS, nargs="?", default="aaai-2027")
    parser.add_argument("targets", nargs="*", help="Optional TeX basenames for this version")
    args = parser.parse_args()
    targets = args.targets or TARGETS[args.version]
    for target in targets:
        if target not in TARGETS[args.version]:
            parser.error(f"Unknown target {target!r}; choose from {TARGETS[args.version]}")
    for command in ("pdflatex", "bibtex"):
        if shutil.which(command) is None:
            parser.error(f"Required command not found: {command}")

    output = ROOT / "build" / args.version
    output.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="sources-", dir=output))
    shutil.copytree(ROOT / "versions" / args.version / "paper", stage, dirs_exist_ok=True)

    def run(command, target):
        with (stage / f"{target}.commands.log").open("a") as log:
            log.write("$ " + " ".join(command) + "\n")
            log.flush()
            result = subprocess.run(command, cwd=stage, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError(f"{command[0]} failed; inspect {stage / (target + '.commands.log')}")

    try:
        for target in targets:
            destination = output / f"{target}.pdf"
            destination.unlink(missing_ok=True)
            latex = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{target}.tex"]
            run(latex, target)
            if "\\bibdata{" in (stage / f"{target}.aux").read_text():
                run(["bibtex", target], target)
            run(latex, target)
            run(latex, target)
            shutil.copy2(stage / f"{target}.pdf", destination)
            print(destination, flush=True)
    except RuntimeError as error:
        parser.exit(1, f"{error}\n")
    print(f"Build logs and intermediate files: {stage}")


if __name__ == "__main__":
    main()
