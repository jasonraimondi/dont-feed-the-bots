import json
import logging
import sys
from typing import List

import redis

from botometer import Botometer
from tweepy import API
from tweepy.streaming import StreamListener


class Tweeter:
    def __init__(self, api: API):
        self.api = api

    def convert_usernames_into_ids(self, users_by_username_or_id: List[str]):
        return list(map(lambda x: self.api.get_user(x).id_str, users_by_username_or_id))

    def tweet_it(self, message, reply_status_id):
        return self.api.update_status(message, in_reply_to_status_id=reply_status_id)


class Store:
    expires_seconds = 60 * 60 * 24 * 7

    def __init__(self, r: redis.client):
        self.redis = r

    def set_user(self, user_id, value):
        return self.redis.set(user_id, value, ex=self.expires_seconds)

    def get_user(self, user_id):
        percent = self.redis.get(user_id)
        if percent:
            return percent.decode("utf-8")


class TweetStreamListener(StreamListener):
    def __init__(self, store: Store, bom: Botometer, tweeter: Tweeter):
        super().__init__()
        self.store = store
        self.bom = bom
        self.tweeter = tweeter

    def on_data(self, data):
        tweet = json.loads(data)

        if "delete" in tweet:
            print("skip delete tweet event")
            return True

        if tweet["user"]["screen_name"].lower() == "dontfeedthebots":
            return True

        origin_screen_name = tweet["user"]["screen_name"]

        user_names = self.list_mentioned_user_names(tweet)
        if not user_names:
            return True

        for screen_name, percent in self.lookup_users(user_names):
            percent = round(float(percent), 2)
            message = "@%s According to botometer, @%s is %s%% likely a bot https://botometer.iuni.iu.edu" \
                      % (origin_screen_name, screen_name, percent)
            if percent > 35:
                self.tweeter.tweet_it(message, tweet["id_str"])
                print("tweeting out: %s" %(message))
            else:
                print(message)
        return True

    def on_error(self, status):
        print(status)

    def list_mentioned_user_names(self, tweet):
        user_mentions = tweet["entities"]["user_mentions"]
        return list(map(lambda x: x["screen_name"], user_mentions))

    def lookup_users(self, user_names):
        for user_name in user_names:
            percent = self.store.get_user(user_name)
            if percent:
                user_names.remove(user_name)
                yield user_name, percent

        for screen_name, result in self.bom.check_accounts_in(user_names):
            uid = result["user"]["id_str"]
            print("looking up %s--%s in botometer" % (uid, screen_name))
            percent = round(float(result["display_scores"]["english"] / 5 * 100), 2)
            self.store.set_user(screen_name, percent)
            yield screen_name, percent
