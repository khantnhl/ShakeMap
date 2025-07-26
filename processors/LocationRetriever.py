import os
from dotenv import load_dotenv

load_dotenv()
GG_PLACE_APIKEY = os.environ['googlePlace']

class LocationRetriever:
    def __init__(self):
        pass

    