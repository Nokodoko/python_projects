#!/bin/env python3

import os
import requests
import pandas

# TODO:
# Write json to memory
# Run output into xlsx (pandas)
# Is there a dynamic way to include growing list of applications?

api_key = os.getenv("DD_API_KEY")
app_key = os.getenv("DD_APP_KEY")

account_ids = {
    "744281823657": "PAT",
    "583937734902": "VDR",
    "515022543707": "FSAPPSE",
    "007911250085": "FEMS",
    "328762180115": "CFTEAM",
    "112364832438": "UAVS",
    "175560568060": "HWP",
    "107895115286": "LLC",
    "007273980385": "FEMS",
    "066399073050": "CIAO",
    "899201081254": "AFF",
    "171226545153": "NRMBP",
    "748257752168": "NMIS-GrowHub",
    "114245151275": "WFWEB",
    "407464523575": "WFSAFE",
    "403938590038": "GPH",
    "227101269271": "HDWI",
    "504420026195": "INCIWEB",
    "878733051466": "Admin"
}

headers = {
    "Accept": "application/json",
    "DD-API-KEY": api_key,
    "DD-APPLICATION-KEY": app_key,
}


def integrations(id):
    link = f"https://api.ddog-gov.com/api/v1/integration/aws/filtering?account_id={id}"
    url = link
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"{response.status_code}")
    else:
        result = [item["namespace"] for item in response.json()["filters"]]
        result_join = "\n".join(result)
        print(result_join, "\n")

    for account_id, account_name in account_ids.items():
        print(account_name)
        integrations(account_id)
