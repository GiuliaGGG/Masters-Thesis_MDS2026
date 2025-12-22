data <-read_csv('/Users/giuliamariapetrilli/Documents/GitHub/masters_thesis/data/processed/data.csv')
data <- data %>% filter(!is.na(revenue))
panelview(revenue ~ boycotted, data = data,  index = c("ticker","time"), pre.post = TRUE) 

system.time(
  out <- gsynth(
  revenue ~ boycotted,
  + cost 
  + depr_amort
  + eps_basic 
  + eps_diluted 
  + interest_exp 
  + operating_exp 
  + r_and_d 
  + shares_basic
  + shares_diluted
  + tax,
  data = data,
  index = c("ticker","time"),
  force = "two-way",
  CV = TRUE,
  r = c(0, 5), # unobserved confounders
  se = TRUE,
  inference = "parametric",
  nboots = 1000,
  parallel = TRUE
)
)

plot(out) # by default
plot(out, theme.bw = FALSE) 
plot(out, type = "gap", ylim = c(-12000000000,12000000000), xlab = "Period", 
     main = "My GSynth Plot")
plot(out, type = "raw")
plot(out,type = "raw", legendOff = TRUE, ylim=c(-120000000,120000000000), main="")
plot(out, type = "counterfactual", raw = "none", main="")
plot(out, type = "ct", raw = "none", main = "", 
     shade.post = FALSE)
plot(out, type = "counterfactual", raw = "band", 
     xlab = "Time", ylim = c(-1000000000,30000000000))
plot(out, type = "counterfactual", raw = "all")
plot(out, type = "counterfactual", id = 'MCD')
plot(out, type = "counterfactual", id = 'MCD', 
     raw = "band", ylim = c(-10000000000, 30000000000))
plot(out, type = "counterfactual", id = 'MCD', 
     raw = "all", legendOff = TRUE)

out$est.att
out$est.avg
out$est.beta
