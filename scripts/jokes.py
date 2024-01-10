#!/bin/env python3

import requests
import json
# import pandas as pd

url = 'https://api.chucknorris.io/jokes/random'

data = requests.get(url)

if data.status_code == 200:
    value = data.json().get('value')
    if value is not None:
        pretty_value = json.dumps(value, indent=4)
        print(pretty_value)
    else:
        print(f'could not find value {data.status_code}')

# WORKING PANDAS SCRIPT
# joke = requests.get(url)

# if joke.status_code != 200:
#    print(f"Error: {joke.status_code}")
# else:
#    response = joke.json()
#    j_response = joke.text
#    df = pd.json_normalize(response)
#    df.describe().T
#    print(df)
#
#    j_obj = json.loads(j_response)
#    job_df = pd.json_normalize(j_obj)
#    job_df.describe().T
#    print(job_df)
