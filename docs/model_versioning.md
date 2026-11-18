# Model Versioning Protocol

LLM behavior changes across releases. Reviewers will reject results that do
not pin versions explicitly. Every run must record, per model:

| Field | Example | Where recorded |
|---|---|---|
| `vendor` | openai / anthropic / google | every record |
| `model_family` | gpt-4o | every record |
| `model_id` (exact) | `gpt-4o-2024-08-06` (dated snapshot) | every record |
| `api_version` | openai API version header; anthropic `anthropic-version` | every record |
| `run_date_utc` | `2026-11-18T10:00:00Z` | every record |
| `temperature` | 0.0 | every record |
| `max_tokens` | 1024 | every record |
| `system_prompt` | fixed string, sha256 recorded | `src/evaluation/harness.py` |
| `prompt_template` | paper appendix | paper |

## Rules

1. **Dated snapshot IDs only.** Never report `gpt-4o` without the exact
   version string.
2. **Temperature 0** for all reported runs. If an API ignores temperature,
   note it in the paper's reproducibility appendix.
3. **One release, one batch.** All headline-experiment models must be run
   within the same two-week window, stated as such in the paper.
4. **Re-verification:** after each major vendor release, re-run the full
   benchmark and report the new snapshot in an appendix; original numbers
   stay as the dated record.
5. **Open-weights models** (if any) record HF revision hash and inference
   stack (inference engine version, quantization, hardware).
6. Never write API keys to logs, results, or the repo. Keys come only from
   environment variables.
