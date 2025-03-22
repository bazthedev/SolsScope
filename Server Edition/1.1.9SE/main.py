#           Baz's Macro/SolsRNGBot
#   A discord bot for macroing Sol's RNG on Roblox
#   Version: 1.1.9SE (Server Edition)
#   https://github.com/bazthedev/SolsRNGBot
#

try:
    import sys
    import os
    import discord
    import pyautogui as pag
    from datetime import datetime
    import json
    from pynput import mouse, keyboard
    from pynput.keyboard import Key
    from PIL import ImageGrab
    import requests
    import screeninfo as si
    import re
    import glob
    import shutil
    import tempfile
    import psutil
    import random
    import tkinter as tk
    from tkinter import ttk, messagebox
    import mousekey as mk
    import time
    import threading
except ModuleNotFoundError:
    print("A module is missing, please reinstall the requirements to fix this.")
    sys.exit()

mkey = mk.MouseKey()
MACROPATH = os.path.expandvars(r"%localappdata%\Baz Macro SE") # Windows Roaming Path
LOCALVERSION = "1.1.9SE"
PRERELEASE = False
SERVERMACRO_EDITION = True
WEBHOOK_ICON_URL = "https://raw.githubusercontent.com/bazthedev/SolsRNGBot/a93aaa9a42a7184047f12aa4135f3dab0857f05d/Server%20Edition/whicon.png"
if PRERELEASE:
    print(f"Warning! This is a prerelease version of SolsRNGBot, meaning you can expect bugs and some errors to occur!\nYou can find logs relating to events that occur during the prerelease in this folder: {MACROPATH}\n\nYou are currently running prerelease for version {LOCALVERSION}, are you sure you wish to continue?")
    input("Press ENTER to continue using the macro: ")
if SERVERMACRO_EDITION or LOCALVERSION.endswith("SE"):
    print("This is a stripped down version of SolsRNGBot designed for people who macro in Glitch Hunt Servers.")
DEFAULTSETTINGS = {"WEBHOOK_URL": "", "__version__" :  LOCALVERSION,  "merchant_detection" : False, "ping_glitched_id" : 0, "ping_dreamspace_id" : 0, "send_mari" : True, "ping_mari_id" : 0, "send_jester" : True, "ping_jester_id" : 0, "auto_craft_mode" : False, "auto_craft_item" : {"Heavenly Potion I" : False, "Heavenly Potion II" : True, "Warp Potion" : False},  "edit_settings_mode" : True, "failsafe_key" : "ctrl+e", "private_server_link" : "", "biomes" : {"snowy" : False, "windy" : False, "rainy" : False, "sandstorm" : False, "hell" : False, "starfall" : False, "corruption" : False, "null" : False, "glitched" : True, "dreamspace" : True}, "send_start_message" : True, "ping_everyone_on_dreamspace" : True}
VALIDSETTINGSKEYS = ["WEBHOOK_URL", "__version__", "merchant_detection", "ping_glitched_id", "ping_dreamspace_id", "send_mari", "ping_mari_id", "send_jester", "ping_jester_id", "auto_craft_mode", "auto_craft_item", "edit_settings_mode", "failsafe_key",  "private_server_link", "biomes", "send_start_message", "ping_everyone_on_dreamspace"]
STARTUP_MSGS = ["Let's go gambling!", "Nah, I'd Roll", "I give my life...", "Take a break", "Waste of time", "I can't stop playing this", "Touch the grass", "Eternal time...", "Break the Reality", "Finished work for today", "When is payday???", "-One who stands before God-", "-Flaws in the world-", "We do a little bit of rolling", "Exotic Destiny", "Always bet on yourself", "(Lime shivers quietly in the cold)", "There's no way to stop it!", "[Tip]: Get Lucky", "I'm addicted to Sol's RNG", "The Lost"]


if not os.path.exists(f"{MACROPATH}"):
    os.mkdir(MACROPATH)

if not os.path.isfile(f"{MACROPATH}/settings.json"):
    with open(f"{MACROPATH}/settings.json", "w") as f:
        json.dump(DEFAULTSETTINGS, f, indent=4)

if not os.path.isfile(f"{MACROPATH}/icon.ico"):
    dl = requests.get("https://raw.githubusercontent.com/bazthedev/SolsRNGBot/main/icon.ico")
    f = open(f"{MACROPATH}/icon.ico", "wb")
    f.write(dl.content)
    f.close()

def update_settings(settings):
    with open(f"{MACROPATH}/settings.json", "w") as f:
        json.dump(settings, f, indent=4)

def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def hex2rgb(_hex):
    _hex = _hex.lstrip("#")
    return tuple(int(_hex[i:i+2], 16) for i in (0, 2, 4))

def reload_settings():
    global settings
    with open(f"{MACROPATH}/settings.json", "r") as f:
        settings = json.load(f)

def validate_settings():
    found_keys = []
    todel = []
    for k in settings.keys():
        if k not in VALIDSETTINGSKEYS:
            todel.append(k)
            print(f"Invalid setting ({k}) detected")
        else:
            found_keys.append(k)
    for _ in todel:
        del settings[_]
        print(f"Invalid setting ({_}) deleted")
    for _ in VALIDSETTINGSKEYS:
        if _ not in found_keys:
            settings[_] = DEFAULTSETTINGS[_]
            print(f"Missing setting ({_}) added")
    update_settings(settings)
    reload_settings()

def validate_pslink(ps_server_link : str):
    if "https://www.roblox.com/share?code=" not in ps_server_link:
        return False
    if "&type=Server" not in ps_server_link:
        return False
    return True


def get_latest_hovertext(logs_dir):
    log_files = glob.glob(os.path.join(logs_dir, "*.log"))
    if not log_files:
        return None

    latest_log_file = max(log_files, key=os.path.getctime)
    try:
        temp_file = os.path.join(tempfile.gettempdir(), "solsrngbot_biome_detection.log")
        shutil.copy2(latest_log_file, temp_file)
    except PermissionError:
        return None

    json_pattern = re.compile(r'\{.*\}')
    last_hover_text = None

    try:
        with open(temp_file, "r", encoding="utf-8") as file:
            for line in reversed(file.readlines()):
                match = json_pattern.search(line)
                if match:
                    try:
                        json_data = json.loads(match.group())
                        hover_text = json_data.get("data", {}).get("largeImage", {}).get("hoverText")
                        if hover_text:
                            return hover_text
                    except json.JSONDecodeError:
                        continue
    except Exception:
        return None
    
    return last_hover_text

def exists_procs_by_name(name):
    for p in psutil.process_iter(['name']):
        if p.info['name'].lower() == name.lower():
            return True
    return False


def use_item(item_name : str, amount : int, close_menu : bool):
    mkey.left_click_xy_natural(inv_button_pos[0], inv_button_pos[1])
    time.sleep(0.2)
    mkey.left_click_xy_natural(items_pos[0], items_pos[1])
    time.sleep(0.2)
    mkey.left_click_xy_natural(search_pos[0], search_pos[1])
    time.sleep(0.2)
    _keyboard.type(item_name)
    time.sleep(0.2) 
    mkey.left_click_xy_natural(query_pos[0], query_pos[1])
    time.sleep(0.2)
    mkey.left_click_xy_natural(item_amt_pos[0], item_amt_pos[1])
    time.sleep(0.2)
    _keyboard.press(Key.ctrl)
    _keyboard.press("a")
    time.sleep(0.2)
    _keyboard.release("a")
    _keyboard.release(Key.ctrl)
    time.sleep(0.2)
    _keyboard.type(str(amount))
    time.sleep(0.2)
    mkey.left_click_xy_natural(use_pos[0], use_pos[1])
    time.sleep(0.2)
    if close_menu:
        mkey.left_click_xy_natural(close_pos[0], close_pos[1])
        time.sleep(0.2)

now = datetime.now()
_mouse = mouse.Controller()
_keyboard = keyboard.Controller()
screens = si.get_monitors()
monitor = None
for mon in screens:
    if mon.is_primary:
        monitor = mon
scale_w = monitor.width / 2560
scale_h = monitor.height / 1440
aura_button_pos = ((53 * scale_w), (538 * scale_h))
inv_button_pos = ((67 * scale_w), (732 * scale_h))
default_pos = ((1280 * scale_w), (720 * scale_h))
close_pos = ((1887 * scale_w), (399 * scale_h))
search_pos = ((1164 * scale_w), (486 * scale_h))
secondary_pos = ((564 * scale_w), (401 * scale_h))
query_pos = ((1086 * scale_w), (572 * scale_h))
equip_pos = ((812 * scale_w), (844 * scale_h))
use_pos = ((910 * scale_w), (772 * scale_h))
item_amt_pos = ((756 * scale_w), (772 * scale_h))
items_pos = ((1692 * scale_w), (440 * scale_h)) 
purchase_btn_pos = ((990 * scale_w), (860 * scale_h))
quantity_btn_pos = ((910 * scale_w), (796 * scale_h))
open_merch_pos = ((876 * scale_w), (1256 * scale_h))
menu_btn_pos = ((42 * scale_w), (898 * scale_h))
settings_btn_pos = ((1278 * scale_w), (738 * scale_h))
rolling_conf_pos = ((888 * scale_w), (498 * scale_h))
cutscene_conf_pos = ((1518 * scale_w), (812 * scale_h))
craft_btn_pos = ((764 * scale_w), (764 * scale_h))
hp1_pos_potions = ((1064 * scale_w), (840 * scale_h))
hp1_pos_celestial = ((1064 * scale_w), (1024 * scale_h))
hp2_pos_potions = ((1064 * scale_w), (910 * scale_h))
auto_btn_pos = ((940 * scale_w), (762 * scale_h))
auto_mode_swap = 0
auto_craft_index = 3
hp1_recipe_pos = ((1516 * scale_w), (684 * scale_h))
hp2_recipe_pos = ((1516 * scale_w), (836 * scale_h))
warp_recipe_pos = ((1516 * scale_w), (980 * scale_h))
merchant_face_pos_1 = (int(841 * scale_w), int(1056 * scale_h))
merchant_face_pos_2 = (int(855 * scale_w), int(1063 * scale_h))
collection_open_pos = ((54 * scale_w), (624 * scale_h))
sys.exit_collection_pos = ((510 * scale_w), (146 * scale_h))
start_btn_pos = ((1252 * scale_w), (1206 * scale_h))
reconnect_btn_pos = ((1370 * scale_w), (800 * scale_h))
mari_cols = ["#767474", "#767476", "#757474", "#7c7c7c", "#7c7a7c", "#7a7878", "#787678", "#787878"]
jester_cols = ["#e2e2e2", "#e1e1e1", "#e0e0e0"]
biome_cols = {"windy" : (145, 247, 255), "snowy" : (196, 245, 246), "rainy" : (67, 133, 255), "hell" : (74, 23, 34), "starfall" : (103, 132, 224), "corruption" : (144, 66, 255), "null" : (7, 9, 16), "dreamspace" : (234, 108, 188), "glitched" : (100, 252, 100)}
previous_biome = None
valid_ps = False
item_collection_index = 1
use_ms_rblx = False
rblx_player_log_dir = os.path.expandvars(r"%localappdata%\Roblox\logs") # This is for the Roblox Player
ms_rblx_log_dir = os.path.expandvars(r"%LOCALAPPDATA%\Packages\ROBLOXCorporation.ROBLOX_55nm5eh3cm0pr\LocalState\logs") # This is for the Microsoft Store version of Roblox
print(f"Starting SolsRNGBot v{LOCALVERSION}")

class SettingsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Baz's Macro Server Edition Settings Editor")

        try:
            self.root.iconbitmap(f"{MACROPATH}/icon.ico")
        except Exception:
            pass

        self.original_settings = self.load_settings()
        self.entries = {}

        self.create_ui()
    
    def load_settings(self):
        try:
            with open(f"{MACROPATH}/settings.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def format_key(self, key):
        if " " in key:
            return key
        return key.replace("_", " ").title()


    def create_ui(self):
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.create_widgets(self.original_settings, self.scrollable_frame)

        save_button = ttk.Button(self.root, text="Save and Start Macro", command=self.save_settings)
        save_button.pack(pady=10)

    def create_widgets(self, settings, parent, entry_dict=None):
        if entry_dict is None:
            entry_dict = self.entries

        for key, value in settings.items():
            if key == "edit_settings_mode":
                continue
            formatted_key = self.format_key(key)

            row = ttk.Frame(parent)
            row.pack(fill=tk.X, pady=2)

            label = ttk.Label(row, text=formatted_key + ":", width=25, anchor="w")
            label.pack(side=tk.LEFT)

            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                checkbox = ttk.Checkbutton(row, variable=var)
                checkbox.pack(side=tk.LEFT)
                entry_dict[key] = var

            elif isinstance(value, dict):
                subframe = ttk.LabelFrame(parent, text=formatted_key, padding=5)
                subframe.pack(fill=tk.X, padx=10, pady=5)
                entry_dict[key] = {}
                self.create_widgets(value, subframe, entry_dict[key])

            else:
                var = tk.StringVar(value=str(value))
                entry = ttk.Entry(row, textvariable=var, width=30)
                entry.pack(side=tk.LEFT)
                entry_dict[key] = var

    def get_updated_values(self, original, entries):
        updated_settings = {}

        for key, widget in entries.items():
            if isinstance(widget, dict):
                sub_updates = self.get_updated_values(original.get(key, {}), widget)
                if sub_updates:
                    updated_settings[key] = sub_updates
            else:
                new_value = widget.get()
                if isinstance(original.get(key), bool):
                    new_value = bool(new_value)
                elif isinstance(original.get(key), (int, float)):
                    try:
                        new_value = int(new_value)
                    except ValueError:
                        try:
                            new_value = float(new_value)
                        except ValueError:
                            pass

                if new_value != original.get(key):
                    updated_settings[key] = new_value

        return updated_settings

    def save_settings(self):
        updated_values = self.get_updated_values(self.original_settings, self.entries)

        if not updated_values:
            self.root.destroy()
            return

        try:
            with open(f"{MACROPATH}/settings.json", "r") as f:
                current_settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            current_settings = {}

        def merge_dicts(original, updates):
            for key, value in updates.items():
                if isinstance(value, dict) and isinstance(original.get(key), dict):
                    merge_dicts(original[key], value)
                else:
                    original[key] = value

        merge_dicts(current_settings, updated_values)

        try:
            with open(f"{MACROPATH}/settings.json", "w") as f:
                json.dump(current_settings, f, indent=4)
            messagebox.showinfo("Baz's Macro Server Edition Settings Editor", "Settings saved successfully!")
            reload_settings()
            print("Settings were reloaded.")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Baz's Macro Server Edition Settings Editor", f"Failed to save settings:\n{e}")

if not os.path.exists(f"{MACROPATH}/settings.json"):
    x = open(f"{MACROPATH}/settings.json", "w")
    x.write('{}')
    x.close()
    with open(f"{MACROPATH}/settings.json", "w") as f:
        json.dump(DEFAULTSETTINGS, f, indent=4)
    print("Settings have been created!")

if not os.path.exists(f"{MACROPATH}/scr/"):
    os.mkdir(f"{MACROPATH}/scr/")

reload_settings()


if settings["__version__"] < LOCALVERSION:
    settings["__version__"] = LOCALVERSION
    settings["edit_settings_mode"] = True
    update_settings(settings)
    reload_settings()
    print(f"The macro has been updated to version {LOCALVERSION}!")

if settings["__version__"] > LOCALVERSION:
    print("You are running newer settings with an older version of this program. This may delete some of your settings. Are you sure you want to continue (y)? ")
    confirm = input("")
    if confirm[0].lower() != "y":
        sys.exit("You are running newer settings with an older version of this program.")
        
# Settings integrity check
validate_settings()

mkey.enable_failsafekill(settings["failsafe_key"])


root = tk.Tk()
app = SettingsApp(root)
root.protocol("WM_DELETE_WINDOW", sys.exit)
root.mainloop()
print("Validating settings, then starting macro...")
validate_settings()


if exists_procs_by_name("Windows10Universal.exe"):
    rblx_log_dir = ms_rblx_log_dir
    print("Using Microsoft Store Roblox (detected as running)")
elif exists_procs_by_name("RobloxPlayerBeta.exe"):
    rblx_log_dir = rblx_player_log_dir
    print("Using Roblox Player (detected as running)")
else:
    print("Roblox is not running, please run the macro when Roblox is running.")

if settings["private_server_link"] != "":
    if not validate_pslink(settings["private_server_link"]):
        print("Invalid Private Server Link")
        valid_ps = False
    else:
        valid_ps = True

__version__ = settings["__version__"]

def auto_craft():
    global auto_mode_swap, auto_craft_index
    items_to_craft = []
    for itm in settings["auto_craft_item"].keys():
        if settings["auto_craft_item"][itm]:
            items_to_craft.append(itm)
    if len(items_to_craft) < 1:
        return
    while True:
        _keyboard.press("f")
        time.sleep(0.2)
        _keyboard.release("f")
        time.sleep(0.2)
        mkey.left_click_xy_natural(hp1_recipe_pos[0], hp1_recipe_pos[1])
        time.sleep(0.2)
        _mouse.scroll(0, -30)
        time.sleep(0.2)
        _mouse.scroll(0, -30)
        time.sleep(0.2)
        _mouse.scroll(0, -30)
        time.sleep(0.2)
        _mouse.scroll(0, -30)
        time.sleep(0.2)
        _mouse.scroll(0, -30)
        time.sleep(0.2)
        if auto_mode_swap == 9:
            auto_mode_swap = 0
            if auto_craft_index == 1:
                if settings["auto_craft_item"]["Heavenly Potion II"]:
                    auto_craft_index = 2
                    mkey.left_click_xy_natural(hp2_recipe_pos[0], hp2_recipe_pos[1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                    time.sleep(0.2)
                elif settings["auto_craft_item"]["Warp Potion"]:
                    auto_craft_index = 3
                    mkey.left_click_xy_natural(warp_recipe_pos[0], warp_recipe_pos[1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                    time.sleep(0.2)
            elif auto_craft_index == 2:
                if settings["auto_craft_item"]["Warp Potion"]:
                    auto_craft_index = 3
                    mkey.left_click_xy_natural(warp_recipe_pos[0], warp_recipe_pos[1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                    time.sleep(0.2)
                elif settings["auto_craft_item"]["Heavenly Potion I"]:
                    auto_craft_index = 1    
                    mkey.left_click_xy_natural(hp1_recipe_pos[0], hp1_recipe_pos[1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                    time.sleep(0.2)
            elif auto_craft_index == 3:
                if settings["auto_craft_item"]["Heavenly Potion I"]:
                    auto_craft_index = 1
                    mkey.left_click_xy_natural(hp1_recipe_pos[0], hp1_recipe_pos[1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                    time.sleep(0.2)
                elif settings["auto_craft_item"]["Heavenly Potion II"]:
                    auto_craft_index = 2
                    mkey.left_click_xy_natural(hp2_recipe_pos[0], hp2_recipe_pos[1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                    time.sleep(0.2)
        if "Heavenly Potion I" in items_to_craft:
            mkey.left_click_xy_natural(hp1_recipe_pos[0], hp1_recipe_pos[1])
            time.sleep(0.2)
            mkey.left_click_xy_natural(craft_btn_pos[0], craft_btn_pos[1])
            time.sleep(0.2)
            mkey.left_click_xy_natural(hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
            time.sleep(0.2)
            _keyboard.press(Key.end)
            time.sleep(0.2)
            _keyboard.release(Key.end)
            time.sleep(0.2)
            _keyboard.press(Key.backspace)
            time.sleep(2)
            _keyboard.release(Key.backspace)
            time.sleep(0.2)
            _keyboard.type("100")
            time.sleep(0.2)
            mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
            time.sleep(0.2)
            _mouse.scroll(0, -10)
            time.sleep(0.2)
            mkey.left_click_xy_natural(hp1_pos_celestial[0], hp1_pos_celestial[1])
            time.sleep(0.2)
            _mouse.scroll(0, 10)
            time.sleep(0.2)
        if "Heavenly Potion II" in items_to_craft:
            mkey.left_click_xy_natural(hp2_recipe_pos[0], hp2_recipe_pos[1])
            time.sleep(0.2)
            mkey.left_click_xy_natural(craft_btn_pos[0], craft_btn_pos[1])
            time.sleep(0.2)
            mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
            time.sleep(0.2)
            mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
            time.sleep(0.2)
            mkey.left_click_xy_natural(hp2_pos_potions[0], hp2_pos_potions[1])
            time.sleep(0.2)
            mkey.left_click_xy_natural(hp2_pos_potions[0] - (110 * scale_w), hp2_pos_potions[1])
            time.sleep(0.2)
            _keyboard.press(Key.end)
            time.sleep(0.2)
            _keyboard.release(Key.end)
            time.sleep(0.2)
            _keyboard.press(Key.backspace)
            time.sleep(2)
            _keyboard.release(Key.backspace)
            time.sleep(0.2)
            _keyboard.type("125")
            time.sleep(0.2)
            mkey.left_click_xy_natural(hp2_pos_potions[0], hp2_pos_potions[1])
            time.sleep(0.2)
            _mouse.scroll(0, 10)
            time.sleep(0.2)
            _mouse.scroll(0, -10)
            time.sleep(0.2)
            mkey.left_click_xy_natural(hp1_pos_celestial[0], hp1_pos_celestial[1])
            time.sleep(0.2)
            mkey.left_click_xy_natural(craft_btn_pos[0], craft_btn_pos[1])
            time.sleep(0.2)
            mkey.left_click_xy_natural(hp1_pos_celestial[0], hp1_pos_celestial[1])
            time.sleep(0.2)
            _mouse.scroll(0, 10)
        if "Warp Potion" in items_to_craft:
            mkey.left_click_xy_natural(warp_recipe_pos[0], warp_recipe_pos[1])
            time.sleep(0.2)
            mkey.left_click_xy_natural(craft_btn_pos[0], craft_btn_pos[1])
            time.sleep(0.2)
            mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
            time.sleep(0.2)
            _mouse.scroll(0, -30)
            time.sleep(0.2)
            _mouse.scroll(0, -30)
            time.sleep(0.2)
            mkey.left_click_xy_natural(hp1_pos_celestial[0] - (110 * scale_w), hp1_pos_celestial[1])
            time.sleep(0.2)
            _keyboard.press(Key.end)
            time.sleep(0.2)
            _keyboard.release(Key.end)
            time.sleep(0.2)
            _keyboard.press(Key.backspace)
            time.sleep(2)
            _keyboard.release(Key.backspace)
            time.sleep(0.2)
            _keyboard.type("1000")
            time.sleep(0.2)
            mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
            time.sleep(0.2)
            mkey.left_click_xy_natural(hp1_pos_celestial[0], hp1_pos_celestial[1])
            time.sleep(0.2)
            _mouse.scroll(0, 30)
            time.sleep(0.2)
            _mouse.scroll(0, 30)
            time.sleep(0.2)
        auto_mode_swap += 1
        time.sleep(60)
    
def merchant_detection():
    while True:
        use_item("Merchant Teleport", 1, False)
        px = ImageGrab.grab().load()
        colour = px[default_pos[0], default_pos[1]]
        hex_col = rgb2hex(colour[0], colour[1], colour[2])
        colour2 = px[secondary_pos[0], secondary_pos[1]]
        hex_col2 = rgb2hex(colour2[0], colour2[1], colour2[2])
        if (hex_col == "#000000" and hex_col2 == "#000000"):
            rnow = datetime.now()
            mkey.left_click_xy_natural(close_pos[0], close_pos[1])
            time.sleep(1)
            _keyboard.press("e")
            time.sleep(2)
            _keyboard.release("e")
            time.sleep(3)
            px = ImageGrab.grab().load()
            time.sleep(2)
            mkey.left_click_xy_natural(open_merch_pos[0], open_merch_pos[1])
            time.sleep(0.5)
            merchimg = pag.screenshot(f"{MACROPATH}/scr/screenshot_merchant.png")
            time.sleep(0.2)
            up = discord.File(f"{MACROPATH}/scr/screenshot_merchant.png", filename="merchant.png")
            _break = False
            cols = []
            try:
                for y in range(merchant_face_pos_1[1], merchant_face_pos_2[1]):
                    for x in range(merchant_face_pos_1[0], merchant_face_pos_2[0]):
                        if _break:
                            break
                        colour = px[x, y]
                        hex_col = rgb2hex(colour[0], colour[1], colour[2])
                        cols.append(hex_col)
                        print(hex_col)
                        if hex_col in mari_cols:
                            emb = discord.Embed(
                                            title = f"Mari Spawned",
                                            description = f"A Mari selling the following items in the screenshot has been detected at time: {rnow.strftime('%d/%m/%Y %H:%M:%S')}",
                                            colour = discord.Color.from_rgb(255, 255, 255)
                            )
                            emb.set_image(url="attachment://merchant.png")
                            if settings["send_mari"]:
                                if settings["ping_jester"] != 0:
                                    webhook.send(username="SolsRNGBot Server Edition", avatar_url=WEBHOOK_ICON_URL, content=f"<@{settings['ping_mari_id']}>", embed=emb, file=up)
                                else:
                                    webhook.send(username="SolsRNGBot Server Edition", avatar_url=WEBHOOK_ICON_URL, embed=emb, file=up)
                            _break = True
                        elif hex_col in jester_cols:
                            emb = discord.Embed(
                                        title = f"Jester Spawned",
                                        description = f"A Jester selling the following items in the screenshot has been detected at time: {rnow.strftime('%d/%m/%Y %H:%M:%S')}",
                                        colour = discord.Color.from_rgb(176, 49, 255)
                            )
                            emb.set_image(url="attachment://merchant.png")
                            if settings["send_jester"]:
                                if settings["ping_jester"] != 0:
                                    webhook.send(username="SolsRNGBot Server Edition", avatar_url=WEBHOOK_ICON_URL, content=f"<@{settings['ping_jester_id']}>", embed=emb, file=up)
                                else:
                                    webhook.send(username="SolsRNGBot Server Edition", avatar_url=WEBHOOK_ICON_URL, embed=emb, file=up)
                            _break = True
                    if _break:
                        break
            except Exception as e:
                print(e)
        else:
            mkey.left_click_xy_natural(close_pos[0], close_pos[1])
        time.sleep(180)

def biome_detection():
    global previous_biome
    while True:
        current_biome = get_latest_hovertext(rblx_log_dir)
        if previous_biome == None:
            previous_biome = current_biome
            continue
        if current_biome == previous_biome:
            continue
        try:
            if current_biome.lower() in settings["biomes"].keys():
                previous_biome = current_biome
                if current_biome.lower() == "normal":
                    continue
                rnow = datetime.now()
                if settings["biomes"][current_biome.lower()]:
                    if valid_ps:
                        emb = discord.Embed(
                            title=f"Biome Started: {current_biome}",
                            description=f"Biome {current_biome} has started at time: {rnow.strftime('%d/%m/%Y %H:%M:%S')}\nServer Invite: {settings['private_server_link']}",
                            colour=discord.Colour.from_rgb(biome_cols[current_biome.lower()][0], biome_cols[current_biome.lower()][1], biome_cols[current_biome.lower()][2])
                        )
                    else:
                        emb = discord.Embed(
                            title=f"Biome Started: {current_biome}",
                            description=f"Biome {current_biome} has started at time: {rnow.strftime('%d/%m/%Y %H:%M:%S')}",
                            colour=discord.Colour.from_rgb(biome_cols[current_biome.lower()][0], biome_cols[current_biome.lower()][1], biome_cols[current_biome.lower()][2])
                        )
                    if current_biome.lower() == "glitched":
                        if settings["ping_glitched_id"] != 0:
                            webhook.send(username="SolsRNGBot Server Edition", avatar_url=WEBHOOK_ICON_URL, content=f"@<{settings['ping_glitched_id']}", embed=emb)
                        else:
                            webhook.send(username="SolsRNGBot Server Edition", avatar_url=WEBHOOK_ICON_URL, content="@everyone", embed=emb)
                    elif current_biome.lower() == "dreamspace":
                        if settings["ping_dreamspace_id"] != 0:
                            webhook.send(username="SolsRNGBot Server Edition", avatar_url=WEBHOOK_ICON_URL, content=f"@<{settings['ping_dreamspace_id']}", embed=emb)
                        elif settings["ping_everyone_on_dreamspace"]:
                            webhook.send(username="SolsRNGBot Server Edition", avatar_url=WEBHOOK_ICON_URL, content="@everyone", embed=emb)
                        else:
                            webhook.send(username="SolsRNGBot Server Edition", avatar_url=WEBHOOK_ICON_URL, embed=emb)
                    else:
                        webhook.send(username="SolsRNGBot Server Edition", avatar_url=WEBHOOK_ICON_URL, embed=emb)
        except KeyError:
            pass
        except AttributeError:
            pass
        except Exception as e:
            print(e)

if settings["WEBHOOK_URL"] == "":
    print("You need to provide a Webhook URL")
    sys.exit()
try:
    webhook = discord.Webhook.from_url(settings["WEBHOOK_URL"], adapter=discord.RequestsWebhookAdapter())
except Exception:
    print("You are probably seeing this because your webhook link is invalid.")
    sys.exit()
print(random.choice(STARTUP_MSGS))
print(f"Started at {now.strftime('%d/%m/%Y %H:%M:%S')} running v{__version__} using local version {LOCALVERSION}")
if not (exists_procs_by_name("Windows10Universal.exe") or exists_procs_by_name("RobloxPlayerBeta.exe")):
    print("Roblox is not running, waiting for it to start...")
    while not (exists_procs_by_name("Windows10Universal.exe") or exists_procs_by_name("RobloxPlayerBeta.exe")):
        pass
    while get_latest_hovertext(rblx_log_dir) == None:
        pass
    print("Roblox is now running and you are detected as being in the game.")
    time.sleep(10)
if settings["auto_craft_mode"] and not settings["merchant_detection"]:
    crafts = ""
    for item in settings["auto_craft_item"].keys():
        if settings["auto_craft_item"][item]:
            crafts += f"{item}\n"
    print("[WARNING] Auto Craft Mode is on. You will not be able to use certain features whilst this settings is on.")
    print(f"The item(s) you are automatically crafting are:\n{crafts}")
    print("Please ensure that you are standing next to the cauldron so that you can see the \"f\" prompt.")
    print("Starting auto craft mode. Please click back onto Roblox and wait 10 seconds")
    time.sleep(10)
    auto_craft_thread = threading.Thread(target=auto_craft)
    auto_craft_thread.start()
emb = discord.Embed(
        title="Macro Started",
        description=f"Started at {now.strftime('%d/%m/%Y %H:%M:%S')}"
    )
emb.set_footer(text=f"bazthedev/SolsRNGBot v{LOCALVERSION}")
if settings["send_start_message"]:
    webhook.send(username="SolsRNGBot Server Edition", avatar_url=WEBHOOK_ICON_URL, embed=emb)
for _ in settings["biomes"].keys():
    if settings["biomes"][_]:
        biome_detection_thread = threading.Thread(target=biome_detection)
        biome_detection_thread.start()
        print("Started Biome Detection")
        break
if settings["merchant_detection"] and not settings["auto_craft_mode"]:
    merchant_detection_thread = threading.Thread(target=merchant_detection)
    print("Starting Merchant detection in 10 seconds, please click back onto Roblox.")
    time.sleep(10)
    merchant_detection_thread.start()
    print("Started Merchant Detection")
print(f"Started SolsRNGBot v{LOCALVERSION}")
root = tk.Tk()
app = SettingsApp(root)
root.withdraw()
root.protocol("WM_DELETE_WINDOW", sys.exit)
root.mainloop()
print("SolsRNGBot has stopped.")
