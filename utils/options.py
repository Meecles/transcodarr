import json
import os
import sys


class Options:

    def __init__(self):
        self.purge_db_on_startup = False
        self.transcoder_id = None
        self.mongo_ip, self.mongo_port = None, None
        self.radarr_url = None
        self.sonarr_url = None
        self.radarr_api_key = None
        self.sonarr_api_key = None
        self.plex_url, self.plex_api_key = None, None
        self._load_from_config()
        self.parse_args()
        self.parse_env()

    def _load_from_config(self, config_file="conf/config.json"):
        with open(config_file, "r") as f:
            lines = f.read()
            content = json.loads(lines)
            if "radarr" in content:
                radarr = content["radarr"]
                if "url" in radarr:
                    self.radarr_url = radarr["url"]
                if "api_key" in radarr:
                    self.radarr_api_key = radarr["api_key"]
            if "sonarr" in content:
                sonarr = content["sonarr"]
                if "url" in sonarr:
                    self.sonarr_url = sonarr["url"]
                if "api_key" in sonarr:
                    self.sonarr_api_key = sonarr["api_key"]

    def has_env(self, var, require_true=False):
        if require_true:
            return var in os.environ and os.environ.get(var).lower() == "true"
        return var in os.environ

    def _env_val(self, value):
        if value in os.environ:
            return os.environ.get(value)
        return None

    def parse_args(self):
        if "--purge-database" in sys.argv:
            self.purge_db_on_startup = True

    def parse_env(self):
        if self.has_env("PURGE_DATABASE", require_true=True):
            self.purge_db_on_startup = True

        self.transcoder_id = self._env_val("TRANSCODER_ID") if "TRANSCODER_ID" in os.environ else "Default"

        if "RADARR_API_KEY" in os.environ:
            self.radarr_api_key = self._env_val("RADARR_API_KEY")
        if "SONARR_API_KEY" in os.environ:
            self.sonarr_api_key = self._env_val("SONARR_API_KEY")
