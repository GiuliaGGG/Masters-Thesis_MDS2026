source("./r/setup.r")

sc_out <-
  data_company_id %>%

  synthetic_control(
    outcome = revenue_std,
    unit = ticker,
    time = time,
    i_unit = "MCD",
    i_time = 8096,
    generate_placebos = TRUE
  ) %>%

  # --- predictors: lagged outcomes only (canonical SCM) ---
  generate_predictor(
    time_window = 8045:8095,
    revenue_pre = mean(revenue_std, na.rm = TRUE)
  ) %>%

  # --- fit weights ---
  generate_weights(
    optimization_window = 8045:8095
  ) %>%

  # --- build synthetic control ---
  generate_control()


sc_out %>% plot_trends()
sc_out %>% plot_differences()
sc_out %>% plot_weights()
sc_out %>% grab_balance_table()
sc_out %>% plot_placebos()
sc_out %>% plot_placebos(prune = FALSE)
sc_out %>% plot_mspe_ratio()
sc_out %>% grab_significance()
