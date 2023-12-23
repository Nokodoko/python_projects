#!/bin/env python3
import xlsxwriter
import os
import requests
import pandas as pd

# TODO:
# IS THERE A DYNAMIC WAY TO INCLUDE GROWING LIST OF APPLICATIONS?
# BOILERPLATE PYTHON GUARD CLAUSE

api_key = os.getenv("DD_API_KEY")
app_key = os.getenv("DD_APP_KEY")

account_ids = {
    "007911250085": "FEMS",
    "066399073050": "CIAO",
    "107895115286": "LLC",
    # "112364832438": "UAVS",
    # "114245151275": "WFWEB",
    # "171226545153": "NRMBP",
    # "175560568060": "HWP",
    # "227101269271": "HDWI",
    # "328762180115": "CFTEAM",
    # "403938590038": "GPH",
    # "407464523575": "WFSAFE",
    # "504420026195": "INCIWEB",
    # "515022543707": "FSAPPSE",
    # "583937734902": "VDR",
    # "744281823657": "PAT",
    # "748257752168": "NMIS-GrowHub",
    # "878733051466": "Admin",
    # "899201081254": "AFF",
}

headers = {
    "Accept": "application/json",
    "DD-API-KEY": api_key,
    "DD-APPLICATION-KEY": app_key,
}


def integrations(id):
    link = f"https://api.ddog-gov.com/api/v1/integration/aws/filtering?account_id={id}"
    url = link
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        # TODO: ADD NAME TO ERROR AND NO JUST ID
        # RENAME NAMESPACE COLUMN TO SOMETHING MORE RELEVANT (I.E. CLOUD_SERVICE -- MIGHT NEED TO FOLLOW CONVENTIONAL URL RULES)
        print(f"{response.status_code} for {id}")
        return pd.DataFrame()
    else:
        result = [item["namespace"] for item in response.json()["filters"]]
        df = pd.DataFrame(result, columns=['namespace'])
        return df


def integration_writer(account_list):
    integration_file = pd.DataFrame()
    writer = pd.ExcelWriter('fs_integrations_list.xlsx',
                            engine='xlsxwriter')
    # .writer = pd.ExcelWriter('fs_integrations_list.xlsx', engine='xlsxwriter')
    workbook = writer.book
    worksheet = workbook.add_worksheet('Integration_List')

    for account_id, account_name in account_list.items():
        print(account_name)
        df = integrations(account_id)
        if not df.empty:
            df['account_name'] = account_name
            df['account_id'] = account_id
            integration_file = pd.concat(
                [integration_file, df], ignore_index=True)

    integration_file.to_excel(
        writer, sheet_name='Integration_List', index=False)

    data_validation_options = {
        'validate': 'list',
        'source': list(account_list.values()),
        'input_message': 'Choose account name',
        'error_message': 'Invalid Selection'
    }
    worksheet.data_validation('B2:B{}'.format(
        len(account_list) + 1), data_validation_options)

    writer._save()


integration_writer(account_ids)

if __name__ == "__main__":
    integration_writer(account_ids)
