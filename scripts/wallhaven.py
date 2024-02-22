#!/bin/env python3
import requests
import os
import helpers as h
from typing import Dict
from typing import List


api_key: str = os.getenv('WALLHAVEN')
if not api_key:
    raise ValueError("WALLHAVEN api_key not set")

SEARCH: str = 'https://wallhaven.cc/api/v1/search?'
INSTRUCTIONS: str = 'Wallhaven Downloader:'
NS_MSG: str = 'Wallhaven Downloader'
PIC_PATH: str ='~/Pictures/downloads/'
KEEP: str ='~/Pictures/downloads/keep'
DESTROY: str ='~/Pictures/downloads/destroy/'
QUERY: str = h.dmenu('yellow', INSTRUCTIONS)

search_headers: Dict[str, str] = {
    "Accept": "application/json",
    "X-API-Key": api_key
}

def search_pics() -> None:
    pagination = range(1, 10)
    for page in pagination:
        params: Dict[str, str] = {
            "q": f'{QUERY}',
            "categories": "110",
            "purity": "111",
            "atleast": "2560x1440",
            "page": str(page),
            "ratios": "16x9,16x10"
        }
        response = requests.get(url=SEARCH, headers=search_headers, params=params, stream=True)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
        else:
            pictures = response.json()
            url_list: List[str] = [items['path'] for items in pictures['data']]
            pic_url: str
            file_number: int = 0
            for pic_url in url_list:
                filename: str = os.path.basename(QUERY)
                file_extension: str = os.path.splitext(filename)[1]
                local_file: str = os.path.expanduser(f'{DESTROY}{filename}_{file_number}_{page}{file_extension}')
                os.makedirs(os.path.dirname(local_file), exist_ok=True)

                file_response = requests.get(pic_url, stream=True)
                if file_response.status_code == 200:
                    with open(local_file, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                file.write(chunk)
                                file_number += 1
                                h.notify_send(f'Download: {file_number}', 'low')
                            else:
                                h.notify_send(f'{pic_url}:{file_response.status_code}', 'critical')
        h.notify_send('Completed Download', 'low')

search_pics()
