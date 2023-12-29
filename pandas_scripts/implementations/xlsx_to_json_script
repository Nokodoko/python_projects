#!/bin/env python

import sys

FILE = sys.argv[1]
OUTPUT = sys.argv[2]


import pandas as pd
data = pd.read_excel(FILE)

json_data = data.to_json(orient='records')

with open(OUTPUT, 'w') as json_file:
    json_file.write(json_data)
