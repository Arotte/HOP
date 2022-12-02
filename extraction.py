""" extraction.py

    Contains the function `extract_links_all` which
    extracts all links from a Wikipedia article.

    Return a list of tuples (link, link_text).

    Running this file will print the links extracted
    from the article "Python (programming language)".

    Tested with Python 3.10.7
    Author: Aron Molnar (gh/Arotte)
    Last modified: 2021-11-08
"""

import requests
from bs4 import BeautifulSoup

from helpers import parenthetic_contents


def extract_links_all(page_url: str) -> list:
    """
    Extract first N links from the description of a Wikipedia article
    page_url: url of the Wikipedia article
    i: the i-th link to extract
    """

    ### retrieve page html

    data = requests.get(page_url).text

    # check data
    if data is None:
        print(f"Extraction failed: no data (url: {page_url})")
        return (None, None, None)

    soup = BeautifulSoup(data, "html.parser")

    ### clean up the html

    # remove thumbnails
    for div in soup.find_all("div", {"class": "thumb"}):
        div.decompose()
    # remove sidebars
    for div in soup.find_all("table", {"class": "sidebar"}):
        div.decompose()
    # remove all tables
    for table in soup.find_all("table"):
        table.decompose()
    # remove notes at the top (class: hatnote)
    for div in soup.find_all("div", {"class": "hatnote"}):
        div.decompose()

    ### find paragraphs in html

    # find containers with classes specific classes
    containers = soup.find_all(
        "div", {"class": ["mw-parser-output", "mw-body-content", "vector-body"]}
    )

    if containers is None:
        print(f"Extraction failed: no containers")
        return (None, None, None)

    # list of paragraphs inside containers
    ps = []

    for container in containers:
        ps += container.find_all("p")

    links = []

    ### extract links from paragraphs

    # look in first x paragraphs
    max_paras = 3
    x = max_paras if len(ps) > max_paras else len(ps)

    for paragraph_n in range(0, x):
        # get contents of parentheses
        nested_paren_contents = list(parenthetic_contents(str(ps[paragraph_n])))
        strs_in_paren = [
            s[1] for s in nested_paren_contents
        ]  # get second element of each tuple (level, contents)

        # for all anchor tags inside the current paragraph
        for a in ps[paragraph_n].find_all("a"):
            if a.has_attr("href") and a["href"].startswith("/wiki/"):

                # check if the anchor tag is inside parentheses
                in_paren = False
                for para in strs_in_paren:
                    if str(a) in para:
                        in_paren = True
                        break

                if not in_paren:
                    links.append(a)

    ### if no links found, try a different strategy

    if len(links) == 0:
        # try another link searching strategy:
        # look for anchor tags that have an href attribute
        # starting with 'wiki/' and are not inside parentheses
        for a in soup.find_all("a"):
            if a.has_attr("href") and a["href"].startswith("/wiki/"):
                links.append(a)

        # check for parentheses
        nested_paren_contents = list(parenthetic_contents(str(soup)))
        strs_in_paren = [s[1] for s in nested_paren_contents]

        for a in links:
            in_para = False
            for para in strs_in_paren:
                if str(a) in para:
                    in_para = True
                    break

            if in_para:
                links.remove(a)

    ### little post-processing and cleanup
    ret = [(a["href"], a.text.strip()) for a in links]
    for l in ret:

        # remove links that are not links to articles
        if "wikipedia:" in l[0].lower(): # and "how?" in l[1].lower()
            ret.remove(l)

    ### done, return (link, link_text) tuples

    return ret


# ==============================================================
# Tests
# ==============================================================

if __name__ == "__main__":
    from helpers import print_list_pretty

    test_url = "https://en.wikipedia.org/wiki/Python_(programming_language)"

    print("Testing extraction.py")
    print("Extracting links from", test_url)

    links = extract_links_all(test_url)
    print_list_pretty(links)

    print("Done testing extraction.py")
