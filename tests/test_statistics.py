import pytest

from src.analysis.statistics import (bootstrap_mean_ci, language_gap_ci,
                                     mcnemar_exact, paired_permutation_p)


def test_bootstrap_ci_contains_mean():
    samples = [0.6] * 40 + [0.2] * 10
    mean, lo, hi = bootstrap_mean_ci(samples, iters=2000, seed=7)
    assert lo <= mean <= hi
    assert mean == pytest.approx(0.52)


def test_bootstrap_deterministic_seed():
    samples = [0.1, 0.5, 0.9]
    a = bootstrap_mean_ci(samples, iters=500, seed=3)
    b = bootstrap_mean_ci(samples, iters=500, seed=3)
    assert a == b


def test_mcnemar_exact_known_value():
    assert mcnemar_exact(1, 9) == pytest.approx(2 * (11 / 1024))


def test_mcnemar_no_discordance():
    assert mcnemar_exact(0, 0) == 1.0


def test_paired_permutation_symmetric():
    x = [2, 1, 2, 0, 1, 2]
    y = [0, 0, 1, 0, 0, 1]
    assert paired_permutation_p(x, y, iters=2000) < 0.1


def test_paired_permutation_identity_high_p():
    x = [1, 0, 2, 1]
    assert paired_permutation_p(x, x, iters=500) == 1.0


def test_language_gap_paired():
    result = language_gap_ci([2, 1, 2, 2], [1, 1, 2, 0])
    assert result["n"] == 4
    assert result["mean_gap"] == pytest.approx(0.75)
    assert result["ci95"][0] <= result["mean_gap"] <= result["ci95"][1]


def test_language_gap_requires_same_length():
    with pytest.raises(ValueError):
        language_gap_ci([1, 2], [1])
