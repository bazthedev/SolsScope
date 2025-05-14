from pynput import mouse
from pynput.mouse import Button
from mousekey import MouseKey

mkey = MouseKey()

mkey.enable_failsafekill("ctrl+e")
_mouse = mouse.Controller()

previous_pos = None

while True:
    if previous_pos != _mouse.position:
        print(f"({str(_mouse.position[0])}/2560, {str(_mouse.position[1])}/1440)")
        previous_pos = _mouse.position
