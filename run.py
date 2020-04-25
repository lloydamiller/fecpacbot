# run.py
from Twitter import TwitterAPI

if __name__ == "__main__":
    print("Activating Twitter Bot")
    print("...checking connection to Federal Election Commission")
    # intiialize FEC API
    print("...checking connection to Twitter")
    # Intialize Twitter bot
    try:
        twitter = TwitterAPI()
    except:
        print("[!] Error: failed to connect to Twitter")
        exit(1)

    # begin process
    print("[*] Checking for new PAC registrations")
    # get most recent tweet from account that uses pattern "New PAC:"
    # get PAC name and registration date
    # search FEC for PACs registered since date, sorted by date
    # save all PACs until most recent tweeted PAC
    # if new registrations found, for each new PAC:
    #   extract filing URL, PAC name, location (city, state), and treasurer name
    #   search FEC for PACs associated with treasurer
    #   produce list of PACs with the same treasurer name
