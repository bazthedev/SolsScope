# Made using ReTask by JustSoftware & cresqnt

CPU_INTENSIVE_HIGH_ACCURACY_SLEEP = True
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
from mousekey import MouseKey
from time import sleep, perf_counter
from fractions import Fraction

NONVIP = False
SCALE = float(Fraction(342, 277))

def preprocess_macro(macro, nonvip=True):
    processed = []
    for action in macro:
        if action["type"] == "wait":
            new_action = action.copy()
            if nonvip:
                new_action["duration"] = int(action["duration"] * SCALE)
            processed.append(new_action)
        else:
            processed.append(action.copy())
    return processed

from time import perf_counter

def busy_wait_sleep(duration_ms: float):
    """
    High-accuracy sleep that does NOT use time.sleep().
    Burns CPU while waiting.
    """
    duration = duration_ms / 1000.0
    target = perf_counter() + duration
    while perf_counter() < target:
        pass

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

def run_macro(macro, delay=2, min_wait=30):
    sleep(delay)

    for action in macro:
        match action["type"]:
            case "wait":
                dur = max(action["duration"], min_wait)
                if CPU_INTENSIVE_HIGH_ACCURACY_SLEEP:
                    busy_wait_sleep(dur)
                else:
                    sleep(dur / 1000.0)
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


macro_actions = [{'type': 'key_press', 'key': 's'},
{'type': 'wait', 'duration': 7},
{'type': 'key_press', 'key': 'a'},
{'type': 'wait', 'duration': 3506},
{'type': 'key_release', 'key': 'a'},
{'type': 'wait', 'duration': 2352},
{'type': 'key_release', 'key': 's'},
{'type': 'wait', 'duration': 230},
{'type': 'key_press', 'key': 'd'},
{'type': 'wait', 'duration': 1116},
{'type': 'key_press', 'key': 's'},
{'type': 'wait', 'duration': 371},
{'type': 'key_release', 'key': 's'},
{'type': 'wait', 'duration': 133},
{'type': 'key_press', 'key': 's'},
{'type': 'wait', 'duration': 186},
{'type': 'key_release', 'key': 's'},
{'type': 'wait', 'duration': 75},
{'type': 'key_release', 'key': 'd'},
{'type': 'wait', 'duration': 84},
{'type': 'key_press', 'key': 'w'},
{'type': 'wait', 'duration': 146},
{'type': 'key_release', 'key': 'w'},
{'type': 'wait', 'duration': 121},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 63},
{'type': 'key_press', 'key': 'd'},
{'type': 'wait', 'duration': 73},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 191},
{'type': 'key_release', 'key': 'd'},
{'type': 'wait', 'duration': 220},
{'type': 'key_press', 'key': 's'},
{'type': 'wait', 'duration': 507},
{'type': 'key_press', 'key': 'a'},
{'type': 'wait', 'duration': 1194},
{'type': 'key_release', 'key': 'a'},
{'type': 'wait', 'duration': 5113},
{'type': 'key_press', 'key': 'a'},
{'type': 'wait', 'duration': 2017},
{'type': 'key_release', 'key': 'a'},
{'type': 'wait', 'duration': 227},
{'type': 'key_press', 'key': 'a'},
{'type': 'wait', 'duration': 178},
{'type': 'key_release', 'key': 'a'},
{'type': 'wait', 'duration': 149},
{'type': 'key_press', 'key': 'a'},
{'type': 'wait', 'duration': 96},
{'type': 'key_release', 'key': 'a'},
{'type': 'wait', 'duration': 236},
{'type': 'key_press', 'key': 'a'},
{'type': 'wait', 'duration': 101},
{'type': 'key_release', 'key': 'a'},
{'type': 'wait', 'duration': 317},
{'type': 'key_press', 'key': 'a'},
{'type': 'wait', 'duration': 538},
{'type': 'key_release', 'key': 'a'},
{'type': 'wait', 'duration': 67},
{'type': 'key_press', 'key': 'a'},
{'type': 'wait', 'duration': 587},
{'type': 'key_release', 'key': 'a'},
{'type': 'wait', 'duration': 19},
{'type': 'key_release', 'key': 's'},
{'type': 'wait', 'duration': 226},
{'type': 'key_press', 'key': 'w'},
{'type': 'wait', 'duration': 188},
{'type': 'key_release', 'key': 'w'},
{'type': 'wait', 'duration': 87},
{'type': 'key_press', 'key': 'd'},
{'type': 'wait', 'duration': 145},
{'type': 'key_release', 'key': 'd'},
{'type': 'wait', 'duration': 116},
{'type': 'key_press', 'key': 's'},
{'type': 'wait', 'duration': 82},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 200},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 498},
{'type': 'key_release', 'key': 's'},
{'type': 'wait', 'duration': 128},
{'type': 'key_press', 'key': 'a'},
{'type': 'wait', 'duration': 79},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 204},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 2989},
{'type': 'key_release', 'key': 'a'},
{'type': 'wait', 'duration': 236},
{'type': 'key_press', 'key': 's'},
{'type': 'wait', 'duration': 2157},
{'type': 'key_release', 'key': 's'},
{'type': 'wait', 'duration': 3478},
{'type': 'key_press', 'key': 'a'},
{'type': 'wait', 'duration': 971},
{'type': 'key_release', 'key': 'a'},
{'type': 'wait', 'duration': 921},
{'type': 'key_press', 'key': 'f'},
{'type': 'wait', 'duration': 94},
{'type': 'key_release', 'key': 'f'}]

macro_actions = preprocess_macro(macro_actions, NONVIP)

if __name__ == "__main__":
    run_macro(macro_actions)