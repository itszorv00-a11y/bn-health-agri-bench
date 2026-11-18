import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analysis.error_analysis import (aggregate, error_profile,
                                         mcnemar_by_model,
                                         paired_language_gaps)
from src.utils.io import load_jsonl, save_json


def merge(records_path: Path, annotations_path: Path) -> list[dict]:
    records = load_jsonl(records_path)
    annotations = {}
    import csv
    with open(annotations_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["item_id"], row["model_id"], row["language"])
            annotations[key] = row
    merged = []
    for record in records:
        key = (record["item_id"], record["model_id"], record["language"])
        annotation = annotations.get(key)
        if annotation is None:
            continue
        merged.append({
            **record,
            "correctness": int(annotation["correctness"]),
            "safety_label": annotation.get("safety_label", ""),
            "error_tags": [t for t in (annotation.get("error_tags") or "").split(";") if t],
            "item_type": annotation.get("item_type", "unknown"),
        })
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap statistics and error analysis")
    parser.add_argument("--records", required=True)
    parser.add_argument("--annotations", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    merged = merge(Path(args.records), Path(args.annotations))
    if not merged:
        print("no records matched annotations; nothing to analyze")
        return 1
    results = {
        "n_merged": len(merged),
        "aggregate": aggregate(merged),
        "mcnemar_language": mcnemar_by_model(merged),
        "language_gaps": paired_language_gaps(merged),
        "errors": error_profile(merged),
    }
    save_json(results, args.out)
    print(json.dumps(results["aggregate"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
