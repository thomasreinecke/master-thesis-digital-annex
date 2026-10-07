#!/usr/bin/env python3
"""Replay the RQ1 screening rule from the stored criterion answers.

Each screening model answered seven criteria per record with YES, NO, or UNCERTAIN.
A deterministic rule then derived the model-level decision (Section 3.2, Step 2 of the
thesis). This script recomputes every decision from criterion-answers.csv and compares
it with model-decisions.csv.

A clean run shows that the stored decisions follow the published rule. It does not show
that the criterion answers themselves were correct.

Usage:  python3 replay_screening_rule.py
Exit code 0 = every decision reproduced, 1 = at least one deviation.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CRITERIA = (
    "topic_relevance",
    "ea_or_itg_context",
    "generalizable_contribution",
    "transformation_readiness",
    "is_technical_artifact",
    "is_case_application",
    "is_scholarly",
)


def derive(r: dict) -> str:
    """The screening rule in its documented order. The first matching rule decides."""
    u = "UNCERTAIN"
    if r["is_technical_artifact"] == "YES":
        return "EXCLUDE"
    if r["is_case_application"] == "YES" and r["generalizable_contribution"] != "YES":
        return "EXCLUDE"
    if r["is_scholarly"] == "NO":
        return "EXCLUDE"
    if r["topic_relevance"] == "YES" and r["generalizable_contribution"] == "YES":
        return "INCLUDE"
    if (r["topic_relevance"] == "YES" and r["generalizable_contribution"] == u
            and (r["ea_or_itg_context"] == "YES" or r["transformation_readiness"] == "YES")):
        return u
    if sum(1 for c in CRITERIA if r[c] == u) >= 2:
        return u
    return "EXCLUDE"


def main() -> int:
    with (HERE / "model-decisions.csv").open(encoding="utf-8") as fh:
        stored = {(r["corpus_id"], r["model_label"]): r["decision"] for r in csv.DictReader(fh)}
    deviations = 0
    total = 0
    with (HERE / "criterion-answers.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            total += 1
            key = (r["corpus_id"], r["model_label"])
            if derive(r) != stored.get(key):
                deviations += 1
                print(f"deviation: record {key[0]}, {key[1]}: rule {derive(r)}, stored {stored.get(key)}")
    print(f"replayed {total} model decisions, {deviations} deviations")
    return 0 if deviations == 0 and total else 1


if __name__ == "__main__":
    sys.exit(main())
