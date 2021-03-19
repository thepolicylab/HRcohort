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
df.rename(columns={'size':'dup_count'}, inplace=True)
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
# Deliberately preserve slash, comma, apostrophe, paren, and colon for descriptiveness
for row,job in enumerate(df['temp_job_title']):
    new_job = ''
    prev_char = ' '
    for char in job:
        if char in """!#$%&*+-.;<=?@[\\]_¿‐–†聳聽�""":
            if prev_char != ' ':
                new_job += ' '
            else:
                pass
        else: new_job += char
        prev_char = char
    df['temp_job_title'].iat[row] = new_job.strip().upper()
# Rename the temp column to be cleaned
df.rename(columns={'temp_job_title':'cleaned_job_title'}, inplace=True)
        
#%% Find out what the most common words are in the 'job_title' column
# Create a frequency dictionary of all words used
freqs = {}
for row,job in enumerate(df['cleaned_job_title']):
    words = job.split()
    for word in words:
        # Exclude comma that may be at word end
        while not word[0].isalnum():
            word = word[1:]
        while not word[-1].isalnum():
            word = word[:-1]
        word = ''.join([let for let in word if let!='/'])
        if word not in freqs:
            freqs[word] = [0,[row]] 
        else:
            freqs[word][0] += 1
            freqs[word][1].append(row)

# Sort the dictionary by value (i.e. frequency)
# The following data wrangling relies on manual observations from this dictionary
freqs = dict(sorted(freqs.items(), key=lambda term:term[1], reverse=True))

#%% Start manually replacing job titles that contain common, unequivocal words
df.insert(4, 'simple_job_title', ['' for row in range(df.shape[0])])

for row in freqs['TEACHER'][1]:
    if (df['cleaned_job_title'].iat[row][-7:]=='TEACHER' 
    or 'TEACHER,' in df['cleaned_job_title'].iat[row]):
        df['simple_job_title'].iat[row] = 'TEACHER'

for row in freqs['SOFTWARE'][1]:
    if (df['cleaned_job_title'].iat[row][-8:]=='ENGINEER' 
    or 'ENGINEER,' in df['cleaned_job_title'].iat[row]
    or 'ENGINEER ' in df['cleaned_job_title'].iat[row]):
        if 'SOFTWARE' in df['cleaned_job_title'].iat[row]:
            df['simple_job_title'].iat[row] = 'SOFTWARE DEVELOPER'
        elif 'ELECTRICAL' in df['cleaned_job_title'].iat[row]:
            df['simple_job_title'].iat[row] = 'ELECTRICAL ENGINEER'


for row in freqs['ENGINEER'][1]:
    if (df['cleaned_job_title'].iat[row][-8:]=='ENGINEER' 
    or 'ENGINEER,' in df['cleaned_job_title'].iat[row]
    or 'ENGINEER ' in df['cleaned_job_title'].iat[row]):
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

# Deal with titles later 'lead, principal, chief, manager, technician, intern, supervisor
# senior, supervising, '

for row in freqs['OFFICER'][1]:
    if (df['cleaned_job_title'].iat[row][-7:]=='OFFICER' 
    or 'OFFICER,' in df['cleaned_job_title'].iat[row]
    or 'OFFICER ' in df['cleaned_job_title'].iat[row]):
        if 'ELECTRICAL' in df['cleaned_job_title'].iat[row]:
            df['simple_job_title'].iat[row] = 'ELECTRICAL ENGINEER'
        elif 'MECHANICAL' in df['cleaned_job_title'].iat[row]:
            df['simple_job_title'].iat[row] = 'MECHANICAL ENGINEER'        
