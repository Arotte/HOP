import math

from nltk.corpus import wordnet as wn

from extraction import extract_links_all
from word_selection import select_link, SelectionStrategy
from helpers import *

PHIL_WORD = "philosophy"


def getgeci(word):
    word_synsets = wn.synsets(word)
    phil_synsets = wn.synsets(PHIL_WORD)

    shortest_path_lengths = []
    for word_synset in word_synsets:

        phil_path = 0
        for phil_synset in phil_synsets:
            dist = word_synset.shortest_path_distance(phil_synset)
            if dist is not None:
                phil_path += dist

        shortest_path_lengths.append(phil_path / len(phil_synsets))

    path_len = sum(shortest_path_lengths) / len(shortest_path_lengths)

    return path_len


def main():

    words = [
        "cat",
        "dog",
        "car",
        "concept",
        "philosophy",
        "philosophical",
        "philosophically",
        "philosophies",
        "philosophize",
        "leader",
        "leadership",
    ]

    for word in words:
        print(f"{word}: {getgeci(word)}")


def main2():

    test_link = "https://en.wikipedia.org/wiki/Research"

    links = extract_links_all(test_link)

    print_list_pretty(links)

    link_idx = select_link([link[1] for link in links], SelectionStrategy.WORDNET)

    print(f"Selected link: {links[link_idx]}")


if __name__ == "__main__":
    # main()

    # main2()
    phil_synset = wn.synset("philosophy.n.02")
    print(phil_synset)

    a = wn.synset("creative.a.01")
    aa = wn.synset("creative.s.02")
    d = a.path_similarity(phil_synset)
    d2 = aa.path_similarity(phil_synset)
    print(d)
    print(d2)
    print((d + d2) / 2)

    words = [
        PHIL_WORD,
        "car",
        "dog",
        "cat",
        "programming",
        "computer",
        "science",
        "mathematics",
        "clock",
        "cloaking",
        "time",
        "banana",
        "potato",
        "tasty",
        "delicious",
        "asdasd awdawdw",
        "knowledge",
        "creative",
        "business studies",
    ]

    for word in words:

        word_synsets = wn.synsets(word)
        print(word_synsets)

        sims = []
        sims2 = []
        for word_synset in word_synsets:
            # print(word_synset)
            # print(word_synset.definition())
            # print(word_synset.examples())

            # dist = word_synset.shortest_path_distance(phil_synset)
            # print(dist)
            # sims.append(dist)

            dist2 = word_synset.path_similarity(phil_synset)
            # print(dist2)
            if dist2 is not None:
                sims.append(dist2)

            # check same part of speech
            if word_synset.pos() == phil_synset.pos():
                lch = word_synset.lch_similarity(phil_synset)
                # print(lch)
                if lch is not None:
                    sims2.append(lch)

        try:
            mean_sim = sum(sims) / float(len(sims))
        except ZeroDivisionError:
            mean_sim = 0

        try:
            mean_sim2 = sum(sims2) / float(len(sims2))
        except ZeroDivisionError:
            mean_sim2 = 0

        print(f"{word}: {mean_sim}, {mean_sim2}")
