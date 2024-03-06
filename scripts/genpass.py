#!/bin/env python3

from typing import List
import subprocess as sp

#SPCHAR
ECHO_SPCHAR: List[str] = ['echo', '!@#$%^&*()_=+-']
FOLD: List[str] = ['fold', '-w1']
SHUF: str = 'SHUF'
HEAD_SPCHAR: List[str] = ['head', '-c1']

#PASS
DATE: List[str] = ['date', '+%s%N']
MD5SUM: str = 'md5sum'
CUT: List[str] = ['cut', '-c1-18']
HEAD_PASS: List[str] = ['head', '-c32']
ECHO_PASS: List[str] = ['echo', 'B']

#XCLIP
XCLIP: List[str] = ['xclip', '-sel', 'c']

def executioner(cmd: List[str]) -> str|None:
    try:
        output: str
        err: str
        command = sp.Popen[cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True]
        output, err = command.communicate()
        if command.returncode != 0:
            print(f'Error: {err}')
            return None
        return output.strip()
    except Exception as e:
        print('Failed to execute command {}: {}'.format(cmd, e))

def executioner_with_input(cmd: List[str], input: List[str]) -> str|None:
    try:
        output: str
        err: str
        command = sp.Popen[cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True]
        output, err = command.communicate(input=input)
        if command.returncode != 0:
            print(f'Error: {err}')
            return None
        return output.strip()
    except Exception as e:
        print('Failed to pipe {}:{}'.format(input, e))

def special_char():
    inputs: str = executioner_with_input(HEAD_SPCHAR, executioner_with_input(SHUF, executioner_with_input(FOLD, executioner(ECHO_SPCHAR))))
    echo: str = 'echo'
    cmd = sp.Popen(echo, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True)

