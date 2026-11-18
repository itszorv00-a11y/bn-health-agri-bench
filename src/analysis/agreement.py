from collections import Counter
from itertools import combinations
from typing import Sequence


def cohen_kappa(y1: Sequence, y2: Sequence) -> float:
    if len(y1) != len(y2) or not y1:
        raise ValueError("raters must label the same non-empty items")
    n = len(y1)
    po = sum(a == b for a, b in zip(y1, y2)) / n
    cats = set(y1) | set(y2)
    p1 = Counter(y1)
    p2 = Counter(y2)
    pe = sum((p1[c] / n) * (p2[c] / n) for c in cats)
    if pe == 1.0:
        return 1.0 if po == 1.0 else 0.0
    return (po - pe) / (1 - pe)


def fleiss_kappa(counts: Sequence[Sequence[int]]) -> float:
    counts = [list(row) for row in counts]
    if not counts:
        raise ValueError("no units")
    n_categories = len(counts[0])
    if any(len(row) != n_categories for row in counts):
        raise ValueError("all rows must have the same number of categories")
    n_units = len(counts)
    raters = sum(counts[0])
    if raters < 2 or any(sum(row) != raters for row in counts):
        raise ValueError("each unit must have the same number of ratings (>= 2)")

    p_j = [sum(row[j] for row in counts) / (n_units * raters) for j in range(n_categories)]
    p_i = []
    for row in counts:
        p_i.append((sum(c * c for c in row) - raters) / (raters * (raters - 1)))
    p_bar = sum(p_i) / n_units
    p_e = sum(p ** 2 for p in p_j)
    if p_e == 1.0:
        return 1.0 if p_bar == 1.0 else 0.0
    return (p_bar - p_e) / (1 - p_e)


def krippendorff_alpha(ratings: Sequence[Sequence], level: str = "nominal") -> float:
    if level not in {"nominal", "ordinal"}:
        raise ValueError("level must be 'nominal' or 'ordinal'")
    units = [[r for r in unit if r is not None and r != ""] for unit in ratings]
    units = [u for u in units if len(u) >= 2]
    if not units:
        raise ValueError("need at least one unit with >= 2 ratings")

    flat = [r for unit in units for r in unit]
    n_total = len(flat)
    cat_counts = Counter(flat)
    values = sorted(cat_counts)

    def disagree(a, b) -> float:
        if level == "nominal":
            return 0.0 if a == b else 1.0
        if len(values) < 2:
            return 0.0
        ranks = {v: i for i, v in enumerate(values)}
        return ((ranks[a] - ranks[b]) / (len(values) - 1)) ** 2

    obs_sum = 0.0
    obs_pairs = 0
    for unit in units:
        for a, b in combinations(unit, 2):
            obs_sum += disagree(a, b)
            obs_pairs += 1
    if obs_pairs == 0:
        return 1.0
    d_obs = obs_sum / obs_pairs

    all_pairs = n_total * (n_total - 1) / 2
    same_pairs = sum(c * (c - 1) / 2 for c in cat_counts.values())
    d_exp = 1.0 - same_pairs / all_pairs
    if d_exp == 0.0:
        return 1.0
    return 1.0 - d_obs / d_exp
