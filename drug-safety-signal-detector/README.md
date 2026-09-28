# 🔬 Pharmacovigilance Safety Signal Explorer (openFDA / FAERS)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: Pytest](https://img.shields.io/badge/tests-pytest-green.svg)](https://docs.pytest.org/)
[![Deployment: Render](https://img.shields.io/badge/Live%20Demo-Render-46E3B7.svg)](https://drug-safety-signal-detector.onrender.com)

An end-to-end data engineering and statistical screening tool designed to detect adverse drug reaction (ADR) disproportionality signals using official FDA FAERS data and **Evans' pharmacovigilance criteria**.

**Live Interactive Application:** [Launch the Dashboard](https://drug-safety-signal-detector.onrender.com)  
 **Source Code Repository:** [GitHub Project](https://github.com/Ikeepmyideas/drug-safety-signal-detector)

---

## Project Overview

This project bridges modern **Data Engineering** best practices with specialized **Biomedical Data Science**. It extracts nested adverse event records from the US Food and Drug Administration (FDA) openFDA API, strictly validates them via **Pydantic v2** models, and computes regulatory disproportionality metrics (PRR, Yates' corrected Chi-square, 95% Confidence Intervals).

Results are rendered inside an interactive **Streamlit** web dashboard featuring dynamic volcano plots and exportable clinical screening summaries.

---

## Architecture & Pipeline

```text
  [openFDA FAERS API]
          │
          │ (HTTPS REST / JSON Extraction)
          ▼
  [src/api_client.py]
          │   • Custom User-Agent & timeout control
          │   • Resilient network handling (404/retry safe)
          ▼
  [src/schemas.py]
          │   • Pydantic v2 strict schema enforcement
          │   • Extraction of MedDRA Preferred Terms (PT) & drug roles
          ▼
  [src/metrics.py]
          │   • 2x2 Contingency Table construction
          │   • Proportional Reporting Ratio (PRR) computation
          │   • 95% Confidence Interval (log-transformed SE)
          │   • Pearson's Chi-Square with Yates' continuity correction
          ▼
  [app.py (Streamlit & Plotly)]
          │   • Interactive query controls (substances, thresholds, limits)
          │   • Volcano-style disproportionality scatter plot
          │   • Filterable tabular reports with CSV export
          ▼
  [Render Cloud Deployment]
              • Web Service hosting the live interactive application
```

---

## Epidemiological Methodology (Evans et al., 2001)

In pharmacovigilance, disproportionate reporting measures whether an adverse event is reported significantly more often with a specific drug compared to the background database.

### 2×2 Contingency Table Layout

| Exposure / Outcome         | Target Event ($E$) | Other Events ($\neg E$) |  Total  |
| :------------------------- | :----------------: | :---------------------: | :-----: |
| **Target Drug ($D$)**      |        $a$         |           $b$           | $a + b$ |
| **Other Drugs ($\neg D$)** |        $c$         |           $d$           | $c + d$ |
| **Total**                  |      $a + c$       |         $b + d$         |   $N$   |

### Mathematical Formulations

- **Proportional Reporting Ratio (PRR):**
  $$\text{PRR} = \frac{a / (a + b)}{c / (c + d)}$$

- **95% Confidence Interval:**
  $$\text{CI}_{95\%} = \exp\left(\ln(\text{PRR}) \pm 1.96 \cdot \sqrt{\frac{1}{a} - \frac{1}{a+b} + \frac{1}{c} - \frac{1}{c+d}}\right)$$

- **Chi-Square with Yates' Continuity Correction ($\chi^2$):**
  $$\chi^2 = \frac{N \cdot \left(\max\left(0, \vert{}ad - bc\vert{} - \frac{N}{2}\right)\right)^2}{(a+b)(c+d)(a+c)(b+d)}$$

### Decision Rules for Signal Flagging

A drug-event association is flagged as a potential safety signal when:

1. Exposed case count: $a \ge 3$
2. Disproportion threshold: $\text{PRR} \ge 2.0$
3. Statistical significance: $\chi^2 \ge 4.0$ ($p < 0.05$)

---

## Repository Structure

```text
drug-safety-signal-detector/
│
├── .github/
│   └── workflows/
│       └── ci.yml               # Automated Pytest suite on push/PR
├── src/
│   ├── __init__.py
│   ├── api_client.py            # openFDA REST client with error resilience
│   ├── schemas.py               # Pydantic v2 domain schemas & validation
│   └── metrics.py               # Epidemiological calculations (PRR, Yates Chi2)
├── tests/
│   ├── __init__.py
│   ├── test_api_client.py       # Mocked HTTP tests for openFDA endpoints
│   └── test_metrics.py          # Unit tests validating Evans criteria rules
├── app.py                       # Streamlit interactive dashboard & Plotly charts
├── requirements.txt             # Production runtime dependencies
├── pyproject.toml               # Pytest configuration & module resolution
└── README.md                    # Project documentation
```

---

## Local Installation & Setup

### Prerequisites

- Python 3.10 or higher
- Git

### Step-by-Step Guide

1. **Clone the repository:**

   ```bash
   git clone [https://github.com/Ikeepmyideas/drug-safety-signal-detector.git](https://github.com/Ikeepmyideas/drug-safety-signal-detector.git)
   cd drug-safety-signal-detector
   ```

2. **Initialize a virtual environment:**

   ```bash
   python -m venv .venv
   # On Linux/macOS:
   source .venv/bin/activate
   # On Windows:
   .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   pip install pytest
   ```

4. **Execute unit tests:**

   ```bash
   pytest -v
   ```

5. **Start the local Streamlit server:**
   ```bash
   streamlit run app.py
   ```
   Open your browser at `http://localhost:8501`.

---

## ⚖️ Regulatory & Ethical Disclaimer

- This tool is strictly intended for **educational, academic, and exploratory research** purposes. It is **not** a medical device and must **never** be used to guide direct clinical decisions or medical treatments.
- Data is sourced dynamically from the US Food and Drug Administration (FDA) openFDA public domain endpoints.
- Spontaneous reporting systems (FAERS) are subject to reporting bias, underreporting, and confounding factors. A high PRR indicates **statistical disproportionality within reported cases** and **does not demonstrate causal relationship** between the drug and the adverse event.

---

## Author & Contact

- **Role:** Data Scientist (Pharma & Healthcare)
- **GitHub:** [Ikeepmyideas](https://github.com/Ikeepmyideas)
