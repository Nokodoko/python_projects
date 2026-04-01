#!/bin/env python3

import os
from typing import List
import subprocess as sp
import sys
import helpers as h

PASS: str = os.getenv('PASS', '')


def choice(file: str) -> List[str] | None:
    try:
        with open(file, 'r') as f:
            pw = [line.strip().replace(r'\_', '_') for line in f if line.strip().endswith(r'\_')]
            return pw
    except FileNotFoundError:
        print(f'could not open {file}')
        return None


def rofi(list: List[str], msg: str) -> str | None:
    rofi_command = ["rofi", "-dmenu",
                    "-theme", "Arc-Dark",
                    "-font", "VictorMono Nerd Font Mono 11",
                    "-m", "0",
                    "-theme-str", "window { location: center; }",
                    "-p", "\uf023",
                    "-mesg", msg,
                    "-i"]
    try:
        with sp.Popen(rofi_command, stdin=sp.PIPE,
                      stderr=sp.PIPE, stdout=sp.PIPE, text=True) as rm:
            output: str
            err: str
            output, err = rm.communicate(input='\n'.join(list))
            if rm.returncode != 0:
                h.notify_send(f'{err}', 'critical')
                return None
            else:
                h.notify_send('Selected!', 'low')
                return output.strip()
    except Exception as e:
        h.notify_send(f'Error with rofi {e}', 'critical')


def clip(password: str) -> None:
    xclip = ['xclip', '-sel', 'c', '-l', '1']
    result = sp.run(xclip, input=password, text=True, stderr=sp.PIPE)
    if result.returncode != 0:
        h.notify_send(f'No password Copied:{result.stderr}', 'critical')
    else:
        h.notify_send('Password Copied!', 'low')
#


def parser(program: str) -> str | None:
    with open(PASS, 'r') as f:
        found = False
        for line in f:
            if found:
                clip(line.strip())
                sys.exit(0)
            cleaned = line.replace(r'\_', '_')
            if program in cleaned:
                found = True
        h.notify_send('No password Copied', 'critical')
        print("Could not find password")
        return None


if not PASS:
    h.notify_send('PASS env var not set', 'critical')
    sys.exit(1)

prompt = 'Select your password'
entries = choice(PASS)
if not entries:
    sys.exit(1)

selection = rofi(entries, prompt)
if not selection:
    sys.exit(1)

parser(selection)
