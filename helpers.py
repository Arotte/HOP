""" helpers.py

    Helper functions for the project.
"""
import requests
import re

from config import WIKIPEDIA_BASE_URL, WIKIPEDIA_API_BASE_URL
from urllib.parse import unquote


def check_url(url: str) -> str:
    """Check if url is full or partial"""

    if url.startswith("http"):
        return url
    else:
        return WIKIPEDIA_BASE_URL + url


def reduce_full_url(url: str) -> str:
    """Reduce full url to just the article name"""

    if "/" in url:
        url = url.split("/")[-1]

    return url


def url_to_pageid(wiki_url: str) -> str:
    # example get:
    # https://en.wikipedia.org/w/api.php?action=query&titles=Main%20Page
    # {
    #     "batchcomplete": "",
    #     "query": {
    #         "pages": {
    #             "15580374": {
    #                 "pageid": 15580374,
    #                 "ns": 0,
    #                 "title": "Main Page"
    #             }
    #         }
    #     }
    # }
    
    wiki_url = encode_fix(wiki_url)

    pageid = requests.get(
        WIKIPEDIA_API_BASE_URL,
        params={
            "action": "query",
            "titles": reduce_full_url(wiki_url),
            "format": "json",
        },
    ).json()["query"]["pages"]

    pageid = list(pageid.keys())[0]
    return pageid


def rm_non_alphanum(seq: str) -> str:
    """Remove non-alphanumeric characters from a string"""

    # do not remove whitespace

    return re.sub(r"[^a-zA-Z0-9 ]", "", seq)


def parenthetic_contents(string: str):
    """Generate parenthesized contents in string as pairs (level, contents)"""
    stack = []
    for i, c in enumerate(string):
        if c == "(":
            stack.append(i)
        elif c == ")" and stack:
            start = stack.pop()
            yield (len(stack), string[start + 1 : i])


def print_list_pretty(l: list):
    """Print list in a (semi-)pretty way"""

    for i in range(len(l)):
        print(f"{i+1}: {l[i]}")


def encode_fix(url: str) -> str:
    """Fix encoding of url"""

    # if url includes %, it is encoded
    if "%" in url:
        url = unquote(url)

    return url
