#!/bin/env python3

import subprocess as sp
import json
kube_cmd = ['kubectl', 'config', 'view', '-o', 'json']


def config():
    kube = sp.Popen(kube_cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    output, err = kube.communicate()
    if kube.returncode != 0:
        print(f"Error: {err.decode()}")
    else:
        jbody = json.loads(output)
        apiVersion = jbody['apiVersion']
        print(apiVersion)


config()
