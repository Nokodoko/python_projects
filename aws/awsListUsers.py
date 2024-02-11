#!/bin/env python3

import subprocess as sp
from typing import List
import sys
import json
import helpers as h


USERS: List[str] = ['aws', 'iam', 'list-users']


# TODO:
# 1.create dmenu as a module,
# import dmenu and call list_users in the dmenu function

def list_users(userlist: List[str]) -> List[str]:
    ls = sp.Popen(userlist, stdin=sp.PIPE, stdout=sp.PIPE,
                  stderr=sp.PIPE, text=True)
    users: str
    err: str
    users, err = ls.communicate()
    if ls.returncode != 0:
        print(err)
        sys.exit(1)
    else:
        everyone = json.loads(users.strip())
        names = [item['UserName'] for item in everyone['Users']]
        return names

dmenu_prompt = "Select User"
ns_message = "Selected!"
h.dmenu( list_users(USERS),'cyan',ns_message, dmenu_prompt)
