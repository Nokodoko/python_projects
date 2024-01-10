#!/bin/env python3

import pandas as pd

json_file = '../data.json'
json_data = pd.read_json(json_file)

description = json_data.describe(include='all')
mean = description.mean()
print(description.T)
print(f"\t{mean}")

# app_name = description.at['unique', 'App Name']
# descript = description.at['unique', 'Description']
# serverCount = description.at['unique', 'ServerCount']
# owner = description.at['unique', 'Owner']
# tpoc1 = description.at['unique', 'TPOC 1']
# tpoc2 = description.at['unique', 'TPOC 2']
#
# print(f"App Name: {app_name}")
# print(f"Description: {descript}")
# print(f"Server Count: {serverCount}")
# print(f"Owner: {owner}")
# print(f"TPOC1: {tpoc1}")
# print(f"TPOC2: {tpoc2}")
