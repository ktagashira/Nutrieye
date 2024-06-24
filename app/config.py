from os import environ
from dotenv import load_dotenv

load_dotenv(verbose=True)

LINE_CHANNEL_ACCESS_TOKEN = environ.get(
    "LINE_CHANNEL_ACCESS_TOKEN",
    "",
)
LINE_CHANNEL_SECRET = environ.get("LINE_CHANNEL_SECRET", "")
