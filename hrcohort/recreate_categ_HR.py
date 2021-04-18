#%% Importing libraries
import re as re
from pathlib import Path

import ftfy
import numpy as np
import pandas as pd

from hrcohort import constants, data_utils

#%% Defining constants
print("Defining constants")
DATA_DIRECTORY = Path("../data")
FILTERED_COHORT_FILE = DATA_DIRECTORY / "filtered_hrcohort.csv.gz"
BUDGET_ANALYST_FILE = DATA_DIRECTORY / "budget_analysts.csv.gz"
BUDGET_PROFESSIONALS_FILE = DATA_DIRECTORY / "budget_professionals.csv.gz"
CLEAN_OUTPUT_FILE = DATA_DIRECTORY / "clean_output.csv.gz"

#%% Importing CSV, dropping useless rows, counting+dropping duplicate rows
print("Importing CSV, dropping useless rows, counting+dropping duplicate rows")
# Read the dataframe with pre-set data types.
df = pd.read_csv(
    FILTERED_COHORT_FILE,
    compression="gzip",
    dtype=constants.cohort_file_dtypes,
)