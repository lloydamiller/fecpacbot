# run.py
from Twitter import TwitterAPI
from FEC import FECAPI
import time

if __name__ == "__main__":
    print("Activating Twitter Bot")
    print("[*] Initializing connection to Federal Election Commission")
    # intiialize FEC API
    fec = FECAPI()
    print("[*] Initializing connection to Twitter")
    # Intialize Twitter bot
    twitter = TwitterAPI()

    # begin process
    last_pac = False
    print("[*] Checking for new PAC registrations")
    # search FEC for PACs registered since date, sorted by date
    new_pacs = fec.get_new_pacs()
    if len(new_pacs) == 0:
        print("[*] No new PACs registered since last run")
        pass  # continue in loop
    else:
        for pac in new_pacs:
            pac_name = pac["name"]
            pac_state = pac["state"]
            pac_treasurer = pac["treasurer_name"].title()
            committee_id = pac["committee_id"]
            registration_url = fec.get_pac_registration_url(committee_id)
            try:
                associated_pacs = fec.get_treasurer_committees(pac_treasurer)
                if len(associated_pacs) > 0:
                    # make list of affiliated PACs
                    pass
                else:
                    pass
            except:
                pass
            pac_tweet = f"New PAC Registered: {pac_name} ({pac_state})\nTreasurer: {pac_treasurer}\n{registration_url}"
            twitter.send_tweet(pac_tweet)
            time.sleep(60)
