import pandas as pd
from pathlib import Path
import ftfy

## CONSTANTS
DATA_DIRECTORY = Path("../data")
FILTERED_COHORT_FILE = DATA_DIRECTORY / "filtered_hrcohort.csv.gz"

## Read the data
df = pd.read_csv(FILTERED_COHORT_FILE,
                   compression='gzip',
                   # encoding='latin_1',
                   dtype={'postal': str, 'year': int, 'job_title': str, 'agency': str,
                          'annual_salary': str, 'yrs_in_service': str})

# Verify if the data columns have been read with correct types
df.dtypes
# Drop any row with an empty 'job_title' since they are useless to HRcohort
df = df[~df['job_title'].isna()]
# Replace NaN or empty values with an underscore, which is unlikely to be confused with
# valid, pre-existing job titles
df[['postal','agency','annual_salary','yrs_in_service']] = \
    df[['postal','agency','annual_salary','yrs_in_service']].fillna('_')
# Replace NaN or empty values with zero, which is unlikely to be confused with
# valid, pre-existing year values
df['year'] = df['year'].fillna(0)
# Creates a new column with a count of duplicates and then drops duplicates
df = df.groupby(df.columns.tolist(),as_index=False).size()
df.rename(columns={'size':'dup_count'}, inplace=True)
df.drop_duplicates(inplace=True)


# Stripping the commas, and then stripping alphabet and common symbols
# Kepp this column as string because of all the remaining weirdness
df.annual_salary = df.annual_salary.str.replace(',', '')\
  .str.strip()\
  .str.replace(r'[a-zA-Z_$-]', '', regex=True).astype(str)

# Let's figure out which ones have 0 length, and set those rows as NA
is_no_salary = df.annual_salary.apply(lambda x: len(x) == 0)
df.loc[is_no_salary, "annual_salary"] = pd.NA

df.annual_salary.astype(float)

pd.to_numeric(df.annual_salary)