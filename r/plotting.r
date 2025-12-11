# plotting in facets 

library(dplyr)
library(tidyr)
library(ggplot2)

vars <- c(
  "revenue","gross_profit","net_income","operating_expenses","r_and_d",
  "depr_amort","interest_expense","interest_income","income_before_tax",
  "tax_expense","eps_basic","eps_diluted","shares_basic","shares_diluted",
  "assets","assets_current","liabilities","liabilities_current","equity",
  "cash","accounts_receivable","inventory","long_term_debt","capex",
  "operating_cf","investing_cf","financing_cf","employees","gross_margin_pct",
  "net_margin_pct"
)

df_long <- test %>% filter(ticker == 'NKE') %>% filter(!fp == 'Q1') %>% filter(!fp == 'Q2') %>% filter(!fp == 'Q3') %>% 
  pivot_longer(cols = all_of(vars), names_to = "variable", values_to = "value")

ggplot(df_long, aes(time_numeric, value, colour = ticker)) +
  geom_line() +
  geom_point() +
  facet_wrap(~ variable, scales = "free_y") +
  theme_minimal()
