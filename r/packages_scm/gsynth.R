data <-read_csv('/Users/giuliamariapetrilli/Documents/GitHub/masters_thesis/data/processed/data.csv')
data <- data %>% filter(!is.na(revenue))
panelview(revenue ~ boycotted, data = data,  index = c("ticker","time"), pre.post = TRUE) 

system.time(
  out <- gsynth(
  revenue ~ boycotted,
  data = data,
  index = c("ticker","time"),
  force = "two-way",
  CV = TRUE,
  r = c(0, 5),
  se = TRUE,
  inference = "parametric",
  nboots = 1000,
  parallel = TRUE
)
)

cumu1 <- cumuEff(out, cumu = TRUE, id = NULL, period = c(0,5))
cumu1 <- cumuEff(out)
cumu1$est.catt

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


# EM method 
'The EM algorithm proposed by Gobillon and Magnac (2016) 
takes advantage of the treatment group information in 
the pre-treatment period. We implement this method. 
The estimation takes more time, but the results are 
very similar to that from the original method – the 
coefficients will be slightly more precisely estimated.'
system.time(
  out <- gsynth(revenue ~ boycotted,
                #+shares_basic+ assets,
                data = data,  
                index = c("ticker","time"),
                EM = TRUE, 
                force = "two-way",
                inference = "parametric", 
                se = TRUE, nboots = 500, r = c(0, 5), 
                CV = TRUE, parallel = TRUE, cores = 4)
)
plot(out, main = "Estimated ATT (EM)")
plot(out, theme.bw = FALSE) 
plot(out, type = "gap", ylim = c(-1200000000,1200000000), xlab = "Period", 
     main = "My GSynth Plot")
plot(out, type = "raw")
plot(out,type = "raw", legendOff = TRUE, ylim=c(-10,40), main="")
plot(out, type = "counterfactual", raw = "none", main="")
plot(out, type = "ct", raw = "none", main = "", 
     shade.post = FALSE)
plot(out, type = "counterfactual", raw = "band", 
     xlab = "Time", ylim = c(0,30000000000))
plot(out, type = "counterfactual", raw = "all")
plot(out, type = "counterfactual", id = 'MCD')
plot(out, type = "counterfactual", id = 'MCD', 
     raw = "band", ylim = c(-10000000000, 30000000000))
plot(out, type = "counterfactual", id = 'MCD', 
     raw = "all", legendOff = TRUE)
plot(out, type = "loadings")

