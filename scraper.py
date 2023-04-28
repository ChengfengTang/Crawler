import re
from urllib.parse import urljoin, urlparse, urldefrag

from bs4 import BeautifulSoup
from collections import defaultdict

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
    #print(len(visited)) The total number of pages 
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
    print(links)
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
            print("no domain found " + subDomain)
        print("d: " + domain)
        print("sd: " + subDomain)
        # Ex.
        # domain: ics.uci.edu
        # subdomain: vision.ics.edu

        # If not a subdomain
        if subDomain in set(["ics.uci.edu","cs.uci.edu","informatics.uci.edu", "stat.uci.edu"]):
            domain = subDomain
        if domain not in set(["ics.uci.edu","cs.uci.edu","informatics.uci.edu", "stat.uci.edu"]):
            return False
        domainCount[subDomain] = domainCount.get(subDomain,0) + 1
        subdomains[domain].add(subDomain)
        print(domainCount)
        print(subdomains)

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