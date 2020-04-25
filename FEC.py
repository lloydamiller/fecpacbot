from random import randint
import urllib.parse
import requests
import time
import json


class FECAPI:

    def __init__(self, api_key):
        with open("Resources/keys.json", "r") as f:
            self.api_key = json.load(f)["FEC"]

    def api_call(self, endpoint, params, per_page=100):
        base = "https://api.open.fec.gov/v1"
        params["per_page"] = per_page
        page = 0
        results = []
        while True:
            page += 1
            params["page"] = page
            api_key = self.api_key[randint(0, len(self.api_key) - 1)]
            params["api_key"] = api_key
            params_encoded = urllib.parse.urlencode(params)
            uri = f"{base}{endpoint}?{params_encoded}"
            r = requests.get(uri)
            if r.status_code == 200:
                try:
                    j = r.json()
                    if len(j["results"]) == 0:
                        break
                except AttributeError:
                    print(f"[!] Results not returned as JSON")
                    break
                try:
                    if page == 1:
                        page_count = j["pagination"]["pages"]
                        total_results = j["pagination"]["count"]
                        print(f"[*] Found {total_results} results over {page_count} pages")
                    print(f"[*] Retrieved page {page}")
                    results.extend(j["results"])
                    if "last_indexes" in j["pagination"].keys():
                        for key in j["pagination"]["last_indexes"]:
                            params[key] = j["pagination"]["last_indexes"][key]
                    else:
                        break
                except Exception as e:
                    print(f"[!] Error: {e}")
                    break
            else:
                print(f"[!] Connection Error: {r.status_code}")
                break
            time.sleep(0.5)
        return results

    @staticmethod
    def get_new_pacs(self):
        # get new PAC's since the registration date of the most previous PAC posted to Twitter + name
        pass

    @staticmethod
    def get_treasurer_committees(self, treasurer_first_name, treasurer_last_name):
        # get all committees registered by
        name = f"{treasurer_first_name} {treasurer_last_name}"
        pass
