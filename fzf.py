#!/usr/bin/env python3
import sys
import subprocess as sp
import os

DIRS = os.listdir(".")
FZF = ["fzf", "--prompt", "Search: "]


def fzf(list):
    if list is None:
        print("no list to filter")
        return
    input: str = "\n".join(list)
    fzf_command: sp.Popen[str] = sp.Popen(FZF, stdin=sp.PIPE, stdout=sp.PIPE, text=True)
    output = []
    output, _ = fzf_command.communicate(input=input.encode())
    if fzf_command.returncode != 0:
        print(f"Error:{fzf_command.returncode}")
        sys.exit(1)
    return output.strip()


fzf(DIRS)
