import math
from typing import Dict, List, Optional, Tuple
import pandas as pd
from pydantic import BaseModel, Field

class ContingencyTable(BaseModel):
    """
    2x2 contingency table counts for a single drug-adverse event pair.

    Layout:
                    Target Event (E)    Other Events (~E)     Total
    Target Drug (D)        a                   b              a + b
    Other Drugs (~D)       c                   d              c + d
    Total                a + c               b + d              N
    """
    a: int = Field(..., ge=0, description="Target drug + Target adverse event")
    b: int = Field(..., ge=0, description="Target drug + Other adverse events")
    c: int = Field(..., ge=0, description="Other drugs + Target adverse event")
    d: int = Field(..., ge=0, description="Other drugs + Other adverse events")

    @property
    def total_records(self) -> int:
        """Return the sum of all cell counts (N)."""
        return self.a + self.b + self.c + self.d


class DisproportionalityResult(BaseModel):
    """Encapsulates the statistical indicators and safety signal classification."""
    reaction_term: str
    target_cases: int
    prr: float
    prr_ci_lower: float
    prr_ci_upper: float
    chi2: float
    is_signal: bool


def calculate_prr(table: ContingencyTable) -> float:
    """
    Calculate the Proportional Reporting Ratio (PRR).

    Formula:
        PRR = [a / (a + b)] / [c / (c + d)]
    """
    row1_sum = table.a + table.b
    row2_sum = table.c + table.d

    if row1_sum == 0 or row2_sum == 0:
        return 0.0

    numerator = table.a / row1_sum
    denominator = table.c / row2_sum

    if denominator == 0.0:
        return 0.0

    return round(numerator / denominator, 3)


def calculate_prr_ci(table: ContingencyTable, prr: float) -> Tuple[float, float]:
    """
    Compute the 95% Confidence Interval for the PRR using log-transform standard error.

    SE(ln(PRR)) = sqrt( 1/a - 1/(a+b) + 1/c - 1/(c+d) )
    CI_95% = exp( ln(PRR) +/- 1.96 * SE )
    """
    if prr <= 0.0 or table.a == 0 or table.c == 0:
        return 0.0, 0.0

    row1_sum = table.a + table.b
    row2_sum = table.c + table.d

    try:
        variance = (1.0 / table.a) - (1.0 / row1_sum) + (1.0 / table.c) - (1.0 / row2_sum)
        if variance < 0:
            return 0.0, 0.0

        se = math.sqrt(variance)
        log_prr = math.log(prr)

        lower_bound = math.exp(log_prr - 1.96 * se)
        upper_bound = math.exp(log_prr + 1.96 * se)

        return round(lower_bound, 3), round(upper_bound, 3)

    except (ValueError, ZeroDivisionError):
        return 0.0, 0.0


def calculate_chi2_yates(table: ContingencyTable) -> float:
    """
    Calculate Pearson's Chi-squared statistic with Yates' continuity correction.

    Formula:
        Chi2 = [ N * (|ad - bc| - N/2)^2 ] / [ (a+b)(c+d)(a+c)(b+d) ]
    """
    n = table.total_records
    ad_minus_bc = abs(table.a * table.d - table.b * table.c)
    corrected_diff = max(0.0, ad_minus_bc - (n / 2.0))

    numerator = n * (corrected_diff ** 2)
    denominator = (
        (table.a + table.b)
        * (table.c + table.d)
        * (table.a + table.c)
        * (table.b + table.d)
    )

    if denominator == 0:
        return 0.0

    return round(numerator / denominator, 3)


def analyze_disproportion(
    reaction_term: str,
    table: ContingencyTable,
    min_cases: int = 3,
    prr_threshold: float = 2.0,
    chi2_threshold: float = 4.0,
) -> DisproportionalityResult:
    """
    Evaluate whether a drug-event association satisfies Evans' pharmacovigilance criteria.

    Standard Evans Criteria:
        - a >= 3
        - PRR >= 2.0
        - Chi-square (Yates) >= 4.0
    """
    prr = calculate_prr(table)
    ci_lower, ci_upper = calculate_prr_ci(table, prr)
    chi2 = calculate_chi2_yates(table)

    is_signal = (
        table.a >= min_cases
        and prr >= prr_threshold
        and chi2 >= chi2_threshold
    )

    return DisproportionalityResult(
        reaction_term=reaction_term,
        target_cases=table.a,
        prr=prr,
        prr_ci_lower=ci_lower,
        prr_ci_upper=ci_upper,
        chi2=chi2,
        is_signal=is_signal,
    )


if __name__ == "__main__":
    # Integration smoke test using synthetic contingency data
    sample_table = ContingencyTable(a=15, b=85, c=50, d=950)
    sample_reaction = "ALOPECIA"

    evaluation = analyze_disproportion(reaction_term=sample_reaction, table=sample_table)

    print("--- Pharmacovigilance Signal Evaluation ---")
    print(f"Adverse Reaction : {evaluation.reaction_term}")
    print(f"Exposed Cases (a): {evaluation.target_cases}")
    print(f"PRR              : {evaluation.prr} [95% CI: {evaluation.prr_ci_lower} - {evaluation.prr_ci_upper}]")
    print(f"Chi-square (Yat.): {evaluation.chi2}")
    print(f"Signal Flag      : {'POSITIVE SIGNAL DETECTED' if evaluation.is_signal else 'NO SIGNAL'}")