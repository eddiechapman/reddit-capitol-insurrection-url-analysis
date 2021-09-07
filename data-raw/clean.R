library(dplyr)
library(igraph)
library(lubridate)


comments <- 
  readr::read_csv('data-raw/reddit_data.csv') %>%
  select(comment_id = id, author, created, created_utc, score, ups, downs, controversiality) %>%
  mutate(created_utc = lubridate::as_datetime(created_utc, tz='America/Chicago'),
         created = lubridate::as_datetime(created, tz='America/Chicago'))

urls
  

urls <-
  readr::read_csv('data-raw/extracted_urls.csv') %>%  
  select(comment_id = document_id, platform, profile, content) %>%
  filter(!is.na(content)) %>%
  mutate(url_id = group_indices(., platform, profile, content)) %>%
  arrange(url_id)

comment_urls <- select(urls, comment_id, url_id)

urls <-
  urls %>%
  select(url_id, platform, profile, content) %>%
  unique()

  



