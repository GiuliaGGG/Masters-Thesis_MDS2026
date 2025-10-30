###################################################
### chunk number 1: 
###################################################
library("Synth")
library(readr)
library('dplyr')
df <- read_csv("merged_dataset.csv")

id_cols <- c("boycotted", "ticker", "fy", "fp", "end")

# Step 2: Convert all other columns to numeric
df_clean <- df %>%
  mutate(across(
    .cols = -all_of(id_cols),          # all columns except identifiers
    .fns  = ~ as.numeric(.)  # convert to numeric, quietly
  ))
df <- df_clean %>%
  mutate(company_id = as.numeric(as.factor(ticker)))  # creates 1, 2, 3, ...

###################################################
### chunk number 2: 
###################################################
df_clean[85:89, 1:4]

###################################################
### chunk number 3: 
###################################################
dataprep.out <- dataprep(
  foo = df_clean,
  predictors = c("assets", "employees", "gross_margin_pct", "net_margin_pct",
                 "r_and_d", "long_term_debt", "operating_expenses"),
  predictors.op = "mean",
  time.predictors.prior = 2021:2023,  # pre-boycott quarters
  special.predictors = list(
    list("revenue", 2021:2020, "mean"),   # Include mean past revenue
    list("net_income", 2021:2020, "mean")
  ),
  dependent = "revenue",
  unit.variable = "ticker",
  time.variable = "fy",
  treatment.identifier = 1,         # Boycotted company
  controls.identifier = c(2:20),    # Non-boycotted companies
  time.optimize.ssr = 2021:2020,
  time.plot = 2021:2025
)


###################################################
### chunk number 4: 
###################################################
dataprep.out$X1 #treated unit’s predictor values (Basque Country).

###################################################
### chunk number 5: 
###################################################
dataprep.out$Z1 #treated unit’s outcome values (Basque Country).


