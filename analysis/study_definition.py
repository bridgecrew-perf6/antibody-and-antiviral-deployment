################################################################################
#
# Description: This script provides the formal specification of the study data 
#              that will be extracted from the OpenSAFELY database.
#
# Output: output/data/input_*.csv.gz
#
# Author(s): M Green
# Date last updated: 11/01/2022
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

campaign_start = "2021-12-16"
index_date = date.today().isoformat()


## Define study population and variables
study = StudyDefinition(
  
  # PRELIMINARIES ----
  
  ## Configure the expectations framework
  default_expectations = {
    "date": {"earliest": "2019-01-01", "latest": "today"},
    "rate": "uniform",
    "incidence": 0.2,
  },
  
  ## Define index date
  index_date = index_date,
  
  # POPULATION ----
  population = patients.satisfying(
    """
    NOT has_died
    AND
    registered
    """,
    
    has_died = patients.died_from_any_cause(
      on_or_before = "index_date",
      returning = "binary_flag",
    ),
    
    registered = patients.registered_as_of("index_date"),
    
  ),
  
  
  # NEUTRALISING MONOCLONAL ANTIBODIES OR ANTIVIRALS ----
  
  ## Administration of anti-infective agent
  anti_infective_agent = patients.with_these_clinical_events(
    anti_infective_agent_codes,
    between = [campaign_start, index_date],
    returning = "binary_flag",
    return_expectations = {
      "incidence": 0.5,
    },
  ),
  
  ### Sotrovimab
  sotrovimab = patients.with_these_medications(
    sotrovimab_codes,
    between = [campaign_start, index_date],
    returning = "binary_flag",
    return_expectations = {
      "incidence": 0.2,
    },
  ),
  
  sotrovimab_code = patients.with_these_medications(
    sotrovimab_codes,
    between = [campaign_start, index_date],
    returning = "code",
    return_expectations = {
      "category": {"ratios": {str(40219011000001108): 1.0}}
    },
  ),
  
  sotrovimab_date = patients.with_these_medications(
    sotrovimab_codes,
    between = [campaign_start, index_date],
    returning = "date",
    date_format = "YYYY-MM-DD",
    find_first_match_in_period = True,
  ),
  
  ### Ronapreve
  ronapreve = patients.with_these_medications(
    ronapreve_codes,
    between = [campaign_start, index_date],
    returning = "binary_flag",
    return_expectations = {
      "incidence": 0.2,
    },
  ),
  
  ronapreve_code = patients.with_these_medications(
    ronapreve_codes,
    between = [campaign_start, index_date],
    returning = "code",
    return_expectations = {
      "category": {"ratios": {str(40025711000001108): 0.8, str(39654011000001101): 0.2}}
    },
  ),
  
  ronapreve_date = patients.with_these_medications(
    ronapreve_codes,
    between = [campaign_start, index_date],
    returning = "date",
    date_format = "YYYY-MM-DD",
    find_first_match_in_period = True,
  ),
  
  ## Provision of antiviral therapy
  antiviral_therapy = patients.with_these_clinical_events(
    antiviral_therapy_codes,
    between = [campaign_start, index_date],
    returning = "binary_flag",
    return_expectations = {
      "incidence": 0.3,
    },
  ),
  
  ### Molnupiravir
  molnupiravir = patients.with_these_medications(
    molnupiravir_codes,
    between = [campaign_start, index_date],
    returning = "binary_flag",
    return_expectations = {
      "incidence": 0.2,
    },
  ),
  
  molnupiravir_code = patients.with_these_medications(
    molnupiravir_codes,
    between = [campaign_start, index_date],
    returning = "code",
    return_expectations = {
      "category": {"ratios": {str(40251211000001109): 1.0}}
    },
  ),
  
  molnupiravir_date = patients.with_these_medications(
    molnupiravir_codes,
    between = [campaign_start, index_date],
    returning = "date",
    date_format = "YYYY-MM-DD",
    find_first_match_in_period = True,
  ),
  
  ## Date of (first) nMABS or antiviral
  nMABS_antiviral_date = patients.with_these_medications(
    codelist = combine_codelists(sotrovimab_codes, ronapreve_codes, molnupiravir_codes),
    between = [campaign_start, index_date],
    returning = "date",
    date_format = "YYYY-MM-DD",
    find_first_match_in_period = True,
  ),
  
  
  # HIGH RISK GROUPS ----
  
  ## Down's syndrome
  downs_syndrome_nhsd_snomed = patients.with_these_clinical_events(
    downs_syndrome_nhsd_snomed_codes,
    returning = "date",
    date_format = "YYYY-MM-DD",
    find_first_match_in_period = True,
    on_or_before = index_date,
  ),
  
  downs_syndrome_nhsd_icd10 = patients.admitted_to_hospital(
    returning = "date_admitted",
    with_these_diagnoses = downs_syndrome_nhsd_icd10_codes,
    on_or_before = index_date,
    find_first_match_in_period = True,
    date_format = "YYYY-MM-DD",
  ),
  
  downs_syndrome_nhsd = patients.minimum_of("downs_syndrome_nhsd_snomed", "downs_syndrome_nhsd_icd10"), 
  
  ## Sickle cell disease
  sickle_cell_disease_nhsd_snomed = patients.with_these_clinical_events(
    sickle_cell_disease_nhsd_snomed_codes,
    returning = "date",
    date_format = "YYYY-MM-DD",
    find_first_match_in_period = True,
    on_or_before = index_date,
  ),
  
  sickle_cell_disease_nhsd_icd10 = patients.admitted_to_hospital(
    returning = "date_admitted",
    with_these_diagnoses = sickle_cell_disease_nhsd_icd10_codes,
    on_or_before = index_date,
    find_first_match_in_period = True,
    date_format = "YYYY-MM-DD",
  ),
  
  sickle_cell_disease_nhsd = patients.minimum_of("sickle_cell_disease_nhsd_snomed", "sickle_cell_disease_nhsd_icd10"), 
  
  ## Solid cancer
  cancer_opensafely_snomed = patients.with_these_clinical_events(
    combine_codelists(
      non_haematological_cancer_opensafely_snomed_codes,
      lung_cancer_opensafely_snomed_codes,
      chemotherapy_radiotherapy_opensafely_snomed_codes
    ),
    returning = "date",
    date_format = "YYYY-MM-DD",
    find_first_match_in_period = True,
    on_or_before = "index_date",
  ),
  
  ## Rare neurological conditions
  
  ### Multiple sclerosis
  multiple_sclerosis_nhsd_snomed = patients.with_these_clinical_events(
    multiple_sclerosis_nhsd_snomed_codes,
    returning = "date",
    date_format = "YYYY-MM-DD",
    find_first_match_in_period = True,
    on_or_before = index_date,
  ),
  
  multiple_sclerosis_nhsd_icd10 = patients.admitted_to_hospital(
    returning = "date_admitted",
    with_these_diagnoses = multiple_sclerosis_nhsd_icd10_codes,
    on_or_before = index_date,
    find_first_match_in_period = True,
    date_format = "YYYY-MM-DD",
  ),
  
  multiple_sclerosis_nhsd = patients.minimum_of("multiple_sclerosis_nhsd_snomed", "multiple_sclerosis_nhsd_icd10"), 
  
  ### Motor neurone disease
  motor_neurone_disease_nhsd_snomed = patients.with_these_clinical_events(
    motor_neurone_disease_nhsd_snomed_codes,
    returning = "date",
    date_format = "YYYY-MM-DD",
    find_first_match_in_period = True,
    on_or_before = index_date,
  ),
  
  motor_neurone_disease_nhsd_icd10 = patients.admitted_to_hospital(
    returning = "date_admitted",
    with_these_diagnoses = motor_neurone_disease_nhsd_icd10_codes,
    on_or_before = index_date,
    find_first_match_in_period = True,
    date_format = "YYYY-MM-DD",
  ),
  
  motor_neurone_disease_nhsd = patients.minimum_of("motor_neurone_disease_nhsd_snomed", "motor_neurone_disease_nhsd_icd10"),
  
  ### Myasthenia gravis
  myasthenia_gravis_nhsd_snomed = patients.with_these_clinical_events(
    myasthenia_gravis_nhsd_snomed_codes,
    returning = "date",
    date_format = "YYYY-MM-DD",
    find_first_match_in_period = True,
    on_or_before = index_date,
  ),
  
  myasthenia_gravis_nhsd_icd10 = patients.admitted_to_hospital(
    returning = "date_admitted",
    with_these_diagnoses = myasthenia_gravis_nhsd_icd10_codes,
    on_or_before = index_date,
    find_first_match_in_period = True,
    date_format = "YYYY-MM-DD",
  ),
  
  myasthenia_gravis_nhsd = patients.minimum_of("myasthenia_gravis_nhsd_snomed", "myasthenia_gravis_nhsd_icd10"),
  
  ### Huntington’s disease
  huntingtons_disease_nhsd_snomed = patients.with_these_clinical_events(
    huntingtons_disease_nhsd_snomed_codes,
    returning = "date",
    date_format = "YYYY-MM-DD",
    find_first_match_in_period = True,
    on_or_before = index_date,
  ),
  
  huntingtons_disease_nhsd_icd10 = patients.admitted_to_hospital(
    returning = "date_admitted",
    with_these_diagnoses = huntingtons_disease_nhsd_icd10_codes,
    on_or_before = index_date,
    find_first_match_in_period = True,
    date_format = "YYYY-MM-DD",
  ),
  
  huntingtons_disease_nhsd = patients.minimum_of("huntingtons_disease_nhsd_snomed", "huntingtons_disease_nhsd_icd10"),
  
  
  
  
  
  
  
  # OTHER VARIABLES ----
  
  
)


