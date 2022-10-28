import re
from urllib.parse import urlparse
from nltk import download
from nltk.corpus import stopwords
from urllib.request import urlopen
from collections import defaultdict

from bs4 import BeautifulSoup

f = open("out.txt", "w")
download('stopwords')

cache = set()
stops = set(stopwords.words('english'))

hashWords = defaultdict(int)

def scraper(url, resp):
    links = extract_next_links(url, resp)

    ret = []

    for link in links:
        if is_valid(link):
            ret.append(link)
            # adding to cache
            cache.add(link)

    for url in ret:
        f.write(url + "\n")
    return ret


#Analysis questions #3
def mostCommon():
    return sorted(hashWords, key = lambda x: hashWords[x])


#Analysis questions #2
def longestPage():
    max1 = 0
    maxPage = ""
    for page in cache:
        f = urlopen(page)
        f = f.read().decode('utf-8')

        lineTokens = []

        #tokenizing words
        for line in f:
            line = re.sub('<[^<]+?>', '', line)
            line = re.split('[^a-zA-Z0-9]+', line)
            for v in line:
                lineTokens.append(v)

        lineTokens = [val for val in lineTokens if val != ""]

        for val in lineTokens:
            if val not in stops:
                hashWords[val] += 1
        if(len(lineTokens) > max1):
            max1 = len(lineTokens)
            maxPage = page
    return maxPage

        
#Analysis questions #1
def uniquePages():
    return len(cache)


def extract_next_links(url, resp):
    ret = []
    if resp.error is not None:
        print(resp.error)
        return list()

    if resp.raw_response is None:
        return list()

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    for link in soup.find_all('a'):
        url_link = link.get('href')
        if url_link is not None and is_valid(url_link):
            index = url_link.find("#")
            if index != -1:
                ret.append(url_link[0:index])
            else:
                ret.append(url_link)
        
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    return ret


def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if (parsed.scheme not in set(["http", "https"])) or url in cache:
            return False

        domain = parsed.netloc

        if domain.startswith('www.'):
            domain = domain[4:]

        if(domain not in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"])):
            return False

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
