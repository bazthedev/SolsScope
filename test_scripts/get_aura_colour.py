from PIL import ImageGrab

def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

default_pos = (1280, 720)

while True:
    px = ImageGrab.grab().load()
    color = px[default_pos[0], default_pos[1]]
    hex_col = rgb2hex(color[0], color[1], color[2])
    print(hex_col)
