################################################################################
#
# Description: This script provides the formal specification of the study data 
#              that will be extracted from the OpenSAFELY database.
#
# Output: output/data/input_sgtf.csv.gz
#
# Author(s): M Green
# Date last updated: 24/06/2022
#
################################################################################


# IMPORT STATEMENTS ----

## Import code building blocks from cohort extractor package
from cohortextractor import (
  StudyDefinition,
  patients,
  codelist_from_csv,
  codelist,
  filter_codes_by_category,
  combine_codelists,
  Measure
)

## Import codelists from codelist.py (which pulls them from the codelist folder)
from codelists import *
  
  
# DEFINE STUDY POPULATION ----

## Define study time variables
from datetime import date

## Define study population and variables
study = StudyDefinition(
  
  # PRELIMINARIES ----
  
  ## Configure the expectations framework
  default_expectations = {
    "date": {"earliest": "2021-11-01", "latest": "2021-05-30"},
    "rate": "uniform",
    "incidence": 0.05,
  },
  
  ## Define index date
  index_date = "2020-03-01",
  
  # POPULATION ----
  population = patients.satisfying(
    
    """
    sgtf_alltests != ""
    """,
    
  ),
  
  
  # S-GENE TARGET FAILURE Target
  
  ## SGTF
  sgtf_alltests = patients.with_test_result_in_sgss(
    pathogen = "SARS-CoV-2",
    test_result = "positive",
    find_first_match_in_period = True,
    between = ["index_date", "index_date + 6 days"],
    returning = "s_gene_target_failure",
    restrict_to_earliest_specimen_date = False,
    return_expectations = {
      "rate": "universal",
      "category": {"ratios": {"0": 0.7, "1": 0.1, "8": 0.05, "9": 0.05, "": 0.1}},
    },
  ), 
  
  # OTHER VARIABLES
  
  ## Age
  age = patients.age_as_of(
    "index_date",
    return_expectations = {
      "rate": "universal",
      "int": {"distribution": "population_ages"},
      "incidence" : 0.9
    },
  ),
  
  ## Sex
  sex = patients.sex(
    return_expectations = {
      "rate": "universal",
      "category": {"ratios": {"M": 0.49, "F": 0.51}},
    }
  ),
  
  ## Region - NHS England 9 regions
  region_nhs = patients.registered_practice_as_of(
    "index_date",
    returning = "nuts1_region_name",
    return_expectations = {
      "rate": "universal",
      "category": {
        "ratios": {
          "North East": 0.1,
          "North West": 0.1,
          "Yorkshire and The Humber": 0.1,
          "East Midlands": 0.1,
          "West Midlands": 0.1,
          "East": 0.1,
          "London": 0.2,
          "South West": 0.1,
          "South East": 0.1,},},
    },
  ),
  
  
)
