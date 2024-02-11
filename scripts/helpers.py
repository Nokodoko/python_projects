#!/bin/env python3

import subprocess as sp

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
