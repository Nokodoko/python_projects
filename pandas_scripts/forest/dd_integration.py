#!/bin/env python3

import os
import requests
import pandas as pd

# TODO:
# Is there a dynamic way to include growing list of applications?

api_key = os.getenv("DD_API_KEY")
app_key = os.getenv("DD_APP_KEY")
aws = "aws"
azure = "azure"

account_ids = {
    "007911250085": "FEMS",
    "066399073050": "CIAO",
    "107895115286": "LLC",
    "112364832438": "UAVS",
    "114245151275": "WFWEB",
    "171226545153": "NRMBP",
    "175560568060": "HWP",
    "227101269271": "HDWI",
    "328762180115": "CFTEAM",
    "403938590038": "GPH",
    "407464523575": "WFSAFE",
    "504420026195": "INCIWEB",
    "515022543707": "FSAPPSE",
    "583937734902": "VDR",
    "744281823657": "PAT",
    "748257752168": "NMIS-GrowHub",
    "878733051466": "Admin",
    "899201081254": "AFF",
}

headers = {
    "Accept": "application/json",
    "DD-API-KEY": api_key,
    "DD-APPLICATION-KEY": app_key,
}


def integrations(app_id, app_name):
    link = f"https://api.ddog-gov.com/api/v1/integration/aws/filtering?account_id={app_id}"
    url = link
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"{response.status_code} for {app_name}")
        return pd.DataFrame()
    else:
        result = [item["namespace"] for item in response.json()["filters"]]
        df = pd.DataFrame(result, columns=['cloud_service'])
        return df


def integration_writer(list, cloud_service):
    integration_list = pd.DataFrame()
    for account_id, application_name in list.items():
        print(application_name)
        df = integrations(account_id, application_name)
        if not df.empty:
            df['application_name'] = application_name
            df['account_id'] = account_id
            integration_list = pd.concat(
                [integration_list, df], ignore_index=True)
    integration_list.columns = [column.upper()
                                for column in integration_list.columns]
    with pd.ExcelWriter('integrations_list.xlsx', engine='xlsxwriter') as writer:
        integration_list.to_excel(
            writer, sheet_name=f'{cloud_service}_list', index=False)
        workbook = writer.book
        worksheet = writer.sheets[f'{cloud_service}_list']

        for i, column in enumerate(integration_list.columns):
            column_len = integration_list[column].astype(
                str).apply(len)
            max_len = max(column_len.max(), len(column)) + 2
            worksheet.set_column(i, i, max_len)

        account_name_index = integration_list.columns.get_loc(
            'APPLICATION_NAME')

    worksheet.autofilter(0, account_name_index, len(
        integration_list), account_name_index)


integration_writer(account_ids, aws)

if __name__ == "__main__":
    pass
