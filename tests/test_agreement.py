import pytest

from src.analysis.agreement import cohen_kappa, fleiss_kappa, krippendorff_alpha


def test_cohen_kappa_perfect_agreement():
    assert cohen_kappa([2, 2, 0, 1], [2, 2, 0, 1]) == pytest.approx(1.0)


def test_cohen_kappa_chance_level():
    y1 = ["a", "a", "b", "b"]
    y2 = ["a", "b", "a", "b"]
    assert cohen_kappa(y1, y2) == pytest.approx(0.0, abs=1e-9)


def test_cohen_kappa_hand_computed():
    y1 = ["a", "a", "b", "a", "b"]
    y2 = ["a", "a", "a", "b", "b"]
    assert cohen_kappa(y1, y2) == pytest.approx(1 / 6, abs=1e-9)


def test_fleiss_kappa_hand_computed():
    counts = [[3, 0], [2, 1], [1, 2], [0, 3]]
    assert fleiss_kappa(counts) == pytest.approx(1 / 3, abs=1e-9)


def test_fleiss_kappa_perfect():
    counts = [[3, 0], [3, 0], [0, 3], [0, 3]]
    assert fleiss_kappa(counts) == pytest.approx(1.0)


def test_fleiss_kappa_mismatched_raters_rejected():
    with pytest.raises(ValueError):
        fleiss_kappa([[2, 1], [2]])


def test_krippendorff_alpha_perfect():
    assert krippendorff_alpha([[1, 1, 1], [2, 2, 2], [0, 0, 0]]) == pytest.approx(1.0)


def test_krippendorff_alpha_matches_fleiss_data():
    units = [[2, 2, 2], [2, 2, 1], [2, 1, 1], [1, 1, 1]]
    expected = 1 - (4 / 12) / (72 / 132)
    assert krippendorff_alpha(units, level="nominal") == pytest.approx(expected, abs=1e-9)


def test_krippendorff_alpha_tolerates_missing():
    units = [[1, 1, None], [2, "", 2], [0, 0, 0]]
    value = krippendorff_alpha(units)
    assert 0.0 <= value <= 1.0


def test_krippendorff_alpha_anti_agreement_negative():
    units = [[0, 1], [1, 0], [0, 1], [1, 0]]
    assert krippendorff_alpha(units) < 0
