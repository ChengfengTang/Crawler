import re
from urllib.parse import urljoin, urlparse, urldefrag

from bs4 import BeautifulSoup
from collections import defaultdict

stop_words = [
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's",
    "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's",
    "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't",
    "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
]

# Finds the number of unique page
visited = []
# Finds the 50 most common words
words = {}
# Finds the longest page
longestPage = 0;
# Finds how many pages for each subdomain
domainCount = {}

# Finds how many subdomains for each main domain
subdomains = defaultdict(set)

def scraper(url, resp):
    links = extract_next_links(url, resp)
    print(len(visited)) #The total number of pages
    print(longestPage)
    print(sorted(words.items(), key=lambda x: x[1], reverse=True)[:5])
    print(domainCount)
    print(subdomains)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    # Check if the response status is OK (200)
    if resp.status != 200:
        return []
    # Extract the URLs from the response content
    # Create a bs4 object called "soup" and scrape the html response using a html parser
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    text = soup.get_text()

    # Find all the words
    global words
    for x in re.findall(r'\b\w+\b', text):
        if(x not in stopWords): # self-exp
            words[x] = words.get(x,0) +1

    # update longest page
    global longestPage
    longestPage = max(longestPage, len(text))

    links = []
    # Find all the links
    for temp in soup.find_all('a', href=True):
        href = temp.get('href')
        # Absolute url with href
        absoluteURL = urljoin(url,href)
        # Absolute url without fragment part
        absoluteURL,fragment = urldefrag(absoluteURL)
        if is_valid(absoluteURL):
            global visited
            global domainCount
            domainCount[absoluteURL] = domainCount.get(url,0) + 1
            links.append(absoluteURL)
            visited.append(absoluteURL)
    # Testing    
    #print(links)
    links = []    
    return links

def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    global visited
    global domainCount
    global subdomains
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        # Already visited
        if url in visited:
            return False
        visited.append(url)
        domain = ""
        subDomain = parsed.hostname
        if subDomain.startswith("www."):
            subDomain = subDomain [4:]
        domainP = r"(?:[^.]+\.)(?P<domain>[^.]+\..+)$"
        domainM = re.search(domainP, subDomain)
        if (domainM):
            domain = domainM.group("domain")
        else:
            # for url like uci.edu/
            #print("no domain found " + subDomain)
            return False
        if subDomain in set(["ics.uci.edu","cs.uci.edu","informatics.uci.edu", "stat.uci.edu"]):
            domain = subDomain
        # print("d: " + domain)
        # print("sd: " + subDomain)
        # Ex.
        # domain: ics.uci.edu
        # subdomain: vision.ics.edu

        # If not a subdomain

        if domain not in set(["ics.uci.edu","cs.uci.edu","informatics.uci.edu", "stat.uci.edu"]):
            return False
        domainCount[subDomain] = domainCount.get(subDomain,0) + 1
        subdomains[domain].add(subDomain)
        #print(domainCount)
        #print(subdomains)

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
"""
if __name__ == "__main__":
    is_valid("http://www.vision.ics.uci.edu/somethings/anything/")
    print()
    is_valid("http://vision.ics.uci.edu/somethings/anything/")
    is_valid("http://www.abc.ics.uci.edu/somethings/anything/")
"""
