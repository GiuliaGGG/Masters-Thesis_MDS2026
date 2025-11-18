
df <- read_csv("data/merged_dataset_2025-11-18_13-31.csv")

boycotted_firm = "MCD"
# Preprocessing
df_clean <- df %>%
  
  # in a df with many boycotted, just pick one
  filter( (boycotted == 1 & ticker == boycotted_firm) | boycotted == 0 )  %>% 
  filter(fy < "2026") %>% 
  
  # columns 
  select(where(~ !all(is.na(.)))) %>% 
  
  # Create useful columns 
  mutate(company_id = as.numeric(as.factor(ticker))) %>%
  mutate(net_income_margin = net_income / assets) %>% 
  
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
  
  
  #inpute nas for the dependent variable 
  # group_by(ticker) %>% 
  # fill(net_income_margin, .direction = "downup") %>% 
  # ungroup() %>% 
  
  group_by(ticker) %>% 
  fill(everything(), .direction = "downup") %>% 
  ungroup() %>% 
  # if a column has any missingness, drop the whole column 
  #select(where(~ !any(is.na(.x)))) %>% 
  
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
  as.data.frame() %>% 
  # apply treatment 
  { 
    mutate(., boycotted = ifelse(
      .$ticker == boycotted_firm & .$time_numeric >= 2023.25,
      1,
      0
    ))
  } %>% 
  # --- Remove any duplicates & tidy up ---
  distinct(ticker, time_numeric, .keep_all = TRUE) 



