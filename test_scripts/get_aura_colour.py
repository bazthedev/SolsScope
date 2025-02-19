from PIL import ImageGrab

def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

default_pos = (1280, 720)
secondary_pos = (564, 401)
tertiary_pos = (2049, 1118)
temp = []
while True:
    px = ImageGrab.grab().load()
    colour = px[default_pos[0], default_pos[1]]
    hex_col = rgb2hex(colour[0], colour[1], colour[2])
    colour2 = px[secondary_pos[0], secondary_pos[1]]
    hex_col2 = rgb2hex(colour2[0], colour2[1], colour2[2])
    colour3 = px[tertiary_pos[0], tertiary_pos[1]]
    hex_col3 = rgb2hex(colour3[0], colour3[1], colour3[2])
    print(f"{hex_col},{hex_col2},{hex_col3}")
