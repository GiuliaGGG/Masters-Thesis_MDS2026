library(ggplot2)
library(dplyr)
library(did)


did <- lm(
  revenue_std ~ boycotted + factor(ticker) + factor(time),
  data = data
)
summary(did)

plot(did)

data_plot <- data %>%
  mutate(
    is_mcd = ifelse(ticker == "MCD", 1, 0)
  )

plot_data <- data_plot %>%
  group_by(time, is_mcd) %>%
  summarise(
    mean_revenue = mean(revenue_std, na.rm = TRUE),
    .groups = "drop"
  )


ggplot(plot_data, aes(x = time, y = mean_revenue, color = factor(is_mcd))) +
  geom_line(size = 1.1) +
  geom_point(size = 2) +
  geom_vline(
    xintercept = min(data_plot$time[data_plot$boycotted == 1]),
    linetype = "dashed",
    color = "black"
  ) +
  scale_color_manual(
    values = c("0" = "steelblue", "1" = "firebrick"),
    labels = c("Other firms", "McDonald’s")
  ) +
  labs(
    title = "Standardized Revenue Over Time",
    subtitle = "McDonald’s vs Other Firms",
    x = "Time",
    y = "Revenue (standardized to period 0)",
    color = "Firm"
  ) +
  theme_minimal(base_size = 13)


# did package from callway and Callaway, Brantly and Pedro H.C. Sant’Anna. “Difference-in-Differences with Multiple Time Periods.” Journal of Econometrics, Vol. 225, No. 2, pp. 200-230, 2021.

treated_unit <- "7"
t0 <- 8097  # first treated period in your time index

df_did <- data_c %>%
  mutate(
    first_treat = ifelse(company_id == treated_unit, t0, 0)  # 0 = never treated
  )

out <- att_gt(
  yname  = "revenue_std",
  gname  = "first_treat",
  idname = "company_id",
  tname  = "time",
  xformla = ~ 1,
  data   = df_did,
  est_method = "reg",
  control_group = "nevertreated"  # important with single treated unit
)

es <- aggte(out, type = "dynamic")
ggdid(es)



