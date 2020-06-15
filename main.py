import os

import botometer
import redis
from tweepy import OAuthHandler, Stream

from load_users_file import get_users_from_file
from tweet_stream_listener import TweetStreamListener, Store, convert_usernames_into_ids

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

store = Store(redis.Redis(host='localhost', port=6379))

auth = OAuthHandler(twitter_app_auth["consumer_key"], twitter_app_auth["consumer_secret"])
auth.set_access_token(twitter_app_auth["access_token"], twitter_app_auth["access_token_secret"])

stream_listener = TweetStreamListener(store, botometer)

users = os.environ.get("USERS")

if not users:
    print("getting users from file")
    users = get_users_from_file()

if not users:
    print("environment variable \"USERS\" or a users.json file required")
    exit(1)

if isinstance(users, str):
    users = users.replace(" ", "").split(",")

user_ids = convert_usernames_into_ids(auth, users)
print(users)
print(user_ids)
stream = Stream(auth, stream_listener)
stream.filter(follow=user_ids)

# stream.disconnect()
