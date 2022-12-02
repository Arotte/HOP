import tqdm
import requests
import sys
import os
import csv
from bs4 import BeautifulSoup

from word_selection import SelectionStrategy, select_link
from extraction import extract_links_all
from research import hop2phil, read_starters

from helpers import *
from config import *

# full path of this script
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


def main():

    starters = read_starters()[:1]

    for starter in starters:
        print(f"\nStarting from '{starter}'")
        hop2phil(starter[1], SelectionStrategy.RANDOM, debug_print=True)


if __name__ == "__main__":
    print(f"Testing WordNet word selection strategy...")
    main()
