from random import randint
import urllib.parse
import requests
import time
import json
from datetime import datetime, timedelta


def timestamp():
    d = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return d


class FECAPI:

    def __init__(self):
        with open("Resources/keys.json", "r") as f:
            self.api_key = json.load(f)["FEC"]

    def api_call(self, endpoint, params):
        base = "https://api.open.fec.gov/v1"
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
                    print(f"[!] {timestamp()} Results not returned as JSON")
                    break
                try:
                    if page == 1:
                        page_count = j["pagination"]["pages"]
                        total_results = j["pagination"]["count"]
                        # print(f"[*] Found {total_results} results over {page_count} page(s) from {endpoint}")
                    results.extend(j["results"])
                    if "last_indexes" in j["pagination"].keys():
                        for key in j["pagination"]["last_indexes"]:
                            params[key] = j["pagination"]["last_indexes"][key]
                    else:
                        break
                except Exception as e:
                    print(f"[!] {timestamp()} Error: {e}")
                    break
            else:
                print(f"[!] {timestamp()} Connection Error: {r.status_code}")
                break
            time.sleep(0.5)
        print(f"[*] {timestamp()} Found {len(results)} result(s) from FEC {endpoint}")
        return results

    def get_new_pacs(self, last_known_date=False):
        # get new PAC's since the registration date of the most previous PAC posted to Twitter + name
        days_to_get = timedelta(days=5)
        if last_known_date is False:
            last_known_date = datetime.now() - days_to_get
        else:
            last_known_date = last_known_date - days_to_get
        last_known_date = last_known_date.strftime("%Y-%m-%d")
        endpoint = "/committees/"
        params = {
            "min_first_file_date": last_known_date,
            "per_page": "100",
            "sort_hide_null": "false",
            "sort_null_only": "false"
        }
        results = self.api_call(endpoint, params)
        # filter and format
        committee_types = ["N", "O", "Q", "V", "W"]
        filtered_results = []
        for result in results:
            if result["committee_type"] in committee_types:
                filtered_results.append({
                    "name": result["name"],
                    "state": result["state"],
                    "filing_date": result["first_file_date"],
                    "committee_id": result["committee_id"],
                    "treasurer_name": result["treasurer_name"]
                })
        return filtered_results

    def get_pac_registration_url(self, committee_id):
        endpoint = f"/committee/{committee_id}/filings/"
        params = {
            "per_page": "1",
            "sort_hide_null": "false",
            "sort_null_only": "false",
            "form_type": "F1"
        }
        results = self.api_call(endpoint, params)[0]
        return results["html_url"]

    def get_treasurer_committees(self, treasurer_name):
        # get all committees registered by
        endpoint = "/committees/"
        params = {
            "treasurer_name": treasurer_name,
            "per_page": "100",
            "sort_hide_null": "false",
            "sort_null_only": "false"
        }
        results = self.api_call(endpoint, params)
        filtered_results = []
        for result in results:
            filtered_results.append({
                "name": result["name"],
                "state": result["state"],
                "cycles": ", ".join([str(x) for x in result["cycles"]]),
                "most_recent_cycle": max(result["cycles"])
            })
        return filtered_results
