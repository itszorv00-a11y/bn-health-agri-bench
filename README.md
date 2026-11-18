# bn-health-agri-bench

**Bangla Health & Agriculture LLM Reliability Benchmark** — একটি annotated
paired-language (Bangla/English) benchmark ও evaluation framework, যা বাংলায়
স্বাস্থ্য ও কৃষি বিষয়ক প্রশ্নে LLM-এর সঠিকতা (correctness), নিরাপত্তা
(safety) এবং ভাষা-ভিত্তিক পার্থক্য (language gap) পরিমাপ করে।

> ⚠️ **টেমপ্লেট স্টেট:** এই repo-তে এখন শুধু framework, schema, annotation
> guideline, seed টেমপ্লেট (ডেমো আইটেম) এবং paper skeleton আছে। বাস্তব
> প্রশ্ন সংগ্রহ ও expert annotation হলো human workflow —
> [docs/ethics_and_data_collection.md](docs/ethics_and_data_collection.md)
> দেখুন। `data/seed/`-এর আইটেমগুলো বেঞ্চমার্ক নয়, শুধু ফরম্যাটের উদাহরণ।
> Gold answer গুলো domain expert দিয়ে verify না হওয়া পর্যন্ত চূড়ান্ত নয়।

## Pipeline

```
collect questions → paired translation → expert annotation → IAA check
        → run models (bn + en) → score (correctness + safety) →
bootstrap stats + McNemar → error analysis → figures → paper
```

## Repository layout

| Path | What |
|---|---|
| `data/schema/` | JSON Schemas: question, annotation; safety + error taxonomy |
| `data/seed/` | Format-exemplar items (demo only, not the benchmark) |
| `data/gold/` | Expert gold answers + annotations (you add these) |
| `data/results/` | Model outputs (JSONL, gitignored) |
| `docs/` | Annotation guideline, ethics & collection protocol, model versioning |
| `src/models/` | Unified LLM API client (OpenAI / Anthropic / Google / Mock) |
| `src/evaluation/` | Harness, rubric + key-point scoring, safety flags |
| `src/analysis/` | IAA (Cohen/Fleiss/Krippendorff), bootstrap stats, McNemar, error analysis |
| `scripts/` | CLIs: validate, run_eval, compute_iaa, bootstrap_stats, make_figures |
| `paper/` | LaTeX skeleton (`main.tex` + sections) |

## Quickstart

```bash
pip install -r requirements.txt
make validate            # check seed data against schema rules
make test                # unit tests (agreement, stats, scoring)

# 1. Annotate collected questions per docs/annotation_guideline.md
#    → data/gold/questions.json, data/gold/annotations.csv, IAA >= 0.6 target

# 2. Run models (API keys via environment; never hardcode)
export OPENAI_API_KEY=... ANTHROPIC_API_KEY=... GOOGLE_API_KEY=...
python scripts/run_eval.py --questions data/gold/questions.json \
    --models gpt-4o-2024-08-06,claude-sonnet-4-20250514,gemini-1.5-pro-002 \
    --out data/results/records.jsonl

# 3. Statistics and analysis
python scripts/bootstrap_stats.py --records data/results/records.jsonl \
    --annotations data/gold/annotations.csv --out data/results/stats.json
python scripts/make_figures.py --out figures/

# 4. Paper
make paper
```

## Design commitments

- **Paired translation:** every item exists in Bangla and English; language
  gap is measured within-item (paired), not across different questions.
- **Determinism:** `temperature=0`, fixed system prompt, exact model
  version/snapshot recorded with every response (see
  [docs/model_versioning.md](docs/model_versioning.md)).
- **Human-verified scoring:** automated key-point coverage and safety flags
  are *assistive*; final labels require human annotators, and disagreement
  rates (IAA) are reported.
- **Honest safety taxonomy:** labels are defined *before* model runs
  ([data/schema/taxonomy.json](data/schema/taxonomy.json)) to avoid post-hoc bias.

## Requirements

Python ≥ 3.10, `numpy`, `matplotlib`, `requests`, `pytest` (dev).
