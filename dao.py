""" dao.py

    Data Access Object. Used to access and interact
    with the SQLite3 database of the project.

    
"""

import sqlite3
import os

from config import WIKI_PAGEID_OF_PHILOSOPHY


class Page:
    def __init__(
        self,
        db_rowid,
        wiki_pageid,
        pagetitle,
        ithlink,
        i,
        fullurl,
        titleurl,
        parent_rowid,
    ):
        self.db_rowid = db_rowid
        self.wiki_pageid = wiki_pageid
        self.pagetitle = pagetitle
        self.ithlink = ithlink
        self.i = i
        self.fullurl = fullurl
        self.titleurl = titleurl
        self.parent_rowid = parent_rowid

    def to_tuple(self):
        return (
            self.db_rowid,
            self.wiki_pageid,
            self.pagetitle,
            self.ithlink,
            self.i,
            self.fullurl,
            self.titleurl,
            self.parent_rowid,
        )

    def tuple_without_rowid(self):
        return self.to_tuple()[1:]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"WikiPage(\n\tdb_rowid={self.db_rowid},\n\twiki_pageid={self.wiki_pageid},\n\tpagetitle={self.pagetitle},\n\tithlink={self.ithlink},\n\ti={self.i},\n\tfullurl={self.fullurl},\n\ttitleurl={self.titleurl},\n\tparent_rowid={self.parent_rowid}\n)"


def page_from_sql_get(sql_get: tuple) -> Page:
    return Page(*sql_get)


class TreeDao:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.c = self.conn.cursor()

        self.create_db()

    def close(self):
        self.conn.close()

    # ====================================================================================
    # DB CREATION
    # ====================================================================================

    def create_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute(
            """CREATE TABLE IF NOT EXISTS traversal_tree (
            rowid INTEGER PRIMARY KEY,
            wiki_page_id INTEGER,
            page_title TEXT,
            ithlink TEXT,
            i INTEGER,
            fullurl TEXT,
            titleurl TEXT,
            rowid_of_parent INTEGER
        )"""
        )

        # insert the root node Philosophy if not exists
        if self.get_philosophy() is None:
            c.execute(
                """INSERT INTO traversal_tree (
                wiki_page_id, page_title, ithlink, i, fullurl, titleurl, rowid_of_parent
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    WIKI_PAGEID_OF_PHILOSOPHY,  # wiki_page_id
                    "Philosophy",  # page_title
                    None,  # ithlink
                    None,  # i
                    "https://en.wikipedia.org/wiki/Philosophy",  # fullurl
                    "Philosophy",  # titleurl
                    None,  # rowid_of_parent
                ),
            )

        conn.commit()
        conn.close()

    # ====================================================================================
    # ADDERS
    # ====================================================================================

    def add(self, page: Page) -> Page:

        # check if entry already exists
        if self.get_by_pageid(page.wiki_pageid) is not None:
            return None

        self.c.execute(
            """INSERT INTO traversal_tree (
            wiki_page_id,
            page_title,
            ithlink,
            i,
            fullurl,
            titleurl,
            rowid_of_parent
        ) VALUES (
            :wiki_page_id,
            :page_title,
            :ithlink,
            :i,
            :fullurl,
            :titleurl,
            :rowid_of_parent
        )""",
            page.tuple_without_rowid(),
        )

        # get the rowid of the inserted entry .lastrowid
        page.db_rowid = self.c.lastrowid

        self.conn.commit()

        return page

    def add_more(self, entries):
        inserted = []
        for entry in entries:
            added = self.add(entry)
            if added is not None:
                inserted.append(added)

        return inserted

    # ====================================================================================
    # GETTERS
    # ====================================================================================

    def get_by_pageid(self, wiki_page_id: str) -> Page:
        self.c.execute(
            "SELECT * FROM traversal_tree WHERE wiki_page_id = ?", (wiki_page_id,)
        )

        # get result and return a Page object
        result = self.c.fetchone()
        if result is None:
            return None
        return page_from_sql_get(result)

    def get_by_rowid(self, rowid: str) -> Page:
        self.c.execute("SELECT * FROM traversal_tree WHERE rowid = ?", (rowid,))

        # get result and return a Page object
        result = self.c.fetchone()
        if result is None:
            return None
        return page_from_sql_get(result)

    def get_custom(self, where_clause: str) -> list:
        self.c.execute(f"SELECT * FROM traversal_tree WHERE {where_clause}")

        # get result and return a Page object
        result = self.c.fetchall()
        if result is None:
            return None
        return [page_from_sql_get(r) for r in result]

    def get_all(self) -> list:
        self.c.execute("SELECT * FROM traversal_tree")

        # get result and return a Page object
        result = self.c.fetchall()
        if result is None:
            return None
        return [page_from_sql_get(r) for r in result]

    def get_random(self) -> Page:
        self.c.execute("SELECT * FROM traversal_tree ORDER BY RANDOM() LIMIT 1")

        # get result and return a Page object
        result = self.c.fetchone()
        if result is None:
            return None
        return page_from_sql_get(result)

    # ====================================================================================
    # STATS
    # ====================================================================================

    def count(self):
        self.c.execute("SELECT COUNT(*) FROM traversal_tree")
        return self.c.fetchone()[0]

    # ====================================================================================
    # MISC
    # ====================================================================================

    def drop_table(self): 
        self.c.execute("DROP TABLE traversal_tree")
        self.conn.commit()

    def get_philosophy(self) -> Page:
        return self.get_by_pageid(WIKI_PAGEID_OF_PHILOSOPHY)

    def set_parent(self, p_wiki_pageid: str, parent_wiki_pageid: str) -> None:
        p = self.get_by_pageid(p_wiki_pageid)
        parent = self.get_by_pageid(parent_wiki_pageid)

        if p is None or parent is None:
            return

        self.c.execute(
            "UPDATE traversal_tree SET rowid_of_parent = ? WHERE wiki_page_id = ?",
            (parent.db_rowid, p.wiki_pageid),
        )

        self.conn.commit()
