
#data("smoking")

df_clean %>% dplyr::glimpse()
df_out <-
  
  df_clean %>%
  
  # initial the synthetic control object
  synthetic_control(outcome = revenue, # outcome
                    unit = ticker, # unit index in the panel data
                    time = time, # time index in the panel data
                    i_unit = 'MCD', # unit where the intervention occurred
                    i_time = 2023.25, # time period when the intervention occurred
                    generate_placebos=T # generate placebo synthetic controls (for inference)
  ) %>%
  
  # Generate the aggregate predictors used to fit the weights
  
  # average log income, retail price of cigarettes, and proportion of the
  # population between 15 and 24 years of age from 1980 - 1988
  generate_predictor(time_window = 2009.25:2025.75,
                     shares_basic = mean(shares_basic, na.rm = T),
                     liabilities_current = mean(liabilities_current, na.rm = T),
                     assets = mean(assets, na.rm = T),
                     #gross_profit = mean(gross_profit, na.rm = T),
                     equity = mean(equity, na.rm = T),
                     net_income = mean(net_income, na.rm = T),
                     cash = mean(cash, na.rm = T)) %>%
  # 
  # # average beer consumption in the donor pool from 1984 - 1988
  # generate_predictor(time_window = 1984:1988,
  #                    beer_sales = mean(beer, na.rm = T)) %>%
  # 
  # # Lagged cigarette sales 
  # generate_predictor(time_window = 1975,
  #                    cigsale_1975 = cigsale) %>%
  # generate_predictor(time_window = 1980,
  #                    cigsale_1980 = cigsale) %>%
  # generate_predictor(time_window = 1988,
  #                    cigsale_1988 = cigsale) %>%
  # 
  
  # Generate the fitted weights for the synthetic control
  generate_weights(optimization_window = 2009.25:2025.75, # time to use in the optimization task
                   margin_ipop = .02,sigf_ipop = 7,bound_ipop = 6 # optimizer options
  ) %>%
  
  # Generate the synthetic control
  generate_control()

df_out  %>% plot_trends()

df_out %>% plot_differences()
df_out %>% plot_weights()
df_out %>% grab_balance_table()
df_out %>% plot_placebos()
df_out %>% plot_placebos(prune = FALSE)
df_out %>% plot_mspe_ratio()

df_out %>% grab_significance()
df_out
df_out %>% 
  tidyr::unnest(cols = c(.outcome)) 

