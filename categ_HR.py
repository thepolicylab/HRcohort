# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 12:18:07 2021

@author: dwang
"""

#%%
import pandas as pd
import numpy as np
import missingno as msno

#%%
# Read the dataframe with pre-set data types.
df = pd.read_csv('/Users/edward/projects/HRcohort/filtered_hrcohort.csv.gz',
                   compression='gzip',
                   dtype={'postal': str, 'year': int, 'job_title': str,
                          'cleaned_job_title': str, 'agency': str,
                          'annual_salary': str, 'yrs_in_service': str})

#%% Make dtype consistent within each column
# Make sure that you remove the datasets that have NaN, because pandas.groupby will behave erratically
print(df.shape)
nan_df = df[df.job_title.isna()]
df = df[~df.job_title.isna()]
# There were 1458218 rows that had NaN as job titles.
print(df.shape)
# How many rows are considered duplicates? 880766
print(df.duplicated().sum())

# The reason why groupby and drop_duplicates is different is because the default behavior of
# group by is "if group keys contain NA values, NA values together with row/column will be dropped."
# Further refer to `dropna` command in
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.groupby.html
groupby_counts = df.groupby(['postal', 'year', 'job_title', 'agency', 'annual_salary'],
                  as_index=False).size()
groupby_counts.drop_duplicates(inplace=True)
print(groupby_counts.shape)
drop_dup_counts = df.drop_duplicates()
print(drop_dup_counts.shape)

diff_df = pd.merge(drop_dup_counts, groupby_counts.drop('size', axis=1), how='outer', indicator='Exist')
left_only_df = diff_df[diff_df.Exist.isin(['left_only'])]
# Notice that the rows that are not included in the groupby_df are those that have NaNs.
msno.matrix(left_only_df)

# redefine a copy of the column.
df['cleaned_job_title'] = df['job_title']
# The concerning encoding.
df[df.job_title.str.contains('聽')]

### Aside: Analyze bahvior of nan_df
msno.matrix(nan_df)
# Retain rows that have at least 1 other column with data other than postal & year.
nan_df.dropna(thresh=3, inplace=True)
nan_df.postal.value_counts()
# Notice that MD and FL are overrepresented. Pinging Chris Calley about these states


#
# # df = df.astype({'postal':str, 'year':int, 'job_title':str, 'cleaned_job_title':str,
# #                 'agency':str, 'annual_salary':str, 'yrs_in_service':str})
#
# df['cleaned_job_title'] = df['cleaned_job_title'].str.upper()
# df['agency'] = df['agency'].str.upper()

#%% Fix weird typography in 'annual_salary' column

# weird_jobs = np.empty((0,3))
# for row,job in enumerate(df['job_title']):
#     for char in job:
#         if char in syms:
#             weird_jobs = np.vstack((weird_jobs , [row,char,job]))
#
# # Sort by offending char so that similar typos are grouped together for viewing
# weird_jobs = weird_jobs[np.argsort(weird_jobs[:,1]) , :]
#
# weirds = {'l', ')', 'u', 'U', 'E', 'R', 'A', 'e', 't', '(', '+', 'n', 'D', ' ', 'a', 'S', '-'}
#
# #%% Fix weird characters usage in 'job_title' column so that all full English words can be parsed
# # Identify the full universe of characters used in job titles
# univ = set()
# for job in df['job_title']:
#     for char in job:
#         univ.add(char)
#
# univ = sorted(univ)
#
# # The following are especially weird symbols manually picked from univ
# syms = ['/',"'",'(',')','-','.','&',",",'$','+','*','[','#','‐',':',';','¿','<','_','%','@','!',
# '\\','聳',']','聽','–','?','Ô','ø','Ω','=','','†']
#
# #%% Clean problematic job titles
# # For now, I replace offending chars with spaces to facilitate parsing later
# # I have made sure that doing so will not chop apart too many sensible English words
# for row,job in enumerate(df['job_title']):
#     for sym in syms:
#         job = job.replace(sym,' ')
#     df['job_title'].iat[row] = job
#
# # for row,job in enumerate(df['job_title']):
# #     to_fix = False
# #     for i,sym in enumerate(syms):
# #         if sym in job:
# #             to_fix = True
# #             sym_1 = i
# #             break
# #     if to_fix:
# #         tmp = job
# #         for sym in syms[sym_1:]:
# #             tmp = tmp.replace()
# #         df['job_title'].iat[row] = ''.join(tmp)
#
# # Make some manual fixes
# df['job_title'].iat[
#     df.index[df['job_title'] == 'DIRECTOR  DEPARTMENT OF FI CAL'][0]
#     ] = 'DIRECTOR  DEPARTMENT OF FISCAL'
#
# #%% Find out what the most common words are in the 'job_title' column
# # First, create a frequency dictionary of all words used
# freq = set()
#
# for
#     for raw_word in words:
#         word = raw_word.strip(unwanted_chars)
#         if word not in wordfreq:
#             wordfreq[word] = 0
#         wordfreq[word] += 1
#
# freq = dict(sorted(x.items(), key=lambda item: item[1]))
