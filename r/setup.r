# Library
library(readr)
library(dplyr)
library(magrittr)
library(ggplot2)

## Method Packages 
library(did)
library("Synth")
library(tidysynth)
library(panelView)
library(gsynth)
library(augsynth)
library(fixest)

# read data 
data_log_simple <-read_csv('data/processed/batch_3/data_log_simple.csv')
data_log_simple_company_id <- data_log_simple %>% 
  mutate(company_id = as.integer(as.factor(ticker))) %>% as.data.frame()

time_lookup <- data_company_id %>%
  distinct(time, time_label) %>%
  arrange(time)

time_labels <- setNames(
  time_lookup$time_label,
  time_lookup$time
)

time_breaks <- time_lookup$time[seq(1, nrow(time_lookup), by = 4)]
time_labels <- time_lookup$time_label[seq(1, nrow(time_lookup), by = 4)]



