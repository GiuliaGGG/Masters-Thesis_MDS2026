###################################################
### chunk number 1: 
###################################################
library("Synth")
library(readr)
library(dplyr)
library(skimr)
library(tidyr)

df <- read_csv("data/merged_dataset_2025-11-01_16-55.csv")

# Preprocessing
df_clean <- df %>%
  
  # Filter
    # rows
    filter(ticker != "COKE") %>% #make sure there just one target
    filter(ticker != "BROS") %>%  #drop for now, has very few years , might be an issue from the data fetching 
    filter(fy < "2026") %>% 
    filter(fy != "2009") %>% # quick and dirty fix for now
  
    # columns 
    select(where(~ !all(is.na(.)))) %>% 
  
  # Create useful columns 
    mutate(company_id = as.numeric(as.factor(ticker))) %>%  
  
    # Balance 
    #complete(
    complete(
      ticker,
      fy = full_seq(unique(fy), 1)  # fills all years in the full observed range
    ) %>%
    # fill stable company info ---
    group_by(ticker) %>%
    fill(company_id, boycotted, .direction = "downup") %>%
    ungroup() %>%
    
    # --- Count quarters per company-year ---
    group_by(ticker, fy) %>%
    mutate(n_quarters = n_distinct(fp)) %>%
    ungroup() %>%
    
    # --- Now handle both complete and incomplete in one go ---
    { 
      bind_rows(
        # 1️⃣ Keep companies with all quarters (complete)
        filter(., n_quarters == 3) %>% 
          select(-n_quarters),
        
        # 2️⃣ Fill missing quarters for incomplete ones
        filter(., n_quarters < 3) %>%
          select(-n_quarters) %>%
          complete(ticker, fy, fp = c("Q1", "Q2", "Q3")) %>%
          group_by(ticker) %>%
          fill(company_id, boycotted, .direction = "downup") %>%
          ungroup()
      )
    } %>% 
    
    # --- Remove any duplicates & tidy up ---
    distinct(ticker, fy, fp, .keep_all = TRUE) %>%
    arrange(ticker, fy, fp) %>% 

    #inpute nas for the dependent variable 
    group_by(ticker) %>% 
    fill(net_income, .direction = "downup") %>% 
    ungroup() %>% 
    
  
    #filter(ticker != "CMG") %>% #    drop for now, must see if script runs when df is balanced 
    #filter(ticker != "BROS") %>% #drop for now, must see if script runs when df is balanced 
  
   # Turn fp (Q1, Q2, Q3, Q4) into numeric quarter fraction
    mutate( 
      quarter_num = case_when(
        fp == "Q1" ~ 0.25,
        fp == "Q2" ~ 0.50,
        fp == "Q3" ~ 0.75,
        fp == "Q4" ~ 1.00,
        TRUE ~ NA_real_
      ),
      # Combine fiscal year and quarter into one numeric time variable
      time_numeric = fy + quarter_num) %>% 
      select(-quarter_num) %>%
    as.data.frame()  
  
  
  
  
# dataprep 
dataprep(
  foo = df_clean,
  predictors = c("assets",  "net_margin_pct"),
  dependent = "net_income",
  unit.variable = "company_id",          # numeric ID column
  unit.names.variable = "ticker",        # readable name
  time.variable = "time_numeric",                  # or numeric time index
  treatment.identifier = 1,              # treated company ID
  controls.identifier = c(2:5), # control company IDs
  time.predictors.prior = 2010.25:2023.75,
  time.optimize.ssr = 2010.25:2023.75,         # pre-treatment period
  time.plot = 2010.25:2025.75                  # full period to plot
)
