""" config.py
    Configuration file for the project.
"""

WIKIPEDIA_API_BASE_URL = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_BASE_URL = "https://en.wikipedia.org"


WIKI_PAGEID_OF_PHILOSOPHY = 13692155
WIKI_URL_OF_PHILOSOPHY = "/wiki/Philosophy"
PHIL_WORD = 'philosophy'


MAX_HOPS = 100
MAX_LINK_EXTRACT = 20

# 
N = 15

DEFAULT_SQLITE_DB_NAME = "traversal_tree.db"


# =============================================================================

def print_config():
    print("Configuration:")
    print(f"    WIKIPEDIA_API_BASE_URL = {WIKIPEDIA_API_BASE_URL}")
    print(f"    WIKIPEDIA_BASE_URL = {WIKIPEDIA_BASE_URL}")
    print(f"    WIKI_PAGEID_OF_PHILOSOPHY = {WIKI_PAGEID_OF_PHILOSOPHY}")
    print(f"    WIKI_URL_OF_PHILOSOPHY = {WIKI_URL_OF_PHILOSOPHY}")
    print(f"    PHIL_WORD = {PHIL_WORD}")
    print(f"    MAX_HOPS = {MAX_HOPS}")
    print(f"    N = {N}")
    print(f"    DEFAULT_SQLITE_DB_NAME = {DEFAULT_SQLITE_DB_NAME}")