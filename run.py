# run.py
from Twitter import TwitterAPI
from FEC import FECAPI
import time
from datetime import datetime
import json


def timestamp():
    d = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return d


if __name__ == "__main__":
    print("Activating Twitter Bot")
    print(f"[*] {timestamp()} Initializing connection to Federal Election Commission")
    # intiialize FEC API
    fec = FECAPI()
    print(f"[*] {timestamp()} Initializing connection to Twitter")
    # Intialize Twitter bot
    twitter = TwitterAPI()
    current_user_account = twitter.api.me()
    print(f"[*] {timestamp()} You are now logged in as {current_user_account.name} (@{current_user_account.screen_name})")

    # begin process
    last_pac_date = False
    while True:
        counter = 0
        with open("Resources/posted_pacs.json", "r") as f:
            saved_pacs_object = json.load(f)
            saved_pacs = saved_pacs_object["saved_pacs"]
        new_pacs = fec.get_new_pacs(last_known_date=last_pac_date)
        if len(new_pacs) == 0:
            print(f"[*] {timestamp()} No new PACs registered")
            pass
        else:
            print(f"[*] {timestamp()} Found {len(new_pacs)} new registration(s)")
            for pac in new_pacs:
                counter += 1
                pac_name = pac["name"]
                if pac_name not in saved_pacs:
                    saved_pacs.append(pac_name)
                    pac_state = pac["state"]
                    pac_treasurer = pac["treasurer_name"].title()
                    committee_id = pac["committee_id"]
                    registration_url = fec.get_pac_registration_url(committee_id)
                    pac_tweet = f"New PAC: {pac_name} ({pac_state})\nTreasurer: {pac_treasurer}\n{registration_url}"
                    post_id = twitter.send_tweet(pac_tweet)
                    time.sleep(10)
                    # Get associated PACs based on matching treasurer
                    try:
                        associated_pacs = fec.get_treasurer_committees(pac_treasurer)
                        if len(associated_pacs) > 0:
                            associated_pacs.sort(key=lambda x: associated_pacs.most_recent_cycle, reverse=True)
                            associated_pacs = associated_pacs[:10]
                            for associated_pac in associated_pacs:
                                affiliated_pac_name = associated_pac["name"]
                                if pac_name != affiliated_pac_name:
                                    affiliated_pac_state = associated_pac["state"]
                                    affiliated_pac_cyles = associated_pac["cycles"]
                                    pac_tweet = f"Associated PAC: {affiliated_pac_name} ({affiliated_pac_state})\nActive: {affiliated_pac_cyles}"
                                    if len(pac_tweet) > 280:
                                        pac_tweet = pac_tweet[:280]
                                    if post_id is not False:
                                        post_id = twitter.send_tweet(pac_tweet, in_reply_to_status_id=post_id)
                        else:
                            pass
                    except:
                        pass
            if counter == 0:
                print(f"[*] {timestamp()} No new PACs registered")
            else:
                print(f"[*] {timestamp()} Added {counter} new PAC registrations")
        # save new PACs to the master PAC JSON file
        with open("Resources/posted_pacs.json", "w") as f:
            cut_off_length = 500
            if len(saved_pacs) > (cut_off_length + 100):
                saved_pacs_object["saved_pacs"] = saved_pacs[cut_off_length:]
            else:
                saved_pacs_object["saved_pacs"] = saved_pacs
            json.dump(saved_pacs_object, f, indent=4, ensure_ascii=False)
        last_pac_date = datetime.now().strftime("%Y-%m-%d")
        time.sleep(3600)
