# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 12:18:07 2021

@author: dwang
"""

#%% Import libraries
import pandas as pd
import ftfy

#%% Import CSV, drop useless rows, replace NaN, and count duplicates
# Read the dataframe with pre-set data types.
orig = pd.read_csv('filtered_hrcohort.csv.gz',
                   compression='gzip',
                   # encoding='latin_1',
                   dtype={'postal': str, 'year': int, 'job_title': str, 'agency': str,
                          'annual_salary': str, 'yrs_in_service': str})

df = orig
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
df.drop_duplicates(inplace=True)

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
# Wipe all characters that are not numeric, a period, or scientific notation
# Convert all values to dtype float

for row,sal in enumerate(df['annual_salary']):
    new_sal = ''
    for idx,char in enumerate(sal):
        if char.isnumeric() or (char in '.-+E'):
            new_sal += char
    # if the value is empty or only one character (for whatever reason), make it 0.001
    # I chose this value since it is unlikely to be confused valid salaries
    if not new_sal or len(new_sal)==1:
        df['annual_salary'].iat[row] = 0.001
    else: df['annual_salary'].iat[row] = float(new_sal)        

#%% Make new column for job titles being edited, and use FTFY library fix encodings
df.insert(3, 'temp_job_title', df['job_title'])
for row,job in enumerate(df['temp_job_title']):
    df['temp_job_title'].iat[row] = ftfy.fix_text(job)

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

#%% Substitute blank space instead of any weird symbols/encodings that remain
for row,job in enumerate(df['temp_job_title']):
    new_job = ''
    for idx,char in enumerate(job):
        if char in "!#$%&()*+,-./:;<=?@[\\]_¿‐–†聳聽�":
            new_job += ' '
        else: new_job += char
    df['temp_job_title'].iat[row] = new_job
        
#%% Find out what the most common words are in the 'job_title' column
# Create a frequency dictionary of all words used
freqs = {}
for job in df['temp_job_title']:
    words = job.split()
    for word in words:
        if word.upper() not in freqs:
            freqs[word.upper()] = 0 
        else: freqs[word.upper()] += 1
# Sort the dictionary by value (i.e. frequency)
freqs = dict(sorted(freqs.items(), key=lambda term:term[1]))

#%% Start 