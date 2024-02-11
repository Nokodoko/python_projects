#!/bin/env python3
import os
import subprocess as sp
import sys
from typing import List

USER: str = os.getenv('USER')

# TODO: :
# 1. refactor with the runner function to keep the script 'dry'


def runner(prog_list: str | None = None,
           prog: str | None = None,
           cancelled: str | None = None,
           input: str | None = None) -> str | None:
    if prog_list is None:
        output: str
        err: str
        output, err = sp.Popen(prog, stdin=sp.PIPE,
                               stdout=sp.PIPE, stderr=sp.PIPE,
                               text=True).communicate(input=input)
        if output.returncode != 0:
            print(err)
            sys.exit(1)
        else:
            if output:
                return output.strip()
            else:
                print(f'{cancelled}')
                return None
    else:
        output: str
        err: str
        output, err = sp.Popen(prog_list, stdin=sp.PIPE,
                               stdout=sp.PIPE, stderr=sp.PIPE,
                               text=True).communicate(input=input)
        if output.returncode != 0:
            print(err)
            sys.exit(1)
        else:
            if output:
                return output.strip()
            else:
                print(f'{cancelled}')
                return None


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


def proc_list(user: str) -> str | None:
    proc: List[str] = ['ps', '-u', user, "-o", "pid,comm"]
    procs = sp.Popen(proc, stdin=sp.PIPE, stdout=sp.PIPE, text=True)
    proc_ids, err = procs.communicate()
    if procs.returncode != 0:
        print(err)
        sys.exit(1)
    else:
        if proc_ids:
            return proc_ids.strip()
        else:
            print("No Selection was made")
            return None


def dmenu() -> str:
    dmenu_command = ["dmenu", "-m", "0", "-fn", "VictorMono:size=20",
                     "-nf", "green", "-nb", "black",
                     "-nf", "red", "-sb", "black"]
    dmenu = sp.Popen(dmenu_command, stdin=sp.PIPE, stdout=sp.PIPE, text=True)
    output: str
    output, _ = dmenu.communicate(input=proc_list(USER))
    if dmenu.returncode != 0:
        message = 'Cancelled Murder'
        notify_send(message, 'low')
        sys.exit(1)
    else:
        return output.strip()


def killer(pid: str) -> None:
    proc: str
    proc, proc_name = pid.split()
    slay: List[str] = ['kill', proc]
    murder = sp.Popen(slay, stdin=sp.PIPE, stdout=sp.PIPE, text=True)
    err: str
    _, err = murder.communicate()
    if murder.returncode != 0:
        failed: str = f"Failed to kill {err}"
        notify_send(failed, 'critical')
    else:
        success: str = f"Merked {proc_name}"
        notify_send(success, 'low')


killer(dmenu())
