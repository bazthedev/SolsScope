# Made using ReTask by JustSoftware & cresqnt

CPU_INTENSIVE_HIGH_ACCURACY_SLEEP = True
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
from mousekey import MouseKey
from time import sleep, perf_counter
from fractions import Fraction

NONVIP = False
SCALE = float(Fraction(342, 277))
SCALE = 1.25

def preprocess_macro(macro, nonvip=True):
    processed = []
    for action in macro:
        if action["type"] == "wait":
            new_action = action.copy()
            if nonvip:
                new_action["duration"] = (action["duration"] * SCALE)
            processed.append(new_action)
        else:
            processed.append(action.copy())
    return processed

kc = KeyboardController()
mc = MouseController()
mkey = MouseKey()


pynput_special_keys = {
    "Key.alt": Key.alt,
    "Key.alt_l": Key.alt_l,
    "Key.alt_r": Key.alt_r,
    "Key.backspace": Key.backspace,
    "Key.caps_lock": Key.caps_lock,
    "Key.cmd": Key.cmd,
    "Key.cmd_l": Key.cmd_l,
    "Key.cmd_r": Key.cmd_r,
    "Key.ctrl": Key.ctrl,
    "Key.ctrl_l": Key.ctrl_l,
    "Key.ctrl_r": Key.ctrl_r,
    "Key.delete": Key.delete,
    "Key.down": Key.down,
    "Key.end": Key.end,
    "Key.enter": Key.enter,
    "Key.esc": Key.esc,
    "Key.f1": Key.f1,
    "Key.f2": Key.f2,
    "Key.f3": Key.f3,
    "Key.f4": Key.f4,
    "Key.f5": Key.f5,
    "Key.f6": Key.f6,
    "Key.f7": Key.f7,
    "Key.f8": Key.f8,
    "Key.f9": Key.f9,
    "Key.f10": Key.f10,
    "Key.f11": Key.f11,
    "Key.f12": Key.f12,
    "Key.home": Key.home,
    "Key.insert": Key.insert,
    "Key.left": Key.left,
    "Key.menu": Key.menu,
    "Key.num_lock": Key.num_lock,
    "Key.page_down": Key.page_down,
    "Key.page_up": Key.page_up,
    "Key.pause": Key.pause,
    "Key.print_screen": Key.print_screen,
    "Key.right": Key.right,
    "Key.scroll_lock": Key.scroll_lock,
    "Key.shift": Key.shift,
    "Key.shift_l": Key.shift_l,
    "Key.shift_r": Key.shift_r,
    "Key.space": Key.space,
    "Key.tab": Key.tab,
    "Key.up": Key.up
}

pynput_special_buttons = {
    "Button.left": Button.left,
    "Button.right": Button.right,
    "Button.middle": Button.middle
}

def run_macro(macro, delay=2):
    sleep(delay)

    for action in macro:
        match action["type"]:
            case "wait":
                sleep(action["duration"] / 1000.0)
            case "key_press":
                key = action["key"]
                kc.press(pynput_special_keys.get(key, key))
            case "key_release":
                key = action["key"]
                kc.release(pynput_special_keys.get(key, key))
            case "mouse_movement":
                mkey.move_to(int(action["x"]), int(action["y"]))
            case "mouse_press":
                mc.press(pynput_special_buttons[action["button"]])
            case "mouse_release":
                mc.release(pynput_special_buttons[action["button"]])
            case "mouse_scroll":
                if "x" in action:
                    mkey.move_to(int(action["x"]), int(action["y"]))
                mc.scroll(action["dx"], action["dy"])


macro_actions = [
{'type': 'wait', 'duration': 10},    
{'type': 'key_press', 'key': 'd'},
{'type': 'wait', 'duration': 8},
{'type': 'key_press', 'key': 'w'},
{'type': 'wait', 'duration': 2415},
{'type': 'key_release', 'key': 'w'},
{'type': 'wait', 'duration': 4917},
{'type': 'key_release', 'key': 'd'},
{'type': 'wait', 'duration': 140},
{'type': 'key_press', 'key': 's'},
{'type': 'wait', 'duration': 319},
{'type': 'key_press', 'key': 'd'},
{'type': 'wait', 'duration': 533},
{'type': 'key_release', 'key': 'd'},
{'type': 'wait', 'duration': 88},
{'type': 'key_press', 'key': 'd'},
{'type': 'wait', 'duration': 290},
{'type': 'key_release', 'key': 'd'},
{'type': 'wait', 'duration': 76},
{'type': 'key_release', 'key': 's'},
{'type': 'wait', 'duration': 161},
{'type': 'key_press', 'key': 'w'},
{'type': 'wait', 'duration': 160},
{'type': 'key_release', 'key': 'w'},
{'type': 'wait', 'duration': 62},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 127},
{'type': 'key_press', 'key': 'd'},
{'type': 'wait', 'duration': 32},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 447},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 143},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 1390},
{'type': 'key_press', 'key': 'w'},
{'type': 'wait', 'duration': 424},
{'type': 'key_release', 'key': 'w'},
{'type': 'wait', 'duration': 1950},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 195},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 319},
{'type': 'key_release', 'key': 'd'},
{'type': 'wait', 'duration': 223},
{'type': 'key_press', 'key': 'd'},
{'type': 'wait', 'duration': 16},
{'type': 'key_press', 'key': 's'},
{'type': 'wait', 'duration': 331},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 171},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 549},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 205},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 273},
{'type': 'key_release', 'key': 'd'},
{'type': 'wait', 'duration': 181},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 202},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 123},
{'type': 'key_release', 'key': 's'},
{'type': 'wait', 'duration': 223},
{'type': 'key_press', 'key': 'd'},
{'type': 'wait', 'duration': 34},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 211},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 392},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 180},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 860},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 224},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 187},
{'type': 'key_release', 'key': 'd'},
{'type': 'wait', 'duration': 185},
{'type': 'key_press', 'key': 'd'},
{'type': 'wait', 'duration': 73},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 264},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 422},
{'type': 'key_release', 'key': 'd'},
{'type': 'wait', 'duration': 155},
{'type': 'key_press', 'key': 'w'},
{'type': 'wait', 'duration': 831},
{'type': 'key_release', 'key': 'w'},
{'type': 'wait', 'duration': 146},
{'type': 'key_press', 'key': 'd'},
{'type': 'wait', 'duration': 667},
{'type': 'key_release', 'key': 'd'},
{'type': 'wait', 'duration': 328},
{'type': 'key_press', 'key': 'w'},
{'type': 'wait', 'duration': 330},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 207},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 426},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 206},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 1154},
{'type': 'key_release', 'key': 'w'},
{'type': 'wait', 'duration': 176},
{'type': 'key_press', 'key': 'd'},
{'type': 'wait', 'duration': 127},
{'type': 'key_release', 'key': 'd'},
{'type': 'wait', 'duration': 117},
{'type': 'key_press', 'key': 'w'},
{'type': 'wait', 'duration': 73},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 208},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 270},
{'type': 'key_release', 'key': 'w'},
{'type': 'wait', 'duration': 256},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 82},
{'type': 'key_press', 'key': 'w'},
{'type': 'wait', 'duration': 99},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 531},
{'type': 'key_press', 'key': 'a'},
{'type': 'wait', 'duration': 950},
{'type': 'key_release', 'key': 'a'},
{'type': 'wait', 'duration': 89},
{'type': 'key_release', 'key': 'w'},
{'type': 'wait', 'duration': 245},
{'type': 'key_press', 'key': 's'},
{'type': 'wait', 'duration': 188},
{'type': 'key_release', 'key': 's'},
{'type': 'wait', 'duration': 197},
{'type': 'key_press', 'key': 'd'},
{'type': 'wait', 'duration': 184},
{'type': 'key_release', 'key': 'd'},
{'type': 'wait', 'duration': 163},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 70},
{'type': 'key_press', 'key': 'w'},
{'type': 'wait', 'duration': 130},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 211},
{'type': 'key_release', 'key': 'w'},
{'type': 'wait', 'duration': 214},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 38},
{'type': 'key_press', 'key': 'a'},
{'type': 'wait', 'duration': 130},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 1268},
{'type': 'key_release', 'key': 'a'},
{'type': 'wait', 'duration': 133},
{'type': 'key_press', 'key': 'w'},
{'type': 'wait', 'duration': 1188},
{'type': 'key_press', 'key': 'a'},
{'type': 'wait', 'duration': 124},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 210},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 396},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 290},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 107},
{'type': 'key_release', 'key': 'a'},
{'type': 'wait', 'duration': 224},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 225},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 403},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 205},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 131},
{'type': 'key_release', 'key': 'w'},
{'type': 'wait', 'duration': 326},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 99},
{'type': 'key_press', 'key': 'w'},
{'type': 'wait', 'duration': 113},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 138},
{'type': 'key_release', 'key': 'w'},
{'type': 'wait', 'duration': 238},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 114},
{'type': 'key_press', 'key': 'a'},
{'type': 'wait', 'duration': 34},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 891},
{'type': 'key_release', 'key': 'a'},
{'type': 'wait', 'duration': 154},
{'type': 'key_press', 'key': 'w'},
{'type': 'wait', 'duration': 190},
{'type': 'key_release', 'key': 'w'}]

macro_actions = preprocess_macro(macro_actions, NONVIP)

if __name__ == "__main__":
    run_macro(macro_actions)