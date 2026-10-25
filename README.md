# Digital Annex – Master Thesis on Transformation-Enabling Conditions

This repository is the digital annex of the master thesis
*Enterprise Transformation Readiness: A Design Science Study of Transformation-Enabling
Conditions Operationalised in an AI-Supported Governance Application*
(Thomas Reinecke, M.Sc. Artificial Intelligence, IU International University of Applied Sciences, 2026).

## Orientation

The thesis answers three research questions in sequence: a systematic literature review that synthesises a framework of transformation-enabling conditions (RQ1), the operationalisation of these conditions in an enterprise governance application (RQ2), and AI-based collection of the facts the implemented functions need (RQ3).

The printed thesis reports every method, result, and register that fits on a page.
This annex holds the records that are too large to print in full:

1. the **screening record**, with the criterion answers and decisions of both screening models for the 1,295 screened records and the author decisions, including the three records that the coverage audit added after screening;
2. the **Condition Findings**, with the source locators of their audited evidence and the bibliographic details of the 209 contributing publications;
3. the **aspect register** of RQ2, with the classification record of all 75 condition aspects and the fit of the operationalisable ones.

Everything else stays in the thesis:

| Material | Where in the thesis |
|---|---|
| Search queries and screening rule | Section 3.2, Tables 3.2 and 3.4 |
| Screening prompt | Appendix A-1 |
| Contributing publications and their characteristics | Appendix B |
| Conditions, domains, and the framework | Chapter 4, Appendix C |
| Operationalisability requirements, classification records, fit and selection | Chapter 5, Appendix D |
| RQ3 system prompt and capability catalogue | Appendix E-3 |
| Fact-collection results | Chapter 6, Appendix E |
| AI usage and evidence record | Section 3.6, Appendix F |

The framework can be browsed in the companion web application **TECF**: <https://thomasreinecke.github.io/TECF/>.

### What the annex leaves out

- The record list of the Scopus search, which the Scopus licence terms do not allow to redistribute. Screened records are identified by a corpus identifier, and the [search queries](rq1-literature-review/search/search-queries.md) let anyone with Scopus access rebuild the search.
- Abstracts and full texts of all publications.
- Free-text model responses.
- Every record of the enterprise case studied for RQ2 and RQ3, including its person-identifying fields.

The complete internal research record is retained by the author and available to the supervisor on request (Appendix F-2 of the thesis).

## Table of Contents

### [`rq1-literature-review/`](rq1-literature-review/)

| File | Content | Records | Thesis reference |
|---|---|---:|---|
| [`search/search-queries.md`](rq1-literature-review/search/search-queries.md) | Scopus search expressions, filters, execution date, and records per query, plus the further sources of the corpus | 3 queries | Section 3.2, Step 1; Table 3.2; Section 4.1 |
| [`screening/screening-runs.csv`](rq1-literature-review/screening/screening-runs.csv) | Configuration of the two screening runs: model, prompt version and hash, batch size, temperature | 2 | Section 3.2, Step 2 |
| [`screening/criterion-answers.csv`](rq1-literature-review/screening/criterion-answers.csv) | Answers (YES, NO, UNCERTAIN) of each model to the seven screening criteria per record | 2,590 | Section 3.2, Step 2; Section 3.5 |
| [`screening/model-decisions.csv`](rq1-literature-review/screening/model-decisions.csv) | Model-level decision derived from the answers by the deterministic screening rule | 2,590 | Section 3.2, Step 2 |
| [`screening/author-decisions.csv`](rq1-literature-review/screening/author-decisions.csv) | Author decisions with review channel and date | 303 | Section 3.2, Step 2; Section 4.1 |
| [`screening/replay_screening_rule.py`](rq1-literature-review/screening/replay_screening_rule.py) | Recomputes every model decision from the stored answers and reports deviations | – | Section 3.5 |
| [`synthesis/condition-findings.csv`](rq1-literature-review/synthesis/condition-findings.csv) | Condition Findings with statement, mechanism, operationalisation hint, page or section, condition, and audit outcome | 599 | Section 3.2, Steps 4–5; Sections 4.2–4.3 |
| [`synthesis/source-fidelity-locators.csv`](rq1-literature-review/synthesis/source-fidelity-locators.csv) | Source locators of the audited evidence spans: publication, section, and line range | 1,248 | Section 3.2, Step 5; Section 3.5 |
| [`synthesis/contributing-publications.csv`](rq1-literature-review/synthesis/contributing-publications.csv) | Bibliographic details of the publications that contribute Condition Findings: authors, year, title, venue, and DOI where available | 209 | Section 4.1; Appendix B |

Finding statements may contain short quotations from the source publication.
Each finding names its publication by `corpus_id`, which resolves to a full citation in `contributing-publications.csv`, and the source locators name the section and lines of the passage.
The build shortens marked quotations longer than 25 words. Wording close to the source without quotation marks is not detected automatically.

### [`rq2-operationalisation/`](rq2-operationalisation/)

| File | Content | Records | Thesis reference |
|---|---|---:|---|
| [`aspect-register.csv`](rq2-operationalisation/aspect-register.csv) | Classification record of every condition aspect: label, text anchor in its condition, cited Condition Findings, use (OR1), information (OR2), and producer (OR3) with the result of each test, classification, exclusion by the scope of the study, and for operationalisable aspects the platform capability, fit, baseline coverage, and selection | 75 | Section 3.3, Steps 4–5; Sections 5.2–5.3; Appendix D-1 |

The classification fields describe each aspect independently of the governance application and carry no case identifier.
The design sketches and the free-text fit notes of the internal register are not exported, because they name internal schema elements.
Test results are `pass`, `fail`, or `na` (not testable without specified information).
The column `study_boundary` marks an operationalisable aspect that the scope of the study excludes from implementation, shown as *Yes, excluded* in the column *Op.* of Table D.2 of the thesis.

### [`tools/`](tools/)

| File | Content |
|---|---|
| [`build_annex.py`](tools/build_annex.py) | Builds the annex from the internal research record. Every exported field is listed explicitly. |
| [`replay_screening_rule.py`](tools/replay_screening_rule.py) | Source of the replay script in `rq1-literature-review/screening/` |

## Conventions

- Files are UTF-8 encoded CSV with a header row.
- `corpus_id` links the files with each other and with TECF.
- Condition Findings are identified as `CF#n`, conditions as `CCnn`, and condition aspects as `CCnn-An`, as in the thesis.
- Dates follow ISO 8601.

## Citation

Citation metadata for this annex are in [`CITATION.cff`](CITATION.cff).
Cite the archived Zenodo release, not the moving branch.

## Licence

- Data and documentation: [CC BY-NC 4.0](LICENSE). Commercial use requires the author's prior written consent.
- Scripts: [MIT](LICENSE-CODE).
- Quotations from third-party publications and their bibliographic details are not covered by these licences.
