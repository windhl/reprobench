"""Restore optional literature PDFs from sources.json; verify original SHA-256."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
STUDIES = ("positioning-study-2026-11-19", "empirical-related-work-2026-11-19")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def restore(study, source, offline, with_text):
    pdf = study / source["pdf_path"]
    expected = source["sha256"]
    if pdf.exists():
        if digest(pdf) != expected:
            raise ValueError(f"existing file has a different SHA-256: {pdf}")
    else:
        local = source.get("local_source", "")
        candidate = ROOT / local.removeprefix("reprobench/") if local else None
        pdf.parent.mkdir(parents=True, exist_ok=True)
        # Publish only complete files with the expected hash; preserve any existing file.
        with tempfile.TemporaryDirectory(dir=pdf.parent) as temp:
            staged = Path(temp) / pdf.name
            if candidate and candidate.is_file() and digest(candidate) == expected:
                shutil.copyfile(candidate, staged)
            else:
                url = source.get("pdf_url")
                if offline or not url:
                    raise ValueError(f"PDF unavailable locally; source: {source['source_url']}")
                if not url.startswith("https://"):
                    raise ValueError("only HTTPS PDF URLs are supported")
                version = re.search(r"\d{4}\.\d{4,5}v\d+", source.get("downloaded_version", ""))
                if version and url.startswith("https://arxiv.org/pdf/"):
                    url = "https://arxiv.org/pdf/" + version.group()
                request = urllib.request.Request(url, headers={"User-Agent": "ReproBench-literature/1.0"})
                with urllib.request.urlopen(request, timeout=60) as response, staged.open("wb") as out:
                    shutil.copyfileobj(response, out)
            if digest(staged) != expected:
                raise ValueError("download SHA-256 differs from sources.json; original PDF required")
            staged.replace(pdf)
    if with_text:
        target = study / source["text_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=target.parent) as temp:
            staged_text = Path(temp) / target.name
            subprocess.run(["pdftotext", "-layout", str(pdf), str(staged_text)], check=True)
            staged_text.replace(target)
    print(f"OK {study.name}/{source['id']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", choices=STUDIES, action="append", help="default: both studies")
    parser.add_argument("--offline", action="store_true", help="verify/reuse local PDFs without downloading")
    parser.add_argument("--with-text", action="store_true", help="regenerate full text with pdftotext -layout")
    args = parser.parse_args()
    if args.with_text and not shutil.which("pdftotext"):
        parser.error("--with-text requires pdftotext on PATH")
    failures = 0
    for name in args.study or STUDIES:
        study = ROOT / "references" / name
        for source in json.loads((study / "sources.json").read_text(encoding="utf-8")):
            try:
                restore(study, source, args.offline, args.with_text)
            except (OSError, ValueError, subprocess.CalledProcessError) as exc:
                failures += 1
                print(f"ERROR {name}/{source['id']}: {exc}", file=sys.stderr)
    return int(failures > 0)


if __name__ == "__main__":
    sys.exit(main())
