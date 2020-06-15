# Import the necessary methods from tweepy library
import json

from botometer import Botometer
from tweepy.streaming import StreamListener


# Create the class that will handle the tweet stream
class TweetStreamListener(StreamListener):
    def __init__(self, bom: Botometer):
        self.bom = bom

    def on_data(self, data):
        user_ids = self.list_mentioned_user_ids(data)
        if not user_ids:
            return True

        for screen_name, percent in self.lookup_users(user_ids):
            message = "According to botometer, %s is %s percent likely a bot" % (screen_name, percent)
            print(message)
        return True

    def on_error(self, status):
        print(status)

    def list_mentioned_user_ids(self, data):
        tweet = json.loads(data)
        if "delete" in tweet:
            print("skip delete tweet event")
            return []
        user_mentions = tweet["entities"]["user_mentions"]
        return list(map(lambda x: x["id"], user_mentions))

    def lookup_users(self, user_ids):
        for uid, result in self.bom.check_accounts_in(user_ids):
            screen_name = result["user"]["screen_name"]
            percent = str(round(result["display_scores"]["english"] / 5, 2))
            yield screen_name, percent

