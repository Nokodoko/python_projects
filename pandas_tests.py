#!/bin/env python3

from operator import index
import pandas as pd

df = pd.DataFrame({'integrations': [10, 20, 30, 40]})

df.to_excel('test.xlsx', index=False)
