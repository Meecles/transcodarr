import os
import time
import uuid

from api import radarr
from utils.db_config import db
from utils.options import Options


def startup(options: Options):
    print("Starting...")
    if options.purge_db_on_startup:
        print("Purging database")
        db["tracker"].delete_many({})
    print("Started!")


def iterate_queue(options: Options):
    processed = 0
    movies = radarr.get_movies(options=options)
    print(movies)



if __name__ == '__main__':
    options = Options()
    startup(options)
    iterate_queue(options)
