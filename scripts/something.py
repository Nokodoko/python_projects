#!/usr/bin/env python3
import sys
import os
import subprocess as sp

ARG = sys.argv[1]

if arg == 0:
    print("Need to provide an argement")
output
err
output, err = sp.Popen(
    "echo", stdin=Pipe, stdout=sp.Pipe, stderr=sp.Pipe, text=True
).communicate(input)
if output.returncode != 0:
    print(err)
    sys.exit(1)
