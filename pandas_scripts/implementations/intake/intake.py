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
    "Technologies": "",
    "Application URL": "",
    "Monitoring Tiers": "",
    "Operating System": ""
}

intake_df = pd.DataFrame([question_col])

print(intake_df)


def validation(start, idx, validation_map, wksheet):
    col_letter = chr(idx + ord('A'))
    dv_range = f'{col_letter}{start}:{col_letter}1048576'
    return wksheet.data_validation(dv_range, validation_map)


with pd.ExcelWriter('APM_Implementation_Requests.xlsx', engine='xlsxwriter') as writer:
    intake_df.to_excel(
        writer, sheet_name='APM_Implementation_Requests', index=False)
    workbook = writer.book
    apm_impl_worksheet = writer.sheets['APM_Implementation_Requests']

    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        # 'valign': 'top',
        'fg_color': "#D7E4BC",
        'border': 1
    })

    for column, val in enumerate(intake_df.columns.values):
        apm_impl_worksheet.write(0, column, val, header_format)

    cloud_application = [
        "yes",
        "no"
    ]

    cloud_provider = [
        "aws",
        "azure"
        "gcp",
        "vdc"
    ]

    cloud_service = [
        "custom",
        "ec2",
        "ecr",
        "eks",
        "elb",
        "fargate",
        "lambda",
        "network_elb",
        "rds",
        "sqs",
    ]

    technologies = [
        "java",
        ".net",
        "node",
        "php",
        "python"
    ]

    os_list = [
        "rhel",
        "solaris",
        "windows"
    ]

    confirm_cloud_app = {
        'validate': 'list',
        'source': cloud_application,
        'dropdown': True
    }

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

    technologies_validation = {
        'validate': 'list',
        'source': technologies,
        'dropdown': True
    }

    os_validation = {
        'validate': 'list',
        'source': os_list,
        'dropdown': True
    }

    cloud_application_validation = validation(
        2, 4, confirm_cloud_app, apm_impl_worksheet)

    cloud_provider_validation = validation(
        2, 5, cloud_data_validation, apm_impl_worksheet)

    service_validation = validation(
        2, 6, cloud_service_validation, apm_impl_worksheet)

    technologies_validation = validation(
        2, 7, technologies_validation, apm_impl_worksheet)

    os_validation = validation(
        2, 10, os_validation, apm_impl_worksheet)

    for i, column in enumerate(intake_df.columns):
        col_len = intake_df[column].astype(str).apply(len)
        max_len = max(col_len.max(), len(column)) + 2
        apm_impl_worksheet.set_column(i, i, max_len)
