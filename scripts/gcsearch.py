#!/usr/bin/env python3
import subprocess as sp
from typing import List
import json
import sys

DIR = "/home/n0ko/Programs/"
ARG = sys.argv[1]


def git_list(target_dir: str) -> str | None:
    fd_cmd: List[str] = ["fd", ".", "-td", "-d1", "--full-path", target_dir]
    dir_list = sp.Popen(
        fd_cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True
    )
    output: str
    err: str
    output, err = dir_list.communicate()
    if dir_list.returncode != 0:
        print(f"failed to run fd commmand: {err}")
        return None
    else:
        print(output.strip())
        return output.strip()


def push_pop(dir: str) -> None:
    push_pop_cmd: List[str] = [
        "pushd",
        dir,
        "&&",
        "gitcheckout",
        "master",
        "&&git",
        "pull",
        "&&",
        "popd",
    ]
    output: str
    err: str
    output, err = sp.Popen(
        push_pop_cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True
    )
    if push_pop_cmd != 0:
        print(f"{err}: {dir}")
        return None
    else:
        print(output.strip())


def search_repositories(query: str):
    query_template = (
        """
    {
      search(query: "%s", type: REPOSITORY, first: 10) {
        nodes {
          ... on Repository {
            nameWithOwner
            description
            url
          }
        }
      }
    }
    """
        % query
    )

    result = sp.run(
        ["gh", "api", "graphql", "-f", f"query={query_template}"],
        stdout=sp.PIPE,
        stderr=sp.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise Exception(f"GraphQL query failed: {result.stderr}")

    output = json.loads(result.stdout)
    for item in output["data"]["search"]["nodes"]:
        url = item["url"]
        return url


def git_pull(programs: List[str]) -> None:
    for dir in programs.split("\n"):
        git_cmd: List[str] = ["git", "pull", f"{dir}"]
        puller = sp.Popen(
            git_cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True
        )
        output: str
        err: str
        output, err = puller.communicate()
        if puller.returncode != 0:
            print(f"failed to pull directory: {dir}", err)
        else:
            print(output.strip())


if __name__ == "__main__":
    print(search_repositories(ARG))
    # git_pull(search_repositories(ARG))


# function gsearch() {
#  gh api graphql -f query="
#  {
#    search(query: \"$1\", type: REPOSITORY, first: 10) {
#      nodes {
#        ... on Repository {
#          nameWithOwner
#          description
#          url
#        }
#      }
#    }
#  }" | jq '.data.search.nodes[]|.url' | flisty "GIT SEARCH FOR $1" | sed 's/"//g'
# }
