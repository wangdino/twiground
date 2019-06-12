import tweepy
import pandas as pd

from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET


def twi_oauth():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api


def get_user_tl(username):
    api = twi_oauth()
    tweets = api.user_timeline(username)
    return tweets


def get_home_tl():
    api = twi_oauth()
    tweets = api.home_timeline()
    return tweets


def get_tweet_object():
    return


def get_details(tweet_object):
    tweet_list = list()
    for tweet in tweet_object:
        id = tweet.id
        text = tweet.text
        fav_count = tweet.favorite_count
        rt_count = tweet.retweet_count
        time = tweet.created_at
        source = tweet.source
        re_to_status = tweet.in_reply_to_status_id
        re_to_user = tweet.in_reply_to_screen_name
        tweet_list.append({'id': id,
                           'text': text,
                           'fav_count': fav_count,
                           'rt_count': rt_count,
                           'time': time,
                           'source': source,
                           're_to_status': re_to_status,
                           're_to_user': re_to_user})
        df = pd.DataFrame(tweet_list, columns=['id',
                                               'text',
                                               'fav_count',
                                               'rt_count',
                                               'time',
                                               'source',
                                               're_to_status',
                                               're_to_user'])
    return df


def main():
    tw = get_user_tl('wangdino')
    df = get_details(tw)
    print(df)


if __name__ == "__main__":
    main()
