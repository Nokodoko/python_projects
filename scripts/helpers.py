#!/bin/env python3
import subprocess as sp
from typing import List
import sys


def dmenu(color: str, prompt: str) -> str:
    dmenu_command: List[str] = ["dmenu", "-m", "0", "-fn", "VictorMono:size=20",
                                "-nf", "green", "-nb", "black",
                                "-nf", color, "-sb", "black", "-p", prompt]
    dmenu = sp.Popen(dmenu_command, stdin=sp.PIPE, stdout=sp.PIPE, text=True)
    output: str
    output, err = dmenu.communicate()
    if dmenu.returncode != 0:
        notify = err
        notify_send(notify, 'low')
        sys.exit(1)
    else:
        return output.strip()


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


if __name__ == "__main__":
    pass
