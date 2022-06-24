from plexapi.server import PlexServer

import config


def test_items(items, search):
    if len(items) < 1:
        return False
    search = search.lower()
    for item in items:
        title = item.title.lower()
        if title == search:
            return True
    return False


def movie_exists(title, debug=False):
    url = config.get_value("plex_url")
    token = config.get_value("plex_api_key")
    library = config.get_value("MOVIE_LIBRARY") or "Movies"
    plex = PlexServer(url, token)
    search_title = title
    items = plex.library.section(library).search(title=search_title)
    if debug:
        return test_items(items, title), items
    return test_items(items, title)


def episode_exists(show_title, season, episode):
    url = config.get_value("plex_url")
    token = config.get_value("plex_api_key")
    library = config.get_value("TV_SHOW_LIBRARY") or "TV Shows"
    plex = PlexServer(url, token)
    show = None
    show_exists = True
    try:
        show = plex.library.section(library).get(show_title)
    except Exception as e:
        return False
    try:
        episode = show.episode(season=season, episode=episode)
        return True
    except Exception as e:
        pass
    return False


def get_show_upload_path(item):
    url = config.get_value("plex_url")
    token = config.get_value("plex_api_key")
    library = config.get_value("TV_SHOW_LIBRARY") or "TV Shows"
    plex = PlexServer(url, token)
    show = None
    show_exists = True
    try:
        show = plex.library.section(library).get(item["series_title"])
    except Exception as e:
        show_exists = False
        pass
    show_folder = None
    if not show_exists:
        show_folder = item["series_title"].replace(" ", "_")
    else:
        show_folder = show.locations[0]

    if "/" in show_folder:
        show_folder = show_folder.split("/")[len(show_folder.split("/")) - 1]

    s_num = str(item["season"]).zfill(2) if 0 <= item["season"] <= 99 else str(item["season"])
    season_folder = "Season{}".format(s_num)
    pth = "{}/{}/".format(show_folder, season_folder) \
        .replace(" ", "\\ ") \
        .replace("(", "\\(") \
        .replace(")", "\\)")
    return pth


def get_compare_list(episode_checks):
    ep_strings = []
    for item in episode_checks:
        ep_num = item["episode"]
        s_num = item["season"]
        item["formatted"] = "s{}e{}".format(s_num, ep_num)
        ep_strings.append(item)
    return ep_strings


def list_missing_movies(movies=None):
    url = config.get_value("plex_url")
    token = config.get_value("plex_api_key")
    library = config.get_value("MOVIE_LIBRARY") or "Movies"
    plex = PlexServer(url, token)
    movies = [] if movies is None else movies
    missing = []
    for movie in movies:
        search_title = movie["title"] + "whee"
        items = plex.library.section(library).search(title=search_title)
        if len(items) < 1:
            missing.append(movie)
    return missing


def list_missing_shows(show_name, episode_checks=None):
    episode_checks = [] if episode_checks is None else episode_checks
    ep_strings = get_compare_list(episode_checks)
    url = config.get_value("plex_url")
    token = config.get_value("plex_api_key")
    library = config.get_value("TV_SHOW_LIBRARY") or "TV Shows"
    plex = PlexServer(url, token)
    episodes = None
    try:
        episodes = plex.library.section(library).get(show_name).episodes()
    except Exception as e:
        pass
    missing = []
    if episodes is None:
        # print("TV Show not found: {}".format(show_name))
        for item in ep_strings:
            missing.append(item)
        return missing, []
    existing = []
    for episode in episodes:
        ep_num = episode.episodeNumber
        s_num = episode.seasonNumber
        ep_string = "s{}e{}".format(s_num, ep_num)
        if ep_string not in existing:
            existing.append(ep_string)
    not_missing = []
    for item in ep_strings:
        item["series_title"] = show_name
        if item["formatted"] not in existing:
            missing.append(item)
        else:
            not_missing.append(item)
    return missing, not_missing
