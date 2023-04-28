CS121 2023S

Crawler features to be implemented: 

Follow the politeness rule (0.5s per server) and only crawl websites that allows crawling. ☑️

Multi-threaded crawling

Detect and avoid infinite traps (repeated url patterns) ☑️

Crawl all pages with high textual information content ☑️

Detect and avoid sets of similar pages with no information ☑️

Detect redirects and if the page redirects your crawler, index the redirected content ☑️

Detect and avoid dead URLs that return a 200 status but no data (click here to see what the different HTTP status codes meanLinks to an external site.) ☑️

Detect and avoid crawling very large files, especially if they have low information value ☑️



REPORT:

How many unique pages did you find? Uniqueness for the purposes of this assignment is ONLY established by the URL, but discarding the fragment part. So, for example, http://www.ics.uci.edu#aaa and http://www.ics.uci.edu#bbb are the same URL. Even if you implement additional methods for textual similarity detection, please keep considering the above definition of unique pages for the purposes of counting the unique pages in this assignment.

What is the longest page in terms of the number of words? (HTML markup doesn’t count as words)

What are the 50 most common words in the entire set of pages crawled under these domains ? (Ignore English stop words, which can be found, for example, hereLinks to an external site.) Submit the list of common words ordered by frequency.

How many subdomains did you find in the ics.uci.edu domain? Submit the list of subdomains ordered alphabetically and the number of unique pages detected in each subdomain. The content of this list should be lines containing URL, number, for example:
http://vision.ics.uci.edu, 10 (not the actual number here)
