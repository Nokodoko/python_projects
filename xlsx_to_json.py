#!/bin/env python


import pandas as pd
data = pd.read_excel('~/Downloads/FS Application Monitoring - List of Applications v2 - with POCs (2).xlsx')

json_data = data.to_json(orient='records')

with open('data.json', 'w') as json_file:
    json_file.write(json_data)
