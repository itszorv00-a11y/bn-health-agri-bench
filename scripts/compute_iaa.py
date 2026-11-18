import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analysis.agreement import cohen_kappa, fleiss_kappa, krippendorff_alpha


def load_annotations(path: Path) -> list[dict]:
    records = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"item_id", "model_id", "language", "annotator_id", "correctness"}
        if not required.issubset(reader.fieldnames or []):
            raise SystemExit(f"missing columns: {sorted(required - set(reader.fieldnames or []))}")
        for row in reader:
            row["correctness"] = int(row["correctness"])
            records.append(row)
    return records


def unit_vectors(records: list[dict]) -> tuple[list[list], list[str]]:
    groups: dict[tuple, dict[str, int]] = defaultdict(dict)
    for r in records:
        key = (r["item_id"], r["model_id"], r["language"])
        groups[key][r["annotator_id"]] = r["correctness"]
    annotators = sorted({r["annotator_id"] for r in records})
    units = [[groups[key].get(a) for a in annotators] for key in sorted(groups)]
    return units, annotators


def fleiss_matrix(units: list[list]) -> list[list[int]]:
    complete = [u for u in units if all(v is not None for v in u)]
    categories = sorted({v for u in complete for v in u})
    return [[u.count(c) for c in categories] for u in complete]


def main() -> int:
    parser = argparse.ArgumentParser(description="Inter-annotator agreement report")
    parser.add_argument("annotations")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    records = load_annotations(Path(args.annotations))
    units, annotators = unit_vectors(records)
    report: dict = {"n_records": len(records), "annotators": annotators,
                    "n_units": len(units)}

    for i in range(len(annotators)):
        for j in range(i + 1, len(annotators)):
            y1 = [u[i] for u in units if u[i] is not None and u[j] is not None]
            y2 = [u[j] for u in units if u[i] is not None and u[j] is not None]
            if y1:
                report[f"kappa_{annotators[i]}_{annotators[j]}"] = round(cohen_kappa(y1, y2), 4)

    try:
        counts = fleiss_matrix(units)
        report["fleiss_kappa"] = round(fleiss_kappa(counts), 4)
    except ValueError as exc:
        report["fleiss_kappa"] = None
        report["fleiss_kappa_note"] = str(exc)

    alpha = krippendorff_alpha(units)
    report["krippendorff_alpha"] = round(alpha, 4)
    report["meets_target"] = alpha >= 0.60

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.out:
        from src.utils.io import save_json
        save_json(report, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
