from PIL import ImageGrab
import json, os
import screeninfo as si


screens = si.get_monitors()
monitor = None
for mon in screens:
    if mon.is_primary:
        monitor = mon
scale_w = monitor.width / 2560
scale_h = monitor.height / 1440

x = []

def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

MACROPATH = os.path.expandvars(r"%localappdata%\\Baz's Macro") # Windows Roaming Path

default_pos = (1280 * scale_w, 720 * scale_h)
secondary_pos = (564 * scale_w, 401 * scale_h)

while True:
    px = ImageGrab.grab().load()
    colour = px[default_pos[0], default_pos[1]]
    hex_col = rgb2hex(colour[0], colour[1], colour[2])
    colour2 = px[secondary_pos[0], secondary_pos[1]]
    hex_col2 = rgb2hex(colour2[0], colour2[1], colour2[2])
    print(f"{hex_col},{hex_col2}")
    x.append(f"{hex_col},{hex_col2}")
    if len(x) > 400:
        break
    
with open(f"{MACROPATH}/aura_dump.json", "w") as f:
    json.dump(x, f, indent=4)
