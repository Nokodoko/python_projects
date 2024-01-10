#!/bin/env python

import sys
import pandas as pd

FILE = sys.argv[1]
OUTPUT = sys.argv[2]

with open(FILE, 'r') as json_file:
    data = pd.read_json(json_file, orient='records')
# Save to Excel
data.to_excel(OUTPUT)
