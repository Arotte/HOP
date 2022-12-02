import requests
import wikipedia # wrapper around the Wikipedia API
import nltk
import os
import csv

from helpers import *
from config import *
from extraction import extract_links_all
from dataset_collection import get_random_pages

import csv

# ==================================================================================
# CONSTANTS
# ==================================================================================

url = 'http://localhost:5000'
url_embed = url + '/embed'
url_sim = url + '/similarity'

N_LINKS = 20

# ==================================================================================
# EXTRACT
# ==================================================================================

def txt_of(page_name: str) -> str:
    pn = reduce_full_url(encode_fix(page_name))
    content = None
    try: 
        content = wikipedia.page(title=pn).content
    except:
        content = wikipedia.page(pageid=url_to_pageid(pn)).content
    return content


def postprocess_wiki_content(content: str) -> str:
    sentences = nltk.sent_tokenize(content) # this gives us a list of sentences
    return "\n".join(sentences)

# ==================================================================================
# SIMILARITY
# ==================================================================================


def most_similar_to_phil(words: list, text: str) -> dict:
    try:
        max_tries = 3
        ret = None

        for _ in range(max_tries):
            r = requests.post(url_sim, json={'text': text, 'words': words})
            ret = r.json()

            if ret is not None:
                break
            else:
                continue
            
        return ret

    except Exception as e:
        print("ERROR: Couldn't reach BERT server. Make sure it's running.")
        print(e)
        return None


# ==================================================================================
# HOPPER
# ==================================================================================


def bert_hopper(start_url: str, verbose: int = 2) -> list:
    """Hop from a Wikipedia article to Philosophy.

    Args:
        start_url (str): url of starting article
        verbose (int): print debug information (0: no, 1: some, 2: all)

    Returns:
        path (list): list of urls of articles visited
    """
    if verbose >= 1:
        print(f"BERT hopping from {start_url}")

    path = []
    cycle = False
    other_err = False
    cycle_eliminated = False

    current_url = start_url
    for hop in range(MAX_HOPS):
        # get list of urls of links from starting article
        links = extract_links_all(current_url)[:N_LINKS]
        words = [link[1].lower().strip() for link in links]

        # get wiki article text (for BERT)
        article_txt = txt_of(current_url)
        if article_txt is None:
            print(f"ERROR: Couldn't extract text from {current_url}")
            break
        last_word = words[-1]
        last_occurrence = article_txt.rfind(last_word) # last occurrence of last_word in article
        article_txt = article_txt[:last_occurrence]
        article_txt = postprocess_wiki_content(article_txt)

        # get most similar word to "Philosophy"
        sim = most_similar_to_phil(words, article_txt)
        
        # if all sim scores are None, error
        if sim['winner'][0] == '' and sim['winner'][1] == 0.0:
            print(f"ERROR: Couldn't find a similar word to 'Philosophy' in {current_url}")
            other_err = True
            break
        
        most_similar = sim['winner']
        most_similar_index = words.index(most_similar[0].lower().strip())

        # get url of selected link
        link_url = links[most_similar_index][0]

        # add url to path
        path.append(link_url)

        if verbose >= 2:
            print(f"\t{hop+1}: {link_url} ({most_similar[0]}, {most_similar[1]:.2f})")

        # try to avoid cycles
        # if cycle is detected, remove last link from path
        # and remove the word corresponding to that link
        if link_url in path[:-1]:
            path = path[:-1]
            words.pop(most_similar_index)
            links.pop(most_similar_index)
            new_most_similar = most_similar_to_phil(words, article_txt)
            new_most_similar_index = words.index(new_most_similar['winner'][0].lower().strip())
            new_link_url = links[new_most_similar_index][0]
            path.append(new_link_url)
            cycle_eliminated = True
            if verbose >= 2:
                print(f"\tCycle detected. Replacing {link_url} with {new_link_url}.")
            link_url = new_link_url

        # detect cycle
        if link_url in path[:-1] and cycle_eliminated:
            if verbose >= 1:
                print(f"\tCycle detected, terminating...")
            cycle = True
            break

        # check if url is philosophy
        if link_url == WIKI_URL_OF_PHILOSOPHY:
            if verbose >= 1:
                print(f"\tReached philosophy, terminating...")
            break

        # set url of next hop
        current_url = check_url(link_url)

    if not cycle and not other_err:
        return path
    else:
        return None    

# ==================================================================================
# TESTS
# ==================================================================================


def test_wiki_textract():

    test_articles = [
        'Pet_door',
        'Philosophy',
        'Philosophy_of_science',
        'Wikipedia'
    ]

    # print(extract_text("Wikipedia"))

def test_bert_server():
    import time
    import re

    # ==================================================================================
    # Prepare test data

    test_text = """
    Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation.[33]

    Python is dynamically-typed and garbage-collected. It supports multiple programming paradigms, including structured (particularly procedural), object-oriented and functional programming. It is often described as a "batteries included" language due to its comprehensive standard library.[34][35]

    Guido van Rossum began working on Python in the late 1980s as a successor to the ABC programming language and first released it in 1991 as Python 0.9.0.[36] Python 2.0 was released in 2000 and introduced new features such as list comprehensions, cycle-detecting garbage collection, reference counting, and Unicode support. Python 3.0, released in 2008, was a major revision that is not completely backward-compatible with earlier versions. Python 2 was discontinued with version 2.7.18 in 2020.[37]

    Python consistently ranks as one of the most popular programming languages.[38][39][40][41]

    Python was conceived in the late 1980s[42] by Guido van Rossum at Centrum Wiskunde & Informatica (CWI) in the Netherlands as a successor to the ABC programming language, which was inspired by SETL,[43] capable of exception handling (from the start plus new capabilities in Python 3.11) and interfacing with the Amoeba operating system.[13] Its implementation began in December 1989.[44] Van Rossum shouldered sole responsibility for the project, as the lead developer, until 12 July 2018, when he announced his "permanent vacation" from his responsibilities as Python's "benevolent dictator for life", a title the Python community bestowed upon him to reflect his long-term commitment as the project's chief decision-maker.[45] In January 2019, active Python core developers elected a five-member Steering Council to lead the project.[46][47]

    Python 2.0 was released on 16 October 2000, with many major new features.[48] Python 3.0, released on 3 December 2008, with many of its major features backported to Python 2.6.x[49] and 2.7.x. Releases of Python 3 include the 2to3 utility, which automates the translation of Python 2 code to Python 3.[50]

    Python 2.7's end-of-life was initially set for 2015, then postponed to 2020 out of concern that a large body of existing code could not easily be forward-ported to Python 3.[51][52] No further security patches or other improvements will be released for it.[53][54] Currently only 3.7 and later are supported. In 2021, Python 3.9.2 and 3.8.8 were expedited[55] as all versions of Python (including 2.7[56]) had security issues leading to possible remote code execution[57] and web cache poisoning.[58]

    In 2022, Python 3.10.4 and 3.9.12 were expedited[59] and 3.8.13, and 3.7.13, because of many security issues.[60] When Python 3.9.13 was released in May 2022, it was announced that the 3.9 series (joining the older series 3.8 and 3.7) will only receive security fixes going forward.[61] On September 7, 2022, four new releases were made due to a potential denial-of-service attack: 3.10.7, 3.9.14, 3.8.14, and 3.7.14.[62][63]

    As of November 2022, Python 3.11.0 is the current stable release and among the notable changes from 3.10 are that it is 10–60% faster and significantly improved error reporting.[64]

    Python 3.12 (alpha 2) has improved error messages.

    The deprecated smtpd module has been removed from Python 3.12 (alpha). And a number of other old, broken and deprecated functions (e.g. from unittest module), classes and methods have been removed. The deprecated wstr and wstr_ length members of the C implementation of Unicode objects were removed,[65] to make UTF-8 the default in later Python versions.

    Historically, Python 3 also made changes from Python 2, e.g. changed the division operator.
    """

    # remove references of the form [1], [2], etc.
    test_text = re.sub(r'\[\d+\]', '', test_text)

    test_words = [
        'stable',
        'release',
        'among',
        'notable',
        'divison',
        'operator',
        'changes',
        'python',
        'language',
        'dynamically-typed',
        'garbage-collected',
        'supports',
        'multiple',
        'programming',
        'historically',
        'paradigms',
        'including',
        'division',
        'code readability',
        'end-of-life',
    ]

    test_words = [word.lower().strip() for word in test_words]

    # ==================================================================================
    # Test

    start = time.time()
    ret = most_similar_to_phil(test_words, test_text)
    end = time.time()

    if ret is not None:
        for sim in zip(test_words, ret["similarities"]):
            print(sim)
        print()

        most_similar_word = ret["winner"]
        print(f"Most similar to 'philosophy' is '{most_similar_word[0]}', {most_similar_word[1]:.2f}")
        print(f"{end - start:.2f} seconds")

def get_starters_from_csv(filename):
    import csv
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # discard header
        next(reader)
        # discard empty rows
        for row in reader:
            if row:
                yield row[1]

def record(path_: list) -> None:
    HOP_STATS_FILE = "hop_stats_all_vocab.csv"
    len_path = len(path_)
    with open(HOP_STATS_FILE, "a", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [path_[0], path_[1], "EMBEDDING_BERT", len_path]
        ) if len_path != 0 else None


def hop_forever():
    import sys

    # hop_stat_links = list(get_starters_from_csv('hop_stats.csv'))
    # hop_stat_links = list(set(hop_stat_links))[1:]
    # for link in hop_stat_links:
    #     try:
    #         p = bert_hopper(link)
    #         if p is not None:
    #             record(p)
    #     except Exception as e:
    #         print(e)
    #         continue

    try:
        while True:
                random_starters = get_random_pages(20)
                for starter in random_starters:
                    try:
                        p = bert_hopper(starter[1])
                        if p is not None:
                            record(p)
                    except Exception as e:
                        print(e)
                        continue

    except KeyboardInterrupt:
        print('Exiting...')
        sys.exit(0)

    except Exception as e:
        print(e)
        sys.exit(1)













def bert_hopper_record(start_url: str, verbose: int = 2) -> list:
    """Hop from a Wikipedia article to Philosophy.

    Args:
        start_url (str): url of starting article
        verbose (int): print debug information (0: no, 1: some, 2: all)

    Returns:
        path (list): list of urls of articles visited
    """
    if verbose >= 1:
        print(f"BERT hopping from {start_url}")

    path = []
    cycle = False
    other_err = False
    cycle_eliminated = False

    current_url = start_url
    for hop in range(MAX_HOPS):
        # get list of urls of links from starting article
        links = extract_links_all(current_url)[:N_LINKS]
        words = [link[1].lower().strip() for link in links]

        # get wiki article text (for BERT)
        article_txt = txt_of(current_url)
        if article_txt is None:
            print(f"ERROR: Couldn't extract text from {current_url}")
            break
        last_word = words[-1]
        last_occurrence = article_txt.rfind(last_word) # last occurrence of last_word in article
        article_txt = article_txt[:last_occurrence]
        article_txt = postprocess_wiki_content(article_txt)

        # get most similar word to "Philosophy"
        sim = most_similar_to_phil(words, article_txt)
        
        # if all sim scores are None, error
        if sim['winner'][0] == '' and sim['winner'][1] == 0.0:
            print(f"ERROR: Couldn't find a similar word to 'Philosophy' in {current_url}")
            other_err = True
            break

        with open("bert_hop_from_london.csv", "a", encoding="utf-8") as f:
            # curr_url,words_considered,words_considered_scores,winner_word,winner_score
            writer = csv.writer(f)
            writer.writerow(
                [current_url, words, sim['similarities'], sim['winner'][0], sim['winner'][1]]
            )
        
        most_similar = sim['winner']
        most_similar_index = words.index(most_similar[0].lower().strip())

        # get url of selected link
        link_url = links[most_similar_index][0]

        # add url to path
        path.append(link_url)

        if verbose >= 2:
            print(f"\t{hop+1}: {link_url} ({most_similar[0]}, {most_similar[1]:.2f})")

        # try to avoid cycles
        # if cycle is detected, remove last link from path
        # and remove the word corresponding to that link
        if link_url in path[:-1]:
            path = path[:-1]
            words.pop(most_similar_index)
            links.pop(most_similar_index)
            new_most_similar = most_similar_to_phil(words, article_txt)
            new_most_similar_index = words.index(new_most_similar['winner'][0].lower().strip())
            new_link_url = links[new_most_similar_index][0]
            path.append(new_link_url)
            cycle_eliminated = True
            if verbose >= 2:
                print(f"\tCycle detected. Replacing {link_url} with {new_link_url}.")
            link_url = new_link_url

        # detect cycle
        if link_url in path[:-1] and cycle_eliminated:
            if verbose >= 1:
                print(f"\tCycle detected, terminating...")
            cycle = True
            break

        

        # check if url is philosophy
        if link_url == WIKI_URL_OF_PHILOSOPHY:
            if verbose >= 1:
                print(f"\tReached philosophy, terminating...")
            break

        # set url of next hop
        current_url = check_url(link_url)

    if not cycle and not other_err:
        return path
    else:
        return None    











if __name__ == '__main__':

    # bert_hopper('https://en.wikipedia.org/wiki/Jim_Dolan_(sculptor)')

    bert_hopper_record('https://en.wikipedia.org/wiki/London')

    # hop_forever()