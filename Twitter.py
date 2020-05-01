import tweepy
import json
from datetime import datetime, timedelta
import time
import webbrowser


def timestamp():
    d = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return d


class TwitterAPI:

    def __init__(self):
        with open("Resources/keys.json", "r") as f:
            keys = json.load(f)["Twitter"]

        api_key = keys["API_KEY"]
        api_key_secret = keys["API_KEY_SECRET"]

        auth = tweepy.OAuthHandler(api_key, api_key_secret)

        print(f"[*] {timestamp()} Opening web browser. Login to target Twitter account and copy PIN.")

        try:
            redirect_url = auth.get_authorization_url()
            webbrowser.open(redirect_url)
        except tweepy.TweepError:
            print(f"[!] {timestamp()} Error, failed to get request token. Exiting program.")
            quit()

        while True:
            try:
                pin = input("[?] Enter pin: ").strip()
                token = auth.get_access_token(verifier=pin)
                access_token = token[0]
                access_token_secret = token[1]
                auth.set_access_token(access_token, access_token_secret)
                self.api = tweepy.API(auth, wait_on_rate_limit_notify=True)
                break
            except tweepy.error.TweepError:
                print(f"[!] {timestamp()} Error, pin not valid, please re-enter.")

    def rate_limit_check(self):
        rate_limit = self.api.rate_limit_status()["resources"]
        for rate in rate_limit:
            endpoints = rate_limit[rate]
            for endpoint in endpoints:
                limit = rate_limit[rate][endpoint]["limit"]
                remaining = rate_limit[rate][endpoint]["remaining"]
                if remaining == 0:
                    print(f"[!] {timestamp()} Rate limit hit for {rate}:{endpoint}, max limit is {limit}, ")
                elif limit > remaining:
                    print(f"[-] {timestamp()} {remaining}/{limit} calls remaining for {rate}:{endpoint}")

    def send_tweet(self, text, in_reply_to_status_id=False):
        while True:
            try:
                if in_reply_to_status_id is False:
                    post = self.api.update_status(text)
                else:
                    post = self.api.update_status(text, in_reply_to_status_id=in_reply_to_status_id)
                screen_name = self.api.me().screen_name
                posted_tweet_url = f"https://twitter.com/{screen_name}/status/{post.id_str}"
                print(f"[*] {timestamp()} Tweet posted to {posted_tweet_url}")
                return post.id_str
            except tweepy.error.RateLimitError:
                resume_time = (datetime.now() + timedelta(minutes=15)).strftime("%I:%M:%S %p")
                print(f"[!] {timestamp()} Potential rate limit hit for an endpoint, initiating 15-minute pause, will resume at {resume_time}")
                self.rate_limit_check()
                time.sleep(60 * 15)
            except tweepy.TweepError as e:
                error_message = e.args[0][0]["message"]
                print(f"[!] {timestamp()} Error posting tweet: {error_message}")
                return False
