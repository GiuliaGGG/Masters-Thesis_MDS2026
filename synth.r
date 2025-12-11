
# dataprep 
dataprep.out <- dataprep(
  foo = df_clean_cut,
  predictors = c("assets", 'shares_basic', 'equity'),
  dependent = "net_margin_pct",
  unit.variable = "company_id",          # numeric ID column
  unit.names.variable = "ticker",        # readable name
  time.variable = "time_numeric",                  # or numeric time index
  treatment.identifier = 9,              # treated company ID
  controls.identifier = c(1:8, 10:21), # control company IDs
  time.predictors.prior = 2018.25:2023.75,
  time.optimize.ssr = 2018.25:2023.75,         # pre-treatment period
  time.plot = 2018.25:2025.75                  # full period to plot
)

###################################################
### chunk number 4: 
###################################################
dataprep.out$X1 #treated unit’s predictor values (Basque Country).

###################################################
### chunk number 5: 
###################################################
dataprep.out$Z1 #treated unit’s outcome values (Basque Country).

###################################################
### chunk number 7: 
###################################################
# run synth
synth.out <- synth(
  data.prep.obj = dataprep.out,
  method = "BFGS"
)

###################################################
### chunk number 8: 
###################################################
gaps <- dataprep.out$Y1plot - (dataprep.out$Y0plot %*% synth.out$solution.w)
gaps[1:3, 1]

###################################################
### chunk number 9: 
###################################################
synth.tables <- synth.tab(dataprep.res = dataprep.out,
                          synth.res = synth.out
)

###################################################
### chunk number 10: 
###################################################
names(synth.tables)

###################################################
### chunk number 11: 
###################################################
synth.tables$tab.pred

###################################################
### chunk number 12: 
###################################################
synth.tables$tab.w[8:14, ]


###################################################
### chunk number 13: 
###################################################
path.plot(
  synth.res = synth.out,
  dataprep.res = dataprep.out,
  Ylab = "net_income",
  Xlab = "year",
  Ylim = c(0, 1),
  Legend = c(
    paste0(boycotted_firm),
    paste0("Synthetic ", boycotted_firm)
  ),
  Legend.position = "topleft"
)


abline(v = 2023.25, col = "red", lwd = 2, lty = 2)  # vertical red line at 2023.75
df_clean_cut %>% filter(ticker != 'TRIP') %>%   filter(ticker != 'JNJ') %>%  filter(ticker != 'DAL')   %>% ggplot(aes(time_numeric, net_margin_pct, colour = ticker)) + geom_point() + geom_line()
df_clean_cut   %>% ggplot(aes(time_numeric, net_margin_pct, colour = ticker)) + geom_point() + geom_line()
