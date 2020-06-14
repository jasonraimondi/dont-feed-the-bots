# Import the necessary methods from tweepy library
import json

from botometer import Botometer
from tweepy.streaming import StreamListener


# Create the class that will handle the tweet stream
class TweetStreamListener(StreamListener):

    def on_data(self, data):
        print(data)
        # list_mentioned_users(data)
        return True

    def on_error(self, status):
        print(status)



def list_mentioned_users(data):
    tweet = json.loads(data)
    for user in tweet["entities"]["user_mentions"]:
        print(user)

