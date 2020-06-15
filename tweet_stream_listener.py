import json
import redis

from botometer import Botometer
from tweepy import API
from tweepy.streaming import StreamListener


def convert_usernames_into_ids(auth, u):
    api = API(auth)
    return list(map(lambda x: api.get_user(x).id_str, u))


def tweet_it(auth, message, reply_status_id):
    api = API(auth)
    return api.update_status(message, in_reply_to_status_id="")


class Store:
    expires_seconds = 60 * 60 * 24 * 7

    def __init__(self, r: redis.client):
        self.redis = r

    def set_user(self, user_id, value):
        return self.redis.set(user_id, value, ex=self.expires_seconds)

    def get_user(self, user_id):
        percent = self.redis.get(user_id)
        if not percent:
            return None
        return percent.decode("utf-8")


class TweetStreamListener(StreamListener):
    def __init__(self, store: Store, bom: Botometer, auth):
        super().__init__()
        self.store = store
        self.bom = bom
        self.auth = auth

    def on_data(self, data):
        tweet = json.loads(data)
        if "delete" in tweet:
            print("skip delete tweet event")
            return True

        user_ids = self.list_mentioned_user_ids(tweet)
        if not user_ids:
            return True

        for screen_name, percent in self.lookup_users(user_ids):
            message = "According to botometer, %s is %s%% likely a bot https://botometer.iuni.iu.edu" \
                      % (tweet["user"]["screen_name"], percent)
            tweet_it(self.auth, message, tweet["id"])
            print(message)
        return True

    def on_error(self, status):
        print(status)

    def list_mentioned_user_ids(self, tweet):
        user_mentions = tweet["entities"]["user_mentions"]
        return list(map(lambda x: x["id"], user_mentions))

    def lookup_users(self, user_ids):
        for uid in user_ids:
            percent = self.store.get_user(uid)
            if percent:
                user_ids.remove(uid)
                yield uid, percent

        for uid, result in self.bom.check_accounts_in(user_ids):
            screen_name = result["user"]["screen_name"]
            print("looking up %s--%s in botometer" % (uid, screen_name))
            percent = round(result["display_scores"]["english"] / 5 * 100, 2)
            self.store.set_user(uid, percent)
            yield uid, percent
