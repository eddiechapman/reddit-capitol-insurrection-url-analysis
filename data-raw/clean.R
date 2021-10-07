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
    created_utc, 
    score, 
    ups, 
    downs, 
    controversiality
  ) %>%
  mutate(
    created_utc = as_datetime(created_utc, tz='US/Central'),
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
  mutate(code = stringr::str_split(codes, '\n')) %>%
  tidyr::unnest_longer(code) %>%
  filter(!is.na(code)) %>%
  select(quote_id, doc_id, code)


urls_df <-
  readr::read_csv(file = urls_path) %>%
  mutate(url_id = row_number()) %>%
  select(url_id, document_id, url, platform, profile, content, community)


motivations_df <-
  quotes_df %>%
  left_join(codes_df) %>%
  left_join(reddit_df, by = c('doc_id' = 'comment_id')) %>%
  filter(code == 'motivation') %>%
  select(doc_id, quote, author, created_utc, score) 
  

  
# output
write_csv(reddit_df, file = file.path('data', 'reddit.csv'))
write_csv(quotes_df, file = file.path('data', 'quotes.csv'))
write_csv(docs_df, file = file.path('data', 'docs.csv'))
write_csv(codes_df, file = file.path('data', 'codes.csv'))
write_csv(urls_df, file = file.path('data', 'urls.csv'))
write_csv(motivations_df, file = file.path('data', 'motivations.csv'))

  



