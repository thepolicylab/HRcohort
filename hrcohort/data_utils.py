"""
Refactor code in categ_HR into functions for categ_HR
"""
from typing import List, Union

import pandas as pd
from hrcohort import constants

def select_budget_analysts(
    df: pd.DataFrame, search_colname: Union[str, List] = "simple_job_title"
) -> pd.DataFrame:
    """
    Filter Dataframe for Budget Analysts
    Args:
      df (pd.DataFrame): Dataframe of all job titles
      search_colname (str): Specify which column to look through. Default is "simple_job_title"
    Returns: pd.DataFrame

    """
    if df.columns.isin(list(search_colname)).any():
        # do the budget filtering
        pass
    else:
        raise Exception(f"{search_colname} column does not exist")
