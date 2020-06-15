import os

import botometer
from tweepy import OAuthHandler, API, Stream

from load_users_file import get_users_from_file
from tweet_stream_listener import TweetStreamListener

twitter_app_auth = {
    "consumer_key": os.environ["TW_CONSUMER_KEY"],
    "consumer_secret": os.environ["TW_CONSUMER_SECRET"],
    "access_token": os.environ["TW_ACCESS_KEY"],
    "access_token_secret": os.environ["TW_ACCESS_SECRET"],
}

rapidapi_key = os.environ["RAPIDAPI_KEY"]

botometer = botometer.Botometer(wait_on_ratelimit=True,
                                rapidapi_key=rapidapi_key,
                                **twitter_app_auth)

stream_listener = TweetStreamListener(botometer)
auth = OAuthHandler(twitter_app_auth["consumer_key"], twitter_app_auth["consumer_secret"])
auth.set_access_token(twitter_app_auth["access_token"], twitter_app_auth["access_token_secret"])


def get_ids_for_users(users):
    api = API(auth)
    return list(map(lambda x: api.get_user(x).id_str, users))


users = get_users_from_file()
user_ids = get_ids_for_users(users)

stream = Stream(auth, stream_listener)
stream.filter(follow=user_ids)

# stream.disconnect()
