#!/bin/env python3
import json
import subprocess as sp
import pandas as pd

kube_command = ['kubectl', 'config', 'view', '-o', 'json']
aws_command = ['aws', 'sts', 'get-caller-identity']

process = sp.Popen(aws_command, stdout=sp.PIPE, stderr=sp.PIPE, text=True)
output, err = process.communicate()

if process.returncode == 0:
    data = json.loads(output)
    df = pd.json_normalize(data)
    print(df)
else:
    print(f"Could not execute {process}, err: {err}")
