#!/usr/bin/env python3
"""Build the digital annex of the master thesis from the internal research record.

The annex holds the records that the printed thesis cannot carry in full: for RQ1 the
screening record and the Condition Findings with their source locators, and for RQ2 the
aspect register with the classification record of every condition aspect.
Everything else the thesis reports in its chapters and appendices.

The script reads the research database read-only and writes only the fields listed
below. It excludes:
- the record list of the database search, which Scopus licence terms do not allow to
  redistribute. Screened records are identified by corpus identifier only, and the
  search queries let anyone with Scopus access rebuild the search;
- publication full texts and abstracts;
- free-text model responses;
- every record of the enterprise case;
- person-identifying fields of the enterprise case and the names of deciders.

Bibliographic details are published only for the publications that contribute
Condition Findings. The thesis cites these works, and the details serve as the source
attribution of the findings and their quotations.

Finding statements may contain short quotations from the source publication. The
automatic check covers quotations marked by double quotation marks: any such quotation
longer than MAX_QUOTE_WORDS words is shortened, and the build fails if a longer one
remains. Unmarked wording close to the source is not detected by this check.

Usage:
    python3 tools/build_annex.py [--source /path/to/_Masterarbeit]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sqlite3
import sys
from pathlib import Path

ANNEX = Path(__file__).resolve().parents[1]
MAX_QUOTE_WORDS = 25
KEEP_QUOTE_WORDS = 20
QUOTE = re.compile(r'"([^"]+)"|“([^”]+)”')

CRITERIA = (
    "topic_relevance",
    "ea_or_itg_context",
    "generalizable_contribution",
    "transformation_readiness",
    "is_technical_artifact",
    "is_case_application",
    "is_scholarly",
)


def connect(db: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{db}?mode=ro&immutable=1", uri=True)
    con.row_factory = sqlite3.Row
    return con


def write_csv(path: Path, header: list[str], rows) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        for row in rows:
            writer.writerow(["" if v is None else v for v in row])
            count += 1
    return count


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


SEARCH_QUERIES = """# Search queries

The formal search ran in Scopus on 6 July 2026 (Section 3.2, Step 1, and Table 3.2 of the
thesis). Anyone with Scopus access can rebuild the search from the expressions below.
Scopus changes continuously, so a later run returns a similar, not an identical, set.

Filters applied to every query: `OA ( ALL )`, `PUBYEAR > 2016`, `LIMIT-TO ( LANGUAGE , "English" )`

| Query | Literature stream | Scopus search expression | Records on 6 July 2026 |
|---|---|---|---:|
| TQ1 | Digital transformation | `TITLE ("digital transformation") AND TITLE-ABS-KEY (readiness OR "enabling condition*" OR "dynamic capabilit*" OR "digital maturity")` | 743 |
| TQ2 | Enterprise architecture | `TITLE-ABS-KEY ("enterprise architecture" AND (transformation OR governance OR "decision right*" OR alignment OR maturity OR readiness))` | 391 |
| TQ3 | IT governance | `TITLE-ABS-KEY (("IT governance" OR "information technology governance" OR "enterprise governance of IT") AND ("decision right*" OR alignment OR "business-IT alignment" OR maturity OR "governance mechanism*" OR "value delivery"))` | 147 |

## Further sources

- Six mandatory anchor publications named in the research proposal and 29 purposive
  foundational selections raised the identified set from 1,281 to 1,316 records
  (Section 4.1, Step 2).
- After duplicate removal, 1,295 unique records entered title-and-abstract screening.
- The coverage audit added three foundational publications through the purposive channel
  after screening. The author decided these three records without model screening
  (Section 4.1, Step 3).

The contributing publications are listed with full bibliographic details in
`../synthesis/contributing-publications.csv` and in Appendix B of the thesis.
"""


def json_list(value: str | None) -> str:
    try:
        return "; ".join(json.loads(value or "[]"))
    except (json.JSONDecodeError, TypeError):
        return value or ""


def limit_quotes(text: str | None) -> tuple[str, int]:
    """Shorten every quotation longer than MAX_QUOTE_WORDS words. Returns text and count."""
    if not text:
        return text or "", 0
    shortened = 0

    def cut(match: re.Match) -> str:
        nonlocal shortened
        inner = match.group(1) if match.group(1) is not None else match.group(2)
        words = inner.split()
        if len(words) <= MAX_QUOTE_WORDS:
            return match.group(0)
        shortened += 1
        short = " ".join(words[:KEEP_QUOTE_WORDS]) + " […]"
        return f'"{short}"' if match.group(1) is not None else f"“{short}”"

    return QUOTE.sub(cut, text), shortened


def longest_quote(text: str) -> int:
    return max((len((m.group(1) or m.group(2)).split()) for m in QUOTE.finditer(text or "")), default=0)


def build(con: sqlite3.Connection, out: Path) -> dict:
    counts = {}

    write_text(out / "search" / "search-queries.md", SEARCH_QUERIES)

    counts["screening_runs"] = write_csv(
        out / "screening" / "screening-runs.csv",
        ["run_id", "model_label", "model", "prompt_version", "prompt_hash", "batch_size",
         "temperature", "max_tokens", "records", "processed", "errors"],
        con.execute(
            "select id, model_label, lmstudio_model, prompt_version, prompt_hash, batch_size,"
            " temperature, max_tokens, total_papers, processed_count, error_count"
            " from screening_runs order by id"
        ),
    )
    counts["criterion_answers"] = write_csv(
        out / "screening" / "criterion-answers.csv",
        ["corpus_id", "model_label", *CRITERIA],
        con.execute(
            "select c.corpus_id, r.model_label, " + ", ".join("c." + k for k in CRITERIA) +
            " from screening_criteria c join screening_runs r on r.id = c.run_id"
            " order by c.corpus_id, r.model_label"
        ),
    )
    counts["model_decisions"] = write_csv(
        out / "screening" / "model-decisions.csv",
        ["corpus_id", "model_label", "decision"],
        con.execute(
            "select d.corpus_id, r.model_label, d.decision from screening_decisions d"
            " join screening_runs r on r.id = d.run_id order by d.corpus_id, r.model_label"
        ),
    )
    counts["author_decisions"] = write_csv(
        out / "screening" / "author-decisions.csv",
        ["corpus_id", "decision", "review_channel", "decided_on"],
        con.execute(
            "select corpus_id, decision, review_channel, substr(decided_at, 1, 10)"
            " from human_decisions order by corpus_id"
        ),
    )
    shutil.copy(Path(__file__).with_name("replay_screening_rule.py"),
                out / "screening" / "replay_screening_rule.py")

    shortened = 0
    findings = []
    for r in con.execute(
        """
        select cc.id, cc.corpus_id, code.code, code.status, cc.contribution_type,
               cc.readiness_statement, cc.mechanism, cc.operationalization_hint,
               cc.page_or_section, rev.audit_outcome
        from step9_cf_audit_sample s
        join condition_contributions cc on cc.id = s.cf_id
        left join condition_codes code on code.id = cc.condition_code_id
        left join step9_cf_audit_reviews rev on rev.sample_id = s.id
        order by cc.id
        """
    ):
        texts = []
        for field in (r["readiness_statement"], r["mechanism"], r["operationalization_hint"]):
            text, n = limit_quotes(field)
            shortened += n
            if longest_quote(text) > MAX_QUOTE_WORDS:
                sys.exit(f"quotation longer than {MAX_QUOTE_WORDS} words remains in CF#{r['id']}")
            texts.append(text)
        findings.append((
            f"CF#{r['id']}", r["corpus_id"], r["code"], "yes" if r["status"] == "confirmed" else "no",
            r["contribution_type"], *texts, r["page_or_section"], r["audit_outcome"],
        ))
    counts["condition_findings"] = write_csv(
        out / "synthesis" / "condition-findings.csv",
        ["cf_id", "corpus_id", "condition_code", "retained_in_framework", "contribution_type",
         "finding_statement", "mechanism", "operationalisation_hint", "page_or_section",
         "audit_outcome"],
        findings,
    )
    counts["quotations_shortened"] = shortened

    counts["contributing_publications"] = write_csv(
        out / "synthesis" / "contributing-publications.csv",
        ["corpus_id", "authors", "year", "title", "venue", "doi"],
        con.execute(
            """
            select c.id, c.authors, c.year, c.title, c.journal, c.doi from corpus c
            where c.id in (select distinct cc.corpus_id from step9_cf_audit_sample s
                           join condition_contributions cc on cc.id = s.cf_id)
            order by c.id
            """
        ),
    )

    counts["source_locators"] = write_csv(
        out / "synthesis" / "source-fidelity-locators.csv",
        ["cf_id", "corpus_id", "span_order", "source_section", "line_start", "line_end", "span_status"],
        (
            (f"CF#{r[0]}", *r[1:])
            for r in con.execute(
                """
                select s.cf_id, cc.corpus_id, sp.span_order, sp.source_locator,
                       sp.source_line_start, sp.source_line_end, sp.span_status
                from step9_cf_audit_evidence_spans sp
                join step9_cf_audit_reviews rev on rev.id = sp.audit_review_id
                join step9_cf_audit_sample s on s.id = rev.sample_id
                join condition_contributions cc on cc.id = s.cf_id
                order by s.cf_id, sp.span_order
                """
            )
        ),
    )
    return counts


def build_rq2(source: Path, out: Path) -> dict:
    """Write the aspect register of RQ2: one row per condition aspect.

    The classification fields describe each aspect independently of the governance
    application, so they carry no application, table, or case identifier. The design
    sketches of the register and the free-text notes of the fit records are not exported,
    because they name internal schema elements.
    """
    register = json.loads(
        (source / "master-thesis-full" / "_app" / "scripts" / "data" / "rq2-aspects.en.json")
        .read_text(encoding="utf-8"))["aspects"]
    fit_path = (source / "master-thesis-full" / "output" / "S2-Artifact-Design"
                / "S2-step5-aspect-fit-export-2026-10-05.csv")
    with fit_path.open(newline="", encoding="utf-8") as fh:
        fit = {row["aspect_id"]: row for row in csv.DictReader(fh)}

    def order(aspect_id: str) -> tuple[int, int]:
        m = re.fullmatch(r"CC(\d+)-A(\d+)", aspect_id)
        return int(m.group(1)), int(m.group(2))

    rows = []
    for aspect_id in sorted(register, key=order):
        r = register[aspect_id]
        f = fit.get(aspect_id, {})
        rows.append((
            aspect_id, aspect_id.split("-")[0], r["label"], r.get("text_anchor", ""),
            "; ".join(r.get("cf", [])),
            r.get("use", ""), r.get("information", ""), r.get("route", ""),
            r.get("or1", ""), r.get("or2", ""), r.get("or3", ""),
            "yes" if r["verdict"] == "ja" else "no",
            "yes" if r.get("study_boundary") else "no",
            f.get("platform_capability", ""), f.get("fit", ""), f.get("coverage", ""),
            "yes" if f.get("selected") == "1" else ("no" if f else ""),
        ))
    return {"aspect_register": write_csv(
        out / "aspect-register.csv",
        ["aspect_id", "condition_code", "label", "text_anchor", "condition_findings",
         "use_or1", "information_or2", "producer_or3", "or1_result", "or2_result", "or3_result",
         "operationalisable", "study_boundary", "platform_capability", "fit", "baseline_coverage",
         "selected_for_implementation"],
        rows,
    )}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", type=Path, default=ANNEX.parent,
                        help="folder that holds master-thesis-full (default: parent of the annex)")
    args = parser.parse_args()
    db = args.source / "master-thesis-full" / "_app" / "db" / "app.sqlite"
    counts = build(connect(db), ANNEX / "rq1-literature-review")
    counts.update(build_rq2(args.source, ANNEX / "rq2-operationalisation"))
    for name, n in counts.items():
        print(f"{name}: {n}")


if __name__ == "__main__":
    main()
