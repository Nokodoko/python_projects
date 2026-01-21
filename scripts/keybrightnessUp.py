#!/bin/env python3
import sys
from helpers import notify_send

FILE: str = "/sys/class/leds/kbd_backlight/brightness"
try:
    with open(FILE, "r") as file:
        current_val = int(file.read().strip())
        notify_send(f"Keyboard Brightness:{current_val}", "low")
except FileNotFoundError:
    print(f"{FILE} not found")
    sys.exit(1)
except ValueError:
    print(f"Could not convert {FILE} to an int")
    sys.exit(1)

new_val = current_val + 5

try:
    with open(FILE, "w") as file:
        file.write(str(new_val))
except IOError as e:
    print(f"IOError: {e}")
    sys.exit(1)
