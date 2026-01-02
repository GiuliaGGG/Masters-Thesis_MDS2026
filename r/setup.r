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

# read data 
data <-read_csv('data/processed/batch_3/data.csv')
data <- data %>%  filter(!ticker == 'HD') %>% filter(!ticker == 'NFLX')
data_company_id <- data %>% 
  mutate(company_id = as.integer(as.factor(ticker))) %>% as.data.frame()



