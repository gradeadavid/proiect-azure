#!/usr/bin/env python
"""Ingest every document in data/ through the running API.

    uv run python scripts/ingest_corpus.py
    uv run python scripts/ingest_corpus.py --api http://localhost:7799 --strategy dynamic

Each file must start with a small YAML-ish header (--- ... ---) whose keys
(title, product, audience, effective, version) become Qdrant payload metadata
for every chunk of that document — see app/vectorstore.py upsert(). The
source label is the filename stem, and re-running this script re-ingests
(replaces) each document instead of duplicating it, thanks to the stable
chunk ids in upsert().

Prerequisites
    docker compose up qdrant -d   (or the whole stack)
    uv run uvicorn app.main:app --reload --port 7799
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = REPO_ROOT / "data"


def parse_document(path: Path) -> tuple[dict, str]:
    """Split a file into its header (key: value pairs between --- lines) and body."""
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, raw.strip()

    metadata: dict[str, str] = {}
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        line = lines[i]
        if ":" in line:
            key, _, value = line.partition(":")
            metadata[key.strip()] = value.strip()
        i += 1
    body = "\n".join(lines[i + 1:]).strip()
    return metadata, body


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252; titles have diacritics

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", default="http://localhost:7799", help="Base URL of the running API")
    parser.add_argument("--strategy", default="dynamic", choices=["static", "dynamic", "sentence", "semantic"])
    parser.add_argument("--data-dir", default=str(DATA_DIR), help="Folder holding the .md corpus")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    files = sorted(f for f in data_dir.glob("*.md") if f.name.lower() != "readme.md")
    if not files:
        print(f"x no .md documents found in {data_dir}")
        return 2

    print(f"-> ingesting {len(files)} documents from {data_dir} into {args.api}\n")

    total_chunks = 0
    failed: list[str] = []
    for path in files:
        metadata, body = parse_document(path)
        source = path.stem
        try:
            resp = requests.post(
                f"{args.api}/ingest",
                json={"text": body, "strategy": args.strategy, "source": source, "metadata": metadata},
                timeout=60,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"  [FAIL] {path.name}: {e}")
            failed.append(path.name)
            continue

        data = resp.json()
        count = data["count"]
        total_chunks += count
        title = metadata.get("title", source)
        print(f"  [ok]   {path.name:45s} {count:3d} chunks   ({title})")

    print(f"\n{len(files) - len(failed)}/{len(files)} documents ingested, {total_chunks} chunks total.")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
