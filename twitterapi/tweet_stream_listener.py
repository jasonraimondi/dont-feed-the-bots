# Import the necessary methods from tweepy library
import json

from botometer import Botometer
from tweepy.streaming import StreamListener


# Create the class that will handle the tweet stream
class TweetStreamListener(StreamListener):
    def __init__(self, bom: Botometer):
        self.bom = bom

    def on_data(self, data):
        self.list_mentioned_users(data)
        return True

    def on_error(self, status):
        print(status)

    def list_mentioned_users(self, data):
        tweet = json.loads(data)
        if "delete" in tweet:
            print("Tweet deleted", tweet)
            return

        # if "entites" in tweet and "user_mentions" in tweet["entities"]:
        user_ids = []
        for user in tweet["entities"]["user_mentions"]:
            print(user)
            user_ids.append(user["id"])

        if len(user_ids) > 0:
            for screen_name, result in self.bom.check_accounts_in(user_ids):
                percent = result["display_scores"]["english"] / 5
                # display_percent = f'{percent}%'
                # display_of_five = result["display_scores"]["english"]
                print("%s is %s percent likely a bot" %(screen_name, percent))
