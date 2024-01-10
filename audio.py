#!/bin/env python3

import subprocess as sp
import json
import sys

list_sinks = ['pactl', '-f', 'json', 'list', 'sinks', 'short']
sink_inputs = ['pactl', '-f', 'json', 'list', 'sink-inputs']
FZF = ['fzf', '--reverse', '--prompt', 'Select Device']


def list_dev():
    lister = sp.Popen(list_sinks, stdout=sp.PIPE, stderr=sp.PIPE, text=True)
    output, err = lister.communicate()
    if lister.returncode != 0:
        print(f"Error: {err},\nexiting")
        sys.exit(1)
    else:
        dev_list = json.loads(output)
        dev_name = [item['name'] for item in dev_list]
        return dev_name


def fzf(list):
    if list is None:
        return
    else:
        input = '\n'.join(list)
        fzf_command = sp.Popen(FZF, stdin=sp.PIPE, text=True)
        fzf_command.stdin.write(''.join(input.strip()))
        fzf_command.stdin.close()
        return_code = fzf_command.wait()
        if return_code != 0:
            print(f"Error:{return_code}")
            sys.exit(1)
        else:
            return fzf_command.stdout


# device_list = list_dev()
# fzf(device_list)


# jq '.[]|.properties."media.name"'
def list_sink_inputs():
    sinks = sp.Popen(sink_inputs, stdin=sp.PIPE,
                     stdout=sp.PIPE, stderr=sp.PIPE, text=True)
    output, err = sinks.communicate()
    if sinks.returncode != 0:
        print(f"Error: {err}")
    else:
        sink_output = json.loads(output)
        list = [item['properties']['media.name'] for item in sink_output]
        index = [item['index'] for item in sink_output]
        for name in list:
            print(f"{name}")
            for idx in index:
                print(f"\t{idx}")


list_sink_inputs()
