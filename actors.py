import random
import re

from flask import Blueprint, render_template, request

from movie_showcase_app.db import get_db

bp = Blueprint("actors", __name__, url_prefix="/actors")


@bp.route("/")
def get_actors():
    page = int(request.args.get("page"))
    search_term = ""
    if search_term := request.args.get("search_text"):
        print(search_term)
        pattern = re.compile(f".*{search_term}.*", re.IGNORECASE)
        actor_list = list(
            get_db().actors.find(
                {"name": {"$regex": pattern}}, limit=24, skip=(24 * (page - 1))
            )
        )
    else:
        actor_list = list(get_db().actors.find(limit=24, skip=(24 * (page - 1))))
    actors = []
    for a in actor_list:
        actor = a
        movies = get_db().movies.find({"cast." + str(a["_id"]): {"$exists": True}})
        movie_list = ", ".join([movie["title"] for movie in movies])
        actor["movies"] = movie_list
        actors.append(actor)
    return render_template(
        "actors.html", actors=actors, page=page, search_text=search_term
    )


@bp.route("/<actor_id>")
def get_actor(actor_id):
    actor = get_db().actors.find_one({"_id": actor_id})
    movies = list(
        get_db().movies.find(
            {
                "$or": [
                    {"cast." + str(actor_id): {"$exists": True}},
                    {"producer": {"$in": [actor_id]}},
                    {"director": {"$in": [actor_id]}},
                ]
            },
            projection={"plot": 1, "cast": 1, "poster": 1, "title": 1},
        )
    )
    movies.sort(key=lambda x: x["title"][-5:-1])
    actor["movies"] = movies
    return render_template("actor_detail.html", actor=actor)
