library(tidyverse)
library(dplyr)
library(readxl)
library(purrr)
library('glue')
library('googledrive')

# Step 0: Set your working directory to the correct location
setwd()
# Step 1: find all files by type
DATA_DIRECTORY = "data"
csv_list = list.files(path=DATA_DIRECTORY, pattern="*.csv", full.names=TRUE)
excel_list = list.files(path=DATA_DIRECTORY, pattern="*.xlsx", full.names=TRUE)
pdf_list = list.files(path=DATA_DIRECTORY, pattern="*.pdf", full.names=TRUE)


# Step 2: read all files
## Read all CSV
row_num = 500 # can change depending on need
csv_df = map2(
  csv_list, # file directories
  csv_list, # using file directories as id
  ~read_csv(.x) %>% # reading each csv in first csv_list
    mutate(id = .y) %>% # creating extra column called 'id' with second csv_list
    head(row_num) # limiting the tibble to row number
  ) %>% 
  bind_rows() # combining all the columns 


### lapply downloads your files in a list. 
### You can access individual files via subsetting
### i.e csv_df[1], csv_df[2]

## Read all excel
excel_df = lapply(excel_list, read_excel)
### Likewise, you can find individual files via subsetting
### i.e excel_df[1], excel_df[2]
i = 0

temp <- csv_df %>% map(caller_func, row_num)
temp[[2]]$filename

reduce(full_join)

#======#

# Now, we want to know the column names of each file to see how we can merge
lapply(csv_df, colnames)

df <- csv_df[[1]]
# Assume that the columns we want are 'Pay', 'Name', 'Position Title'
col_cleaner <- function(df) {
  if any(str_detect(colnames(df), "First")):
    df %>% select(contains(c("First","Last"))) %>% mutate("EMP_NAME" = ~.)
    df['temp'] <- glue('{df[fname_col]} {df[lname_col]}')
    
}
glue('{df$`First Name`} {df$`Last Name`}')

# combines all the files together
append(new_df, by = c('name', 'salary'))
