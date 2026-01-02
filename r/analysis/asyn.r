source("./r/setup.r")

syn <- augsynth(
  revenue_std ~ boycotted,
  ticker,
  time,
  data,
  progfunc = "None",
  scm = TRUE
)

asyn <- augsynth(
  revenue_std ~ boycotted,
  ticker,
  time,
  data,
  progfunc = "Ridge",
  scm = TRUE
)
summary(syn)
plot(syn)
summary(asyn)
plot(asyn)
time <- asyn$synth_data$time

# Pre-treatment period only
pre_idx <- which(asyn$data$trt == 0)

# Treated unit
treated <- asyn$data$synth_data$Y1plot[pre_idx]

# Synthetic (ASCM)
synthetic_ascm <- rowMeans(asyn$data$synth_data$Y0plot[pre_idx, , drop = FALSE])

plot(
  time[pre_idx],
  treated,
  type = "l",
  lwd = 2,
  col = "black",
  ylab = "Outcome",
  xlab = "Time",
  main = "Pre-treatment fit: Treated vs ASCM synthetic"
)

lines(
  time[pre_idx],
  synthetic_ascm,
  col = "blue",
  lwd = 2
)

legend(
  "topleft",
  legend = c("Treated unit", "ASCM synthetic"),
  col = c("black", "blue"),
  lwd = 2
)
