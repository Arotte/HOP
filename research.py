""" research.py

"""

import os
import csv

from word_selection import SelectionStrategy, select_link
from dataset_collection import get_random_pages
from extraction import extract_links_all
from helpers import *
from config import *

# full path of this script
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

EMBEDDING_MODEL = None


def INIT_WORDNET():
    # download wordnet
    import nltk

    print("Downloading WordNet...")

    # check if 'wordnet' is already downloaded
    try:
        nltk.data.find("wordnet")
    except LookupError:
        nltk.download("wordnet")

    # check if 'omw-1.4'' is already downloaded
    try:
        nltk.data.find("omw-1.4")
    except LookupError:
        nltk.download("omw-1.4")

    print("WordNet downloaded.")


def LOAD_WORD2VEC():
    print("\nLoading Word2Vec model into memory...")
    word2vec_path = "./embedding_models/glove-twitter-25.gz"

    import time
    from gensim import models

    start = time.time()
    w2v_model = models.KeyedVectors.load_word2vec_format(word2vec_path)
    end = time.time()

    print(f"Loaded Word2Vec model in {end - start} seconds")

    return w2v_model


def hop2phil(
    from_url: str, selection_strat: SelectionStrategy, debug_print: bool = False
) -> list:
    """Hop from a Wikipedia article to Philosophy.

    Args:
        from_url (str): url of starting article
        selection_strat (SelectionStrategy): selection strategy
        debug_print (bool): print debug information

    Returns:
        path (list): list of urls of articles visited
    """

    path = []
    cycle = False
    N_TH_LINK = 1  # TODO: implement n-th link

    for hop in range(MAX_HOPS):
        # get list of urls of links from starting article
        links = extract_links_all(from_url)
        words = [link[1] for link in links]

        # select link using selection strategy
        if selection_strat == SelectionStrategy.NTH_LINK:
            link_index = N_TH_LINK
        else:
            link_index = select_link(words, selection_strat, EMBEDDING_MODEL)

        # # try to avoid cycles
        # # if cycle detected, select SECOND most relevant word
        # if links[link_index][0] in path:
        #     print(f"\tCycle detected, trying to avoid it...")
        #     # remove word from list of words,
        #     # and try to select a new one
        #     idx = words.index(links[link_index][1])
        #     words = words[:idx] + ["xxx"] + words[idx + 1 :]

        #     if selection_strat == SelectionStrategy.NTH_LINK:
        #         link_index = N_TH_LINK + 1
        #     else:
        #         link_index = select_link(words, selection_strat)

        # get url of selected link
        selected_word = links[link_index][1]
        link_url = links[link_index][0]

        # add url to path
        path.append(link_url)

        if debug_print:
            print(f"\t{hop+1}: {link_url} ({selected_word})")

        # detect cycle
        if link_url in path[:-1] and not selection_strat == SelectionStrategy.RANDOM:
            if debug_print:
                print(f"\tCycle detected, terminating...")
            cycle = True
            break

        # check if url is philosophy
        if link_url == WIKI_URL_OF_PHILOSOPHY:
            if debug_print:
                print(f"\tReached philosophy, terminating...")
            break

        # set url of next hop
        from_url = check_url(link_url)

    if not cycle:
        return path
    else:
        return None


def read_starters():
    # read list of starter articles from starter_articles.csv
    starters = []  # (article_name, article_url)
    with open(os.path.join(SCRIPT_PATH, "starter_articles.csv"), "r") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:  # skip empty rows
            if row:
                starters.append((row[0], row[1]))

    return starters


def get_random_starters():
    return get_random_pages(20)


def main():
    TERM_TXT = "Terminating condition reached, skipping..."
    PRINT_PATH = False

    starters = get_random_starters()

    for starter in starters:
        print(f"\nHopping from '{starter[0]}'...")

        ### WORDNET ###
        print("Word selection: WORDNET")
        path_wordnet = hop2phil(
            starter[1], SelectionStrategy.WORDNET, debug_print=PRINT_PATH
        )

        if path_wordnet is None:
            # print(TERM_TXT)
            # continue
            path_wordnet = []

        ### EMBEDDING: WORD2VEC ###
        print("Word selection: WORD2VEC")
        path_word2vec = hop2phil(
            starter[1], SelectionStrategy.EMBEDDING_WORD2VEC, debug_print=PRINT_PATH
        )

        if path_word2vec is None:
            # print(TERM_TXT)
            # continue
            path_word2vec = []

        ### FIRST LINK ###
        # print("Word selection: FIRST LINK")
        # path_nthlink = hop2phil(
        #     starter[1], SelectionStrategy.NTH_LINK, debug_print=PRINT_PATH
        # )

        ### SECOND LINK ###
        print("Word selection: SECOND LINK")
        path_nthlink = hop2phil(
            starter[1], SelectionStrategy.NTH_LINK, debug_print=PRINT_PATH
        )

        if path_nthlink is None:
            # print(TERM_TXT)
            # continue
            path_nthlink = []

        ### RANDOM ###
        # print("Word selection: RANDOM")
        # path_random = hop2phil(
        #     starter[1], SelectionStrategy.RANDOM, debug_print=PRINT_PATH
        # )

        # if path_random is None:
        #     # print(TERM_TXT)
        #     # continue
        #     path_random = []

        # ---------------------------------------------------------------
        ### STATISTICS ###

        hoplen_wordnet = len(path_wordnet)
        hoplen_nthlink = len(path_nthlink)
        hoplen_word2vec = len(path_word2vec)
        # hoplen_random = len(path_random)

        print(f"WordNet: {hoplen_wordnet} hops")
        print(f"Embedding word2vec: {hoplen_word2vec} hops")
        # print(f"First link: {hoplen_nthlink} hops")
        print(f"Second link: {hoplen_nthlink} hops")
        # print(f"Random: {hoplen_random} hops")

        # record statistics to csv file
        # append to 'hop_stats.csv'
        # csv structure: start_article_title,starter_article_url,selection_strat,hops_to_phil
        HOP_STATS_FILE = "hop_stats_all_vocab.csv"
        with open(os.path.join(SCRIPT_PATH, HOP_STATS_FILE), "a", encoding="utf-8") as f:
            writer = csv.writer(f)

            writer.writerow(
                [starter[0], starter[1], "WORDNET", hoplen_wordnet]
            ) if hoplen_wordnet != 0 else None
            # writer.writerow(
            #     [starter[0], starter[1], "NTH_LINK(1)", hoplen_nthlink]
            # ) if hoplen_nthlink != 0 else None
            writer.writerow(
                [starter[0], starter[1], "NTH_LINK(2)", hoplen_nthlink]
            ) if hoplen_nthlink != 0 else None
            writer.writerow(
                [starter[0], starter[1], "EMBEDDING_WORD2VEC", hoplen_word2vec]
            ) if hoplen_word2vec != 0 else None
            # writer.writerow(
            #     [starter[0], starter[1], "RANDOM", hoplen_random]
            # ) if hoplen_random != 0 else None

            print("Statistics recorded.")


if __name__ == "__main__":
    print(f"Running {__file__}...")

    # NOTE: this takes a while to load (~30 seconds)
    EMBEDDING_MODEL = LOAD_WORD2VEC()

    # INIT_WORDNET()

    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("KeyboardInterrupt, terminating...")
            break
        except Exception as e:
            print(f"Exception: {e}")
            continue

    # =================================================================
    # embedding hopping

    # starters = read_starters()
    # for starter in starters:
    #     print(f"\nHopping from '{starter[0]}'...")

    #     print("Word selection: WORD2VEC")
    #     path_word2vec = hop2phil(
    #         starter[1], SelectionStrategy.EMBEDDING_WORD2VEC, debug_print=True
    #     )

    #     if path_word2vec is None:
    #         print("Suboptimal terminting condition reached, skipping...")
    #         continue

    #     hoplen_word2vec = len(path_word2vec)

    #     print(f"Word2Vec: {hoplen_word2vec} hops")
