#!/bin/env python3

import requests
from typing import Dict
import os

API_KEY: str = os.getenv("DD_API_KEY", "")
if not API_KEY:
    raise ValueError("DD_API_KEY is not set")

APP_KEY: str = os.getenv("DD_APP_KEY", "")
if not APP_KEY:
    raise ValueError("DD_APP_KEY is not set")

FS_HEADERS: Dict[str, str] = {
    "Accept": "application/json",
    "DD-API-KEY": API_KEY,
    "DD-APPLICATION-KEY": APP_KEY,
}


def dashboards() -> None:
    url: str = "https://api.ddog-gov.com/api/v1/dashboard"
    headers: Dict[str, str] = FS_HEADERS
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"{response.status_code}")

    result = response.json()
    dashboard_list = result.get('dashboards', [])
    for dashboard in dashboard_list:
        if dashboard.get('author_handle') == 'christopher.montgomery@eccoselect.com':
            auth_name = dashboard.get('author_handle')
            dash_name = dashboard.get('title')
            dash_id = dashboard.get('id')
            print(f"By:{auth_name}\t Name:{dash_name}\n Id:{dash_id}")


if __name__ == "__main__":
    dashboards()
