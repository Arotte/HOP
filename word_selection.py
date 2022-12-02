""" word_selection.py

    A selection strategy determines which link
    to follow from a given page.

    The research defines three strategies:
        1. Random link: select a link at random
        2. WordNet selection: select word which has the shortest
           concept relationship path to the word 'philosophy' in WordNet.
        3. Embedding selection: select the word which has the smallest
           cosine distance to the word 'philosophy' in the embedding space.

    This module implements the three strategies.

    ...

    Tested with Python 3.10.7
    Author: Aron Molnar (gh/Arotte)
    Last modified: 2021-11-08
"""

import random
import enum
import math
import time
from gensim import models
from nltk.corpus import wordnet as wn

from helpers import print_list_pretty
from config import (
    N,
    PHIL_WORD,
)


class SelectionStrategy(enum.Enum):
    """Enumeration of the selection strategies."""

    RANDOM = 1
    NTH_LINK = 2
    WORDNET = 3
    EMBEDDING_WORD2VEC = 4
    EMBEDDING_BERT = 5


def select_link(words: list, strategy: SelectionStrategy, wv_model=None) -> str:
    """Select a link from a list of words.

    Args:
        words (list): list of words
        strategy (SelectionStrategy): selection strategy

    Returns:
        link_index (int): index of selected link in list
    """

    if strategy == SelectionStrategy.RANDOM:
        return select_link_random(words)

    elif strategy == SelectionStrategy.WORDNET:
        return select_link_wordnet(words)

    elif strategy == SelectionStrategy.EMBEDDING_WORD2VEC:
        return select_link_embedding_word2vec(words, wv_model)

    elif strategy == SelectionStrategy.EMBEDDING_BERT:
        return select_link_embedding_bert(words)

    else:
        raise ValueError("Unknown selection strategy")


# =========================================================================
# Random selection
# =========================================================================


def select_link_random(words: list) -> int:
    word_index = random.randint(0, len(words) - 1)
    return word_index


# =========================================================================
# WordNet selection
# =========================================================================


def select_link_wordnet(words: list) -> int:

    # get shortest path length between each link and philosophy
    shortest_path_lengths = []

    # handle multiple words
    # n_link_mulitple_words = sum([1 for word in words if " " in word])
    # if len(words) == n_link_mulitple_words:
    #     # all links are multiple words

    #     for word in words:
    #         shortest_path_lengths.append(get_shortest_path_length_multiple_words(word))

    # else:
    #     # some links are single words

    #     for word in [w for w in words if " " not in w]:
    #         shortest_path_lengths.append(get_shortest_path_length(word))

    for word in words:
        shortest_path_lengths.append(phil_similarity(word))

    # print words and their scores
    # print_list_pretty(
    #     [f"{word}: {score}" for word, score in zip(words, shortest_path_lengths)]
    # )

    # get index of shortest path length
    # TODO: if multiple???
    word_index = shortest_path_lengths.index(max(shortest_path_lengths))

    return word_index


def phil_similarity(word: str) -> int:
    """Get the shortest path length between a word and philosophy.

    Args:
        word (str): word to compare

    Returns:
        shortest_path_length (int): shortest path length
    """

    if " " in word:
        return phil_similarity_multiple_words(word)

    word_synsets = wn.synsets(word)
    phil_synset = wn.synset("philosophy.n.02")

    shortest_path_lengths = []
    for word_synset in word_synsets:

        # phil_path = 0

        # for phil_synset in phil_synsets:
        #     dist = word_synset.shortest_path_distance(phil_synset)
        #     if dist is not None:
        #         phil_path += dist

        # shortest_path_lengths.append(phil_path / len(phil_synsets))

        dist = word_synset.path_similarity(phil_synset)

        if dist is not None:
            shortest_path_lengths.append(dist)

    try:
        path_len = sum(shortest_path_lengths) / len(shortest_path_lengths)
    except ZeroDivisionError:
        path_len = 0.0

    return path_len


def phil_similarity_multiple_words(word: str) -> int:

    # split words into list
    words = word.lower().strip().split(" ")

    # get shortest path length between each word and philosophy
    shortest_path_lengths = []
    for word in words:
        sp = phil_similarity(word)

        if sp is not None:
            shortest_path_lengths.append(sp)

    # mean of shortest path lengths
    try:
        path_len = sum(shortest_path_lengths) / len(shortest_path_lengths)
    except ZeroDivisionError:
        return 0.0

    return path_len


# =========================================================================
# Embedding selection: word2vec
# =========================================================================


def select_link_embedding_word2vec(words: list, wv_model) -> int:
    """Select a link from a list of words using word2vec.

    Args:
        words (list): list of words

    Returns:
        link_index (int): index of selected link in list
    """

    dists = []

    for word in words:
        word = word.lower().strip()

        # if word is actually multiple words,
        # split into list and get mean vector

        if " " in word:
            word_words = word.lower().strip().split(" ")
            dist_word_word = 0.0
            for word_word in word_words:
                try:
                    dist_word_word += wv_model.similarity(word_word, PHIL_WORD)
                except KeyError:
                    # word not in vocabulary
                    pass
            dist_word_word /= len(word_words)
            dists.append(dist_word_word)
            continue

        try:
            dist = wv_model.similarity(PHIL_WORD, word)
        except KeyError:
            # word not in vocabulary
            dist = 0.0

        dists.append(dist)

    # print words and their scores
    # print_list_pretty([f"{word}: {score}" for word, score in zip(words, dists)])

    # get index of highest cos dist
    return dists.index(max(dists))


# =========================================================================
# Embedding selection: BERT
# =========================================================================


def select_link_embedding_bert(words: list) -> int:
    pass


# =========================================================================
# TESTS
# =========================================================================

if __name__ == "__main__":
    from helpers import print_list_pretty

    print("Testing word_selection.py")

    # test words

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

    print("\nWords:")
    print_list_pretty(words)

    # test random selection
    # word_rand = select_link(words, SelectionStrategy.RANDOM)
    # print(f"\nRandom selection: {words[word_rand]}")

    # test wordnet selection
    # word_wordnet = select_link(words, SelectionStrategy.WORDNET)
    # print(f"\nWordNet selection: {words[word_wordnet]}")

    # test embedding selection
    print("\nTesting embedding selection")
    # load pre-trained Word2Vec model
    word2vec_path = "./embedding_models/glove-twitter-25.gz"
    start = time.time()
    w2v_model = models.KeyedVectors.load_word2vec_format(word2vec_path)
    end = time.time()
    print(f"Loaded Word2Vec model in {end - start} seconds")

    word_embedding = select_link_embedding_word2vec(words, w2v_model)
    print(f"\nEmbedding selection: {words[word_embedding]}")
