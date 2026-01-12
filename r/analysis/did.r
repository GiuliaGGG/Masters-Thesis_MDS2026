source("./r/setup.r")

did_simple <- feols(
  revenue_log ~ boycotted | ticker + time,
  data = data_log_simple_company_id,
  cluster = ~ ticker
)
summary(did_simple)

