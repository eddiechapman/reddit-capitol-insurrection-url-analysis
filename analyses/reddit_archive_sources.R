library(dplyr)
library(ggplot2)

reddit_archive_sources_path <- file.path('data', 'reddit_archive_sources.csv')

reddit_archive_df <- readr::read_csv(file = reddit_archive_sources_path)

reddit_archive_df %>%
  mutate(source = forcats::fct_reorder(source, size_gb)) %>%
  ggplot(aes(x = source, y = size_gb)) +
  geom_bar(stat = 'identity', fill = "#f68060", alpha = .6 , width = .4) +
  coord_flip() +
  xlab('') +
  ylab('Size of content collected (Gigabytes)') +
  labs(
    title = '"Archiving the Capitol Hill Riots" Sources',
    caption = 'Source: https://mega.nz/folder/30MlkQib#RDOaGzmtFEHkxSYBaJSzVA') +
  theme_bw()
  

reddit_archive_df %>%
  mutate(source = forcats::fct_reorder(source, items)) %>%
  ggplot(aes(x = source, y = items)) +
  geom_bar(stat = 'identity', fill = "#f68060", alpha = .6 , width = .4) +
  coord_flip() +
  xlab('') +
  ylab('Number of items archived') +
  labs(
    title = '"Archiving the Capitol Hill Riots" Sources',
    caption = 'Source: https://mega.nz/folder/30MlkQib#RDOaGzmtFEHkxSYBaJSzVA') +
  theme_bw()

reddit_archive_df %>%
  ggplot(aes(x = size_gb, y = items)) +
  geom_jitter(width = 2, size = 3, aes(col = source)) +
  ggrepel::geom_text_repel(aes(label = source), size = 4) +
  xlab('Size in GB') +
  ylab('Number of items archived') +
  labs(title = '"Archiving the Captiol Hil Riots" Source Size and Volume',
       caption = 'Source: https://mega.nz/folder/30MlkQib#RDOaGzmtFEHkxSYBaJSzVA') +
  theme_bw()