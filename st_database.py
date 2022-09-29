import logging
import sqlite3

from sqlitedict import SqliteDict

logging.getLogger("sqlitedict").disabled = True


_DB_PATH = ".streamlit/database.sqlite"


class Database:
    def __init__(self, table_name: str = "unnamed") -> None:
        self.table_name = table_name
        self.read_args = {
            "filename": _DB_PATH,
            "tablename": self.table_name,
            "flag": "r",
            "journal_mode": "WAL",
        }
        self.write_args = {
            "filename": _DB_PATH,
            "tablename": self.table_name,
            "autocommit": True,
            "journal_mode": "WAL",
        }

    def __call__(self, tablename: str) -> "Database":
        """
        Allows for the syntax st.database(<table_name>)[<key>] to be used, if you want
        to use a different table from the default one.
        """
        return Database(tablename)

    def __getitem__(self, key):
        with SqliteDict(**self.read_args) as db:
            return db[key]

    def get(self, key, default=None):
        with SqliteDict(**self.read_args) as db:
            return db.get(key, default)

    def __setitem__(self, key, value):
        with SqliteDict(**self.write_args) as db:
            db[key] = value

    def __delitem__(self, key):
        with SqliteDict(**self.write_args) as db:
            del db[key]

    def __iter__(self):
        with SqliteDict(**self.read_args) as db:
            return iter(db)

    def __len__(self):
        with SqliteDict(**self.read_args) as db:
            return len(db)

    def __repr__(self):
        return str(self.read_args)

    def __contains__(self, key):
        with SqliteDict(**self.read_args) as db:
            return key in db

    def __dict__(self):
        with SqliteDict(**self.read_args) as db:
            return dict(db)

    def items(self):
        with SqliteDict(**self.read_args) as db:
            return list(db.items())

    def keys(self):
        with SqliteDict(**self.read_args) as db:
            return list(db.keys())

    def values(self):
        with SqliteDict(**self.read_args) as db:
            return list(db.values())


database = Database()


def get_tables():
    """Get the list of all the current sqlite tables"""
    nested = (
        sqlite3.connect(_DB_PATH)
        .cursor()
        .execute("SELECT name FROM sqlite_schema WHERE type='table'")
    )
    return [row[0] for row in nested]
