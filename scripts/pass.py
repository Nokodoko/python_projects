#!/bin/env python3

import os
from typing import List, Union
import subprocess as sp
import sys
import helpers as h

PASS: Union[str, None] = os.getenv('PASS')


def choice(file: str) -> List[str] | None:
    try:
        with open(file, 'r') as f:
            pw = [line.strip() for line in f if '_' in line]
            return pw
    except FileNotFoundError:
        print(f'could not open {file}')
        return None


def dmenu(list: List[str], msg: str) -> str | None:
    dmenu_command = ["dmenu", "-m", "0", "-fn", "VictorMono:size=10",
                     "-nf", "green", "-nb", "black",
                     "-nf", "cyan", "-sb", "black",
                     "-p", msg]
    try:
        with sp.Popen(dmenu_command, stdin=sp.PIPE,
                      stderr=sp.PIPE, stdout=sp.PIPE, text=True) as dm:
            output: str
            err: str
            output, err = dm.communicate(input='\n'.join(list))
            if dm.returncode != 0:
                h.notify_send(f'{err}', 'critical')
                return None
            else:
                h.notify_send(f'Selected {output.strip()}!', 'low')
                return output.strip()
    except Exception as e:
        h.notify_send(f'Error with dmenu {e}', 'critical')


def clip(selection: str) -> None:
    xclip = ['xclip', '-sel', 'c']
    clipped = sp.Popen(xclip, stdin=sp.PIPE, stdout=sp.PIPE, text=True)
    err: str
    _, err = clipped.communicate(input=selection)
    if clipped.returncode != 0:
        h.notify_send(f'No password Copied:{err}', 'critical')
    else:
        h.notify_send('Cliboard Cleared', 'low')


def parser(program: str) -> str | None:
    with open(PASS, 'r') as f:
        found = False
        for line in f:
            if found:
                clip(line.strip())
                sys.exit(0)
            if program in line:
                found = True
        h.notify_send('No password Copied', 'critical')
        print("Could not find password")
        return None


prompt = 'Select your password'
parser(dmenu(choice(PASS), prompt))
