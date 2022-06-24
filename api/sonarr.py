import json

import requests
from requests.auth import HTTPBasicAuth


def test():
    url = config.get_value("sonarr_url")
    key = config.get_value("sonarr_api_key")
    endpoint = "{}/api/system/status?apikey={}".format(url, key)
    response = requests.get(endpoint)
    print(response.text)


def get_episodes(options=None):
    url = config.get_value("sonarr_url")
    key = config.get_value("sonarr_api_key")
    illegal_chars = [" ", "'"]
    endpoint = "{}/api/series?apikey={}".format(url, key)
    response = requests.get(endpoint)
    text_response = response.text
    need_auth = False
    tuser, tpass = None, None
    if "401 Authorization Required" in text_response and options is not None:
        user = options.sonarr_user
        password = options.sonarr_pass
        tuser, tpass = user, password
        response = requests.get(endpoint, auth=HTTPBasicAuth(user, password))
        text_response = response.text
        need_auth = True
    if "401 Authorization Required" in text_response:
        print("Failed authentication for Sonarr!")
    series = json.loads(text_response)
    items = []
    for show in series:
        title = show["title"]
        uid = show["id"]
        ep = "{}/api/episode?apikey={}&seriesId={}".format(url, key, uid)
        lresp = None
        if need_auth:
            lresp = requests.get(ep, auth=HTTPBasicAuth(tuser, tpass)).text
        else:
            lresp = requests.get(ep).text
        resp = json.loads(lresp)
        eps = []
        invalid_files = []
        for item in resp:
            if "hasFile" in item and item["hasFile"]:
                if "episodeFile" in item and "path" in item["episodeFile"]:
                    filepath = item["episodeFile"]["path"]
                    legal = True
                    failed = []
                    for c in illegal_chars:
                        if c in filepath:
                            legal = False
                            failed.append(c)
                    if legal:
                        eps.append({
                            "title": item["title"],
                            "series_title": show["title"],
                            "season": item["seasonNumber"],
                            "episode": item["episodeNumber"],
                            "file": filepath
                        })
                    else:
                        invalid_files.append(item["title"])
        # if len(invalid_files) > 0:
        #     print("[Warning] Unable to process {} files due to invalid characters in the filepath".format(len(invalid_files)))
        items.append({
            "title": title,
            "id": uid,
            "episodes": eps
        })
    return items
