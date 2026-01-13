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
data <-read_csv('./outputs/data.csv')
data_company_id <- data %>% 
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



