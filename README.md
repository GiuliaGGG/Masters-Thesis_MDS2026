My masters thesis project assesses the effectiveness of the Boycott, Divest, Sanction (BDS) movement's calls on company performance. Through the usage of Synthetic Control Method (SCM) I am generating a reliable counterfactual of what company's X performance would have looked like were the BDS calls for a boycott never happened.


## 📘 SEC XBRL Field Definitions

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
