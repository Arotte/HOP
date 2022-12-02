"""
    gather_words.py

    
"""


import requests
import json
import os
import time
import tqdm
import random
import sys
import re
from bs4 import BeautifulSoup


PAGES_JSON_PATH = "./pages.json"
WIKI_API_URL = "https://en.wikipedia.org/w/api.php"
PHIL_URL = "/wiki/Philosophy"


class PagesJson:
    def __init__(self):
        # create file if it doesn't exist

        if not os.path.exists(PAGES_JSON_PATH):
            with open(PAGES_JSON_PATH, "w") as f:
                f.write("{}")

        self.data = {}

    def load(self):
        with open(PAGES_JSON_PATH, "r") as f:
            self.data = json.load(f)

            # remove objects that have an ithlink parameter starting with '#'
            n_removed = 0
            for pageid in list(self.data.keys()):
                if self.data[pageid]["ithlink"].startswith("#"):
                    del self.data[pageid]
                    n_removed += 1

            if n_removed > 0:
                self.save()
                print(f"Removed {n_removed} pages with internal links from JSON file")

    def save(self):
        with open(PAGES_JSON_PATH, "w") as f:
            json.dump(self.data, f)

    def add(self, pageid, title, ithlink, i, fullurl):
        if pageid in self.data:
            return False

        self.data[pageid] = {
            "pageid": pageid,
            "title": title,
            "ithlink": ithlink,
            "i": i,
            "fullurl": fullurl,
            "titleurl": fullurl.split("/")[-1],
        }

        return True

    def get(self, pageid):
        return self.data[pageid]

    def get_all(self):
        return self.data

    def count(self):
        return len(self.data)

    def get_random(self):
        return random.choice(list(self.data.values()))


def extract_link(page_url, i):
    """
    Extract i-th link from the description of a Wikipedia article

    page_url: url of the Wikipedia article
    i: the i-th link to extract
    """

    # get page content with Wikipedia API
    title_url = page_url.split("/")[-1]

    PARAMS = {
        "action": "parse",
        "page": title_url,
        "prop": "text",
        "format": "json",
    }

    r = requests.get(url=WIKI_API_URL, params=PARAMS)
    data = r.json()["parse"]["text"]["*"]

    soup = BeautifulSoup(data, "html.parser")

    ### clean up the html

    for div in soup.find_all("div", {"class": "thumb"}):
        div.decompose()
    for div in soup.find_all("table", {"class": "sidebar"}):
        div.decompose()

    ####

    ps = soup.find("div", {"class": "mw-parser-output"}).find_all("p")

    links = []
    ps_clean = []

    for p in ps:
        if p.get("class") is not None:
            continue
        ps_clean.append(p)

    for paragraph_n in range(0, 3):
        # get contents of parenthese with regex
        strs_in_para = re.findall("\((.*?)\)", str(ps_clean[paragraph_n]))

        for a in ps_clean[paragraph_n].find_all("a"):
            if a.has_attr("href") and a["href"].startswith("/wiki/"):
                in_para = False
                for para in strs_in_para:
                    if str(a) in para:
                        in_para = True
                        break

                if not in_para:
                    links.append(a)

        if len(links) > 0:
            break

    # print(links)

    if len(links) < i:
        return (None, None, None)

    link = links[i - 1]

    return (link["href"], link.text, link["title"])


def get_rand_pages(n, i):
    print(f"\nGetting {n} random Wikipedia pages with the {i}-th link")

    n_pages_added = 0
    start_time = time.time()

    if n < 1 or n > 500:  # how many random pages to get
        raise ValueError("n must be between 1 and 500")

    if i < 1 or i > 300:  # get i-th link of each page
        raise ValueError("i must be between 1 and 300")

    S = requests.Session()

    # get n random pages

    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "random",
        "rnlimit": str(n),
        "rnnamespace": "0",
    }

    R = S.get(url=WIKI_API_URL, params=PARAMS)
    DATA = R.json()
    RANDOMS = DATA["query"]["random"]

    pages_json = PagesJson()
    pages_json.load()

    for r in tqdm.tqdm(RANDOMS):
        page_title = r["title"]
        page_id = r["id"]

        # get full url of each page

        PARAMS = {
            "action": "query",
            "format": "json",
            "prop": "info",
            "inprop": "url",
            "pageids": page_id,
        }

        R = S.get(url=WIKI_API_URL, params=PARAMS)
        DATA = R.json()

        page_url = DATA["query"]["pages"][str(page_id)]["fullurl"]
        page_lang = DATA["query"]["pages"][str(page_id)]["pagelanguage"]

        if page_lang != "en":
            continue

        # get i-th link of each page which is not inside a () or []

        try:
            (page_ithlink, _, _) = extract_link(page_url, i)
        except:
            continue

        if page_ithlink is None:
            continue

        # save page to the json file

        if not pages_json.add(page_id, page_title, page_ithlink, i, page_url):
            continue

        n_pages_added += 1

    pages_json.save()

    print(
        "{} entry pages added to JSON in {:.3f} seconds\n{} entry pages in total\n".format(
            n_pages_added,
            time.time() - start_time,
            pages_json.count(),
        )
    )


# =============================================================================
# =============================================================================


def traverse_RECURSIVE(url, i):
    (link, word, linkword) = extract_link(url, i)

    if link is None:
        return

    print(f"{word} ({linkword}) -> {link}")

    if link == PHIL_URL:
        print("Found it!")
        return

    link = "https://en.wikipedia.org" + link
    traverse_RECURSIVE(link, i)


# =============================================================================
# =============================================================================


def main():
    myjson = PagesJson()
    myjson.load()

    # get_rand_pages(2, 1)

    # starting_url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    # starting_url = "https://en.wikipedia.org/wiki/Automation"
    # starting_url = "https://en.wikipedia.org/wiki/High-level_programming_language"
    # starting_url = "https://en.wikipedia.org/wiki/Mathematics"

    starting_url = myjson.get_random()["fullurl"]
    # starting_url = "https://en.wikipedia.org/wiki/Super_V-2"
    i = 1
    print(f"\nTraversing Wikipedia from {starting_url} with the {i}-th link\n")
    traverse_RECURSIVE(starting_url, 1)

    # print(
    #     extract_link("https://en.wikipedia.org/wiki/Python_(programming_language)", 1)
    #   )

    # geci = "https://en.wikipedia.org/wiki/Automation"
    # geci = "https://en.wikipedia.org/wiki/High-level_programming_language"
    # geci = "https://en.wikipedia.org/wiki/Arithmetic"
    # geci = "https://en.wikipedia.org/wiki/Mathematics"
    # asd = extract_link(geci, 1)
    # print(asd)


if __name__ == "__main__":
    try:
        main()

    except:
        print("Malformed HTML")
        sys.exit(1)
