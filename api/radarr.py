import json
import time

import requests


def test(options=None):
    url = options.radarr_url
    key = options.radarr_api_key
    endpoint = "{}/api/v3/system/status?apiKey={}".format(url, key)
    response = requests.get(endpoint)
    text_response = response.text
    return True


def get_movies(downloaded_only=True, options=None):
    url = options.radarr_url
    key = options.radarr_api_key
    endpoint = "{}/api/v3/movie?apiKey={}".format(url, key)
    response = requests.get(endpoint)
    text_response = response.text
    if "401 Authorization Required" in text_response:
        print("[Radarr] Failed authentication! (m1)")
        return []
    if not downloaded_only:
        return json.loads(text_response)
    ret = []
    try:
        lst = json.loads(text_response)
        for item in lst:
            if "hasFile" in item and item["hasFile"]:
                ret.append({
                    "title": item["title"],
                    "path": item["movieFile"]["path"]
                })
    except Exception as e:
        print("[Radarr] Failed to load response from api (uncaught)")
        print(text_response)
        time.sleep(5)
    return ret
