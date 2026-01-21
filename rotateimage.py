#!/usr/bin/env python3
import subprocess as sp
import os

# IMAGE = sp.run(["podman", "images", "--name", "eauth"])
# ["podman", "ps", '--format"{{.IMAGE}}"']
# PRUNE = sp.run(["podman", "rm", f"{IMAGE}"])

# CONSTANTS
CONTAINERNAME = ["podman", "ps", '--format"{{.Names}}"']
IMAGENAME = "gcr.io/datadoghq/synthetics-private-location-worker:latest"
PODMANIMAGELISTER = ["podman", "image", "ls"]
IMAGEREMOVER = sp.run(["podman", "image", "rm", IMAGENAME])
PODMANCONTAINERLIST = sp.run(["podman", "ps"])
PULLCOMMAND = [
    "podman",
    "run",
    "--rm",
    "-v",
    "$PWD/worker-config-e_auth-1dfda7758e6eb02738989ddc03348e62.json:/etc/datadog/synthetics-check-runner.json",
    "gcr.io/datadoghq/synthetics-private-location-worker:latest",
]


# FUNCTIONS
def podmanPuller() -> None:
    podmanPull = sp.Popen(
        PULLCOMMAND, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True
    )
    podmanPull.communicate()
    if podmanPull.returncode not in (0, 125):
        print(f"Error pulling new private location image: {podmanPull.returncode},")
    print("image pull successful:")
    sp.run(PODMANIMAGELISTER)

    # TODO:test then convert to systemctl stop container


def containerStopper(containerName: str) -> None:
    # containerstop = [("systemctl", "stop", {containerName})]
    containerstop = ["podman", "stop", containerName]
    runner = sp.Popen(
        containerstop, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True
    )
    if runner.returncode != 0:
        print(f"Error stopping container: {containerName}")
    print(f"Removed: {containerName}")


def imageRemover(imageName: str) -> None:
    containerstop = ["podman", "rm", imageName]
    runner = sp.Popen(
        containerstop, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True
    )
    if runner.returncode != 0:
        print(f"Error removing image {imageName}")
    print(f"removed {imageName}")


# STOP CONTAINERS WITH DATED IMAGE
for i in range(PODMANCONTAINERLIST):
    if IMAGENAME in i:
        containerStopper(i)


# REMOVE DATED IMAGES


# DIRECTORY MANAGEMENT
os.chdir("/etc/datadog/")
print("Now in", os.getcwd())
print("Pulling Image")

# NOTE: TO STREAM OUTPUT WHILE PULLING IMAGE
# def podmanRunner():
#     podmanPull = sp.Popen(PULL_COMMAND, stdout=sp.PIPE, stderr=sp.STDOUT)
#     for line in iter(podmanPull.stdout.readline, b""):
#         print(line.decode(), end="")
#     podmanPull.stdout.close()
#     return_code = podmanPull.wait()
#     if return_code != 0:
#         print(
#             f"Error pulling new private location image with return code: {return_code}"
#         )


podmanPuller()


def podmanServiceCreate() -> None:
    podmanPull = sp.Popen(PULLCOMMAND, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    podmanPull.communicate()
    if podmanPull.returncode not in (0, 125):
        print(f"Error pulling new private location image: {podmanPull.returncode},")
    print("image pull successful:")
    sp.run(PODMANIMAGELISTER)


# create service


# if __name__ == "__main__":
#     podmanRunner()
