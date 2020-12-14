import configparser
import tweepy
import twitter


def get_connection(use_tweepy=True):
    # Twitter API credentials
    config = configparser.ConfigParser(interpolation=None)
    config.read('twitter keys.conf')
    consumer_key = config['DEFAULT']['api_key']
    consumer_secret = config['DEFAULT']['api_secret_key']
    access_key = config['DEFAULT']['access_token']
    access_secret = config['DEFAULT']['access_token_secret']
    bearer_token = config['DEFAULT']['bearer_token']

    if use_tweepy:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        return tweepy.API(auth, wait_on_rate_limit=True)
    else:
        return {'Authorization': 'Bearer {}'.format(bearer_token)}
        # return twitter.Api(consumer_key=consumer_key,
        #                    consumer_secret=consumer_secret,
        #                    access_token_key=access_key,
        #                    access_token_secret=access_secret,
        #                    sleep_on_rate_limit=True,
        #                    base_url='https://api.twitter.com/2')