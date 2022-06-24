import json

from api import radarr, sonarr, plex
from utils.db_config import db


def get_movie(missing):
    for item in missing:
        title = item["title"]
        db_obj = db["processing"].find_one({"title": title, "type": "movie"})
        if db_obj is None:
            item["type"] = "movie"
            if not plex.movie_exists(title):
                return item
    return None


def get_episode(missing):
    for item in missing:
        title = item["title"]
        formatted = item["formatted"]
        db_obj = db["processing"].find_one(
            {"title": title, "formatted": formatted, "series_title": item["series_title"], "type": "tv"}
        )
        if db_obj is None:
            item["type"] = "tv"
            season = item["season"]
            episode = item["episode"]
            if not plex.episode_exists(item["series_title"], season, episode):
                return item
    return None


def get_next(priority="movie", options=None):
    movies = radarr.get_movies(downloaded_only=True, options=options)
    l = len(movies)
    if l > 0:
        movie = json.dumps(movies[0])
        # print(movie)
    else:
        print("No movies")

    items = sonarr.get_episodes(options=options)
    # print("Missing items:")
    missing_items = []
    for item in items:
        title = item["title"]
        episodes = item["episodes"]
        missing, not_missing = plex.list_missing_shows(title, episodes)
        if len(missing) > 0:
            for item in missing:
                missing_items.append(item)
    # print(json.dumps(missing_items))

    radarr_items = radarr.get_movies()
    missing_movies = plex.list_missing_movies(radarr_items)
    # print(json.dumps(missing_movies))
    if priority.lower() == "movie":
        ret_item = get_movie(missing_movies)
        if ret_item is None:
            ret_item = get_episode(missing_items)
        return ret_item  # Can be None
    if priority.lower() == "tv":
        ret_item = get_episode(missing_items)
        if ret_item is None:
            ret_item = get_movie(missing_movies)
        return ret_item  # Can be None
    print("No items in queue!")
    return None
