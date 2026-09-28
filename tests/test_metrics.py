import pytest
from src.metrics import (
    ContingencyTable,
    calculate_prr,
    calculate_prr_ci,
    calculate_chi2_yates,
    analyze_disproportion,
)


@pytest.fixture
def signal_table() -> ContingencyTable:
    """Fixture providing a classic positive signal 2x2 contingency table."""
    # a=15, b=85, c=50, d=950 -> PRR = (15/100) / (50/1000) = 0.15 / 0.05 = 3.0
    return ContingencyTable(a=15, b=85, c=50, d=950)


@pytest.fixture
def non_signal_table() -> ContingencyTable:
    """Fixture providing a balanced, non-signal 2x2 contingency table."""
    # PRR = (2/100) / (20/1000) = 0.02 / 0.02 = 1.0
    return ContingencyTable(a=2, b=98, c=20, d=980)


def test_calculate_prr(signal_table: ContingencyTable):
    """Test exact mathematical computation of the PRR."""
    prr = calculate_prr(signal_table)
    assert prr == 3.0


def test_calculate_prr_zero_division():
    """Ensure edge cases with zero counts do not raise ZeroDivisionError."""
    zero_table = ContingencyTable(a=0, b=10, c=0, d=100)
    assert calculate_prr(zero_table) == 0.0


def test_calculate_prr_ci(signal_table: ContingencyTable):
    """Ensure the 95% Confidence Interval bounds bracket the PRR point estimate."""
    prr = calculate_prr(signal_table)
    lower, upper = calculate_prr_ci(signal_table, prr)
    assert lower > 0
    assert upper > lower
    assert lower <= prr <= upper


def test_calculate_chi2_yates(signal_table: ContingencyTable):
    """Validate Yates' corrected chi-square output against expected bounds."""
    chi2 = calculate_chi2_yates(signal_table)
    assert chi2 > 14.0  # Statistically significant (p < 0.001)


def test_analyze_disproportion_positive_signal(signal_table: ContingencyTable):
    """Verify that a table meeting Evans' criteria flags is_signal as True."""
    result = analyze_disproportion(
        reaction_term="ALOPECIA",
        table=signal_table,
        min_cases=3,
        prr_threshold=2.0,
        chi2_threshold=4.0,
    )
    assert result.is_signal is True
    assert result.reaction_term == "ALOPECIA"
    assert result.target_cases == 15


def test_analyze_disproportion_negative_signal(non_signal_table: ContingencyTable):
    """Verify that sub-threshold data correctly returns is_signal as False."""
    result = analyze_disproportion(
        reaction_term="HEADACHE",
        table=non_signal_table,
        min_cases=3,
        prr_threshold=2.0,
        chi2_threshold=4.0,
    )
    assert result.is_signal is False