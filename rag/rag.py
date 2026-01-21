#!/bin/env python3
import subprocess as sp
import sys
from typing import Optional, List

DIR_PATH = sys.argv[1]
FZF_SELECTOR_PROMPT = 'Select Context Files'

preview_command = 'bat --style=numbers --color=always --line-range :500 {}'

def runner(cmd):
    output, err = cmd.communicate()
    if cmd.returncode != 0:
        print(err)
    else:
        if output:
            return output.strip()
        else:
            print(f"Could not print {output}, check runner method")
            sys.exit(1)

def flist(text_input):
    FZF = ['fzf', '--multi', '--layout', 'reverse', '--border', f'--border-label={text_input}',
           '--preview', preview_command]
    return FZF

def fd(path):
    fd_command = ['fd', '-tf', '.', '--full-path', f'{path}']
    fd_subcmd = sp.Popen(fd_command, stdin=sp.PIPE, stdout=sp.PIPE, text=True)
    return runner(fd_subcmd)

def context() -> Optional[List[str]]:
    fzf_command = flist(FZF_SELECTOR_PROMPT)
    selector = sp.Popen(fzf_command, stdin=sp.PIPE, stdout=sp.PIPE, text=True)
    fzf_output, fzf_err = selector.communicate(input=fd(DIR_PATH))
    file_contents = []
    if selector.returncode != 0:
        print(f'Error with fzf selection method: {fzf_err}')
    else:
        if fzf_output:
            values = fzf_output.strip().split('\n')
            for file_path in values:
                with open(file_path, 'r') as file:
                    file_contents.append(file.read().strip())
            print(file_contents)
            return file_contents

def user_prompt() -> str:
    prompt = "Enter your prompt here:"
    print(prompt)
    collection = ""
    while True:
       message = input()
       if message == "":
           break
       collection += message + '\n'
    print(collection)
    return collection

def collector():
