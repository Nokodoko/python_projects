#!/bin/env python3

dir_path = "/home/n0ko/rag_files/"
fzf_selector_prompt = "Select Context Files"
dmenu = "dmenu -m 0 -fn VictorMono:size=20 \
-nf green -nb black -nf green -sb black"


def flist(text_input):
    fzf = f'fzf --layout reverse --border --border-label="{text_input}" \
    --preview "bat --style=numbers --color=always --line-range :500 {{"}}"'
    return fzf
