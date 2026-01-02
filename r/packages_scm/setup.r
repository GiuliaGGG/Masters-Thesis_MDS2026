# library
library(readr)
library(gsynth)
library(dplyr)
library(panelView)
require(tidysynth)
library(tidysynth)
library(magrittr)
library(augsynth)
library("Synth")

# read data 
data <-read_csv('data/processed/batch_3/data.csv')
data_c <- data %>% 
  mutate(company_id = as.integer(as.factor(ticker))) %>% as.data.frame()



