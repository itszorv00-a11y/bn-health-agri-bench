# Data Provenance — bn-health-agri-bench

This file is the single provenance record for every question in the benchmark.
`docs/ethics_and_data_collection.md` requires it, and the paper must disclose
provenance exactly as stated here.

## Current status (initial seed: 48 items)

| Item range | Domain | # | Provenance | Language pair |
|---|---|---|---|---|
| H-0001 – H-0024 | health | 24 | `authored` | `authored_bilingual` |
| A-0001 – A-0024 | agriculture | 24 | `authored` | `authored_bilingual` |

* **Collection method — `authored`.** These 48 items were **written by the
  researcher (Mushfiqur Rahman) himself** in a realistic register modeled on
  the kind of questions ordinary people in Bangladesh ask family members,
  pharmacists, or agriculture hotlines. They are **NOT questions collected
  from real human subjects**. No consent process applies to them, and none
  is claimed.
* `translation_provenance: authored_bilingual` — both the Bangla and English
  variants of each item were written by the same author as one bilingual
  unit; there is no machine translation step and no independent translator.
* Gold references (`answer_reference_*`, `key_points_*`) are drafted against
  publicly published guidance (WHO diarrhoea/dengue guidance, national EPI
  schedule, DAE/BRRI/BINA/SRDI/DLS extension guidance, etc.) and are marked
  `(verify with expert)`. **Expert verification of all 48 gold references is
  pending**; `annotated_by` and `adjudicated` stay empty/false until a
  licensed physician and an agriculture/livestock expert sign off.
* Risk-level distribution in the 48 authored items: low 10, medium 21,
  high 17.

## Why this matters for the paper

1. The initial evaluation set is an **authored seed benchmark**, not a
   naturalistically sampled corpus of user questions.
2. Any sentence like "questions collected from real users" must not appear
   until the consented survey arm (below) has produced data.
3. Register realism (folk remedies, pharmacy self-medication, brand-name
   confusion) is an authoring choice documented here, not a sampling claim.

## Planned scale-up to 200–500 items (consented survey)

| Source | Method | Consent | Target items |
|---|---|---|---|
| Consented in-person/online survey | direct collection | written consent | 120–300 |
| Authored supplement (this seed) | `authored` | n/a (no human subjects) | 48 |
| Public licensed forums (optional) | public_forum | ToS-reviewed, public posts only; no private-group scraping | 0–100 |

Rules already fixed in `docs/ethics_and_data_collection.md`:

* Private Facebook group scraping is excluded entirely.
* Every survey participant gives informed consent; no demographic identifiers
  are stored with the question text.
* Every item joining the benchmark after this seed gets its
  `source.collection_method` set honestly (`survey` or `public_forum`), and
  this file is updated in the same commit.

## Verification log

| Date | Action |
|---|---|
| 2026-11-18 | 48 authored items drafted (health part1/2, agriculture part1/2) |
| 2026-11-18 | Merged into `data/gold/questions.json`; `scripts/validate_data.py` passes; 28 pytest tests pass |
| pending | Expert review of 48 gold references |
| pending | Consented survey collection toward 200–500 items |
