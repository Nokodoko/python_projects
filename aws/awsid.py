#!/bin/env python3

import subprocess as sp
from typing import List
import pandas as pd
import json

STS: List[str] = ['aws', 'sts', 'get-caller-identity']


def sts_caller(cmd: List[str]) -> None:
    id = sp.Popen(cmd, stdin=sp.PIPE, stdout=sp.PIPE,
                  stderr=sp.PIPE, text=True)
    output: str
    err: str
    output, err = id.communicate()
    if id.returncode != 0:
        print(err)
    else:
        caller = json.loads(output.strip())
        df: pd.DataFrame = pd.DataFrame(caller, index=['values:'])
        print(df)


sts_caller(STS)
