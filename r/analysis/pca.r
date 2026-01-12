# 1. Keep pre-treatment data only
pre_data <- data_log_simple_company_id [data_log_simple_company_id $time < '8096', ]

# 2. Wide format: rows = time, columns = firms
Y_wide <- reshape(
  pre_data[, c("time", "ticker", "revenue_log")],
  idvar = "time",
  timevar = "ticker",
  direction = "wide"
)

# 3. Drop time column and rows with missing values
Y_mat <- as.matrix(na.omit(Y_wide[ , -1]))

# 4. Run PCA
pca <- prcomp(Y_mat, scale. = TRUE)

# 5. Variance explained
summary(pca)
