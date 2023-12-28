#!/bin/env python3

import json
import pandas as pd

json_file = './data.json'
with open(json_file, 'r') as file:
    json_data = json.load(file)

rows = []
# rows2 = []

for values in json_data:
    app_name = values.get('App Name')
    poc = values.get('TPOC 1')
    poc2 = values.get('TPOC 2')
    owner = values.get('Owner')

    new_row = {
        'Service': app_name,
        'Owner': owner,
        'POC': [poc, poc2]
    }

    rows.append(new_row)

jdf1 = pd.DataFrame(rows)

tasks_df = {
    "Requirements": "",
    "DEV/Sandbox": "",
    "CRQ": "",
    "TEST Task Number": "",
    "TEST Environment": "",
    "DEV Agent Removal": "",
    "TEST Task Number": "",
    "DEV Agent Removal": "",
    "PROD Task Number": "",
    "PROD Environment": "",
    "TEST Agent Removal": "",
}
jdf2 = pd.DataFrame([tasks_df])

# for values in json_data:
#    location = values.get('ServerCount')
#
#    more_rows = {
#        "Location": location
#    }
#
#    rows2.append(more_rows)
#
# jdf3 = pd.DataFrame([rows2])

combined_Dataframe = pd.concat(
    [jdf1, jdf2], ignore_index=True, sort=False)
print(combined_Dataframe)

with pd.ExcelWriter('implementations.xlsx', engine='xlsxwriter') as writer:
    combined_Dataframe.to_excel(
        writer, sheet_name='implementations', index=False)
    workbook = writer.book
    worksheet = writer.sheets['implementations']

    cell_format = workbook.add_format({'align': 'left'})

    for i, column in enumerate(combined_Dataframe.columns):
        col_len = combined_Dataframe[column].astype(str).apply(len)
        max_len = max(col_len.max(), len(column)) + 1
        worksheet.set_column(i, i, max_len, cell_format)

#
# json_df_2 = pd.DataFrame(columns=[
#    "LOCATION",
# ])
#
# datadog_infrastructure_df = {
#
# }
