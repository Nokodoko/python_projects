#!/bin/env python3

import subprocess as sp
import sys
from typing import List

def notify_send(msg: str, criticality: str) -> str | None:
    match criticality:
        case 'low':
            ns: List[str] = ['notify-send', '-u', 'low', f'{msg}']
            notify = sp.Popen(ns, stdin=sp.PIPE, stdout=sp.PIPE, text=True)
            output: str
            err: str
            output, err = notify.communicate()
            if notify.returncode != 0:
                print(f"Error running notify-send: {err}")
                return None
            else:
                return output.strip()
        case 'critical':
            ns: List[str] = ['notify-send', '-u', 'critical', f'{msg}']
            notify = sp.Popen(ns, stdin=sp.PIPE, stdout=sp.PIPE, text=True)
            output: str
            err: str
            output, err = notify.communicate()
            if notify.returncode != 0:
                print(f"Error running notify-send: {err}")
                return None
            else:
                return output.strip()

def dmenu(input: List[str], msg_fg:str, ns_msg:str, prompt:str) -> str|None:
    dmenu_command = ["dmenu", "-m", "0", "-fn", "VictorMono:size=20",
                     "-nf", "green", "-nb", "black",
                     "-nf", msg_fg, "-sb", "black", '-p', prompt]
    dmenu = sp.Popen(dmenu_command, stdin=sp.PIPE, stdout=sp.PIPE, text=True)
    output: str
    output, _ = dmenu.communicate(input='\n'.join(input))
    if dmenu.returncode != 0:
        message = ns_msg
        notify_send(message, 'low')
        sys.exit(1)
    else:
        return output.strip()

if __name__ == "__main__":
    pass
