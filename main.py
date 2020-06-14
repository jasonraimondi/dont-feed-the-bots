import json
import os

import botometer
from tweepy import OAuthHandler, API

from twitterapi.tweet_stream_listener import TweetStreamListener

twitter_app_auth = {
    "consumer_key": os.environ["TW_CONSUMER_KEY"],
    "consumer_secret": os.environ["TW_CONSUMER_SECRET"],
    "access_token": os.environ["TW_ACCESS_KEY"],
    "access_token_secret": os.environ["TW_ACCESS_SECRET"],
}

rapidapi_key = os.environ["RAPIDAPI_KEY"]


def get_users_from_file(file_name="users.json"):
    if os.path.exists(file_name):
        fp = open(file_name, "r")
        content = fp.read()
        fp.close()
        return json.loads(content)


userlist = get_users_from_file()

print(userlist)

# Handles Twitter authetification and the connection to Twitter Streaming API
bom = botometer.Botometer(wait_on_ratelimit=True,
                          rapidapi_key=rapidapi_key,
                          **twitter_app_auth)

stream_listener = TweetStreamListener(bom)
auth = OAuthHandler(twitter_app_auth["consumer_key"], twitter_app_auth["consumer_secret"])
auth.set_access_token(twitter_app_auth["access_token"], twitter_app_auth["access_token_secret"])

print(twitter_app_auth["consumer_key"])
print(twitter_app_auth["consumer_secret"])
print(twitter_app_auth["access_token"])
print(twitter_app_auth["access_token_secret"])

api = API(auth)
public_tweets = api.home_timeline()
for tweet in public_tweets:
    print(tweet.text)

# stream = Stream(auth, stream_listener)
# stream.filter(follow=userlist)

# stream.disconnect()
