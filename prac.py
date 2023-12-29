#!/bin/env python

import os 
import subprocess as sp


PATH = os.curdir

FZF = ['fzf', '--reverse']

LIST = '\n'.join(os.listdir(PATH)).encode()

process = sp.Popen(FZF, stdin=sp.PIPE)
process.communicate(input=LIST)



#!/usr/bin/env python
#
#import os 
#import subprocess as sp
#
#PATH = os.curdir
#
## The command should be a list of strings where the first string is the command and the rest are arguments
#FZF = ['fzf']
#
## os.pipe() is used to create a pipe between two processes. Here, we want to pass the output of os.listdir() to FZF.
## This can be achieved by using subprocess.Popen().
#
## First, we convert the list of directory names to a byte stream
#dir_names = '\n'.join(os.listdir(PATH)).encode()
#
## Then, we create a subprocess with stdin from PIPE and pass the byte stream to it
#process = sp.Popen(FZF, stdin=sp.PIPE)
#process.communicate(input=dir_names)
#
