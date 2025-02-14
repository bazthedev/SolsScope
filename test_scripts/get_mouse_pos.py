from pynput import mouse
from pynput.mouse import Button

_mouse = mouse.Controller()

while True:
    print(f"{str(_mouse.position)}")
