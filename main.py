import requests
import re

BASE_URL = "https://cdn.syndication.twimg.com/tweet"

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
}


def edit_tweet_text(tweet_text: str, entities: dict) -> str:
    """
    Replace expended urls with their short version
    
    :param tweet_text: The text of the tweet
    :type tweet_text: str

    :param entities: A dictionary of entities that are present in the tweet
    :type entities: dict

    :return: The tweet text with the media url removed.
    """
    urls = entities.get("urls")
    for url in urls:
        expanded_url = url.get("expanded_url")
        shorted_url = url.get("url")
        tweet_text = tweet_text.replace(shorted_url, expanded_url)
    try:
        media_url = entities.get("media")[0].get("url")
        return tweet_text.replace(f" {media_url}", "")
    except TypeError:
        return tweet_text


def extract_text(data: dict) -> dict:
    """
    Extract Tweet data
    
    :param data: The data that you want to extract the photo from
    :type data: dict

    :return: A dictionary with the following keys:
        - status: True or False, depending on whether the tweet was successfully extracted
        - type_name: "text"
        - data: a dictionary with the following keys:
            - tweet_text: the text of the tweet
            - created_at: the date of tweet created (UTC time)
            - tweet_url: the url of the tweet
            - owner_username: the username of the user who posted the tweet
            - owner_name: the name of the user who posted the tweet
    """
    type_name = "text"
    tweet_id_str = data.get("id_str")
    created_at = data.get("created_at")
    owner_username = data.get("user").get("screen_name")
    owner_name = data.get("user").get("name")

    tweet_text = data.get("text")
    entities = data.get("entities")
    tweet_text = edit_tweet_text(tweet_text, entities)

    tweet_url = f"https://twitter.com/{owner_username}/status/{tweet_id_str}"
    return {
        "status": True,
        "type_name": type_name,
        "data": {
            "tweet_text": tweet_text,
            "tweet_url": tweet_url,
            "created_at": created_at,
            "owner_username": owner_username,
            "owner_name": owner_name,
        }
    }


def extract_video(data: dict) -> dict:
    type_name = "video"


def extract_photos(data: dict) -> dict:
    pass


def extract_photo(data: dict) -> dict:
    """
    Extract Tweet data
    
    :param data: The data that you want to extract the photo from
    :type data: dict

    :return: A dictionary with the following keys:
        - status: True or False, depending on whether the tweet was successfully extracted
        - type_name: "photo"
        - data: a dictionary with the following keys:
            - tweet_text: the text of the tweet
            - created_at: the date of tweet created (UTC time)
            - tweet_url: the url of the tweet
            - photo_url: the url of the photo
            - owner_username: the username of the user who posted the tweet
            - owner_name: the name of the user who posted the tweet
    """
    photos = data.get("photos")
    if len(photos) >= 1:
        extract_photos(data)
    type_name = "photo"
    photo_url = photos[0].get("url") + "?name=large"

    tweet_id_str = data.get("id_str")
    created_at = data.get("created_at")
    owner_username = data.get("user").get("screen_name")
    owner_name = data.get("user").get("name")

    tweet_text = data.get("text")
    entities = data.get("entities")
    tweet_text = edit_tweet_text(tweet_text, entities)

    tweet_url = f"https://twitter.com/{owner_username}/status/{tweet_id_str}"
    return {
        "status": True,
        "type_name": type_name,
        "data": {
            "tweet_text": tweet_text,
            "created_at": created_at,
            "tweet_url": tweet_url,
            "photo_url": photo_url,
            "owner_username": owner_username,
            "owner_name": owner_name,
        }
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
        if "video" in data:
            return extract_video(data)
        else:
            if "photos" in data:
                return extract_photo(data)
            return extract_text(data)
    elif response.status_code == 404:
        return {
            "status": False,
            "status_code": response.status_code,
            "message": "Tweet is not found. It may have been deleted or made private.",
        }
    return {
        "status": False,
        "status_code": response.status_code,
        "message": response.reason,
    }