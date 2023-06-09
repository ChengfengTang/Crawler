import re
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser

from bs4 import BeautifulSoup
from collections import defaultdict

stopWords = [
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's",
    "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
    "what's",
    "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't",
    "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
]

# Finds the number of unique page
visited = set()
# Finds the 50 most common words
words = {}
# Finds the longest page
longestPage = 0;
longestPageURL = "";
# Finds how many pages for each subdomain
domainCount = {}
# Keeps track of depth, avoid traps
depth = {}
# 3-grams fingerprints
fingerprints = []

# Finds how many subdomains for each main domain
subdomains = defaultdict(set)


def scraper(url, resp):
    # Extract next links from the current URL and response
    links = extract_next_links(url, resp)
    # Print summary statistics
    print()
    print("Total # of pages visited: ", len(visited))  # The total number of pages
    print("Longest page ", longestPageURL, " has ", longestPage, "words")
    print(sorted(words.items(), key=lambda x: x[1], reverse=True)[:60])
    print()
    for x, y in subdomains.items():
        print(x, len(y), end=",")
    print()
    for x, y in sorted(domainCount.items()):
        print(x, y, end=",")
    print()
    return links


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

    # print("resp: " + resp.url + "   |  url: " + url)
    """
    parsed = urlparse(resp.url)
    robotsUrl = parsed.scheme + "://" + parsed.netloc + "/robots.txt"
    rp = RobotFileParser()
    rp.set_url(robotsUrl)
    rp.read()
    # Not allowed in robots.txt
    if not rp.can_fetch("*", url):
        return []
    """
    # Extract the URLs from the response content
    # Create a bs4 object called "soup" and scrape the html response using a html parser
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    text = soup.get_text()

    # there should be at least 10% of the content in text
    # Since we are crawling school website, we are not interested in irrelevant
    # If content-length is 0, just set it to len(text)
    contentLen = int(resp.raw_response.headers.get("Content-Length", len(text)))
    # print("CL:" , contentLen)
    # print("TL: " , len(text))
    if contentLen != 0:
        if (len(text) / contentLen) < 0.1:
            return []
    # https://stackoverflow.com/questions/2773396/whats-the-content-length-field-in-http-header
    # 500KB/Page is too large, a normal pure text size is around 200-300 KB, we are
    # Not interested in irrelevant websites
    if contentLen > 512000:
        return []

    # Find all the words
    global words
    # Tokenization Needs improvement
    for x in re.findall(r'[a-zA-Z0-9]+', text.lower()):
        if x not in stopWords:  # self-exp
            words[x] = words.get(x, 0) + 1

    # update longest page
    global longestPage
    global longestPageURL
    if (longestPage < len(text)):
        longestPage = len(text)
        longestPageURL = resp.url

    global depth
    # Might be going too deep if we are 10 levels down
    if depth.get(resp.url, 0) > 10:
        return []

    # Find all the links and add valid ones to the list
    links = []

    global fingerprints
    fp = []
    for i in range(len(text) - 2):
        threeG = text[i:i + 3]
        temp = hash("".join(threeG))
        if temp % 4 == 0:
            fp.append(temp)
    for x in fingerprints:
    # similarity level S > 90% near duplicate
    # AKA Already visited a similar page
        union = len(set(fp).union(set(x)))
        if union != 0:
            similarity = len(set(fp).intersection(set(x))) / union
            if similarity > 0.9:
                return []
    fingerprints.append(fp)

    # Indexing the redirected url only if it's worth visiting
    if resp.url != url:
        # print("redirected" + resp.url)
        # print(url)
        # print()
        if is_valid(resp.url):
            links.append(resp.url)

    # Find all the links
    for temp in soup.find_all('a', href=True):
        href = temp.get('href')
        # Absolute url with href
        absoluteURL = urljoin(url, href)
        # Absolute url without fragment part
        absoluteURL, fragment = urldefrag(absoluteURL)
               # Already visited
        if absoluteURL not in visited and is_valid(absoluteURL):
            global domainCount
            links.append(absoluteURL)
            visited.add(absoluteURL)
        # If the link is valid and should be visited, add it
            depth[absoluteURL] = depth.get(resp.url, 0) + 1
    # Testing
    # print(links)
    # links = []
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

        # Not sure how to get robots.txt without using request
        # Manual sets here

        if parsed.scheme not in set(["http", "https"]):
            return False

        # Some trap patterns mentioned in class
        # /calendar/YYYY/MM
        # /folder
        # /?page=1 ...
        # /www.ics.uci.edu/community/news/view_news?id=2111 seems like a trap during testing
        trapPattern = [r"/calendar/\d{4}/\d{2}",
                       r"(/folder)+",
                  
                       # not allowed by robots
                       r"ics.uci.edu/bin",
                       r"ics.uci.edu/~mpufal",
                       ]

        for x in trapPattern:
            if re.search(x, url):
                return False

        domain = ""
        subDomain = parsed.hostname
        if subDomain is None or subDomain == "calender.ics.uci.edu":
            return False
        if subDomain.startswith("www."):
            subDomain = subDomain[4:]
        domainP = r"(?:[^.]+\.)(?P<domain>[^.]+\..+)$"
        domainM = re.search(domainP, subDomain)
        if domainM:
            domain = domainM.group("domain")
        else:
            # for url like uci.edu/
            # print("no domain found " + subDomain)
            return False
        if subDomain in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]):
            domain = subDomain
        # print("d: " + domain)
        # print("sd: " + subDomain)
        # Ex.
        # domain: ics.uci.edu
        # subdomain: vision.ics.edu

        # If not a subdomain

        if domain not in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]):
            return False
        domainCount[subDomain] = domainCount.get(subDomain, 0) + 1
        subdomains[domain].add(subDomain)
        # print(domainCount)
        # print(subdomains)
        # print(visited)
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
        print("TypeError for ", parsed)
        raise


"""
if __name__ == "__main__":
    is_valid("https://www.ics.uci.edu/brochure-tiles/how-we-live/")
    print()
"""
