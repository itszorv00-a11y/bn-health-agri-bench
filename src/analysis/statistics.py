import random
from math import comb
from typing import Sequence


def bootstrap_mean_ci(samples: Sequence[float], iters: int = 10_000,
                      ci: float = 0.95, seed: int = 1234) -> tuple[float, float, float]:
    if len(samples) == 0:
        raise ValueError("empty samples")
    rng = random.Random(seed)
    samples = [float(s) for s in samples]
    n = len(samples)
    mean = sum(samples) / n
    lo_i = int(((1 - ci) / 2) * iters)
    hi_i = min(int((1 - (1 - ci) / 2) * iters), iters - 1)
    means = []
    for _ in range(iters):
        total = 0.0
        for _ in range(n):
            total += samples[rng.randrange(n)]
        means.append(total / n)
    means.sort()
    return mean, means[lo_i], means[hi_i]


def mcnemar_exact(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    prob = sum(comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * prob)


def paired_permutation_p(x: Sequence[float], y: Sequence[float],
                         iters: int = 10_000, seed: int = 1234) -> float:
    if len(x) != len(y) or not x:
        raise ValueError("x and y must be paired and non-empty")
    diffs = [a - b for a, b in zip(x, y)]
    observed = abs(sum(diffs) / len(diffs))
    rng = random.Random(seed)
    n = len(diffs)
    count = 0
    for _ in range(iters):
        total = sum(d if rng.random() < 0.5 else -d for d in diffs)
        if abs(total / n) >= observed - 1e-12:
            count += 1
    return (count + 1) / (iters + 1)


def language_gap_ci(correct_bn: Sequence[float], correct_en: Sequence[float],
                    iters: int = 10_000, ci: float = 0.95,
                    seed: int = 1234) -> dict:
    if len(correct_bn) != len(correct_en):
        raise ValueError("paired lists must be the same length")
    diffs = [a - b for a, b in zip(correct_bn, correct_en)]
    mean, lo, hi = bootstrap_mean_ci(diffs, iters=iters, ci=ci, seed=seed)
    return {
        "mean_gap": mean,
        "ci95": [lo, hi],
        "n": len(diffs),
        "permutation_p": paired_permutation_p(correct_bn, correct_en,
                                              iters=iters, seed=seed),
    }
