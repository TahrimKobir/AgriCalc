"""Tests for AgriCalc core functions."""

import numpy as np
import pandas as pd
import pytest

from project import (
    build_mean_error_figure,
    calculate_germination,
    clean_dataset,
    significance_letters,
    run_anova,
    treatment_summary,
)


def test_calculate_germination():
    assert calculate_germination(100, 85) == 85.0
    assert np.isnan(calculate_germination(0, 10))
    assert np.isnan(calculate_germination(100, -1))


def test_clean_dataset():
    data = pd.DataFrame(
        {
            "Treatment": [" Control ", "Nano-Zn | Batch 1", "Invalid"],
            "Seeds_Sown": [100, 100, 0],
            "Seeds_Germinated": [80, 90, 10],
            "Yield_g": [40, 55, 20],
        }
    )
    cleaned = clean_dataset(data)
    assert len(cleaned) == 2
    assert cleaned.loc[0, "Germination_%"] == 80.0
    assert cleaned.loc[1, "Treatment_Group"] == "Nano-Zn"


def test_clean_dataset_missing_column():
    data = pd.DataFrame({"Treatment": ["A"]})
    with pytest.raises(ValueError, match="Missing required column"):
        clean_dataset(data)


def test_treatment_summary():
    data = pd.DataFrame(
        {"Treatment_Group": ["A", "A", "B", "B"], "Yield_g": [10, 14, 20, 22]}
    )
    summary = treatment_summary(data)
    means = dict(zip(summary["Treatment_Group"], summary["Mean"]))
    assert means["A"] == 12
    assert means["B"] == 21
    assert summary.loc[summary["Treatment_Group"] == "A", "SE"].iloc[0] == 2.0


def test_run_anova():
    data = pd.DataFrame(
        {
            "Treatment_Group": ["A"] * 4 + ["B"] * 4 + ["C"] * 4,
            "Yield_g": [10, 11, 9, 10, 20, 21, 19, 20, 30, 31, 29, 30],
        }
    )
    f_stat, p_value, tukey = run_anova(data)
    assert f_stat > 0
    assert p_value < 0.05
    assert len(tukey) == 3
    assert {"Treatment 1", "Treatment 2", "Adjusted p", "Significant"}.issubset(tukey.columns)


def test_run_anova_rejects_invalid_alpha():
    data = pd.DataFrame({"Treatment_Group": ["A", "A"], "Yield_g": [1, 2]})
    with pytest.raises(ValueError, match="alpha"):
        run_anova(data, alpha=1.5)


def test_significance_letters():
    data = pd.DataFrame(
        {
            "Treatment_Group": ["A"] * 4 + ["B"] * 4 + ["C"] * 4,
            "Yield_g": [10, 11, 9, 10, 20, 21, 19, 20, 30, 31, 29, 30],
        }
    )
    letters = significance_letters(data)
    assert set(letters) == {"A", "B", "C"}
    assert len(set(letters.values())) == 3


def test_build_mean_error_figure():
    data = pd.DataFrame(
        {
            "Treatment_Group": ["A"] * 3 + ["B"] * 3,
            "Yield_g": [10, 11, 9, 20, 21, 19],
        }
    )
    figure = build_mean_error_figure(data)
    assert len(figure.data) == 1
    assert figure.data[0].orientation == "h"
