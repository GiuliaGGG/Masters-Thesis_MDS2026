source("./r/setup.r")

did_simple <- feols(
  revenue_log ~ boycotted | ticker + time,
  data = data_company_id,
  cluster = ~ ticker
)
summary(did_simple)

