#!/bin/env python3

import requests
import json
import os

api_key = os.getenv("DD_API_KEY")
app_key = os.getenv("DD_APP_KEY")

fs_headers = {
    "Accept": "application/json",
    "DD-API-KEY": api_key,
    "DD-APPLICATION-KEY": app_key,
}


def dashboards():
    url = "https://api.ddog-gov.com/api/v1/dashboard"
    headers = fs_headers
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"{response.status_code}")
    else:
        result = response.json()

        dashboard_list = result.get('dashboards', [])
        for dashboard in dashboard_list:
            if dashboard.get('author_handle') == 'christopher.montgomery@eccoselect.com':
                auth_name = dashboard.get('author_handle')
                dash_name = dashboard.get('title')
                dash_id = dashboard.get('id')
                print(f"By:{auth_name}\t Name:{dash_name}\n Id:{dash_id}")

    # print(result)


dashboards()

# auth_name = response.json().get('author_handle')
# dash_name = response.json().get('title')
# dash_id = response.json().get('id')
# print(f"By:{auth_name}\t Name:{dash_name}\n Id:{dash_id}")
