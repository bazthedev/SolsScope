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

def run_macro(macro):
    sleep(2)  # initial delay
    macro_start = perf_counter()

    for i, action in enumerate(macro):
        # Compute time until this action
        target_time = action["timestamp"]
        now = perf_counter() - macro_start
        time_to_wait = target_time - now
        if time_to_wait > 0:
            sleep(time_to_wait)

        # Execute the action
        match action["type"]:
            case "key_press":
                key = action["key"]
                if key.startswith("Key."):
                    kc.press(pynput_special_keys[key])
                else:
                    kc.press(key)
            case "key_release":
                key = action["key"]
                if key.startswith("Key."):
                    kc.release(pynput_special_keys[key])
                else:
                    kc.release(key)
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
                """case "wait":
                # Optional: if your macro has wait durations separate from timestamps
                sleep(action.get("duration", 0))"""

macro_actions = [{'type': 'key_press', 'key': 'Key.right', 'timestamp': 1.2472091999989061},
{'type': 'wait', 'duration': 1.521, 'timestamp': 1.2472091999989061},
{'type': 'key_release', 'key': 'Key.right', 'timestamp': 2.7685036000002583},
{'type': 'key_press', 'key': 'a', 'timestamp': 2.7685033999987354},
{'type': 'wait', 'duration': 2.453, 'timestamp': 2.7685033999987354},
{'type': 'key_release', 'key': 'a', 'timestamp': 5.221891199998936},
{'type': 'key_press', 'key': 'w', 'timestamp': 5.221891199998936},
{'type': 'wait', 'duration': 6.241, 'timestamp': 5.221891199998936},
{'type': 'key_release', 'key': 'w', 'timestamp': 11.46262409999872},
{'type': 'key_press', 'key': 'd', 'timestamp': 11.46262409999872},
{'type': 'wait', 'duration': 2.898, 'timestamp': 11.46262409999872},
{'type': 'key_press', 'key': 'w', 'timestamp': 14.360902200000055},
{'type': 'wait', 'duration': 0.733, 'timestamp': 14.360902200000055},
{'type': 'key_release', 'key': 'd', 'timestamp': 15.093970399999307},
{'type': 'wait', 'duration': 0.771, 'timestamp': 15.093970399999307},
{'type': 'key_press', 'key': 'a', 'timestamp': 15.865139899999122},
{'type': 'wait', 'duration': 1.886, 'timestamp': 15.865139899999122},
{'type': 'key_release', 'key': 'a', 'timestamp': 17.751372400000037},
{'type': 'key_release', 'key': 'w', 'timestamp': 17.775339199999507},
{'type': 'key_press', 'key': 's', 'timestamp': 17.775339099998746},
{'type': 'wait', 'duration': 0.205, 'timestamp': 17.775339099998746},
{'type': 'key_release', 'key': 's', 'timestamp': 17.980367899999692},
{'type': 'key_press', 'key': 'Key.space', 'timestamp': 17.980368099997577},
{'type': 'wait', 'duration': 0.059, 'timestamp': 17.980368099997577},
{'type': 'key_press', 'key': 'w', 'timestamp': 18.039594099998794},
{'type': 'wait', 'duration': 0.169, 'timestamp': 18.039594099998794},
{'type': 'key_release', 'key': 'Key.space', 'timestamp': 18.20841869999822},
{'type': 'wait', 'duration': 1.863, 'timestamp': 18.20841869999822},
{'type': 'key_release', 'key': 'w', 'timestamp': 20.070975899998302}]

if __name__ == "__main__":
    run_macro([{'type': 'key_press', 'key': 'Key.right', 'timestamp': 1.2472091999989061},
{'type': 'wait', 'duration': 1.521, 'timestamp': 1.2472091999989061},
{'type': 'key_release', 'key': 'Key.right', 'timestamp': 2.7685036000002583},
{'type': 'key_press', 'key': 'a', 'timestamp': 2.7685033999987354},
{'type': 'wait', 'duration': 2.453, 'timestamp': 2.7685033999987354},
{'type': 'key_release', 'key': 'a', 'timestamp': 5.221891199998936},
{'type': 'key_press', 'key': 'w', 'timestamp': 5.221891199998936},
{'type': 'wait', 'duration': 6.241, 'timestamp': 5.221891199998936},
{'type': 'key_release', 'key': 'w', 'timestamp': 11.46262409999872},
{'type': 'key_press', 'key': 'd', 'timestamp': 11.46262409999872},
{'type': 'wait', 'duration': 2.898, 'timestamp': 11.46262409999872},
{'type': 'key_press', 'key': 'w', 'timestamp': 14.360902200000055},
{'type': 'wait', 'duration': 0.733, 'timestamp': 14.360902200000055},
{'type': 'key_release', 'key': 'd', 'timestamp': 15.093970399999307},
{'type': 'wait', 'duration': 0.771, 'timestamp': 15.093970399999307},
{'type': 'key_press', 'key': 'a', 'timestamp': 15.865139899999122},
{'type': 'wait', 'duration': 1.886, 'timestamp': 15.865139899999122},
{'type': 'key_release', 'key': 'a', 'timestamp': 17.751372400000037},
{'type': 'key_release', 'key': 'w', 'timestamp': 17.775339199999507},
{'type': 'key_press', 'key': 's', 'timestamp': 17.775339099998746},
{'type': 'wait', 'duration': 0.205, 'timestamp': 17.775339099998746},
{'type': 'key_release', 'key': 's', 'timestamp': 17.980367899999692},
{'type': 'key_press', 'key': 'Key.space', 'timestamp': 17.980368099997577},
{'type': 'wait', 'duration': 0.059, 'timestamp': 17.980368099997577},
{'type': 'key_press', 'key': 'w', 'timestamp': 18.039594099998794},
{'type': 'wait', 'duration': 0.169, 'timestamp': 18.039594099998794},
{'type': 'key_release', 'key': 'Key.space', 'timestamp': 18.20841869999822},
{'type': 'wait', 'duration': 1.863, 'timestamp': 18.20841869999822},
{'type': 'key_release', 'key': 'w', 'timestamp': 20.070975899998302}])