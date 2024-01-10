#!/bin/env python3


import pandas as pd
import xlsxwriter

worksheet_name = 'test_excelfile.xlsx'
df = pd.DataFrame(["10, 20, 30"], columns=['numbers'])

writer = pd.ExcelWriter(f'{worksheet_name}', engine='xlsxwriter')
