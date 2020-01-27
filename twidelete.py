import io
import os
import sys
import time
import json

import twitter
from datetime import datetime
from dateutil import parser
from config_wangdino import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET


class TweetDestroyer(object):
    def __init__(self, twitter_api, dry_run=False):
        self.twitter_api = twitter_api
        self.dry_run = dry_run

    def destroy(self, tweet_id):
        try:
            print("delete tweet %s" % tweet_id)
            if not self.dry_run:
                self.twitter_api.DestroyStatus(tweet_id)
            # NOTE: A poor man's solution to honor Twitter's rate limits.
            time.sleep(0.5)
        except twitter.TwitterError as err:
            print("Exception: %s\n" % err.message)


class TweetReader(object):
    def __init__(self, reader, until_date=None, filters=[], spare=[], min_likes=0, min_retweets=0):
        self.reader = reader
        self.until_date = datetime.now() if until_date is None else parser.parse(until_date, ignoretz=True)
        self.filters = filters
        self.spare = spare
        self.min_likes = 0 if min_likes is None else min_likes
        self.min_retweets = 0 if min_retweets is None else min_retweets

    def read(self):
        for row in self.reader:
            if row["tweet"].get("created_at", "") != "":
                tweet_date = parser.parse(row["tweet"]["created_at"], ignoretz=True)
                if tweet_date >= self.until_date:
                    continue

            if ("retweets" in self.filters and
                    not row["tweet"].get("full_text").startswith("RT @")) or \
                    ("replies" in self.filters and
                     row["tweet"].get("in_reply_to_user_id_str") == ""):
                continue

            if row["tweet"].get("id_str") in self.spare:
                continue

            if (0 < self.min_likes <= int(row["tweet"].get("favorite_count"))) or \
                    (0 < self.min_retweets <= int(row["tweet"].get("retweet_count"))):
                continue

            yield row


def delete(tweetjs_path, until_date, filters, s, min_l, min_r, dry_run=False):
    with io.open(tweetjs_path, mode="r", encoding="utf-8") as tweetjs_file:
        count = 0

        # api = twitter.Api(consumer_key=os.environ["TWITTER_CONSUMER_KEY"],
        #                   consumer_secret=os.environ["TWITTER_CONSUMER_SECRET"],
        #                   access_token_key=os.environ["TWITTER_ACCESS_TOKEN"],
        #                   access_token_secret=os.environ["TWITTER_ACCESS_TOKEN_SECRET"])
        api = twitter.Api(consumer_key=CONSUMER_KEY,
                          consumer_secret=CONSUMER_SECRET,
                          access_token_key=ACCESS_TOKEN,
                          access_token_secret=ACCESS_SECRET)

        destroyer = TweetDestroyer(api, dry_run)

        tweets = json.loads(tweetjs_file.read()[25:])
        for row in TweetReader(tweets, until_date, filters, s, min_l, min_r).read():
            destroyer.destroy(row["tweet"]["id_str"])
            count += 1

        print("Number of deleted tweets: %s\n" % count)

    sys.exit()


PATH = 'tweet.js'
UNTIL = '2020-01-15'
FILTER = ''
SPARE = ''
MINL = 0
MINR = 0

delete(PATH, UNTIL, FILTER, SPARE, MINL, MINR)