# Made using ReTask by JustSoftware & cresqnt

CPU_INTENSIVE_HIGH_ACCURACY_SLEEP = True
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
from mousekey import MouseKey
from time import sleep, perf_counter

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


macro_actions = [{'type': 'key_press', 'key': 's'},
{'type': 'wait', 'duration': 10},
{'type': 'key_press', 'key': 'd'},
{'type': 'wait', 'duration': 2588},
{'type': 'key_release', 'key': 'd'},
{'type': 'wait', 'duration': 2490},
{'type': 'key_release', 'key': 's'},
{'type': 'wait', 'duration': 112},
{'type': 'key_press', 'key': 'd'},
{'type': 'wait', 'duration': 1125},
{'type': 'key_press', 'key': 's'},
{'type': 'wait', 'duration': 399},
{'type': 'key_release', 'key': 's'},
{'type': 'wait', 'duration': 21},
{'type': 'key_release', 'key': 'd'},
{'type': 'wait', 'duration': 231},
{'type': 'key_press', 'key': 'w'},
{'type': 'wait', 'duration': 113},
{'type': 'key_release', 'key': 'w'},
{'type': 'wait', 'duration': 365},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 127},
{'type': 'key_press', 'key': 's'},
{'type': 'wait', 'duration': 41},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 831},
{'type': 'key_release', 'key': 's'},
{'type': 'wait', 'duration': 202},
{'type': 'key_press', 'key': 'a'},
{'type': 'wait', 'duration': 619},
{'type': 'key_press', 'key': 's'},
{'type': 'wait', 'duration': 1389},
{'type': 'key_release', 'key': 'a'},
{'type': 'wait', 'duration': 475},
{'type': 'key_release', 'key': 's'},
{'type': 'wait', 'duration': 1299},
{'type': 'key_press', 'key': 'e'},
{'type': 'wait', 'duration': 125},
{'type': 'key_release', 'key': 'e'}]

if __name__ == "__main__":
    run_macro([{'type': 'key_press', 'key': 's'},
{'type': 'wait', 'duration': 10},
{'type': 'key_press', 'key': 'd'},
{'type': 'wait', 'duration': 2588},
{'type': 'key_release', 'key': 'd'},
{'type': 'wait', 'duration': 2490},
{'type': 'key_release', 'key': 's'},
{'type': 'wait', 'duration': 112},
{'type': 'key_press', 'key': 'd'},
{'type': 'wait', 'duration': 1125},
{'type': 'key_press', 'key': 's'},
{'type': 'wait', 'duration': 399},
{'type': 'key_release', 'key': 's'},
{'type': 'wait', 'duration': 21},
{'type': 'key_release', 'key': 'd'},
{'type': 'wait', 'duration': 231},
{'type': 'key_press', 'key': 'w'},
{'type': 'wait', 'duration': 113},
{'type': 'key_release', 'key': 'w'},
{'type': 'wait', 'duration': 365},
{'type': 'key_press', 'key': 'Key.space'},
{'type': 'wait', 'duration': 127},
{'type': 'key_press', 'key': 's'},
{'type': 'wait', 'duration': 41},
{'type': 'key_release', 'key': 'Key.space'},
{'type': 'wait', 'duration': 831},
{'type': 'key_release', 'key': 's'},
{'type': 'wait', 'duration': 202},
{'type': 'key_press', 'key': 'a'},
{'type': 'wait', 'duration': 619},
{'type': 'key_press', 'key': 's'},
{'type': 'wait', 'duration': 1389},
{'type': 'key_release', 'key': 'a'},
{'type': 'wait', 'duration': 475},
{'type': 'key_release', 'key': 's'},
{'type': 'wait', 'duration': 1299},
{'type': 'key_press', 'key': 'e'},
{'type': 'wait', 'duration': 125},
{'type': 'key_release', 'key': 'e'}])