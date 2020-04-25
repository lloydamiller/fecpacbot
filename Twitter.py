import tweepy
import json
from datetime import datetime, timedelta
import time


class TwitterAPI:

    def __init__(self):
        with open("Resources/keys.json", "r") as f:
            keys = json.load(f)["Twitter"]

        twitter_api = keys["API_KEY"]
        twitter_api_secret = keys["API_KEY_SECRET"]
        twitter_api_access = keys["ACCESS_TOKEN"]
        twitter_api_access_secret = keys["ACCESS_TOKEN_SECRET"]

        auth = tweepy.OAuthHandler(twitter_api, twitter_api_secret)
        auth.set_access_token(twitter_api_access, twitter_api_access_secret)
        self.api = tweepy.API(auth)

    def rate_limit_check(self):
        rate_limit = self.api.rate_limit_status()["resources"]
        for rate in rate_limit:
            endpoints = rate_limit[rate]
            for endpoint in endpoints:
                limit = rate_limit[rate][endpoint]["limit"]
                remaining = rate_limit[rate][endpoint]["remaining"]
                if remaining == 0:
                    print(f"[!] Rate limit hit for {rate}:{endpoint}, max limit is {limit}, ")
                elif limit > remaining:
                    print(f"[-] {remaining}/{limit} calls remaining for {rate}:{endpoint}")

    def send_tweet(self, text):
        while True:
            try:
                post = self.api.update_status(text)
                screen_name = self.api.me().screen_name
                posted_tweet_url = f"https://twitter.com/{screen_name}/status/{post.id_str}"
                print(f"[*] Tweet posted to {posted_tweet_url}")
                break
            except tweepy.error.RateLimitError:
                resume_time = (datetime.now() + timedelta(minutes=15)).strftime("%I:%M:%S %p")
                print(f"[!] Potential rate limit hit for an endpoint, initiating 15-minute pause, will resume at {resume_time}")
                self.rate_limit_check()
                time.sleep(60 * 15)
            except tweepy.TweepError as e:
                error_message = e.args[0][0]["message"]
                print(f"[!] Error posting tweet: {error_message}")
                break
