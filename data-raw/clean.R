library(dplyr)
library(lubridate)
library(readr)
library(stringr)

# input paths
reddit_path <- file.path('data-raw', 'reddit_data.csv')
docs_path <- file.path('data-raw', 'docs.csv')
quotes_path <- file.path('data-raw', 'quotes.csv')
urls_path <- file.path('data-raw', 'extracted_urls.csv')

reddit_df <- 
  readr::read_csv(file = reddit_path) %>%
  select(
    comment_id = id, 
    author, 
    created, 
    created_utc, 
    score, 
    ups, 
    downs, 
    controversiality
  ) %>%
  mutate(
    created_utc = as_datetime(created_utc, tz='America/Chicago'),
    created = as_datetime(created, tz='America/Chicago')
  )

docs_df <-
  readr::read_csv(file = docs_path) %>%
  select(
    doc_id = Document, 
    comment = Comment, 
    groups = 'Document Groups',
    codes = Codes, 
    n_quotes = 'Quotation Count'
  ) %>%
  mutate(
    codes = str_replace(codes, 'outside project', 'outside_project'),
    removed = str_detect(tidyr::replace_na(groups, ''), 'deleted')
  ) %>%
  select(-groups)


quotes_df <-
  readr::read_csv(file = quotes_path) %>%
  select(
    quote_id = ID, 
    doc_id = Document, 
    quote = 'Quotation Content', 
    codes = Codes
  ) %>%
  mutate(codes = str_replace(codes, 'outside project', 'outside_project'))


codes_df <- 
  quotes_df %>%
  mutate(code = stringr::str_split(codes, ' ')) %>%
  tidyr::unnest_longer(codes) %>%
  select(quote_id, doc_id, code)


urls_df <-
  readr::read_csv(file = urls_path) %>%
  mutate(url_id = row_number()) %>%
  select(url_id, document_id, url, platform, profile, content, community)
  
  
# output
write_csv(reddit_df, file = file.path('data', 'reddit.csv'))
write_csv(quotes_df, file = file.path('data', 'quotes.csv'))
write_csv(docs_df, file = file.path('data', 'docs.csv'))
write_csv(codes_df, file = file.path('data', 'codes.csv'))
write_csv(urls_df, file = file.path('data', 'urls.csv'))


  



