#!/bin/env python3

import pandas as pd

question_col = {
    "Application Owner": "",
    "Owner Email Address": "",
    "TPOC": "",
    "TPOC Email Address": "",
    "Cloud Application": "",
    "Cloud Provider": "",
    "Cloud Service Used": "",
    "Tech Stack": "",
    "Application URL": "",
    "Monitoring Tiers": "",
    "Operating System": ""
}

intake_df = pd.DataFrame([question_col])

print(intake_df)


def validation(start, idx, validation_map, wksheet):
    col_letter = chr(idx + ord('A'))
    dv_range = f'{col_letter}{start}:{col_letter}{start}'
    return wksheet.data_validation(dv_range, validation_map)


with pd.ExcelWriter('APM_Implementation_Requests.xlsx', engine='xlsxwriter') as writer:
    intake_df.to_excel(
        writer, sheet_name='APM_Implementation_Requests', index=False)
    workbook = writer.book
    apm_impl_worksheet = writer.sheets['APM_Implementation_Requests']

    cloud_provider = [
        "aws",
        "azure"
        "gcp",
    ]

    cloud_service = [
        "ec2",
        "ecr",
        "eks",
        "fargate",
    ]

    cloud_data_validation = {
        'validate': 'list',
        'source': cloud_provider,
        'dropdown': True
    }

    cloud_service_validation = {
        'validate': 'list',
        'source': cloud_service,
        'dropdown': True
    }

    cloud_provider_validation = validation(
        2, 5, cloud_data_validation, apm_impl_worksheet)

    service_validation = validation(
        2, 6, cloud_service_validation, apm_impl_worksheet)

    for i, column in enumerate(intake_df.columns):
        col_len = intake_df[column].astype(str).apply(len)
        max_len = max(col_len.max(), len(column)) + 2
        apm_impl_worksheet.set_column(i, i, max_len)
