###################################################
### chunk number 1: 
###################################################
library("Synth")
library(readr)
library('dplyr')
library(skimr)


df <- read_csv("data/merged_dataset_2025-11-01_16-55.csv")
id_cols <- c("boycotted", "ticker", "fp", "end")



# Step 2: preprocessing
df_clean <- df %>%
  filter(ticker != "COKE") %>% #make sure there just one target
  filter(ticker != "CMG") %>% #    drop for now, must see if script runs when df is balanced 
  filter(ticker != "WEN") %>% #drop for now, must see if script runs when df is balanced 
  filter(ticker != "BROS") %>% #drop for now, must see if script runs when df is balanced 
  filter(fy != "2026") %>% 
  mutate(company_id = as.numeric(as.factor(ticker))) %>%  
  group_by(ticker, fy) %>%
  # count quarters per company-year
  mutate(n_quarters = n_distinct(fp)) %>%
  # keep only company-years with at least 3 quarters
  filter(n_quarters >= 3) %>%
  ungroup() %>%
  select(-n_quarters) %>%       # remove helper column
  mutate(across(
    .cols = -all_of(id_cols),          # all columns except identifiers
    .fns  = ~ as.numeric(.))) %>%      # convert to numeric, quietly 
  ungroup() %>%  
  mutate(
    # Turn fp (Q1, Q2, Q3, Q4) into numeric quarter fraction
    quarter_num = case_when(
      fp == "Q1" ~ 0.25,
      fp == "Q2" ~ 0.50,
      fp == "Q3" ~ 0.75,
      fp == "Q4" ~ 1.00,
      TRUE ~ NA_real_
    ),
    # Combine fiscal year and quarter into one numeric time variable
    time_numeric = fy + quarter_num) %>% 
  as.data.frame()
 
'FOR NOW drop nas for the dependent variable'
df_clean <- df_clean %>%
  filter(!is.na(revenue))


df_clean <- df_clean %>%
  group_by(ticker) %>%
  arrange(time_numeric) %>%
  mutate(
    revenue = na.approx(revenue, na.rm = FALSE)
  ) %>%
  ungroup()



###################################################
### chunk number 2: 
###################################################
df_clean[85:89, 1:4]

###################################################
### chunk number 3: 
###################################################


dataprep(
  foo = df_clean,
  predictors = c("assets",  "net_margin_pct"),
  dependent = "revenue",
  unit.variable = "company_id",          # numeric ID column
  unit.names.variable = "ticker",        # readable name
  time.variable = "time_numeric",                  # or numeric time index
  treatment.identifier = 3,              # treated company ID
  controls.identifier = c(1,2), # control company IDs
  time.predictors.prior = 2010.25:2023.75,
  time.optimize.ssr = 2010.25:2023.75,         # pre-treatment period
  time.plot = 2010.25:2025.75                  # full period to plot
)


###################################################
### chunk number 4: 
###################################################
dataprep.out$X1 #treated unit’s predictor values (Basque Country).

###################################################
### chunk number 5: 
###################################################
dataprep.out$Z1 #treated unit’s outcome values (Basque Country).


