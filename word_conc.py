# http://crr.ugent.be/archives/1330
# Word	Bigram	Conc.M	Conc.SD	Unknown	Total	Percent_known	SUBTLEX	Dom_Pos
# concreteness rating column: Conc.M

import numpy as np
import pandas as pd
import requests
import csv

from difflib import SequenceMatcher
from helpers import *

tsv_path = "word_concreteness/Concreteness_ratings_Brysbaert_et_al_BRM_processed.txt"

SIMILARITY_THRESHOLD = 0.9

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def init_conc_df(path):
    return pd.read_csv(path, sep="\t")


def get_concreteness(word, df):
    df = df[df["Word"] == word]
    if len(df) == 0:
        return None
    else:
        return df["Conc.M"].values[0]


def get_concreteness_similar(word, df):
    # get most similar to word
    df["Similarity"] = df["Word"].apply(lambda x: similar(x, word))
    df = df.sort_values(by="Similarity", ascending=False)
    return df["Conc.M"].values[0] if df["Similarity"].values[0] > SIMILARITY_THRESHOLD else None


def concreteness(word: str, df: pd.DataFrame) -> float:
    conc = get_concreteness(word, df)
    if conc is None:
        conc = get_concreteness_similar(word, df)
    return conc

def mean_concreteness(words: list, df: pd.DataFrame) -> float:
    concs = []
    for word in words:
        conc = concreteness(word, df)
        if conc is not None:
            concs.append(conc)
    return float(np.mean(concs))


def get_wiki_contents(wiki_url):
    # eg:
    # https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exsentences=10&exlimit=1&titles=Pet_door&explaintext=1&formatversion=2

    wiki_url = reduce_full_url(encode_fix(wiki_url))
    r = requests.get(
        url=WIKIPEDIA_API_BASE_URL,
        params={
            "action": "query",
            "prop": "extracts",
            "exchars": 1200,
            "exlimit": 1,
            "titles": wiki_url,
            "explaintext": 1,
            "formatversion": 2,
            "format": "json",
    })

    if r.status_code == 200:
        txt = r.json()["query"]["pages"][0]["extract"]
        return txt
    else:
        return None

if __name__ == '__main__':
    df = init_conc_df(tsv_path)

    # print(get_concreteness("apple", df))
    # print(get_concreteness("banana", df))
    # print(get_concreteness("chair", df))
    # print(get_concreteness("table", df))

    # print(get_concreteness_similar("appleasds", df))

    from bert_hopper import get_starters_from_csv
    from helpers import url_to_pageid, rm_non_alphanum
    import wikipedia
    import nltk

    # links = list(get_starters_from_csv('hop_stats_final.csv'))
    # links = list(set(links))
    links = [
        # "https://en.wikipedia.org/wiki/Philosophy",
        # "https://en.wikipedia.org/wiki/Religion",
        # "https://en.wikipedia.org/wiki/BMW",
        # "https://en.wikipedia.org/wiki/BMW_i",
        # "https://en.wikipedia.org/wiki/Stagecoach_Group",
        # "https://en.wikipedia.org/wiki/Abstract_and_concrete",
        # "https://en.wikipedia.org/wiki/Metaphysics",
        "https://en.wikipedia.org/wiki/Mind",
    ]

    print(len(links))

    for link in links:
        print(link)

        txt = get_wiki_contents(link)

        if txt is None:
            continue

        max_idx = 150
        if len(txt) > max_idx:
            txt = txt[:max_idx]
        # print(txt)
        # print("=" * 100)

        sent_text = nltk.sent_tokenize(txt)
        txt_tagged = []
        for sentence in sent_text:
            tokenized_text = nltk.word_tokenize(sentence)
            tagged = nltk.pos_tag(tokenized_text)
            txt_tagged.append(tagged)
        # flatten
        txt_tagged = [item for sublist in txt_tagged for item in sublist]
        txt_words = [x[0] for x in txt_tagged]

        txt_words_conc = [concreteness(x, df) for x in txt_words]
        txt_words_conc = [w for w in txt_words_conc if w is not None]
        # get mean concresness
        mean_conc = float(np.mean(txt_words_conc))
        print(mean_conc)

        fname = 'hop_stats_final_conc.csv'
        with open(fname, 'a') as f:
            writer = csv.writer(f)
            writer.writerow([link, mean_conc])
        
    # for link in hop_stat_links:
    #     pid = url_to_pageid(link)
    #     if pid == -1:
    #         continue

    #     try:
    #         page_title = wikipedia.page(pageid=pid).title
    #     except:
    #         continue

    #     page_title_words = []

    #     sent_text = nltk.sent_tokenize(page_title)
    #     for sentence in sent_text:
    #         tokenized_text = nltk.word_tokenize(sentence)
    #         tagged = nltk.pos_tag(tokenized_text)
    #         page_title_words.append(tagged)

    #     # page_title_nn = [word for word in page_title_words[0] if word[1] == 'NN']
    #     # if len(page_title_nn) == 0:
    #     #     continue

    #     wds = [word[0].lower().strip() for word in page_title_words[0]]
    #     avg_conc = mean_concreteness(wds, df)


    #     print(page_title, avg_conc)




