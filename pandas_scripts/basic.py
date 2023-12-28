#!/bin/env python3

# import numpy as np
import pandas as pd


index_1 = [0, 1, 2, 3]

data_1 = [
    "leo",
    "don",
    "mikey",
    "raph"
]

data_2 = {
    data_1[0]: "leader",
    data_1[1]: "engineer",
    data_1[2]: "comic",
    data_1[3]: "spirit",
}

s1 = pd.Series(data_1, index=index_1)
role_list = s1.map(data_2)

df = pd.DataFrame({
    'name_list': s1,
    'role_list': role_list
})

with pd.ExcelWriter('testing_pandas.xlsx', engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='turtles', index=False)
    worksheet = writer.sheets['turtles']
    for i, col in enumerate(df.columns):
        col_len = df[col].astype(str).apply(len)
        max_len = max(col_len.max(), len(col)) + 2
        worksheet.set_column(i, i, max_len)
print(s1)
print(role_list)
print(f"max: { s1.max() }\n")
print(f"min: { s1.min() }")
