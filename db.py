from flask import g
from pymongo import MongoClient


def get_db():
    if "db" not in g:
        client = MongoClient(host="localhost", port=27017)
        g.db = client.movie_showcase
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.client.close()


def init_app(app):
    app.teardown_appcontext(close_db)
