import tqdm
import requests

from config import WIKIPEDIA_API_BASE_URL, MAX_LINK_EXTRACT

from helpers import *

# =============================================================================
# GET RANDOM WIKI ARTICLES
# =============================================================================


def get_random_pages(n: int) -> list:
    print(f"\nGetting {n} random Wikipedia pages...")

    ### checks

    if n < 1 or n > 500:  # how many random pages to get
        raise ValueError("n must be between 1 and 500")

    ### get random pages via Wikipedia API

    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "random",
        "rnlimit": str(n),
        "rnnamespace": "0",
    }
    S = requests.Session()
    R = S.get(url=WIKIPEDIA_API_BASE_URL, params=PARAMS)
    DATA = R.json()
    RANDOMS = DATA["query"]["random"]

    ### extract info from the pages

    print(f"Extracting data from {n} random Wikipedia pages")

    PAGES = []
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

        S = requests.Session()
        R = S.get(url=WIKIPEDIA_API_BASE_URL, params=PARAMS)
        DATA = R.json()

        page_url = DATA["query"]["pages"][str(page_id)]["fullurl"]
        page_title_from_url = page_url.split("/")[-1]
        page_lang = DATA["query"]["pages"][str(page_id)]["pagelanguage"]

        if page_lang != "en":
            continue

        if page_url is None:
            continue

        PAGES.append((page_title, page_url))

    ### done

    return PAGES


def json2csv():
    import json
    import csv

    jsonfname = "../pages.json"
    csvfname = "./starter_articles.csv"

    with open(jsonfname, "r") as f:
        data = json.load(f)

    with open(csvfname, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["article_name", "article_url"])
        # iterate keys of data
        for key in data.keys():
            # writer.writerow([f'"{data[key]["title"]}"', f'"{data[key]["fullurl"]}"'])
            writer.writerow([data[key]["title"], data[key]["fullurl"]])

    print(f"Done. Wrote {len(data)} rows to {csvfname}")


def populate_csv_rng():
    """Append to the starter_articles.csv file
    with random articles from Wikipedia
    """

    import csv

    csvfname = "./starter_articles.csv"

    # get random pages
    pages = get_random_pages(100)

    # append to csv
    with open(csvfname, "a", encoding="utf-8") as f:
        writer = csv.writer(f)
        for page in pages:
            writer.writerow([page[0], page[1]])

    print(f"Done. Appended {len(pages)} rows to {csvfname}")


def clean_csv():
    """Remove duplicates from starter_articles.csv"""

    import csv

    csvfname = "./starter_articles.csv"

    # read csv
    with open(csvfname, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        data = list(reader)

    # remove empty entries
    data = [x for x in data if x != []]

    # remove duplicates
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if data[i] == data[j]:
                data[j] = []

    # remove empty entries
    data = [x for x in data if x != []]

    # write csv
    with open(csvfname, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)

    print(f"Done. Removed duplicates from {csvfname}")


# =============================================================================
# =============================================================================

if __name__ == "__main__":

    # populate_csv_rng()
    clean_csv()
