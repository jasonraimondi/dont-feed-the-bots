import json
import redis

from botometer import Botometer
from tweepy import API
from tweepy.streaming import StreamListener

def convert_usernames_into_ids(auth, u):
    api = API(auth)
    return list(map(lambda x: api.get_user(x).id_str, u))


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
    def __init__(self, check: Store, bom: Botometer):
        super().__init__()
        self.store = check
        self.bom = bom

    def on_data(self, data):
        user_ids = self.list_mentioned_user_ids(data)
        if not user_ids:
            return True

        for screen_name, percent in self.lookup_users(user_ids):
            message = "According to botometer, %s is %s%% likely a bot https://botometer.iuni.iu.edu" % (screen_name, percent)
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
        for uid in user_ids:
            percent = self.store.get_user(uid)
            if percent:
                user_ids.remove(uid)
                yield uid, percent

        for uid, result in self.bom.check_accounts_in(user_ids):
            screen_name = result["user"]["screen_name"]
            print("looking up %s--%s in botometer" %(uid, screen_name))
            percent = round(result["display_scores"]["english"] / 5, 2)
            self.store.set_user(uid, percent)
            yield uid, percent
