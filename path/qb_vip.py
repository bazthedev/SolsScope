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

macro_actions = [{'type': 'key_press', 'key': 'Key.right', 'timestamp': 1.2704156000017974},
{'type': 'wait', 'duration': 1.502, 'timestamp': 1.2704156000017974},
{'type': 'key_release', 'key': 'Key.right', 'timestamp': 2.7723954000011872},
{'type': 'key_press', 'key': 'a', 'timestamp': 2.7723943000000872},
{'type': 'wait', 'duration': 2.25, 'timestamp': 2.7723943000000872},
{'type': 'key_release', 'key': 'a', 'timestamp': 5.022426900000937},
{'type': 'key_press', 'key': 'w', 'timestamp': 5.022425400002248},
{'type': 'wait', 'duration': 5.247, 'timestamp': 5.022425400002248},
{'type': 'key_release', 'key': 'w', 'timestamp': 10.269403400001465},
{'type': 'key_press', 'key': 'd', 'timestamp': 10.269403500002227},
{'type': 'wait', 'duration': 3.422, 'timestamp': 10.269403500002227},
{'type': 'key_press', 'key': 'w', 'timestamp': 13.691526900003737},
{'type': 'wait', 'duration': 0.065, 'timestamp': 13.691526900003737},
{'type': 'key_release', 'key': 'd', 'timestamp': 13.756434800003262},
{'type': 'wait', 'duration': 0.609, 'timestamp': 13.756434800003262},
{'type': 'key_press', 'key': 'a', 'timestamp': 14.365559300002133},
{'type': 'wait', 'duration': 1.339, 'timestamp': 14.365559300002133},
{'type': 'key_release', 'key': 'a', 'timestamp': 15.70456820000254},
{'type': 'key_release', 'key': 'w', 'timestamp': 15.728893200002858},
{'type': 'key_press', 'key': 's', 'timestamp': 15.728893200002858},
{'type': 'wait', 'duration': 0.266, 'timestamp': 15.728893200002858},
{'type': 'key_release', 'key': 's', 'timestamp': 15.994997500003592},
{'type': 'key_press', 'key': 'Key.space', 'timestamp': 15.994997500003592},
{'type': 'key_press', 'key': 'w', 'timestamp': 15.994997500003592},
{'type': 'wait', 'duration': 0.229, 'timestamp': 15.994997500003592},
{'type': 'key_release', 'key': 'Key.space', 'timestamp': 16.223998100002063},
{'type': 'wait', 'duration': 1.579, 'timestamp': 16.223998100002063},
{'type': 'key_release', 'key': 'w', 'timestamp': 17.802799200002482}]

if __name__ == "__main__":
    run_macro([{'type': 'key_press', 'key': 'Key.right', 'timestamp': 1.2704156000017974},
{'type': 'wait', 'duration': 1.502, 'timestamp': 1.2704156000017974},
{'type': 'key_release', 'key': 'Key.right', 'timestamp': 2.7723954000011872},
{'type': 'key_press', 'key': 'a', 'timestamp': 2.7723943000000872},
{'type': 'wait', 'duration': 2.25, 'timestamp': 2.7723943000000872},
{'type': 'key_release', 'key': 'a', 'timestamp': 5.022426900000937},
{'type': 'key_press', 'key': 'w', 'timestamp': 5.022425400002248},
{'type': 'wait', 'duration': 5.247, 'timestamp': 5.022425400002248},
{'type': 'key_release', 'key': 'w', 'timestamp': 10.269403400001465},
{'type': 'key_press', 'key': 'd', 'timestamp': 10.269403500002227},
{'type': 'wait', 'duration': 3.422, 'timestamp': 10.269403500002227},
{'type': 'key_press', 'key': 'w', 'timestamp': 13.691526900003737},
{'type': 'wait', 'duration': 0.065, 'timestamp': 13.691526900003737},
{'type': 'key_release', 'key': 'd', 'timestamp': 13.756434800003262},
{'type': 'wait', 'duration': 0.609, 'timestamp': 13.756434800003262},
{'type': 'key_press', 'key': 'a', 'timestamp': 14.365559300002133},
{'type': 'wait', 'duration': 1.339, 'timestamp': 14.365559300002133},
{'type': 'key_release', 'key': 'a', 'timestamp': 15.70456820000254},
{'type': 'key_release', 'key': 'w', 'timestamp': 15.728893200002858},
{'type': 'key_press', 'key': 's', 'timestamp': 15.728893200002858},
{'type': 'wait', 'duration': 0.266, 'timestamp': 15.728893200002858},
{'type': 'key_release', 'key': 's', 'timestamp': 15.994997500003592},
{'type': 'key_press', 'key': 'Key.space', 'timestamp': 15.994997500003592},
{'type': 'key_press', 'key': 'w', 'timestamp': 15.994997500003592},
{'type': 'wait', 'duration': 0.229, 'timestamp': 15.994997500003592},
{'type': 'key_release', 'key': 'Key.space', 'timestamp': 16.223998100002063},
{'type': 'wait', 'duration': 1.579, 'timestamp': 16.223998100002063},
{'type': 'key_release', 'key': 'w', 'timestamp': 17.802799200002482}])