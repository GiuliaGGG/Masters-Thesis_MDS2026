source("./r/setup.r")

# original 
sc_out <-
  data_log_simple_company_id %>%

  synthetic_control(
    outcome = revenue_log,
    unit = ticker,
    time = time,
    i_unit = "MCD",
    i_time = 8096,
    generate_placebos = TRUE
  ) %>%

  # --- predictors: lagged outcomes only (canonical SCM) ---
  generate_predictor(
    time_window = 8045:8096,
    shares_pre = mean(shares_basic, na.rm = TRUE),
    revenue_pre = mean(revenue_log, na.rm = TRUE)
  ) %>%

  # --- fit weights ---
  generate_weights(
    optimization_window = 8045:8096
  ) %>%

  # --- build synthetic control ---
  generate_control()

# Synthetic / Observed
sc_out_plot <- sc_out %>%
  plot_trends() +
  scale_x_continuous(
    breaks = time_breaks,
    labels = time_labels
  ) +
  labs(x = "Time") +
  labs(y = "Revenue (Logged)") +
  labs(title = "Time Series of the Synthetic and Observed Revenue for McDonald's")

# Weights 
sc_plot_weights<- sc_out %>% plot_weights()

# plot rmse ratio
sc_plot_mspe <- sc_out %>% plot_mspe_ratio()

ggsave(
  filename = "./images/sc_out_plot.png",
  plot = sc_out_plot,
  width = 13,
  height = 9,
  units = "in",
  dpi = 600
)

ggsave(
  filename = "./images/sc_plot_weights.png",
  plot = sc_plot_weights,
  width = 13,
  height = 9,
  units = "in",
  dpi = 600
)

ggsave(
  filename = "./images/sc_plot_mspe.png",
  plot = sc_plot_mspe,
  width = 13,
  height = 9,
  units = "in",
  dpi = 600
)

# alternative model specifications
pre_periods <- 8045:8095

sc_out_alt <-
  data_log_simple_company_id %>%
  synthetic_control(
    outcome = revenue_log,
    unit = ticker,
    time = time,
    i_unit = "MCD",
    i_time = 8096,
    generate_placebos = TRUE
  ) %>%
  # one predictor per pre-treatment time point
  { 
    tmp <- .
    for (tt in pre_periods) {
      tmp <- tmp %>%
        generate_predictor(
          time_window = tt,
          !!paste0("revenue_", tt) := revenue_log
        )
    }
    tmp
  } %>%
  generate_weights(optimization_window = pre_periods) %>%
  generate_control()

# Synthetic / Observed
sc_out_plot_alt <- sc_out_alt %>%
  plot_trends() +
  scale_x_continuous(
    breaks = time_breaks,
    labels = time_labels
  ) +
  labs(x = "Time") +
  labs(y = "Revenue (Logged)") +
  labs(title = "Time Series of the Synthetic and Observed Revenue for McDonald's")

# Weights 
sc_plot_weights_alt<- sc_out_alt %>% plot_weights()

# plot rmse ratio
sc_plot_mspe_alt <- sc_out_alt %>% plot_mspe_ratio()

ggsave(
  filename = "./images/discussion_section_plots/sc_out_plot_alt.png",
  plot = sc_out_plot_alt,
  width = 13,
  height = 9,
  units = "in",
  dpi = 600
)

ggsave(
  filename = "./images/discussion_section_plots/sc_plot_weights_alt.png",
  plot = sc_plot_weights_alt,
  width = 13,
  height = 9,
  units = "in",
  dpi = 600
)

ggsave(
  filename = "./images/discussion_section_plots/sc_plot_mspe_alt.png",
  plot = sc_plot_mspe_alt,
  width = 13,
  height = 9,
  units = "in",
  dpi = 600
)
