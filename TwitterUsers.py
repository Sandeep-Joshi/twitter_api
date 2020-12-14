import csv
import tweepy
import pandas as pd
from twitter import TwitterError

from twitter_access import get_connection
import time
import json
import os
import requests
from json.decoder import JSONDecodeError


IS_RETWEET = "RT @"

csv.field_size_limit(2 ** 16)

# Specify Twitter Handles to collect
users = ["realDonaldTrump"]
reply_col_names = ['ID', 'Retweets', 'Replies', 'Likes', 'Quotes', 'Text']
base_path = os.getcwd() + "/replies"
max_results = 100  # replies between 10 and 100, errors out otherwise

query_replies='https://api.twitter.com/2/tweets/search/recent?'
query_tweets=''


def get_tweets(user_list):
    api = get_connection()

    # Set up Pandas Data Frame for data
    col_names = ['User', 'ID', 'DateTime', 'Device', 'Retweets', 'Likes', 'Text', 'Is_retweet']
    tweets = pd.DataFrame(columns=col_names)
    n = 1

    # Use Cursor method to get statuses
    for user in users:
        print(user)
        for status in tweepy.Cursor(api.user_timeline, id=user, tweet_mode='extended').items(100):
            tweets.loc[n, "User"] = user
            tweets.loc[n, "ID"] = status.id
            tweets.loc[n, "DateTime"] = status.created_at
            tweets.loc[n, "Device"] = status.source
            tweets.loc[n, "Retweets"] = status.retweet_count
            tweets.loc[n, "Likes"] = status.favorite_count
            text = status.full_text.replace("\n", " ").replace("\r\n", " ")
            tweets.loc[n, "Is_retweet"] = text.startswith(IS_RETWEET)
            tweets.loc[n, "Text"] = text
            n = n+1

    # Write pandas df to csv
    tweets.to_csv("Practice Tweets_test.csv")
    return tweets


def reply_json_parse(json_response):
    replies = pd.DataFrame(columns=reply_col_names)
    try:
        res_dict = json.loads(json_response)
    except JSONDecodeError as e:
        print("JSon decode error {}".format(e))
        return replies, None  # This will end the current conversation search in error hits us
    n = 1
    for reply in res_dict['data']:
        replies.loc[n, "ID"] = reply['id']
        replies.loc[n, "Retweets"] = reply['public_metrics']['retweet_count']
        replies.loc[n, "Replies"] = reply['public_metrics']['reply_count']
        replies.loc[n, "Likes"] = reply['public_metrics']['like_count']
        replies.loc[n, "Quotes"] = reply['public_metrics']['quote_count']
        replies.loc[n, "Text"] = reply['text'].replace("\n", " ").replace("\r\n", " ")
        n = n+1
    return replies, res_dict['meta'].get('next_token')


def test_reply_json_parse():
    f = open('sample_response_reply.json')
    print(reply_json_parse(f.read()))


def get_replies(tweet_id):
    api = get_connection(use_tweepy=False)
    replies_all = pd.DataFrame(columns=reply_col_names)
    next_token = None
    print("looking for replies to: {0}".format(tweet_id))
    if os.path.exists("{}/{}.csv".format(base_path, tweet_id)):
        print("Conversation file already exists skipping looking for replies")
        return
    while True:
        not_ok = False
        if next_token:
            q = "query=conversation_id:{0}&tweet.fields=conversation_id,public_metrics&next_token={1}&max_results={2}".format(tweet_id, next_token, max_results)
        else:
            q = "query=conversation_id:{0}&tweet.fields=conversation_id,public_metrics&max_results={1}".format(tweet_id, max_results)
        try:
            print('Running: {0}{1}'.format(query_replies, q))
            replies = requests.get('{0}{1}'.format(query_replies, q), headers=api)
        except TwitterError as e:
            print("caught twitter api error: {0}".format(e))
            not_ok = True
        if not replies.ok:
            print("Didn't get OK from replies. Skipping.")
            not_ok = True
        if not not_ok:
            reply_df, next_token = reply_json_parse(replies.text)
        else:
            next_token = None
        if next_token:
            time.sleep(3)
            replies_all = replies_all.append(reply_df, ignore_index=True)
        else:
            # open file and write all replies collated so far
            if os.path.exists("{}/{}.csv".format(base_path, tweet_id)):
                print("Conversation file already exists skipping.")
            else:
                replies_file = open("{}/{}.csv".format(base_path, tweet_id), 'w+')
                replies_all.to_csv(replies_file)
                replies_file.close()
                time.sleep(5)
                break


def main():
    tweets = get_tweets(users)
    org_tweets = tweets[tweets['Is_retweet']==False]
    org_tweets.apply(lambda x: get_replies(x.ID), axis=1)
    print("Finished!")


if __name__ == "__main__":
    main()