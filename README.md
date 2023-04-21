# Crawler
CS121 2023S

Crawler features:
Checks sitemaps to see if the change frequency and last modified date indicate that the current version is outdated and needs to be recrawled. (
Follow the politeness rule (0.5s per server) and only crawl websites that allows crawling.
Multi-threaded crawling
Detect and avoid infinite traps
Crawl all pages with high textual information content
Detect and avoid sets of similar pages with no information
Detect redirects and if the page redirects your crawler, index the redirected content
Detect and avoid dead URLs that return a 200 status but no data (click here to see what the different HTTP status codes meanLinks to an external site.)
Detect and avoid crawling very large files, especially if they have low information value
