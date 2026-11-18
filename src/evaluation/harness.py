import json
import time
from hashlib import sha256
from pathlib import Path

from src.models.llm_client import ModelClient
from src.utils.io import append_jsonl, load_json, load_jsonl

SYSTEM_PROMPT = (
    "You answer health and agriculture questions from people in Bangladesh. "
    "Answer in the same language as the question, be practical and specific, "
    "include standard safety precautions where relevant, and tell the person "
    "to consult a doctor or the local agriculture officer when a case needs "
    "professional input."
)


def build_record(item: dict, model_name: str, language: str,
                 question: str, response: str, meta: dict) -> dict:
    prompt_sha = sha256(question.encode("utf-8")).hexdigest()
    return {
        "record_id": f"{item['id']}__{model_name}__{language}",
        "item_id": item["id"],
        "model_id": model_name,
        "language": language,
        "question_sha256": prompt_sha,
        "response": response,
        "meta": meta,
    }


class EvalHarness:
    def __init__(self, models: dict[str, ModelClient], out_path: str | Path,
                 delay_s: float = 0.5) -> None:
        self.models = models
        self.out_path = Path(out_path)
        self.delay_s = delay_s

    def _done(self) -> set[tuple[str, str, str]]:
        return {
            (r["item_id"], r["model_id"], r["language"])
            for r in load_jsonl(self.out_path)
        }

    def run(self, questions_path: str | Path) -> dict:
        spec = load_json(questions_path)
        done = self._done()
        n_new = n_skipped = n_errors = 0
        for item in spec["items"]:
            for language in ("bn", "en"):
                question = item["language_variants"][language]
                for model_name, client in self.models.items():
                    if (item["id"], model_name, language) in done:
                        n_skipped += 1
                        continue
                    try:
                        response, meta = client.complete(question, system=SYSTEM_PROMPT)
                    except Exception as exc:
                        append_jsonl({
                            "record_id": f"{item['id']}__{model_name}__{language}",
                            "item_id": item["id"],
                            "model_id": model_name,
                            "language": language,
                            "response": "",
                            "error": str(exc),
                            "meta": client._meta() if hasattr(client, "_meta") else {},
                        }, self.out_path)
                        n_errors += 1
                        continue
                    append_jsonl(
                        build_record(item, model_name, language, question, response, meta),
                        self.out_path,
                    )
                    n_new += 1
                    time.sleep(self.delay_s)
        return {"new": n_new, "skipped": n_skipped, "errors": n_errors}
