import requests
import re

BASE_URL = "https://cdn.syndication.twimg.com/tweet"

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
}


def download(url):
    url = url.replace("www.", "")
    if "t.co/" in url:
        response = requests.get(url)
        url = response.url
    regex_pattern = r"twitter.com\/.*\/status\/([0-9]*)"
    tweet_id = re.search(regex_pattern, url)
    if tweet_id is None:
        return {
            "status": False,
            "status_code": 400,
            "message": "The url is not a tweet url",
        }
    tweet_id = tweet_id.group(1)
    parameters = (
        ("id", tweet_id),
        ("lang", "en"),
    )
    response = requests.get(BASE_URL, headers=headers, params=parameters)
    if response.status_code == 200:
        data = response.json()
    elif response.status_code == 404:
        return {
            "status": False,
            "status_code": response.status_code,
            "message": "Tweet is not found or doesn't exist",
        }
    return {
        "status": False,
        "status_code": response.status_code,
        "message": response.reason,
    }