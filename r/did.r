library(ggplot2)
library(dplyr)

did <- lm(
  revenue_std ~ boycotted + factor(ticker) + factor(time),
  data = data_standardized
)
summary(did)


data_plot <- data_standardized %>%
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
