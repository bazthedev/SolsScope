from PIL import ImageGrab
from pynput import mouse
from pynput.mouse import Button

_mouse = mouse.Controller()


def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

while True:
    px = ImageGrab.grab().load()
    colour = px[_mouse.position]
    hex_col = rgb2hex(colour[0], colour[1], colour[2])
    print(f"{str(_mouse.position)}: {hex_col}")
