panelview(net_margin_pct ~ boycotted, data = df_clean_cut,  index = c("company_id","time_numeric"), pre.post = TRUE) 

system.time(
out <- gsynth(net_margin_pct ~ boycotted +shares_basic+ assets + equity, data = df_clean_cut, 
                index = c("company_id","time_numeric"), force = "two-way", 
                CV = TRUE, r = c(0, 5), se = TRUE, 
                inference = "parametric", nboots = 1000, 
                parallel = FALSE)
)



out2 <- gsynth(net_margin_pct ~ boycotted +shares_basic+ assets  + equity, data = df_clean_cut, 
               index = c("company_id","time_numeric"), force = "two-way", 
               CV = FALSE, r = c(2, 5), se = TRUE,
               inference = "jackknife", 
               parallel = TRUE, cores = 4)
cumu1 <- cumuEff(out, cumu = TRUE, id = NULL, period = c(0,5))
cumu1$est.catt
cumu2 <- cumuEff(out, cumu = FALSE, id = c(101, 102, 103), period = c(0,5))
cumu2$est.catt
plot(out) # by default
plot(out, theme.bw = FALSE) 
plot(out, type = "gap", ylim = c(-3,12), xlab = "Period", 
     main = "My GSynth Plot")
plot(out, type = "raw")
plot(out,type = "raw", legendOff = TRUE, ylim=c(-10,40), main="")
plot(out, type = "counterfactual", raw = "none", main="")
plot(out, type = "ct", raw = "none", main = "", 
     shade.post = FALSE)
plot(out, type = "counterfactual", raw = "band", 
     xlab = "Time", ylim = c(0,1))
plot(out, type = "counterfactual", raw = "all")
plot(out, type = "counterfactual", id = 102)
plot(out, type = "counterfactual", id = 104, 
     raw = "band", ylim = c(-10, 30))
plot(out, type = "counterfactual", id = 105, 
     raw = "all", legendOff = TRUE)
plot(out, type = "loadings")



# EM method 
'The EM algorithm proposed by Gobillon and Magnac (2016) 
takes advantage of the treatment group information in 
the pre-treatment period. We implement this method. 
The estimation takes more time, but the results are 
very similar to that from the original method – the 
coefficients will be slightly more precisely estimated.'
system.time(
  out <- gsynth(net_margin_pct ~ boycotted +shares_basic+ assets, data = df_clean_cut,  
                index = c("company_id","time_numeric"), EM = TRUE, 
                force = "two-way", inference = "parametric", 
                se = TRUE, nboots = 500, r = c(0, 5), 
                CV = TRUE, parallel = TRUE, cores = 4)
)
plot(out, main = "Estimated ATT (EM)")
