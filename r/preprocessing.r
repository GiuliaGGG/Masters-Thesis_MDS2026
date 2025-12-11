###################################################
### chunk number 1: 
###################################################
library("Synth")
library(readr)
library(dplyr)
library(skimr)
library(tidyr)
library(ggplot2)
library(tidysynth)
# devtools::install_github("edunford/tidysynth")
require(tidysynth)
library(gsynth)
data(gsynth)
library(dplyr)
library(purrr)
ls()
head(simdata)
## devtools::install_github('xuyiqing/panelView')   # if not already installed
library(panelView)

# to check raw data days imbalance 
df <- read_csv("data/with_start_date/merged_dataset_with_start_date_2025-12-10_20-39.csv")

test <- df %>%
  #filter(!frequency == 'A') %>%  
       group_by(boycotted, ticker, fy, fp, end) %>%
       summarise(across(everything(), ~ {
            # If all values are NA, return NA
               # Otherwise return the first non-NA
               if(all(is.na(.x))) NA else .x[which(!is.na(.x))[1]]
        }), .groups = "drop") 

test$interval_days<- test$end - test$start
test$interval_days <- as.numeric(test$interval_days)

# fix irregularities 

test_temp_col <- test %>%
  mutate(
    brackets = case_when(
      interval_days <= 120 ~ "quarterly",
      interval_days >= 121 & interval_days <= 200 ~ "semestral",
      interval_days >= 201 & interval_days <= 280 ~ "three_quarters",
      interval_days > 280                         ~ "annual",
      TRUE ~ NA_character_
    )
  )


vars <- c(
  "revenue","gross_profit","net_income","operating_expenses","r_and_d",
  "depr_amort","interest_expense","interest_income","income_before_tax",
  "tax_expense","eps_basic","eps_diluted","shares_basic","shares_diluted",
  "assets","assets_current","liabilities","liabilities_current","equity",
  "cash","accounts_receivable","inventory","long_term_debt","capex",
  "operating_cf","investing_cf","financing_cf","employees"
)

test_adjusted <- test_temp_col %>%
  group_by(ticker, fy) %>%
  mutate(across(all_of(vars), ~ {
    
    # Compute mean of the other rows
    mean_others <- (sum(.x, na.rm = TRUE) - .x) / (n() - 1)
    threshold <- 2 * mean_others
    
    # # ABOVE threshold → branch on bracket
    # above_val <- case_when(
    #   brackets == "semestral" ~ .x / 2,
    #   brackets == "three_quarters" ~ .x / 3,
    #   brackets == "annual" ~ .x / 4,
    #   brackets == "quarterly" & fp == "FY" ~ .x / 4,
    #   TRUE ~ .x
    # )
    corrected <- case_when(
      period_detected == "quarter"     ~ x,
      period_detected == "semiannual"  ~ x / 2,
      period_detected == "nine_month"  ~ x / 3,
      period_detected == "annual"      ~ x / 4,
      TRUE ~ x
    )
    
    # BELOW threshold → repeat original value
    below_val <- .x
    
    # Final result
    ifelse(.x > threshold, above_val, below_val)
    
  }, .names = "{.col}_test")) %>%
  ungroup() %>% 
  mutate(fp = ifelse(fp == "FY", "Q4", fp)) %>% 
  mutate( 
    quarter_num = case_when(
      fp == "Q1" ~ 0.25,
      fp == "Q2" ~ 0.50,
      fp == "Q3" ~ 0.75,
      fp == "Q4" ~ 0.99,
      TRUE ~ NA_real_
    ),
    # Combine fiscal year and quarter into one numeric time variable
    time_numeric = fy + quarter_num) %>% 
  select(-quarter_num) %>% #this brings to mcd_test 
  # reorder and grab useful 
  select(
    boycotted, ticker, fy, fp, time_numeric,
    ends_with("_test")
  ) %>% #clean the column title by removing test 
  rename_with(~ sub("_test$", "", .x), ends_with("_test"))




#df <- read_csv("data/merged_dataset_2025-11-18_13-31.csv")
#df <- read_csv("data/merged_dataset_2025-11-28_15-00.csv")

#boycotted_firm = "MCD"

# boycotted_firm = "DPZ" # not great
# boycotted_firm = "PZZA" # not great
# boycotted_firm = "QSR" # does not seem to work 
# boycotted_firm = "YUM"
# boycotted_firm = "WIX"

# Preprocessing
df_clean <- test_adjusted %>%
  #filter(!is.na(net_margin_pct)) %>% 
  #filter(!is.na(revenue)) %>% 
  # Drop Brands Missing ≥ 5 Years
  group_by(ticker) %>%
  mutate(
    total_years = 2025 - 2009 + 1,                          # = 17
    years_present = n_distinct(fy[fy >= 2009 & fy <= 2025]),
    years_missing = total_years - years_present
  ) %>%
  filter(years_missing < 5) %>%                             # keep brands missing <5 years
  ungroup() %>%
  # filter(fp != 'Q4') %>% # most brands don't have it 
  #filter(ticker %in% c("BROS", "MCD", "GIS", "META", "DPZ", "WMT")) %>%
  #filter(ticker != "NVDA") %>% 
  #filter(ticker != "DAL") %>% 
  #filter(ticker != "JNJ") %>% 
  #filter(ticker != "TGT") %>% 
  #filter(ticker != "XOM") %>% 
  #filter(ticker != "CMG") %>% 
  #filter(ticker != "WMT") %>% 
  #filter(ticker != "META") %>% 
  #filter(ticker != "PFE") %>% 
  #filter(ticker != "IBM") %>% 
  #filter(ticker != "MDLZ") %>% 
  #filter(ticker != "COST") %>% 
  
  # in a df with many boycotted, just pick one
  #filter( (boycotted == 1 & ticker == boycotted_firm) | boycotted == 0 )  %>% 
  filter(fy < 2026 & fy >= 2009) %>% 
  
  # columns 
  select(where(~ !all(is.na(.)))) %>% 
  
  # Create useful columns 
  mutate(company_id = as.numeric(as.factor(ticker))) %>%
  
  # Balance 
  #complete(
  complete(
    ticker,
    fy = 2009:2025,
    fp = c("Q1", "Q2", "Q3", "Q4")
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
      filter(., n_quarters == 4) %>% 
        select(-n_quarters),
      
      # 2️⃣ Fill missing quarters for incomplete ones
      filter(., n_quarters < 4) %>%
        select(-n_quarters) %>%
        complete(ticker, fy, fp = c("Q1", "Q2", "Q3", 'Q4')) %>%
        group_by(ticker) %>%
        fill(company_id, boycotted, .direction = "downup") %>%
        ungroup()
    )
  } %>% 
  
  group_by(ticker) %>% 
  fill(everything(), .direction = "downup") %>% 
  ungroup() %>% 
  # 
  # # Turn fp (Q1, Q2, Q3) into numeric quarter fraction
  # mutate( 
  #   quarter_num = case_when(
  #     fp == "Q1" ~ 0.25,
  #     fp == "Q2" ~ 0.50,
  #     fp == "Q3" ~ 0.75,
  #     TRUE ~ NA_real_
  #   ),
  #   # Combine fiscal year and quarter into one numeric time variable
  #   time_numeric = fy + quarter_num) %>% 
  # select(-quarter_num) %>%
  as.data.frame() %>% 
  # apply treatment 
  { 
    mutate(., boycotted = ifelse(
      .$ticker == boycotted_firm & .$time_numeric >= 2023.25,
      1,
      0
    ))
  } %>%  
  select(!c(contains('years')))
# 
# df_clean_cut <- df_clean %>% filter(time_numeric > 2018.25)  %>% distinct(company_id, time_numeric, .keep_all = TRUE)
# panel_template <- df_clean_cut %>%
#   distinct(company_id, time_numeric)
# 
# df_clean_cut <- df_clean_cut %>%
#   right_join(panel_template, by = c("company_id", "time_numeric")) %>% filter(!ticker %in% c("NVDA", "OSIS")) 
