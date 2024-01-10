#!/bin/env python3

import os
import requests
import sys

em_api_key = os.getenv("EM_API_KEY")
em_app_key = os.getenv("EM_APP_KEY")
api_key = os.getenv("DD_API_KEY")
app_key = os.getenv("DD_APP_KEY")
user_input = sys.argv[1]


fs_headers = {
    "Accept": "application/json",
    "DD-API-KEY": em_api_key,
    "DD-APPLICATION-KEY": em_app_key,
}

tso_headers = {
    "Accept": "application/json",
    "DD-API-KEY": em_api_key,
    "DD-APPICATION-KEY": em_app_key,
}


def usage():
    url = "https://api.ddog-gov.com/api/v2/usage/hourly_usage"
    headers = tso_headers
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"{response.status_code}")
    else:
        result = response.json()
        print(result)


def dashboards():
    url = "https://api.ddog-gov.com/api/v1/dashboard/lists/manual"
    headers = fs_headers
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"{response.status_code}")
    else:
        result = response.json()
        print(result)


def selection(input):
    match input:
        case "dashboards":
            dashboards()
            if not dashboards:
                print("Could not use dashboard function")
        case "usage":
            usage()
            if not usage:
                print("Could not use usage function")


selection(user_input)
