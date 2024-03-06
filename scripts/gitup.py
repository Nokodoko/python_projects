#!/bin/env python3

import subprocess as sp
from typing import List

DIR = '/home/n0ko/Programs/'

def git_list(target_dir: str) -> str|None:
    fd_cmd: List[str] = ['fd', '.', '-td', '-d1', '--full-path', target_dir]
    dir_list = sp.Popen(fd_cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True)
    output: str
    err: str
    output, err = dir_list.communicate()
    if dir_list.returncode != 0:
        print(f'failed to run fd commmand: {err}')
        return None
    else:
        print(output.strip())
        return output.strip()

def push_pop(dir: str) -> None:
    push_pop_cmd: List[str] = ['pushd', dir, '&&', "git"
                               'checkout', 'master', '&&'
                               'git', 'pull', '&&', 'popd']
    output: str
    err: str
    output, err = sp.Popen(push_pop_cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True)
    if push_pop_cmd != 0:
        print(f'{err}: {dir}')
        return None
    else:
        print(output.strip())


def git_pull(programs: List[str]) -> None:
    for dir in programs.split('\n'):
        git_cmd: List[str] = ['git', 'pull', f'{dir}']
        puller = sp.Popen(git_cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True)
        output: str
        err: str
        output, err = puller.communicate()
        if puller.returncode != 0:
            print(f'failed to pull directory: {dir}', err)
        else:
            print(output.strip())


git_pull(git_list(DIR))
