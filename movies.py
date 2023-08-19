import random
import re

from flask import Blueprint, render_template, request

from movie_showcase_app.db import get_db

bp = Blueprint("movies", __name__, url_prefix="/movies")


@bp.route("/")
def get_movies():
    page = int(request.args.get("page"))
    search_term = ""
    if search_term := request.args.get("search_text"):
        pattern = re.compile(f".*{search_term}.*", re.IGNORECASE)
        movies = list(
            get_db().movies.find(
                {"title": {"$regex": pattern}}, limit=12, skip=(12 * (page - 1))
            )
        )
    else:
        movies = list(get_db().movies.find(limit=12, skip=(12 * (page - 1))))
    return render_template(
        "movies.html", movies=movies, page=page, search_text=search_term
    )


@bp.route("/<movie_id>")
def get_movie(movie_id):
    movie = get_db().movies.find_one({"_id": movie_id})
    movie_cast = movie["cast"]
    actors = []
    producers = []
    directors = []

    for producer_id in movie["producer"]:
        try:
            producer = get_db().actors.find_one({"_id": producer_id})
            producer_info = {
                "_id": producer_id,
                "name": producer["name"],
            }
            producers.append(producer_info)
        except:
            continue
    for director_id in movie["director"]:
        try:
            director = get_db().actors.find_one({"_id": director_id})
            director_info = {"_id": director_id, "name": director["name"]}
            directors.append(director_info)
        except:
            continue
    for actor_id, details in movie_cast.items():
        try:
            actor = {
                "_id": actor_id,
                "photo": get_db().actors.find_one({"_id": actor_id}).get("photo"),
                "name": details["name"],
                "role": details["role"],
            }
            actors.append(actor)
        except:
            continue

    return render_template(
        "movie_detail.html",
        movie=movie,
        actors=actors,
        directors=directors,
        producers=producers,
    )


@bp.route("/random")
def get_random_movie():
    movie = list(get_db().movies.aggregate([{"$sample": {"size": 1}}]))[0]
    return render_template("index.html", movie=movie)
