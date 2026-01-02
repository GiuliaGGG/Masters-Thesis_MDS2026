source("./r/setup.r")

panelview(revenue_std ~ boycotted, data = data,  index = c("ticker","time"), pre.post = TRUE) 

system.time(                     # Measure total runtime of the gsynth estimation
  out <- gsynth(
    revenue_std ~ boycotted,     # Outcome is standardized revenue; treatment is boycott exposure
    data = data,            # Panel dataset with standardized variables
    index = c("ticker","time"),  # Panel identifiers: firm (ticker) and time
    force = "two-way",           # Include both unit and time fixed effects
    CV = TRUE,                   # Use cross-validation to select the number of latent factors
    r = c(0, 5),                 # Allow between 0 and 5 unobserved common factors
    se = TRUE,                   # Compute standard errors
    inference = "parametric",    # Use parametric bootstrap inference
    nboots = 20,                 # Number of bootstrap replications
    parallel = TRUE              # Enable parallel computation for speed
  )
)


plot(out, type = "ct", raw = "none", main = "", 
     shade.post = FALSE)

plot(out) # by default
plot(out, theme.bw = FALSE) 
plot(out, type = "gap", ylim = c(-1,1), xlab = "Period", 
     main = "My GSynth Plot")
plot(out, type = "raw")
plot(out,type = "raw", legendOff = TRUE, ylim=c(-120000000,120000000000), main="")
plot(out, type = "counterfactual", raw = "none", main="")


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
