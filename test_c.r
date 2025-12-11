library(dplyr)
library(purrr)
library(stringr)
df <- read_csv("data/with_start_date/merged_dataset_with_start_date_2025-12-10_20-39.csv")

test <- df %>%
  #filter(!frequency == 'A') %>%  
  group_by(boycotted, ticker, fy, fp, end) %>%
  summarise(across(everything(), ~ {
    # If all values are NA, return NA
    # Otherwise return the first non-NA
    if(all(is.na(.x))) NA else .x[which(!is.na(.x))[1]]
  }), .groups = "drop")
vars <- c(
  "revenue","gross_profit","net_income","operating_expenses","r_and_d",
  "depr_amort","interest_expense","interest_income","income_before_tax",
  "tax_expense","eps_basic","eps_diluted","shares_basic","shares_diluted",
  "assets","assets_current","liabilities","liabilities_current","equity",
  "cash","accounts_receivable","inventory","long_term_debt","capex",
  "operating_cf","investing_cf","financing_cf","employees","gross_margin_pct",
  "net_margin_pct"
)

test_chatgpt <- test %>%
  mutate(fp = ifelse(fp == "FY", "Q4", fp)) %>%  
  group_by(ticker, fy) %>%   # company-year grouping
  mutate(across(all_of(vars), ~ {
    
    x <- .x
    
    # median quarterly value for that company-year
    M <- median(.x, na.rm = TRUE)
    
    # ----------------------------
    # DETECTION OF TRUE PERIOD
    # ----------------------------
    period_detected <- case_when(
      x <= 1.75 * M ~ "quarter",
      x > 1.75 * M & x <= 2.75 * M ~ "semiannual",
      x > 2.75 * M & x <= 3.75 * M ~ "nine_month",
      x > 3.75 * M ~ "annual",
      TRUE ~ "unknown"
    )
    
    # ----------------------------
    # CORRECTION LOGIC
    # ----------------------------
    corrected <- case_when(
      period_detected == "quarter"     ~ x,
      period_detected == "semiannual"  ~ x / 2,
      period_detected == "nine_month"  ~ x / 3,
      period_detected == "annual"      ~ x / 4,
      TRUE ~ x
    )
    
    corrected
    
  }, .names = "{.col}_test")) %>%
  
  # save detection labels separately
  mutate(across(all_of(vars), ~ {
    x <- .x
    M <- median(.x, na.rm = TRUE)
    case_when(
      x <= 1.75 * M ~ "quarter",
      x > 1.75 * M & x <= 2.75 * M ~ "semiannual",
      x > 2.75 * M & x <= 3.75 * M ~ "nine_month",
      x > 3.75 * M ~ "annual",
      TRUE ~ "unknown"
    )
  }, .names = "{.col}_period_detected")) %>%
  
  ungroup()



# Preprocessing
df_clean <- test_chatgpt %>%

  filter(fy < 2026 & fy >= 2009) %>% 
  
  group_by(ticker) %>%
  mutate(
    total_years = 2025 - 2009 + 1,                          # = 17
    years_present = n_distinct(fy[fy >= 2009 & fy <= 2025]),
    years_missing = total_years - years_present
  ) %>%
  filter(years_missing < 5) %>%                             # keep brands missing <5 years
  ungroup() %>%
  
  # Create useful columns 
  mutate(company_id = as.numeric(as.factor(ticker))) %>%
  
  # Balance 
  #complete(
  complete(
    ticker,
    fy = 2009:2025,
    fp = c("Q1", "Q2", "Q3", "Q4")
  ) %>% 
  mutate(
    quarter_num = case_when(
      fp == "Q1" ~ 0.00,
      fp == "Q2" ~ 0.25,
      fp == "Q3" ~ 0.50,
      fp == "Q4" ~ 0.75,
      TRUE       ~ NA_real_
    ),
    time = fy + quarter_num
  ) %>%
  select(-quarter_num) %>%
  
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

  as.data.frame() %>% 
  # apply treatment 
  { 
    mutate(., boycotted = ifelse(
      .$ticker == 'MCD' & .$time >= 2023.25,
      1,
      0
    ))
  } %>%   select(
    boycotted, ticker, fy, fp, time, company_id,
    ends_with("_test")
  ) %>% #clean the column title by removing test 
  rename_with(~ sub("_test$", "", .x), ends_with("_test")) %>% 
  
  select(!c(contains('years'))) %>% 
  # hard coded exclusion of one dulicate observation
  filter(!(ticker == "WMT" &
                                               fy == 2011 &
                                               fp == "Q4" &
                                               time == 2011.75 &
                                               company_id == 11 &
                                               cash == 7063000000))

