# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 12:18:07 2021

@author: dwang
"""

#%% Importing libraries
from pathlib import Path
import pandas as pd
import numpy as np
import ftfy
import re as re

#%% Defining constants
DATA_DIRECTORY = Path("../data")
FILTERED_COHORT_FILE = DATA_DIRECTORY / "filtered_hrcohort.csv.gz"

#%% Importing CSV, dropping useless rows, counting+dropping duplicate rows
# Read the dataframe with pre-set data types.
df = pd.read_csv(FILTERED_COHORT_FILE,
                   compression='gzip',
                   dtype={'postal': str, 'year': int, 'job_title': str, 'agency': str,
                          'annual_salary': str, 'yrs_in_service': str},
#                    encoding='latin1'
                )

# Verify if the data columns have been read with correct types
df.dtypes
# Drop any row with an empty 'job_title' since they are useless to HRcohort
df = df[~df['job_title'].isna()]
# Replace NaN or empty values with an underscore, which is unlikely to be confused with
# valid, pre-existing job titles
df[['agency','annual_salary','yrs_in_service']] = \
    df[['agency','annual_salary','yrs_in_service']].fillna('_')

# Create a new column with a count of duplicates and then drop duplicates
df = df.groupby(df.columns.tolist(),as_index=False).size()
df.rename(columns={'size':'dup_count'}, inplace=True)
df.drop_duplicates(inplace=True)
# Reintroduce NaN
df.replace('^_$', pd.NA, inplace=True, regex=True)

#%% This cell is for viewing the weird typography, not a step of cleaning
# # First create full universe of characters used in 'annual_salary'
# univ_sal = set()
# for sal in df['annual_salary']:
#     for char in sal:
#         univ_sal.add(char)
# univ_sal = sorted(univ_sal)

# # Filter for unexpected symbols
# weird_syms = sorted([char for char in univ_sal if char not in 
#                   ['_',' ','$',',','.','0','1','2','3','4','5','6','7','8','9']])

# # The string below was my abandoned attempt at constructing a regex from weird_syms
# # '\(|\)|\+|\-|A|D|E|R|S|U||a|e|l|n|t|u'
# weird_sym = '\-'
# df_weird_sal = df[df['annual_salary'].str.contains(weird_sym)]

#%% Cleaning 'annual_salary'
# Retain only characters that are numeric, sign, period, or scientific notation
df['annual_salary'] = df['annual_salary']\
    .str.replace('[^\dE.+-]+', '', regex=True)
is_no_sal = df['annual_salary'] \
    .apply(lambda x: pd.isnull(x) or len(x)==0 or not any([char.isnumeric() for char in x]))
df.loc[is_no_sal , 'annual_salary'] = np.nan
df['annual_salary'] = df['annual_salary'].astype(float)

#%% This cell is for viewing the weird typography, not a step of cleaning
# # First create full universe of characters used in 'temp_job_title'
# univ_job = set()
# for job in df['temp_job_title']:
#     for char in job:
#         univ_job.add(char)
# univ_job = sorted(univ_job)

# # The following are especially weird symbols manually picked from univ_job
# weirds = '¿聽†�聳'

# # Make new dataframe by filtering for rows with strange typography in 'temp_job_title' column
# # This dataframe is mostly for viewing the nature of the irregularities
# df_weird_jobs = df[df.temp_job_title.str.contains('\¿|\聽|\†|\�|\聳')]

#%% Cleaning 'job_title' and creating 'cleaned_job_title'
# Make new column for job titles being edited, and use FTFY library to fix encodings
df.insert(3, 'temp_job_title', df['job_title'])
df['temp_job_title'] = df['temp_job_title'].apply(lambda x: ftfy.fix_text(x))

# Remove weird encodings and extra whitespace
df['temp_job_title'] = df['temp_job_title']\
    .str.strip()\
    .str.replace(' +', ' ', regex=True)\
    .str.replace('[¿†聽聳�]', '', regex=True)\
    .str.upper()
# Rename the temp column to showed cleaned
df.rename(columns={'temp_job_title':'cleaned_job_title'}, inplace=True)
        
#%% Creating frequency dictionary of all words used in 'job_title'
# Create a frequency dictionary of all words used
freqs = {}
for row,job in enumerate(df['cleaned_job_title']):
    pure_job = [' ' if not let.isalnum() else let for let in list(job)]
    words = ''.join(pure_job).split()
    for word in words:
        if word not in freqs:
            freqs[word] = [0,[row]] 
        else:
            freqs[word][0] += 1
            freqs[word][1].append(row)

# Sort the dictionary by value (i.e. frequency)
freqs = dict(sorted(freqs.items(), key=lambda term:term[1], reverse=True))

#%% Creating simple_job_title column and identifying budget analysts, etc.
df.insert(4, 'simple_job_title', ['' for row in range(df.shape[0])])

for row in freqs['BUDGET'][1]:
    if bool(re.search('BUDGET ANALYST' , df['cleaned_job_title'].iat[row])):
        df['simple_job_title'].iat[row] = 'BUDGET ANALYST'
    else:
        df['simple_job_title'].iat[row] = 'BUDGET PROFESSIONAL'

ba = df[df['simple_job_title']=='BUDGET ANALYST']
bp = df[df['simple_job_title']=='BUDGET PROFESSIONAL']
ba.to_csv('budget_analysts.csv')
bp.to_csv('budget_professionals.csv')

#%% Manually replacing job titles that contain the most common words
# Some clunky rules written before Daniel learned regex
for row in freqs['TEACHER'][1]:
    if (df['cleaned_job_title'].iat[row][-7:]=='TEACHER' 
    or 'TEACHER,' in df['cleaned_job_title'].iat[row]):
        df['simple_job_title'].iat[row] = 'TEACHER'
    
for row in freqs['OFFICER'][1]:
    if bool(re.search('CORR' , df['cleaned_job_title'].iat[row])):
        df['simple_job_title'].iat[row] = 'CORRECTIONAL OFFICER'
    
for row in freqs['ASSISTANT'][1]:
    if bool(re.search('ADMIN|EXEC|SECRETAR' , df['cleaned_job_title'].iat[row])):
        df['simple_job_title'].iat[row] = 'ADMINISTRATIVE ASSISTANT'

for row in freqs['IT'][1]:
    if bool(re.search('IT SPECIALIST' , df['cleaned_job_title'].iat[row])):
        df['simple_job_title'].iat[row] = 'IT SPECIALIST'

for row in freqs['SOFTWARE'][1]:
    if bool(re.search('DEVELOPMENT SPEC|SOFTWARE DEVELOPER' , df['cleaned_job_title'].iat[row])):
        df['simple_job_title'].iat[row] = 'SOFTWARE DEVELOPER'

for row in freqs['ENGINEER'][1]:
    if df['cleaned_job_title'].iat[row][-8:]=='ENGINEER' \
    or bool(re.search('ENGINEER,|ENGINEER ' , df['cleaned_job_title'].iat[row])):
        if 'SOFTWARE' in df['cleaned_job_title'].iat[row]:
            df['simple_job_title'].iat[row] = 'SOFTWARE DEVELOPER'
        elif 'ELECTRICAL' in df['cleaned_job_title'].iat[row]:
            df['simple_job_title'].iat[row] = 'ELECTRICAL ENGINEER'
        elif 'MECHANICAL' in df['cleaned_job_title'].iat[row]:
            df['simple_job_title'].iat[row] = 'MECHANICAL ENGINEER'        
        elif 'STRUCTURAL' in df['cleaned_job_title'].iat[row]:
            df['simple_job_title'].iat[row] = 'STRUCTURAL ENGINEER' 
        elif 'TRANSPORTATION' in df['cleaned_job_title'].iat[row]:
            df['simple_job_title'].iat[row] = 'TRANSPORTATION ENGINEER'
        elif 'ENVIRONMENTAL' in df['cleaned_job_title'].iat[row]:
            df['simple_job_title'].iat[row] = 'ENVIRONMENTAL ENGINEER'
        elif 'CIVIL' in df['cleaned_job_title'].iat[row]:
            df['simple_job_title'].iat[row] = 'CIVIL ENGINEER'
# Deal with engineer titles later 'lead, principal, chief, manager, technician, intern, supervisor
# senior, supervising, junior'

