#!/usr/bin/env python3

import requests
import sys

URL = sys.argv[1]
response = requests.get(URL)
print(response.status_code)
