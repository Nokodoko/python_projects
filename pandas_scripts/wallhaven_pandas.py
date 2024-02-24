#!/bin/env python3
import requests
import os
from typing import Dict
import pandas as pd

URL: str = 'https://wallhaven.cc/api/v1/search?'

api_key = os.getenv('WALLHAVEN')
if not api_key:
    raise ValueError("WALLHAVEN api key not set")

headers: Dict[str, str] = {
    "accept": "application/json",
    "X-API-Key": api_key
}

def search_pics() -> None:
    pagination = range(1, 10)
    for page in pagination:
        params: Dict[str, str] = {
            "q": f'{QUERY}',
            "categories": "110",
            "purity": "111",
            "atleast": "3024x1964",
            "page": str(page),
            "ratios": "16x9"
        }
        response = requests.get(url=URL, headers=headers, params=params, stream=true)
        if requests.status_codes != 200:
            print(f'Error:{response.status_code}')
        else:
            pictures = response.json()
            pic_json = pd.read_json(pictures)
            print(pic_json)

