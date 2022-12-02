""" WikiArticle.py

    A WikiArticle object represents a Wikipedia article.

    Tested with Python 3.10.7
    Author: Aron Molnar (gh/Arotte)
    Last modified: 2021-11-08
"""


class WikiArticle:
    """ WikiArticle object

        Represents a Wikipedia article.

        Attributes:
            title (str): title of the article
            url (str): url of the article
            pageid (int): pageid of the article
            html (str): html of the article

            N (int): max number of links to extract
            N_links (list): list of fist N links in the article
            N_links_text (list): list of text of first N links in the article
    """

    def __init__(self, title: str, url: str, pageid: int, html: str):
        self.title = title
        self.url = url
        self.pageid = pageid
        self.html = html

        self.N_links = []
        self.N_links_text = []

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"WikiArticle(\n\ttitle={self.title},\n\turl={self.url},\n\tpageid={self.pageid},\n\tn_links={self.n_links},\n\tn_links_text={self.n_links_text}\n)"