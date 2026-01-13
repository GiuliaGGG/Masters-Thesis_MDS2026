## Repo Structure

masters_thesis/
│
├── python/                 # Python analysis pipeline
│   ├── config.py           # Central configuration (paths, email)
│   ├── run_pipeline.py     # Main entry point
│   └── scripts/            # Pipeline steps and helper functions
│
├── data/                   # Generated during execution
│   ├── raw/
│   └── processed/
│
├── outputs/                # Analysis-ready outputs
└── README.md

## My Thesis

Political consumer boycotts have become an increasingly prominent tool of digital activism, yet credible empirical evidence on their economic effects remains limited. This thesis estimates the causal impact of political boycott calls on firm performance, focusing on the Boycott, Divestment, and Sanctions (BDS) movement’s boycott of McDonald’s following the outbreak of the genocide in Gaza in 2023. The study asks whether the movement’s recognition of McDonald’s as a boycott target translated into a measurable decline in the firm’s global revenue.
To address this question, I construct an firm-level panel dataset from U.S. Securities and Exchange Commission (SEC) XBRL filings, covering quarterly revenue data from 2011 to 2025.  The thesis applies the Synthetic Control Method (SCM) to estimate a counterfactual revenue trajectory for McDonald’s in the absence of boycott calls, complemented by a two-way fixed effects Difference-in-Differences (DiD) analysis as a robustness exercise.

The `images/` directory contains the final figures used in the thesis.
All figures are fully reproducible using the scripts in the `r/` folder.

## Data Availability

Raw data are not included in this repository due to size constraints.

All data used in the analysis are publicly available and can be fully
reconstructed using the provided Python scripts. The 1_scrapper.py scrapes the financial raw files. 

Scraping the raw data takes approximately 20 minutes.

## Configuration

Before running the pipeline, please edit `python/config.py` and replace
the placeholder email address with your own institutional email address.

This email is used to identify the user when accessing public APIs
(e.g. SEC EDGAR) for academic research purposes.


## SEC XBRL Field Definitions

Each observation corresponds to a single reported XBRL fact retrieved from the SEC Company Facts / Company Concept API. The following fields are used:

- **`start`**  
  Start date of the reporting period covered by the value.

- **`end`**  
  End date of the reporting period covered by the value.

- **`val`**  
  Reported numeric value for the XBRL concept, expressed in the unit specified by the taxonomy (typically USD).

- **`accn`**  
  SEC accession number identifying the filing in which the value was reported.

- **`fy`**  
  Fiscal year of the filing in which the value appears. This may differ from the calendar year of the reported period.

- **`fp`**  
  Fiscal period of the filing (e.g. `FY`, `Q1`, `Q2`, `Q3`, `Q4`).

- **`form`**  
  SEC form type (e.g. `10-K`, `10-Q`, `20-F`).

- **`filed`**  
  Date on which the filing was submitted to the SEC.

- **`frame`**  
  Standardized time-frame label provided by the SEC (e.g. `CY2007`, `CY2007Q4`), used to align observations across firms.
