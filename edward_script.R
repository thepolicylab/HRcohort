library(tidyverse)
library(dplyr)
library(readxl)
library(purrr)

# Step 1: find all files by type
DATA_DIRECTORY = "data"
csv_list = list.files(path=DATA_DIRECTORY, pattern="*.csv", full.names=TRUE)
excel_list = list.files(path=DATA_DIRECTORY, pattern="*.xlsx", full.names=TRUE)
pdf_list = list.files(path=DATA_DIRECTORY, pattern="*.pdf", full.names=TRUE)


# Step 2: read all files
## Read all CSV
csv_df = lapply(csv_list, read_csv) 
### lapply downloads your files in a list. 
### You can access individual files via subsetting
### i.e csv_df[1], csv_df[2]

## Read all excel
excel_df = lapply(excel_list, read_excel)
### Likewise, you can find individual files via subsetting
### i.e excel_df[1], excel_df[2]

# Now, we want to know the column names of each file to see how we can merge
lapply(csv_df, colnames)
# Notice that 'Full/Part Time" and "Full-time/Part-time" are probably the same thing

my_mutate <- function(df, find_word, replace_word) {
  df %>% 
    rename(toupper) %>% # often easy to convert everything to upper case
    rename_at(vars(contains('/Part')), funs(sub('Full-time', 'Full')))
}




# combines all the files together
append(new_df, by = c('name', 'salary'))
