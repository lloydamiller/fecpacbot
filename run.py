# run.py
from Twitter import TwitterAPI
from FEC import FECAPI
import time
from datetime import datetime
import json

if __name__ == "__main__":
    print("Activating Twitter Bot")
    print("[*] Initializing connection to Federal Election Commission")
    # intiialize FEC API
    fec = FECAPI()
    print("[*] Initializing connection to Twitter")
    # Intialize Twitter bot
    twitter = TwitterAPI()
    current_user_account = twitter.me()
    print(f"[*] You are now logged in as {current_user_account.name} (@{current_user_account.screen_name})")

    # begin process
    last_pac_date = False
    while True:
        with open("Resources/posted_pacs.json", "r") as f:
            saved_pacs_object = json.load(f)
            saved_pacs = saved_pacs_object["saved_pacs"]
        print("[*] Checking for new PAC registrations")
        # search FEC for PACs registered since date, sorted by date
        new_pacs = fec.get_new_pacs(last_known_date=last_pac_date)
        if len(new_pacs) == 0:
            print("[*] No new PACs registered since last run")
        else:
            for pac in new_pacs:
                pac_name = pac["name"]
                if pac_name not in saved_pacs:
                    saved_pacs.append(pac_name)
                    pac_state = pac["state"]
                    pac_treasurer = pac["treasurer_name"].title()
                    committee_id = pac["committee_id"]
                    registration_url = fec.get_pac_registration_url(committee_id)
                    # TODO identify and display affiliated PACs
                    # try:
                    #     associated_pacs = fec.get_treasurer_committees(pac_treasurer)
                    #     if len(associated_pacs) > 0:
                    #         # make list of affiliated PACs
                    #         # tweet thread or image?
                    #     else:
                    #         pass
                    # except:
                    #     pass
                    pac_tweet = f"New PAC Registered: {pac_name} ({pac_state})\nTreasurer: {pac_treasurer}\n{registration_url}"
                    twitter.send_tweet(pac_tweet)
                    time.sleep(60)
        # save new PACs to the master PAC JSON file
        with open("Resources/posted_pacs.json", "w") as f:
            saved_pacs_object["saved_pacs"] = saved_pacs[500:]
            json.dump(saved_pacs_object, f, indent=4, ensure_ascii=False)
        last_pac_date = datetime.now().strftime("%Y-%m-%d")
        time.sleep(3600)
