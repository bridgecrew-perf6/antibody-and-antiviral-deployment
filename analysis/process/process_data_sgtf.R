################################################################################
#
# Description: This script imports data extracted by the cohort extractor and
#              calculates additional variables needed for subsequent analyses 
#              (i.e., eligibility criteria window)
#
# Input: /output/data/input.csv.gz
#
# Output: /output/data/data_processed_sgtf.csv
#
# Author(s): M Green
# Date last updated: 24/06/2022
#
################################################################################


# Preliminaries ----

## Import libraries
library('tidyverse')
library('here')
library('tidyverse')
library('lubridate')
library('arrow')
library('reshape2')
library('dplyr')
library('readr')

## Custom functions
source(here("analysis", "lib", "custom_functions.R"))

# Process data ----
cat("#### process data ####\n")

## Redaction threshold
threshold = 8

## Read in data (don't rely on defaults)
input.files = list.files(path = here::here("output", "data"), pattern = "input_sgtf_weekly_")

weekly_sgtf_counts = lapply(input.files, FUN = calculate_weekly_counts) %>% 
  bind_rows()

weekly_sgtf_counts_by_region = lapply(input.files, FUN = calculate_weekly_counts_by_region) %>% 
  bind_rows()

weekly_sgtf_counts_age_sex = lapply(input.files, FUN = calculate_table) %>% 
  bind_rows() %>%
  group_by(sgtf_alltests, ageband, sex) %>%
  summarise(count = sum(count, na.rm = T)) %>%
  mutate(count = as.numeric(ifelse(count < threshold, NA, count)),
         count_redacted =  plyr::round_any(count, 10)) %>%
  select(sgtf_alltests,  ageband, sex, count_redacted)

## Save dataset(s) ----
write_rds(weekly_sgtf_counts, here::here("output", "data", "weekly_sgtf_counts.rds"))
write_rds(weekly_sgtf_counts_by_region, here::here("output", "data", "weekly_sgtf_counts_by_region.rds"))
write_rds(weekly_sgtf_counts_age_sex, here::here("output", "data", "weekly_sgtf_counts_by_age_sex.rds"))





