import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.io import load_json

TAXONOMY = load_json(Path(__file__).resolve().parents[1] / "data/schema/taxonomy.json")


def validate_items(path: Path) -> list[str]:
    errors = []
    data = load_json(path)
    items = data.get("items", [])
    if not items:
        return [f"{path}: no items found"]
    seen = set()
    for i, item in enumerate(items):
        where = f"{path} item[{i}] ({item.get('id', '?')})"
        for field in ("id", "domain", "risk_level", "item_type", "source",
                      "language_variants", "gold"):
            if field not in item:
                errors.append(f"{where}: missing field '{field}'")
        if item.get("domain") not in TAXONOMY["domains"]:
            errors.append(f"{where}: bad domain")
        if item.get("risk_level") not in TAXONOMY["risk_levels"]:
            errors.append(f"{where}: bad risk_level")
        if item.get("item_type") not in TAXONOMY["item_types"]:
            errors.append(f"{where}: bad item_type")
        if item["id"] in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(item.get("id"))
        if not re.fullmatch(r"(TEMPLATE-)?(H|A)-[0-9]{4}", item.get("id", "")):
            errors.append(f"{where}: id does not match pattern")
        variants = item.get("language_variants", {})
        for lang in ("bn", "en"):
            if not variants.get(lang, "").strip():
                errors.append(f"{where}: missing '{lang}' variant")
        gold = item.get("gold", {})
        for field in ("answer_reference_bn", "answer_reference_en",
                      "answer_source"):
            if not isinstance(gold.get(field), str) or not gold.get(field).strip():
                errors.append(f"{where}: gold missing '{field}'")
        for field in ("key_points_bn", "key_points_en"):
            points = gold.get(field)
            if not isinstance(points, list) or len(points) < 2:
                errors.append(f"{where}: gold '{field}' needs >= 2 points")
            if points and len(gold.get(field, [])) != len(gold.get(field, [])):
                errors.append(f"{where}: key point count mismatch")
        if len(gold.get("key_points_bn", [])) != len(gold.get("key_points_en", [])):
            errors.append(f"{where}: bn/en key point count mismatch")
        src = item.get("source", {})
        if not src.get("collection_date"):
            errors.append(f"{where}: missing source.collection_date")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate benchmark data files")
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()
    all_errors = []
    for raw in args.files:
        path = Path(raw)
        if path.suffix == ".json":
            try:
                all_errors.extend(validate_items(path))
            except json.JSONDecodeError as exc:
                all_errors.append(f"{path}: invalid JSON ({exc})")
        else:
            all_errors.append(f"{path}: unsupported file type")
    if all_errors:
        for error in all_errors:
            print(f"ERROR {error}")
        return 1
    print("all files valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
