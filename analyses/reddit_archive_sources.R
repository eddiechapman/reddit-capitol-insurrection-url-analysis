reddit_archive_sources_path <- file.path('data', 'reddit_archive_sources.csv')

reddit_archive_df <- readr::read_csv(file = reddit_archive_sources_path)

# do some ggplot bar chart to show the size differences between sources