import os


def hostname() -> str:
    hostname: str = os.getenv("router", "")
    if not hostname:
        raise ValueError("hostname variable not set")
    return hostname


def username() -> str:
    username: str = os.getenv("router_admin", "")
    if not username:
        raise ValueError("username variable not set")
    return username


def password() -> str:
    password: str = os.getenv("router_admin", "")
    if not password:
        raise ValueError("password variable not set")
    return password


if __name__ == "__main__":
    pass
