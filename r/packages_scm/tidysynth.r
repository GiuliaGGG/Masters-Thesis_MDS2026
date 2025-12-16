library(dplyr)
library(tidysynth)

# Quick sanity check
data_revenue %>% glimpse()

# ----------------------------
# Define time windows properly
# ----------------------------

treatment_time <- 8103

pre_treatment_window <- min(data_revenue$time): (treatment_time - 1)

# ----------------------------
# Synthetic control
# ----------------------------

df_out <-
  data_revenue %>%
  
  synthetic_control(
    outcome = revenue,
    unit = ticker,
    time = time,
    i_unit = "MCD",
    i_time = treatment_time,
    generate_placebos = TRUE
  ) %>%
  
  # ----------------------------
# Generate predictors (pre-treatment only)
# ----------------------------
generate_predictor(
  time_window = pre_treatment_window,
  shares_basic = mean(shares_basic, na.rm = TRUE),
  net_income = mean(net_income, na.rm = TRUE),
) %>%
  
  # ----------------------------
# Generate weights
# ----------------------------
generate_weights(
  optimization_window = pre_treatment_window,
  margin_ipop = 0.02,
  sigf_ipop = 7,
  bound_ipop = 6
) %>%
  
  # ----------------------------
# Generate synthetic control
# ----------------------------
generate_control()


df_out %>% plot_trends()
df_out %>% plot_differences()
df_out %>% plot_weights()
df_out %>% grab_balance_table()
df_out %>% plot_placebos()
df_out %>% plot_placebos(prune = FALSE)
df_out %>% plot_mspe_ratio()
df_out %>% grab_significance()

df_out

df_out %>% 
  tidyr::unnest(cols = c(.outcome))


