#!/bin/env python3

import subprocess as sp
from typing import List, Optional
import sys

PROMPT: str = "Name your python script:"
SPACE: List[str] = ["echo", "               "]
DFY: List[str] = ["dunstify", "-u", "low"]

def DMENU(prompt: str) -> Optional[str]:
    dmenu: List[str] = ["dmenu", "-m", "0", "-fn", "VictorMono:size=17:italic", "-sf", "#5F5F00", "-nf",
            "green", "-nb", "black", "-sb", "black", "-p", f"{prompt}"]
    dm_command = sp.Popen(dmenu, stdin=sp.PIPE, stdout=sp.PIPE, text=True)
    output, err = dm_command.communicate()
    if dm_command.returncode != 0:
        print(err)
        sys.exit(1)
    else:
        if output:
            return output.strip()
        else:
            print("Could not return dmenu value")
            return None

def user_input(path: str) -> Optional[List[str]]:
    SPELL: List[str] = ['wezterm', '-e', 'nvim', f'{path}']
    write_file = sp.run(SPELL, capture_output=True, text=True)
    err = write_file.stderr
    if err:
        print(err)
        return None
    else:
        write_file.stdout.splitlines()

def spell() -> Optional[str]:
    prompt_result = DMENU(PROMPT)
    if prompt_result is not None:
        user_input(prompt_result)
    else:
        print("Dmenu command failed to run properly")
        sys.exit(1)


spell()
