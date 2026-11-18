from collections import Counter, defaultdict

from src.analysis.statistics import bootstrap_mean_ci, language_gap_ci
from src.evaluation.safety import flag_risk


def aggregate(records: list[dict]) -> dict:
    by_group: dict[tuple, list[dict]] = defaultdict(list)
    for record in records:
        by_group[(record["model_id"], record["language"])].append(record)

    table = {}
    for (model, language), group in sorted(by_group.items()):
        scores = [float(r["correctness"]) for r in group]
        binary = [1.0 if score >= 1 else 0.0 for score in scores]
        mean, lo, hi = bootstrap_mean_ci(binary)
        safety_counts = Counter(r.get("safety_label", "unlabeled") for r in group)
        error_counts = Counter(tag for r in group for tag in (r.get("error_tags") or []))
        table[f"{model}::{language}"] = {
            "n": len(group),
            "accuracy_at_least_partial": mean,
            "accuracy_ci95": [lo, hi],
            "mean_correctness": sum(scores) / len(scores),
            "unsafe_rate": sum(
                1 for r in group
                if str(r.get("safety_label", "")).startswith("unsafe")
            ) / len(group),
            "safety_counts": dict(safety_counts),
            "error_tag_counts": dict(error_counts),
            "heuristic_risk_flags": dict(Counter(
                tag for r in group for tag in flag_risk(r.get("response", ""))
            )),
        }
    return table


def mcnemar_by_model(records: list[dict]) -> dict:
    pairs_by_model: dict[str, dict[tuple, float]] = defaultdict(dict)
    for record in records:
        pairs_by_model[(record["model_id"], record["item_id"])][record["language"]] = 1.0 if float(record["correctness"]) >= 1 else 0.0

    outcomes: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for (model, _item), langs in pairs_by_model.items():
        if "bn" in langs and "en" in langs:
            outcomes[model].append((langs["bn"], langs["en"]))

    result = {}
    for model, pairs in outcomes.items():
        b = sum(1 for bn, en in pairs if bn == 1.0 and en == 0.0)
        c = sum(1 for bn, en in pairs if bn == 0.0 and en == 1.0)
        from src.analysis.statistics import mcnemar_exact
        result[model] = {"n_pairs": len(pairs), "bn_only_correct": b,
                         "en_only_correct": c, "p_mcnemar": mcnemar_exact(b, c)}
    return result


def paired_language_gaps(records: list[dict]) -> dict:
    pairs_by_model: dict[str, dict[tuple, float]] = defaultdict(dict)
    for record in records:
        pairs_by_model[record["model_id"]][(record["item_id"], record["language"])] = float(record["correctness"])

    gaps = {}
    for model, pairs in pairs_by_model.items():
        item_ids = sorted({item for item, _ in pairs})
        if any((item, "bn") not in pairs or (item, "en") not in pairs for item in item_ids):
            continue
        bn = [pairs[(item, "bn")] for item in item_ids]
        en = [pairs[(item, "en")] for item in item_ids]
        gaps[model] = language_gap_ci(bn, en)
    return gaps


def error_profile(records: list[dict]) -> dict:
    per_model: dict[str, Counter] = defaultdict(Counter)
    per_item_type: dict[str, Counter] = defaultdict(Counter)
    for record in records:
        tags = record.get("error_tags") or []
        per_model[record["model_id"]].update(tags)
        per_item_type[record.get("item_type", "unknown")].update(tags)
    totals: Counter = Counter()
    for counter in per_model.values():
        totals.update(counter)
    return {
        "per_model": {model: dict(counter) for model, counter in per_model.items()},
        "per_item_type": {t: dict(counter) for t, counter in per_item_type.items()},
        "totals": dict(totals),
    }
