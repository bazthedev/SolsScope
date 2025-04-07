#           Baz's Macro/SolsRNGBot
#   A discord bot for macroing Sol's RNG on Roblox
#   Version: 1.2.2
#   https://github.com/bazthedev/SolsRNGBot
#
import sys
from tkinter import messagebox
GLOBAL_LOGGER = None
try:
    import os
    import discord
    from discord.ext import commands
    import pyautogui as pag
    from datetime import datetime
    import json
    from pynput import mouse, keyboard
    from pynput.keyboard import Key
    import asyncio
    import requests
    import screeninfo as si
    import re
    import glob
    import shutil
    import tempfile
    import psutil
    import random
    import tkinter as tk
    from tkinter import ttk
    import mousekey as mk
    from aiohttp import ClientSession
    import subprocess
    import typing
    from websockets import connect
    from pathlib import Path
    import zipfile
    import threading
    from tkinter import PhotoImage
    from PIL import Image, ImageTk
    import time
    from difflib import SequenceMatcher
    import cv2
    import pytesseract
    import webbrowser
    import importlib
except ImportError as e:
    messagebox.showerror("Baz's Macro", f"A module was not imported correctly.\n{e}")
    sys.exit()

mkey = mk.MouseKey()
MACROPATH = os.path.expandvars(r"%localappdata%\Baz's Macro") # Windows Roaming Path
LOCALVERSION = "1.2.2"
PRERELEASE = False
SERVERMACRO_EDITION = False
DEFAULTSETTINGS = {"WEBHOOK_URL": "", "__version__" :  LOCALVERSION, "use_roblox_player" : True, "global_wait_time" : 0.2, "skip_aura_download": False, "mention" : True, "mention_id" : 0, "minimum_roll" : "99998", "minimum_ping" : "349999", "reset_aura" : "", "merchant_detection" : False, "send_mari" : True, "ping_mari" : False, "send_jester" : True, "ping_jester" : True, "clear_logs" : False, "pop_in_glitch" : False, "auto_use_items_in_glitch": {"Heavenly Potion" : {"use" : True, "amount" : 200}, "Fortune Potion III" : {"use" : True, "amount" : 1}, "Lucky Potion" : {"use" : True, "amount" : 10}, "Pumpkin" : {"use" : True, "amount" : 10}, "Haste Potion III" : {"use" : False, "amount" : 1}, "Warp Potion" : {"use" : True, "amount" : 1}, "Transcended Potion" : {"use" : False, "amount" : 1}, "Mixed Potion" : {"use" : True, "amount" : 10}, "Stella's Candle" : {"use" : True, "amount" : 1}, "Santa Claus Potion" : {"use" : True, "amount" : 5}, "Hwachae" : {"use" : True, "amount" : 1}}, "pop_in_dreamspace" : False, "auto_use_items_in_dreamspace" : {"Heavenly Potion" : {"use" : False, "amount" : 1}, "Fortune Potion III" : {"use" : True, "amount" : 1}, "Lucky Potion" : {"use" : True, "amount" : 10}, "Pumpkin" : {"use" : True, "amount" : 10}, "Haste Potion III" : {"use" : False, "amount" : 1}, "Warp Potion" : {"use" : True, "amount" : 1}, "Transcended Potion" : {"use" : False, "amount" : 1}, "Mixed Potion" : {"use" : True, "amount" : 10}, "Stella's Candle" : {"use" : True, "amount" : 1}, "Santa Claus Potion" : {"use" : True, "amount" : 5}, "Hwachae" : {"use" : True, "amount" : 1}}, "auto_craft_mode" : False, "skip_auto_mode_warning" : False, "auto_craft_item" : {"Potion of Bound" : False, "Heavenly Potion" : True, "Godly Potion (Zeus)" : True, "Godly Potion (Poseidon)" : True, "Godly Potion (Hades)" : True, "Warp Potion" : True, "Godlike Potion" : True}, "auto_biome_randomizer" : False, "auto_strange_controller" : False, "failsafe_key" : "ctrl+e", "merchant_detec_wait" : 0, "private_server_link" : "", "take_screenshot_on_detection" : False, "ROBLOSECURITY_KEY" : "", "DISCORD_TOKEN" : "", "collect_items" : {"1" : False, "2" : False, "3" : False, "4" : False}, "sniper_enabled" : False, "sniper_toggles" : {"Glitched" : True, "Dreamspace" : False}, "sniper_logs" : True, "change_cutscene_on_pop" : True, "disable_autokick_prevention" : False, "periodic_screenshots" : {"inventory" : False, "storage" : False}, "disconnect_prevention" : False, "check_update" : True, "auto_install_update" : False, "biomes" : {"snowy" : False, "windy" : False, "rainy" : False, "sand storm" : False, "hell" : False, "starfall" : False, "corruption" : False, "null" : False, "glitched" : True, "dreamspace" : True}, "auto_purchase_items_mari" : {"Lucky Potion" : False, "Lucky Potion L" : False, "Lucky Potion XL" : False, "Speed Potion" : False, "Speed Potion L" : False, "Speed Potion XL" : False, "Mixed Potion" : False, "Fortune Spoid" : False, "Gears" : False, "Lucky Penny" : False, "Void Coin" : True}, "auto_purchase_items_jester" : {"Lucky Potion" : False, "Speed Potion" : False, "Random Potion Sack" : False, "Stella's Star" : False, "Rune of Wind": False, "Rune of Frost" : False, "Rune of Rainstorm" : False, "Rune of Hell" : False, "Rune of Galaxy" : False, "Rune of Corruption" : False, "Rune of Nothing" : False, "Rune of Everything" : True, "Strange Potion" : True, "Stella's Candle" : True, "Potion of Bound" : True, "Merchant Tracker" : False, "Heavenly Potion" : True, "Oblivion Potion" : True}, "scan_channels" : [1282542323590496277]}
VALIDSETTINGSKEYS = ["WEBHOOK_URL", "__version__", "use_roblox_player", "global_wait_time", "skip_aura_download", "mention", "mention_id", "minimum_roll", "minimum_ping", "reset_aura", "merchant_detection", "send_mari", "ping_mari", "send_jester", "ping_jester", "clear_logs", "pop_in_glitch", "auto_use_items_in_glitch", "pop_in_dreamspace", "auto_use_items_in_dreamspace", "auto_craft_mode", "skip_auto_mode_warning", "auto_craft_item", "auto_biome_randomizer", "auto_strange_controller", "failsafe_key", "merchant_detec_wait", "private_server_link", "take_screenshot_on_detection", "ROBLOSECURITY_KEY", "DISCORD_TOKEN", "sniper_enabled", "sniper_toggles", "collect_items", "sniper_logs", "change_cutscene_on_pop", "disable_autokick_prevention", "periodic_screenshots", "disconnect_prevention", "check_update", "auto_install_update", "biomes", "auto_purchase_items_mari", "auto_purchase_items_jester", "scan_channels"]
STARTUP_MSGS = ["Let's go gambling!", "Nah, I'd Roll", "I give my life...", "Take a break", "Waste of time", "I can't stop playing this", "Touch the grass", "Eternal time...", "Break the Reality", "Finished work for today", "When is payday???", "-One who stands before God-", "-Flaws in the world-", "We do a little bit of rolling", "Exotic Destiny", "Always bet on yourself", "(Lime shivers quietly in the cold)", "There's no way to stop it!", "[Tip]: Get Lucky", "I'm addicted to Sol's RNG", "The Lost"]
ACCEPTEDPOTIONS = ["Potion of Bound", "Heavenly Potion", "Godly Potion (Zeus)", "Godly Potion (Poseidon)", "Godly Potion (Hades)", "Warp Potion", "Godlike Potion"]
GENERAL_KEYS = ["WEBHOOK_URL", "private_server_link", "failsafe_key", "use_roblox_player", "global_wait_time", "skip_aura_download", "mention", "mention_id"]
AURAS_KEYS = ["minimum_roll", "minimum_ping", "reset_aura", "take_screenshot_on_detection"]
BIOMES_KEYS = ["biomes", "auto_biome_randomizer", "auto_strange_controller", "pop_in_glitch", "auto_use_items_in_glitch", "pop_in_dreamspace", "auto_use_items_in_dreamspace"]
SNIPER_KEYS = ["sniper_enabled", "sniper_toggles", "DISCORD_TOKEN", "ROBLOSECURITY_KEY", "sniper_logs", "scan_channels"]
MERCHANT_KEYS = ["merchant_detection", "send_mari", "ping_mari", "auto_purchase_items_mari", "send_jester", "ping_jester", "auto_purchase_items_jester"]
AUTOCRAFT_KEYS = ["auto_craft_mode", "auto_craft_item", "skip_auto_mode_warning"]
OTHER_KEYS = ["disconnect_prevention", "disable_autokick_prevention", "periodic_screenshots", "check_update", "auto_install_update"]

detected_snipe = False

WEBHOOK_ICON_URL = "https://raw.githubusercontent.com/bazthedev/SolsRNGBot/a93aaa9a42a7184047f12aa4135f3dab0857f05d/Server%20Edition/whicon.png"

if not os.path.exists(f"{MACROPATH}"):
    os.mkdir(MACROPATH)

if not os.path.isfile(f"{MACROPATH}/settings.json"):
    with open(f"{MACROPATH}/settings.json", "w") as f:
        json.dump(DEFAULTSETTINGS, f, indent=4)

PLACE_ID = 15532962292
BASE_ROBLOX_URL = f"https://www.roblox.com/games/{PLACE_ID}/x1000000000-Sols-RNG"
DISCORD_WS_BASE = "wss://gateway.discord.gg/?v=10&encoding-json"
SHARELINKS_API = "https://apis.roblox.com/sharelinks/v1/resolve-link"

if not os.path.isfile(f"{MACROPATH}/icon.ico"):
    dl = requests.get("https://raw.githubusercontent.com/bazthedev/SolsRNGBot/main/icon.ico")
    f = open(f"{MACROPATH}/icon.ico", "wb")
    f.write(dl.content)
    f.close()

def get_auras():
    GLOBAL_LOGGER.write_log("Downloading Aura List")
    try:
        dl = requests.get("https://raw.githubusercontent.com/bazthedev/SolsRNGBot/main/auras_new.json", timeout=5)
        dl.raise_for_status()
        with open(f"{MACROPATH}/auras_new.json", "wb") as f:
            f.write(dl.content)
        GLOBAL_LOGGER.write_log("Downloaded Aura List")
    except requests.RequestException as e:
        GLOBAL_LOGGER.write_log(f"Failed to download Aura List: {e}")

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
    _show_added_msg = False
    for k in settings.keys():
        if k not in VALIDSETTINGSKEYS:
            todel.append(k)
            GLOBAL_LOGGER.write_log(f"Invalid setting ({k}) detected")
        else:
            found_keys.append(k)
    for _ in todel:
        del settings[_]
        GLOBAL_LOGGER.write_log(f"Invalid setting ({_}) deleted")
        _show_added_msg = True
    for _ in VALIDSETTINGSKEYS:
        if _ not in found_keys:
            settings[_] = DEFAULTSETTINGS[_]
            GLOBAL_LOGGER.write_log(f"Missing setting ({_}) added")
            _show_added_msg = True
    if _show_added_msg:
        GLOBAL_LOGGER.write_log("A settings was added/removed, you should restart the macro for the UI to update.")
        messagebox.showwarning("Baz's Macro", "A settings was added/removed, you should restart the macro for the UI to update.")
    update_settings(settings)
    reload_settings()
    if "TOKEN" in todel:
        messagebox.showwarning("Baz's Macro", "This version of the macro REMOVES the discord bot feature. You now need a webhook link instead.")

def validate_potions():
    found_keys = []
    todel = []
    for k in settings["auto_craft_item"].keys():
        if k not in ACCEPTEDPOTIONS:
            todel.append(k)
            GLOBAL_LOGGER.write_log(f"Invalid potion ({k}) detected")
        else:
            found_keys.append(k)
    for _ in todel:
        del settings["auto_craft_item"][_]
        GLOBAL_LOGGER.write_log(f"Invalid potion ({_}) deleted")
    for _ in ACCEPTEDPOTIONS:
        if _ not in found_keys:
            settings["auto_craft_item"][_] = False
            GLOBAL_LOGGER.write_log(f"Missing potion ({_}) added")
    update_settings(settings)
    reload_settings()

def validate_pslink(ps_server_link : str):
    if "https://www.roblox.com/share?code=" not in ps_server_link:
        return False
    if "&type=Server" not in ps_server_link:
        return False
    return True

def format_roblosecurity():
    if "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_" in settings["ROBLOSECURITY_KEY"]:
        new_roblosec = settings["ROBLOSECURITY_KEY"].replace("_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_", "")
        settings["ROBLOSECURITY_KEY"] = new_roblosec
        update_settings(settings)
        reload_settings()


def migrate_settings():
    if os.path.exists("./settings.json") and not os.path.exists(f"{MACROPATH}/settings.json"):
        with open("./settings.json", "r") as f:
            _ = json.load(f)
        with open(f"{MACROPATH}/settings.json", "w+") as f:
            json.dump(_, f, indent=4)
    reload_settings()
    if not os.path.exists(f"{MACROPATH}"):
        GLOBAL_LOGGER.write_log(f"Moving to new directory: {MACROPATH}")



MARI_ITEMS = [
    "Void Coin",
    "Fortune Spoid",
    "Speed Potion",
    "Mixed Potion",
    "Gear B",
    "Lucky Penny",
    "Gear A",
    "Lucky Potion"
]

JESTER_ITEMS = [
    "Lucky Potion",
    "Speed Potion",
    "Random Potion Sack",
    "Stella's Star",
    "Rune of Wind",
    "Rune of Frost",
    "Rune of Rainstorm",
    "Rune of Hell",
    "Rune of Galaxy",
    "Rune of Corruption",
    "Rune of Nothing",
    "Rune of Everything",
    "Strange Potion",
    "Stella's Candle",
    "Merchant Tracker",
    "Potion of Bound",
    "Heavenly Potion",
    "Oblivion Potion"
]

def fuzzy_match(text, known_items, threshold=0.5):
    best_match = None
    best_score = 0
    for item in known_items:
        score = SequenceMatcher(None, text.lower(), item.lower()).ratio()
        if score > best_score:
            best_score = score
            best_match = item
    if best_score >= threshold:
        return best_match
    return text

possible_merchants = ["Mari's Shop", "Jester's Shop"]

def fuzzy_match_merchant(text, options, threshold=0.6):
    best_match = None
    best_score = 0
    for name in options:
        score = SequenceMatcher(None, name.lower(), text.lower()).ratio()
        if score > best_score:
            best_match = name
            best_score = score
    return best_match if best_score >= threshold else None

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

def align_camera():
    GLOBAL_LOGGER.write_log("Aligning Camera....")
    _keyboard.press(Key.esc)
    time.sleep(0.2)
    _keyboard.release(Key.esc)
    time.sleep(0.2)
    _keyboard.press("r")
    time.sleep(0.2)
    _keyboard.release("r")
    time.sleep(0.2)    
    _keyboard.press(Key.enter)
    time.sleep(0.2)
    _keyboard.release(Key.enter)
    time.sleep(0.2)
    mkey.left_click_xy_natural(collection_open_pos[0], collection_open_pos[1])
    time.sleep(0.2)
    mkey.left_click_xy_natural(exit_collection_pos[0], exit_collection_pos[1])
    time.sleep(0.2)
    _keyboard.press(Key.shift)
    time.sleep(0.2)
    _keyboard.release(Key.shift)
    time.sleep(0.2)
    _keyboard.press(Key.shift)
    time.sleep(0.2)
    _keyboard.release(Key.shift)
    time.sleep(0.2)
    for i in range(80):
        _mouse.scroll(0, 30)
    time.sleep(2)
    for i in range(3):
        _mouse.scroll(0, -5)
        time.sleep(0.2)
    time.sleep(0.2)

def do_obby_blessing():
    _keyboard.press(Key.shift)
    time.sleep(0.2)
    _keyboard.release(Key.shift)
    time.sleep(0.2)
    mkey.move_relative(int(500 * scale_w), 0) # 0.36 sens
    time.sleep(0.2)
    _keyboard.press(Key.shift)
    time.sleep(0.2)
    _keyboard.release(Key.shift)
    time.sleep(0.2)
    _keyboard.press("w")
    time.sleep(4.5) # vip +
    _keyboard.release("w")
    time.sleep(0.2)
    _keyboard.press(Key.shift)
    time.sleep(0.2)
    _keyboard.release(Key.shift)
    time.sleep(0.2)
    mkey.move_relative(int(-500 * scale_w), 0) # 0.36 sens
    time.sleep(0.2)
    _keyboard.press("w")
    time.sleep(1.5) # vip +
    _keyboard.release("w")
    time.sleep(0.2)    
    mkey.move_relative(int(500 * scale_w), 0) # 0.36 sens
    time.sleep(0.2)
    _keyboard.press("w")
    time.sleep(2) # vip +
    _keyboard.release("w")
    time.sleep(0.2)
    _keyboard.press("d")
    time.sleep(2) # vip +
    _keyboard.release("d")
    time.sleep(0.2)
    _keyboard.press("a")
    time.sleep(0.2) # vip +
    _keyboard.release("a")
    time.sleep(0.2)
    _keyboard.press("s")
    time.sleep(0.2) # vip +
    _keyboard.release("s")
    time.sleep(0.2)
    _keyboard.press(Key.space)
    _keyboard.press("w")
    time.sleep(0.2) # vip +
    _keyboard.release("w")
    _keyboard.release(Key.space)
    time.sleep(0.2)
    _keyboard.press("w")
    time.sleep(4) # vip +
    _keyboard.release("w")
    time.sleep(1)
    _keyboard.press("w")
    time.sleep(0.2)
    _keyboard.press(Key.space)
    time.sleep(0.3)
    _keyboard.release(Key.space)
    time.sleep(0.6) # vip +
    _keyboard.release("w")
    time.sleep(0.2)    
    mkey.move_relative(int(250 * scale_w), 0) # 0.36 sens
    time.sleep(0.2)
    _keyboard.press("w")
    time.sleep(0.3) # vip +
    _keyboard.release("w")
    time.sleep(1)
    _keyboard.press("s")
    time.sleep(0.2) # vip +
    _keyboard.release("s")
    time.sleep(0.2)
    _keyboard.press("w")
    _keyboard.press(Key.space)
    time.sleep(0.2)
    _keyboard.release(Key.space)
    time.sleep(0.2) # vip +
    _keyboard.release("w")
    time.sleep(0.3) 
    _keyboard.press("w")
    time.sleep(0.2)
    _keyboard.press(Key.space)
    time.sleep(0.3)
    _keyboard.release(Key.space)
    time.sleep(0.6) # vip +
    _keyboard.release("w")
    time.sleep(0.2)
    _keyboard.press("w")
    time.sleep(5) # vip +
    _keyboard.release("w")
    time.sleep(1)
    _keyboard.press("s")
    time.sleep(0.2) # vip +
    _keyboard.release("s")
    time.sleep(0.2)
    _keyboard.press(Key.space)
    _keyboard.press("w")
    time.sleep(0.2) # vip +
    _keyboard.release("w")
    _keyboard.release(Key.space)
    time.sleep(0.2)
    _keyboard.press(Key.space)
    _keyboard.press("w")
    time.sleep(0.2) # vip +
    _keyboard.release("w")
    _keyboard.release(Key.space)
    time.sleep(0.2)
    mkey.move_relative(int(-250 * scale_w), 0) # 0.36 sens
    time.sleep(0.2)
    _keyboard.press("w")
    time.sleep(1.3) # vip +
    _keyboard.release("w")
    time.sleep(1)
    mkey.move_relative(int(-500 * scale_w), 0) # 0.36 sens
    time.sleep(0.2)
    _keyboard.press("s")
    time.sleep(0.2) # vip +
    _keyboard.release("s")
    time.sleep(0.2)
    _keyboard.press(Key.space)
    _keyboard.press("w")
    time.sleep(0.2) # vip +
    _keyboard.release("w")
    _keyboard.release(Key.space)
    time.sleep(0.2) # unfinished

def collect_item(item_collection_index : int):
    while not app.stop_event.is_set():
        align_camera()
        if item_collection_index == 1:
            if not settings["collect_items"]["1"]:
                item_collection_index += 1
            else:
                _keyboard.press(Key.shift)
                time.sleep(0.2)
                _keyboard.release(Key.shift)
                time.sleep(0.2)
                mkey.move_relative(int(500 * scale_w), 0) # 0.36 sens
                time.sleep(0.2)
                _keyboard.press(Key.shift)
                time.sleep(0.2)
                _keyboard.release(Key.shift)
                time.sleep(0.2)
                _keyboard.press("w")
                time.sleep(4.5) # vip +
                _keyboard.release("w")
                time.sleep(0.2)
                _keyboard.press(Key.shift)
                time.sleep(0.2)
                _keyboard.release(Key.shift)
                time.sleep(0.2)
                mkey.move_relative(int(-500 * scale_w), 0) # 0.36 sens
                time.sleep(0.2)
                _keyboard.press("w")
                time.sleep(2) # vip +
                _keyboard.release("w")
                time.sleep(0.2)
        if item_collection_index == 2:
            if not settings["collect_items"]["2"]:
                item_collection_index += 1
            else:
                pass
        if item_collection_index == 3:
            if not settings["collect_items"]["3"]:
                item_collection_index += 1
            else:
                pass
        if item_collection_index == 4:
            if not settings["collect_items"]["4"]:
                item_collection_index += 1
            else:
                pass
        if item_collection_index == 4:
            item_collection_index = 1
        else:
            item_collection_index += 1

def leave_main_menu():
    if get_latest_equipped_aura(rblx_log_dir) == "In Main Menu":
        mkey.left_click_xy_natural(start_btn_pos[0], start_btn_pos[1])
        time.sleep(4)
        leave_main_menu()

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

def get_latest_equipped_aura(logs_dir):
    log_files = glob.glob(os.path.join(logs_dir, "*.log"))
    if not log_files:
        return None

    latest_log_file = max(log_files, key=os.path.getctime)
    try:
        temp_file = os.path.join(tempfile.gettempdir(), "solsrngbot_aura_detection.log")
        shutil.copy2(latest_log_file, temp_file)
    except PermissionError:
        return None

    json_pattern = re.compile(r'\{.*\}')
    
    try:
        with open(temp_file, "r", encoding="utf-8") as file:
            for line in reversed(file.readlines()):
                match = json_pattern.search(line)
                if match:
                    try:
                        json_data = json.loads(match.group())
                        if json_data.get("data", {}).get("state", "") == "In Main Menu":
                            return "In Main Menu"
                        aura = json_data.get("data", {}).get("state", "").replace("Equipped \"", "").replace("\"", "")
                        if aura:
                            aura = aura.replace("_", ": ")
                            return aura
                    except json.JSONDecodeError:
                        continue
    except Exception:
        return None
    
    return None

def detect_client_disconnect(logs_dir, lines_to_check=10):
    log_files = glob.glob(os.path.join(logs_dir, "*.log"))
    if not log_files:
        return False

    latest_log_file = max(log_files, key=os.path.getctime)
    try:
        temp_file = os.path.join(tempfile.gettempdir(), "solsrngbot_biome_detection.log")
        shutil.copy2(latest_log_file, temp_file)
    except PermissionError:
        return False

    disconnect_patterns = [
        r"Lost connection with reason : Lost connection to the game server, please reconnect",
    ]
    
    try:
        with open(temp_file, "r", encoding="utf-8") as file:
            last_lines = file.readlines()[-lines_to_check:]
            for line in reversed(last_lines):
                if any(re.search(pattern, line) for pattern in disconnect_patterns):
                    timestamp_match = re.search(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", line)
                    if timestamp_match:
                        timestamp = timestamp_match.group()
                        GLOBAL_LOGGER.write_log(f"Disconnection detected at {timestamp}")
                    return True
    except Exception:
        return False
    
    return False

def detect_client_reconnect(logs_dir, lines_to_check=20):
    log_files = glob.glob(os.path.join(logs_dir, "*.log"))
    if not log_files:
        return False

    latest_log_file = max(log_files, key=os.path.getctime)
    try:
        temp_file = os.path.join(tempfile.gettempdir(), "solsrngbot_biome_detection.log")
        shutil.copy2(latest_log_file, temp_file)
    except PermissionError:
        return False

    disconnect_patterns = [
        r"NetworkClient:Create",
        r"Info: Stack End",
        r"Connection accepted from"
    ]
    
    try:
        with open(temp_file, "r", encoding="utf-8") as file:
            last_lines = file.readlines()[-lines_to_check:]
            for line in reversed(last_lines):
                if any(re.search(pattern, line) for pattern in disconnect_patterns):
                    timestamp_match = re.search(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", line)
                    if timestamp_match:
                        timestamp = timestamp_match.group()
                        GLOBAL_LOGGER.write_log(f"Reconnection detected at {timestamp}")
                    return True
    except Exception:
        return False
    
    return False

def exists_procs_by_name(name):
    for p in psutil.process_iter(['name']):
        if p.info['name'].lower() == name.lower():
            return True
    return False

def get_process_by_name(name):
    for p in psutil.process_iter(['name']):
        if p.info['name'].lower() == name.lower():
            return p
    return False

def match_rblx_hwnd_to_pid(pid):
    for w in mkey.get_all_windows():
        if w.pid == pid:
            return w
    return False


class Macro:
    def __init__(self, root):
        global GLOBAL_LOGGER
        self.root = root
        self.root.title("Baz's Macro")

        self.root.geometry("600x300")

        try:
            self.root.iconbitmap(f"{MACROPATH}/icon.ico")
        except Exception:
            pass

        self.original_settings = self.load_settings()
        self.entries = {}
        self.listbox_refs = {}

        self.threads = []
        self.running = False
        self.keyboard_lock = threading.Lock()
        self.pause_event = threading.Event()
        self.stop_event = threading.Event()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=1, fill='both')
        
        tab_info = {
            "General": GENERAL_KEYS,
            "Auras": AURAS_KEYS,
            "Biomes": BIOMES_KEYS,
            "Sniper": SNIPER_KEYS,
            "Merchant": MERCHANT_KEYS,
            "Auto Craft": AUTOCRAFT_KEYS,
            "Other": OTHER_KEYS,
        }

        for tab_name, keys in tab_info.items():
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=tab_name)
            self.create_scrollable_tab(tab_frame, keys)
            self.create_bottom_buttons(tab_frame)

            if tab_name == "Merchant":
                self.tesseract_installed = (shutil.which("tesseract") is not None or os.path.exists(r'C:\Program Files\Tesseract-OCR'))
                if self.tesseract_installed and shutil.which("tesseract") is None:
                    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                status_text = "Tesseract OCR: Installed" if self.tesseract_installed else "Tesseract OCR: Not Installed"
                status_color = "green" if self.tesseract_installed else "red"

                ocr_label = ttk.Label(tab_frame, text=status_text, foreground=status_color)
                ocr_label.pack(pady=5, anchor="w", padx=10)

                if not self.tesseract_installed:
                    download_button = ttk.Button(tab_frame, text="Download Tesseract", command=lambda: webbrowser.open("https://github.com/tesseract-ocr/tesseract/releases/latest"))
                    download_button.pack(pady=2, anchor="w", padx=10)

        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs")
        log_container = ttk.Frame(logs_frame)
        log_container.pack(fill='both', expand=True)

        self.log_widget = tk.Text(log_container, state='disabled', height=10)
        scrollbar = ttk.Scrollbar(log_container, orient='vertical', command=self.log_widget.yview)
        self.log_widget.configure(yscrollcommand=scrollbar.set)

        self.log_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.logger = self.Logger(self.log_widget)
        GLOBAL_LOGGER = self.logger
        self.logger.text_widget = self.log_widget
        if self.tesseract_installed and shutil.which("tesseract") is None:
            GLOBAL_LOGGER.write_log("Tesseract was not detected in PATH, but was detected as installed.")

        self.snipers = []

        credits_frame = ttk.Frame(self.notebook)
        self.notebook.add(credits_frame, text="Credits")
        
        ttk.Label(credits_frame, text="Created by Baz").pack(pady=10)

        if not os.path.isfile(f"{MACROPATH}/baz.png"):
            img_dl = requests.get("https://github.com/bazthedev/SolsRNGBot/blob/88024a205599dc812d991f36c195923df599e55c/img/baz.png")
            with open(f"{MACROPATH}/baz.png", "wb") as f:
                f.write(img_dl.content)
                f.close()

        try:
            image_path = f"{MACROPATH}/baz.png"
            img = Image.open(image_path)
            
            img_resized = img.resize((150, 150))
            
            img_tk = ImageTk.PhotoImage(img_resized)
            
            image_label = ttk.Label(credits_frame, image=img_tk)
            image_label.image = img_tk
            image_label.pack(pady=10)
        except Exception as e:
            GLOBAL_LOGGER.write_log(f"Failed to load and resize image: {e}")
        
        ttk.Label(credits_frame, text="Root1527 for yay joins").pack(pady=10)
        
        self.plugins = []
        self.load_plugins()

    def create_scrollable_tab(self, frame, keys):
        canvas = tk.Canvas(frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = ttk.Frame(canvas)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        self.populate_tab(scrollable_frame, keys)

    def populate_tab(self, frame, keys):
        filtered_settings = {k: self.original_settings.get(k, "") for k in keys if k in self.original_settings}
        self.create_widgets(filtered_settings, frame)

    class Logger:
        def __init__(self, text_widget=None):
            self.text_widget = text_widget
            self.write_log(f"Initialising v{LOCALVERSION}\n")

        def write_log(self, message):
            try:
                message = str(message)
            except Exception:
                return
            if self.text_widget:
                self.text_widget.configure(state='normal')
                self.text_widget.insert(tk.END, message + "\n")
                self.text_widget.see(tk.END)
                self.text_widget.configure(state='disabled')
    
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

    def create_list_widget(self, parent, key, items):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, expand=True)

        listbox = tk.Listbox(frame, height=5, selectmode=tk.SINGLE)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for item in items:
            listbox.insert(tk.END, item)

        self.entries[key] = items
        self.listbox_refs[key] = listbox

        button_frame = ttk.Frame(frame)
        button_frame.pack(side=tk.RIGHT, padx=5)

        add_entry = ttk.Entry(button_frame, width=15)
        add_entry.pack(pady=2)

        add_button = ttk.Button(button_frame, text="Add", command=lambda: self.add_to_list(key, add_entry))
        add_button.pack(pady=2)

        remove_button = ttk.Button(button_frame, text="Remove", command=lambda: self.remove_from_list(key))
        remove_button.pack(pady=2)

    def add_to_list(self, key, entry):
        new_item = entry.get().strip()
        if new_item:
            listbox = self.listbox_refs[key]
            if new_item not in self.entries[key]:
                self.entries[key].append(new_item)
                listbox.insert(tk.END, new_item)
                entry.delete(0, tk.END)

    def remove_from_list(self, key):
        listbox = self.listbox_refs[key]
        selection = listbox.curselection()

        if selection:
            index = selection[0]
            listbox.delete(index)
            self.entries[key].pop(index)

    def create_widgets(self, settings, parent, entry_dict=None):
        if entry_dict is None:
            entry_dict = self.entries

        for key, value in settings.items():
            if key == "__version__":
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

            elif isinstance(value, list):
                self.create_list_widget(row, key, value)

            else:
                var = tk.StringVar(value=str(value))
                entry = ttk.Entry(row, textvariable=var, width=30)
                entry.pack(side=tk.LEFT)
                entry_dict[key] = var


    def get_updated_values(self, original, entries):
        updated_settings = {}

        for key, widget in entries.items():
            original_value = original.get(key)
            
            if isinstance(original_value, dict):
                sub_updates = self.get_updated_values(original_value, widget)
                if sub_updates:
                    updated_settings[key] = sub_updates
            else:
                try:
                    new_value = widget.get()
                except AttributeError:
                    new_value = widget

                if isinstance(original_value, bool):
                    new_value = bool(new_value)
                elif isinstance(original_value, (int, float)):
                    try:
                        new_value = int(new_value)
                    except ValueError:
                        try:
                            new_value = float(new_value)
                        except ValueError:
                            pass
                if new_value != original_value:
                    updated_settings[key] = new_value

        return updated_settings


    def save_settings(self):
        updated_values = self.get_updated_values(self.original_settings, self.entries)

        if not updated_values:
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
            messagebox.showinfo("Baz's Macro Settings Editor", "Settings saved successfully!")
            reload_settings()
            GLOBAL_LOGGER.write_log("Settings were reloaded.")
        except Exception as e:
            messagebox.showerror("Baz's Macro Settings Editor", f"Failed to save settings:\n{e}")

    def create_bottom_buttons(self, tab_frame):
        button_frame = ttk.Frame(tab_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        button1 = ttk.Button(button_frame, text="Start", command=self.start_macro)
        button1.pack(side=tk.LEFT, padx=5)

        button2 = ttk.Button(button_frame, text="Stop", command=self.stop_macro)
        button2.pack(side=tk.LEFT, padx=5)

    def load_plugin_config(self, plugin_name):
        config_path = f"{MACROPATH}/plugins/config/{plugin_name}.json"
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
        
    def load_plugins(self):
        plugin_dir = os.path.join(MACROPATH, "plugins")
        config_dir = os.path.join(plugin_dir, "config")
        os.makedirs(config_dir, exist_ok=True)

        plugin_files = glob.glob(os.path.join(plugin_dir, "*.py"))

        for plugin_file in plugin_files:
            try:
                plugin_name = os.path.splitext(os.path.basename(plugin_file))[0]
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                plugin_class = getattr(module, "Plugin", None)
                if plugin_class:
                    plugin_instance = plugin_class(self)
                    plugin_instance.entries = {}

                    tab_frame = ttk.Frame(self.notebook)
                    self.notebook.add(tab_frame, text=plugin_instance.name)

                    plugin_instance.init_tab(tab_frame, {
                        "create_widgets": self.create_widgets,
                        "create_bottom_buttons": self.create_bottom_buttons,
                        "format_key": self.format_key,
                        "entries": plugin_instance.entries
                    })

                    self.plugins.append(plugin_instance)

                    self.logger.write_log(
                        f"Loaded Plugin: {plugin_instance.name} v{getattr(plugin_instance, 'version', 'Unknown')} by {getattr(plugin_instance, 'author', 'Unknown')}"
                    )

            except Exception as e:
                self.logger.write_log(f"Error loading plugin '{plugin_file}': {e}")


    def start_macro(self):
        changes = self.save_settings()
        for plugin in self.plugins:
            plugin.save_config()
        reload_settings()

        if changes:
            GLOBAL_LOGGER.write_log("Changes detected and saved.")
        else:
            GLOBAL_LOGGER.write_log("No changes detected.")

        if self.running:
            messagebox.showerror("Error", "Macro is already running!")
            return

        if settings["WEBHOOK_URL"] == "":
            messagebox.showerror("Error", "You need to provide a Webhook URL")
            return

        self.webhook = discord.Webhook.from_url(settings["WEBHOOK_URL"], adapter=discord.RequestsWebhookAdapter())

        self.running = True
        self.stop_event.clear()

        if not settings["auto_craft_mode"]:
            threading.Thread(target=self._run_macro, daemon=True).start()
        else:
            threading.Thread(target=self._run_autocraft, daemon=True).start()

    def _run_macro(self):
        GLOBAL_LOGGER.write_log("Starting Macro in 5 seconds")
        GLOBAL_LOGGER.write_log(random.choice(STARTUP_MSGS))
        GLOBAL_LOGGER.write_log(f"Started at {now.strftime('%d/%m/%Y %H:%M:%S')} running v{__version__} using local version {LOCALVERSION}")
        for _ in range(5):
            if self.stop_event.is_set():
                GLOBAL_LOGGER.write_log("Macro stopped before starting.")
                self.running = False
                return
            time.sleep(1)
            
        previous_thread = None
        for i in range(10):
            if self.stop_event.is_set():
                break

            if i == 0:
                thread = threading.Thread(target=self.aura_detection, daemon=True)
                GLOBAL_LOGGER.write_log("Started Aura Detection")
            elif i == 1:
                for _ in settings["biomes"].keys():
                    if settings["biomes"][_]:
                        thread = threading.Thread(target=self.biome_detection, daemon=True)
                        GLOBAL_LOGGER.write_log("Started Biome Detection")
                        break
            elif i == 2 and not settings["disable_autokick_prevention"]:
                thread = threading.Thread(target=self.keep_alive, daemon=True)
                GLOBAL_LOGGER.write_log("Started Autokick Prevention")
            elif i == 3 and settings["sniper_enabled"]:
                if not (settings["ROBLOSECURITY_KEY"] == "" or settings["DISCORD_TOKEN"] == ""):
                    for channel_id in settings["scan_channels"]:
                        self.snipers.append(self.Sniper(self, channel_id))
                    def start_snipers():
                        async def run_all_snipers():
                            await asyncio.gather(*(sniper.run() for sniper in self.snipers))

                        asyncio.run(run_all_snipers())

                    thread = threading.Thread(target=start_snipers, daemon=True)
                    GLOBAL_LOGGER.write_log(f"Starting {str(len(self.snipers))} Snipers")
                else:
                    GLOBAL_LOGGER.write_log("You must provide both your ROBLOSECURITY cookie and your Discord Token for the sniper to work. You also need to set a sniper logs channel")
            elif i == 4 and settings["disconnect_prevention"]:
                thread = threading.Thread(target=self.disconnect_prevention, daemon=True)
                GLOBAL_LOGGER.write_log("Started Disconnect Prevention")
            elif i == 5 and settings["merchant_detection"]:
                if self.tesseract_installed:
                    thread = threading.Thread(target=self.merchant_detection, daemon=True)
                    GLOBAL_LOGGER.write_log("Started Merchant Detection")
                else:
                    dl_ts = messagebox.askyesno("Baz's Macro", "Tesseract is not installed, would you like to download it?")
                    if dl_ts:
                        webbrowser.open("https://github.com/tesseract-ocr/tesseract/releases/latest")
                    GLOBAL_LOGGER.write_log("Merchant Detection was not started because Tesseract is not installed.")
            elif i == 6 and settings["auto_biome_randomizer"]:
                thread = threading.Thread(target=self.auto_br, daemon=True)
                GLOBAL_LOGGER.write_log("Started Auto Biome Randomizer")
            elif i == 7 and settings["auto_strange_controller"]:
                thread = threading.Thread(target=self.auto_sc, daemon=True)
                GLOBAL_LOGGER.write_log("Started Auto Strange Controller")
            elif i == 8 and settings["periodic_screenshots"]["inventory"]:
                thread = threading.Thread(target=self.inventory_screenshot, daemon=True)
                GLOBAL_LOGGER.write_log("Started Periodic Inventory Screenshots")
            elif i == 9 and settings["periodic_screenshots"]["storage"]:
                thread = threading.Thread(target=self.inventory_screenshot, daemon=True)
                GLOBAL_LOGGER.write_log("Started Periodic Aura Storage Screenshots")

            if thread != previous_thread:
                thread.start()
                self.threads.append(thread)
            previous_thread = thread

        for plugin in self.plugins:
            try:
                thread = threading.Thread(target=plugin.run, args=(self.stop_event, self.pause_event), daemon=True)
                thread.start()
                self.threads.append(thread)
                GLOBAL_LOGGER.write_log(f"Started plugin thread: {plugin.name}")
            except Exception as e:
                GLOBAL_LOGGER.write_log(f"Failed to start plugin thread '{plugin.name}': {e}")
                
        GLOBAL_LOGGER.write_log("Macro has started.")
        emb = discord.Embed(
            title="Macro has started",
            description=f"Mode: Normal\nStarted at {now.strftime('%d/%m/%Y %H:%M:%S')}",
            colour=discord.Colour.green()
        )
        emb.set_footer(text=f"bazthedev/SolsRNGBot v{LOCALVERSION}")
        self.webhook.send(avatar_url=WEBHOOK_ICON_URL, embed=emb)

    def _run_autocraft(self):
        crafts = ""
        for item in settings["auto_craft_item"].keys():
            if settings["auto_craft_item"][item]:
                crafts += f"{item}\n"
        emb = discord.Embed(
            title="Macro has started",
            description=f"Mode: Auto Craft\nAuto Craft item(s):\n{crafts}\nStarted at {now.strftime('%d/%m/%Y %H:%M:%S')}",
            colour=discord.Colour.green()
        )
        emb.set_footer(text=f"bazthedev/SolsRNGBot v{LOCALVERSION}")
        self.webhook.send(avatar_url=WEBHOOK_ICON_URL, embed=emb)
        GLOBAL_LOGGER.write_log("[WARNING] Auto Craft Mode is on. You will not be able to use certain features whilst this settings is on.")
        GLOBAL_LOGGER.write_log(f"The item(s) you are automatically crafting are:\n{crafts}")
        GLOBAL_LOGGER.write_log("Please ensure that you are standing next to the cauldron so that you can see the \"f\" prompt.")
        if settings["reset_aura"] != "":
            settings["reset_aura"] = ""
            update_settings(settings)
            reload_settings()
        GLOBAL_LOGGER.write_log("Starting auto craft mode. Please click back onto Roblox and wait 10 seconds")
        time.sleep(10)
        thread = threading.Thread(target=self.auto_craft, daemon=True)
        thread.start()
        self.threads.append(thread)
        GLOBAL_LOGGER.write_log("Started Auto Craft")

    def stop_macro(self):
        if not self.running:
            messagebox.showerror("Error", "Macro is not running!")
            return

        GLOBAL_LOGGER.write_log("Stopping Macro...")

        self.stop_event.set()

        for thread in self.threads:
            thread.join(timeout=1)
            GLOBAL_LOGGER.write_log(f"Thread marked for termination: {str(thread)}")

        GLOBAL_LOGGER.write_log("Macro will completely stop after the current thread cycle has finished.")

        self.threads.clear()
        self.running = False

        for sniper in self.snipers:
            sniper.cancel()

        GLOBAL_LOGGER.write_log("Macro was stopped.")
        emb = discord.Embed(
            title="Macro has stopped.",
            colour=discord.Colour.red()
        )
        emb.set_footer(text=f"SolsRNGBot v{LOCALVERSION}", icon_url=WEBHOOK_ICON_URL)
        self.webhook.send(avatar_url=WEBHOOK_ICON_URL, embed=emb)
        messagebox.showinfo("Baz's Macro", "Macro has been stopped.")

    def aura_detection(self):
        global previous_aura
        while not self.stop_event.is_set():
            if self.stop_event.is_set():
                return
            current_aura = get_latest_equipped_aura(rblx_log_dir)
            if previous_aura == None:
                previous_aura = current_aura
                continue
            if current_aura == "In Main Menu":
                continue
            if current_aura == settings["reset_aura"] and settings["reset_aura"] != "":
                continue
            if current_aura == previous_aura:
                continue
            try:
                if current_aura.lower() in auras.keys():
                    previous_aura = current_aura
                    rnow = datetime.now()
                    current_biome = get_latest_hovertext(rblx_log_dir)
                    if current_biome.lower() == auras[current_aura.lower()]["native_biome"].lower():
                        if current_biome.lower() == "snowy":
                            aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / SNOWY_MULTIPLIER)
                        elif current_biome.lower() == "windy":
                            aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / WINDY_MULTIPLIER)
                        elif current_biome.lower() == "rainy":
                            aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / RAINY_MULTIPLER)
                        elif current_biome.lower() == "sand storm":
                            aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / SANDSTORM_MULTIPLIER)
                        elif current_biome.lower() == "hell":
                            aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / HELL_MULTIPLIER)
                        elif current_biome.lower() == "starfall":
                            aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / STARFALL_MULTIPLIER)
                        elif current_biome.lower() == "corruption":
                            aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / CORRUPTION_MULTIPLIER)
                        elif current_biome.lower() == "null":
                            aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / NULL_MULTIPLIER)
                        elif current_biome.lower() == "glitched":
                            aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / GLITCHED_MULTIPLIER)
                        elif current_biome.lower() == "dreamspace":
                            aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / DREAMSPACE_MULTIPLIER)
                        emb = discord.Embed(
                            title=f"Aura Rolled: {current_aura}",
                            description=f"Rolled Aura: {current_aura}\nWith chances of 1/{str(aura_rarity)} (from {auras[current_aura.lower()]["native_biome"]})\nAt time: {rnow.strftime('%d/%m/%Y %H:%M:%S')}",
                            colour=discord.Colour.from_rgb(hex2rgb(auras[current_aura.lower()]["emb_colour"])[0],hex2rgb(auras[current_aura.lower()]["emb_colour"])[1],hex2rgb(auras[current_aura.lower()]["emb_colour"])[2])
                        )
                        if auras[current_aura.lower()]["img_url"] != "":
                            emb.set_thumbnail(url=auras[current_aura.lower()]["img_url"])
                    else:
                        emb = discord.Embed(
                            title=f"Aura Rolled: {current_aura}",
                            description=f"Rolled Aura: {current_aura}\nWith chances of 1/{auras[current_aura.lower()]["rarity"]}\nAt time: {rnow.strftime('%d/%m/%Y %H:%M:%S')}",
                            colour=discord.Colour.from_rgb(hex2rgb(auras[current_aura.lower()]["emb_colour"])[0],hex2rgb(auras[current_aura.lower()]["emb_colour"])[1],hex2rgb(auras[current_aura.lower()]["emb_colour"])[2])
                        )
                        if auras[current_aura.lower()]["img_url"] != "":
                            emb.set_thumbnail(url=auras[current_aura.lower()]["img_url"])
                    if settings["take_screenshot_on_detection"]:
                        auraimg = pag.screenshot(f"{MACROPATH}/scr/screenshot_aura.png")
                        up = discord.File(f"{MACROPATH}/scr/screenshot_aura.png", filename="aura.png")
                        emb.set_image(url="attachment://aura.png")
                        if settings["mention"] and settings["mention_id"] != 0 and (int(auras[current_aura.lower()]["rarity"]) > int(settings["minimum_ping"])):
                            self.webhook.send(avatar_url=WEBHOOK_ICON_URL, content=f"<@{settings['mention_id']}>", embed=emb, file=up)
                        else:
                            self.webhook.send(avatar_url=WEBHOOK_ICON_URL, embed=emb, file=up)
                    else:
                        if settings["mention"] and settings["mention_id"] != 0 and (int(auras[current_aura.lower()]["rarity"]) > int(settings["minimum_ping"])):
                            self.webhook.send(avatar_url=WEBHOOK_ICON_URL, content=f"<@{settings['mention_id']}>", embed=emb)
                        else:
                            self.webhook.send(avatar_url=WEBHOOK_ICON_URL, embed=emb)
                    GLOBAL_LOGGER.write_log(f"Rolled Aura: {current_aura}\nWith chances of 1/{auras[current_aura.lower()]["rarity"]}\nAt time: {rnow.strftime('%d/%m/%Y %H:%M:%S')}")
                    if settings["reset_aura"] != "":
                        if current_aura == settings["reset_aura"]:
                            continue
                        with self.keyboard_lock:
                            mkey.left_click_xy_natural(aura_button_pos[0], aura_button_pos[1])
                            time.sleep(0.2)
                            mkey.left_click_xy_natural(search_pos[0], search_pos[1])
                            time.sleep(0.2)
                            _keyboard.type(settings["reset_aura"])
                            time.sleep(0.2)
                            mkey.left_click_xy_natural(query_pos[0], query_pos[1])
                            time.sleep(0.2)
                            mkey.left_click_xy_natural(equip_pos[0], equip_pos[1])
                            time.sleep(0.2)
                            mkey.left_click_xy_natural(equip_pos[0], equip_pos[1])
                            time.sleep(0.2)
                            mkey.left_click_xy_natural(close_pos[0], close_pos[1])
                            time.sleep(0.2)
                            mkey.left_click_xy_natural(close_pos[0], close_pos[1])
            except KeyError:
                pass
            except AttributeError:
                pass
            except Exception as e:
                GLOBAL_LOGGER.write_log(f"Error with Aura Detection: {e}")

    def biome_detection(self):
        global previous_biome
        while not self.stop_event.is_set():
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
                            self.webhook.send(avatar_url=WEBHOOK_ICON_URL, content="@everyone", embed=emb)
                        else:
                            self.webhook.send(avatar_url=WEBHOOK_ICON_URL, embed=emb)
            except KeyError:
                pass
            except AttributeError:
                pass
            except Exception as e:
                GLOBAL_LOGGER.write_log(f"Error with Biome Detection: {e}")

    def auto_craft(self):
        global auto_mode_swap, auto_craft_index
        items_to_craft = []
        for itm in settings["auto_craft_item"].keys():
            if settings["auto_craft_item"][itm]:
                items_to_craft.append(itm)
        if len(items_to_craft) < 1:
            return
        
        def search_for_potion(potion_name):
            _keyboard.press("f")
            time.sleep(0.2)
            _keyboard.release("f")
            time.sleep(0.2)
            mkey.left_click_xy_natural(potion_search_pos[0], potion_search_pos[1])
            time.sleep(0.2)
            mkey.left_click_xy_natural(potion_search_pos[0], potion_search_pos[1])
            time.sleep(0.2)
            _keyboard.type(potion_name)
            time.sleep(0.2)
            mkey.left_click_xy_natural(first_potion_pos[0], first_potion_pos[1])
            time.sleep(0.2)
            mkey.left_click_xy_natural(potion_search_pos[0], potion_search_pos[1])
            time.sleep(0.2)

        while not self.stop_event.is_set():
            if settings["auto_craft_item"]["Potion of Bound"]:
                search_for_potion("Bound")
                mkey.left_click_xy_natural(craft_btn_pos[0], craft_btn_pos[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
                time.sleep(0.2)
                if auto_craft_index == 1 and len(items_to_craft) > 1:
                    mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                    time.sleep(0.2)
                mkey.left_click_xy_natural(potion_search_pos[0], potion_search_pos[1])
                time.sleep(0.2)
            if settings["auto_craft_item"]["Heavenly Potion"]:
                search_for_potion("Heavenly")
                time.sleep(0.2)
                mkey.left_click_xy_natural(craft_btn_pos[0], craft_btn_pos[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
                time.sleep(0.2)
                _keyboard.type("250")
                mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp2_pos_potions[0], hp2_pos_potions[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp2_pos_potions[0], hp2_pos_potions[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural((1064 * scale_w), (988 * scale_h))
                time.sleep(0.2)
                if auto_craft_index == 2 and len(items_to_craft) > 1:
                    mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                    time.sleep(0.2)
                mkey.left_click_xy_natural(potion_search_pos[0], potion_search_pos[1])
                time.sleep(0.2)
            if settings["auto_craft_item"]["Godly Potion (Zeus)"]:
                search_for_potion("Zeus")
                time.sleep(0.2)
                mkey.left_click_xy_natural(craft_btn_pos[0], craft_btn_pos[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
                time.sleep(0.2)
                _keyboard.type("25")
                mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp2_pos_potions[0] - (110 * scale_w), hp2_pos_potions[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp2_pos_potions[0] - (110 * scale_w), hp2_pos_potions[1])
                time.sleep(0.2)
                _keyboard.type("25")
                mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp2_pos_potions[0], hp2_pos_potions[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural((1064 * scale_w), (988 * scale_h))
                time.sleep(0.2)
                if auto_craft_index == 3 and len(items_to_craft) > 1:
                    mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                    time.sleep(0.2)
                mkey.left_click_xy_natural(potion_search_pos[0], potion_search_pos[1])
                time.sleep(0.2)
            if settings["auto_craft_item"]["Godly Potion (Poseidon)"]:
                search_for_potion("Poseidon")
                time.sleep(0.2)
                mkey.left_click_xy_natural(craft_btn_pos[0], craft_btn_pos[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
                time.sleep(0.2)
                _keyboard.type("50")
                mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp2_pos_potions[0], hp2_pos_potions[1])
                time.sleep(0.2)
                if auto_craft_index == 4 and len(items_to_craft) > 1:
                    mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                    time.sleep(0.2)
                mkey.left_click_xy_natural(potion_search_pos[0], potion_search_pos[1])
                time.sleep(0.2)
            if settings["auto_craft_item"]["Godly Potion (Hades)"]:
                search_for_potion("Hades")
                time.sleep(0.2)
                mkey.left_click_xy_natural(craft_btn_pos[0], craft_btn_pos[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
                time.sleep(0.2)
                _keyboard.type("50")
                mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp2_pos_potions[0], hp2_pos_potions[1])
                time.sleep(0.2)
                if auto_craft_index == 5 and len(items_to_craft) > 1:
                    mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                    time.sleep(0.2)
                mkey.left_click_xy_natural(potion_search_pos[0], potion_search_pos[1])
                time.sleep(0.2)
            if settings["auto_craft_item"]["Warp Potion"]:
                search_for_potion("Warp")
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
                mkey.left_click_xy_natural(hp1_pos_celestial[0] - (110 * scale_w), hp1_pos_celestial[1])
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
                if auto_craft_index == 6 and len(items_to_craft) > 1:
                    mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                    time.sleep(0.2)
                mkey.left_click_xy_natural(potion_search_pos[0], potion_search_pos[1])
                time.sleep(0.2)
            if settings["auto_craft_item"]["Godlike Potion"]:
                search_for_potion("Godlike")
                time.sleep(0.2)
                mkey.left_click_xy_natural(craft_btn_pos[0], craft_btn_pos[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(hp2_pos_potions[0], hp2_pos_potions[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural((1064 * scale_w), (988 * scale_h))
                time.sleep(0.2)
                mkey.left_click_xy_natural(potion_search_pos[0], potion_search_pos[1])
                time.sleep(0.2)
            if auto_craft_index > 6:
                auto_craft_index = 1
            if auto_mode_swap == 5:
                auto_mode_swap = 0
            else:
                auto_mode_swap += 1
            auto_craft_index += 1
            time.sleep(60)


    def merchant_detection(self):
        while not self.stop_event.is_set():
            time.sleep(90)
            with self.keyboard_lock:
                use_item("Merchant Teleport", 1, False)
                rnow = datetime.now()
                mkey.left_click_xy_natural(close_pos[0], close_pos[1])
                time.sleep(1)
                _keyboard.press("e")
                time.sleep(5)
                _keyboard.release("e")
                time.sleep(2)
                mkey.left_click_xy_natural(open_merch_pos[0], open_merch_pos[1])
                time.sleep(2)
                merchimg = pag.screenshot(f"{MACROPATH}/scr/screenshot_merchant.png")
                time.sleep(0.2)
                up = discord.File(f"{MACROPATH}/scr/screenshot_merchant.png", filename="merchant.png")
                try:
                    image_path = f"{MACROPATH}/scr/screenshot_merchant.png"
                    image = cv2.imread(image_path)
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
                    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    contours = sorted(contours, key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))
                    box_data = {}
                    box_id = 1

                    for cnt in contours:
                        x, y, w, h = cv2.boundingRect(cnt)
                        if w > 50 and h > 20:
                            roi = image[y:y+h, x:x+w]
                            text = pytesseract.image_to_string(roi).strip()
                            if text:
                                box_data[box_id] = {
                                    "text": text,
                                    "coordinates": (x, y, w, h)
                                }
                                box_id += 1
                    x1, y1, x2, y2 = merchant_box
                    merchant_crop = image[y1:y2, x1:x2]
                    ocr_merchant = pytesseract.image_to_string(merchant_crop).strip()
                    ocr_merchant_clean = re.sub(r"[^a-zA-Z]", "", ocr_merchant).lower()

                    detected_full = fuzzy_match_merchant(ocr_merchant_clean, possible_merchants)

                    if detected_full:
                        merchant_name = detected_full.split("'")[0]
                        GLOBAL_LOGGER.write_log(f"\nMerchant Detected: {merchant_name} (OCR: {ocr_merchant})")
                    else:
                        continue
                    
                    if merchant_name == "Mari":
                        emb = discord.Embed(
                                        title = "Mari Spawned",
                                        description = f"A Mari has been detected at time: {rnow.strftime('%d/%m/%Y %H:%M:%S')}",
                                        colour = discord.Color.from_rgb(255, 255, 255)
                        )
                        emb.set_thumbnail(url="https://static.wikia.nocookie.net/sol-rng/images/3/37/MARI_HIGH_QUALITYY.png/revision/latest")
                        emb.set_image(url="attachment://merchant.png")
                    elif merchant_name == "Jester":
                        emb = discord.Embed(
                                    title = "Jester Spawned",
                                    description = f"A Jester has been detected at time: {rnow.strftime('%d/%m/%Y %H:%M:%S')}",
                                    colour = discord.Color.from_rgb(176, 49, 255)
                        )
                        emb.set_thumbnail(url="https://static.wikia.nocookie.net/sol-rng/images/d/db/Headshot_of_Jester.png/revision/latest")
                        emb.set_image(url="attachment://merchant.png")

                    detected_items = {}
                    if valid_ps:
                            emb.add_field(name="Server Invite:", value=f"{settings['private_server_link']}", inline=True)

                    for name, (x1, y1, x2, y2) in manual_boxes.items():
                        cropped = image[y1:y2, x1:x2]
                        ocr_raw = pytesseract.image_to_string(cropped).strip()
                        if merchant_name == None:
                            break
                        if merchant_name.lower() == "mari":
                            matched = fuzzy_match(ocr_raw, MARI_ITEMS, threshold=0.5)
                        elif merchant_name.lower() == "jester":
                            matched = fuzzy_match(ocr_raw, JESTER_ITEMS, threshold=0.5)
                        GLOBAL_LOGGER.write_log(f"[{name}] -> {matched} (OCR: {ocr_raw})")
                        detected_items[name] = matched
                        emb.add_field(name=f"{name}", value=f"Detected Item: {matched}\n\nRaw OCR input: `{ocr_raw}`", inline=True)
                    self.webhook.send(avatar_url=WEBHOOK_ICON_URL, embed=emb, file=up)
                    if merchant_name == "Mari":
                        for item in detected_items.keys():
                            if settings["auto_purchase_items_mari"][detected_items[item]]:
                                if item == "Box 1":
                                    mkey.left_click_xy_natural(merch_item_pos_1_purchase[0], merch_item_pos_1_purchase[1], print_coords=False)
                                    time.sleep(0.2)
                                    mkey.left_click_xy_natural(quantity_btn_pos[0], quantity_btn_pos[1], print_coords=False)
                                    time.sleep(settings["global_wait_time"])
                                    _keyboard.type("25")
                                    time.sleep(settings["global_wait_time"])
                                    mkey.left_click_xy_natural(purchase_btn_pos[0], purchase_btn_pos[1], print_coords=False)
                                    time.sleep(settings["global_wait_time"])
                                elif item == "Box 2":
                                    mkey.left_click_xy_natural(merch_item_pos_2_purchase[0], merch_item_pos_2_purchase[1], print_coords=False)
                                    time.sleep(0.2)
                                    mkey.left_click_xy_natural(quantity_btn_pos[0], quantity_btn_pos[1], print_coords=False)
                                    time.sleep(settings["global_wait_time"])
                                    _keyboard.type("25")
                                    time.sleep(settings["global_wait_time"])
                                    mkey.left_click_xy_natural(purchase_btn_pos[0], purchase_btn_pos[1], print_coords=False)
                                    time.sleep(settings["global_wait_time"])
                                elif item == "Box 3":
                                    mkey.left_click_xy_natural(merch_item_pos_3_purchase[0], merch_item_pos_3_purchase[1], print_coords=False)
                                    time.sleep(0.2)
                                    mkey.left_click_xy_natural(quantity_btn_pos[0], quantity_btn_pos[1])
                                    time.sleep(settings["global_wait_time"])
                                    _keyboard.type("25")
                                    time.sleep(settings["global_wait_time"])
                                    mkey.left_click_xy_natural(purchase_btn_pos[0], purchase_btn_pos[1])
                                    time.sleep(settings["global_wait_time"])
                                elif item == "Box 4":
                                    mkey.left_click_xy_natural(merch_item_pos_4_purchase[0], merch_item_pos_4_purchase[1], print_coords=False)
                                    time.sleep(0.2)
                                    mkey.left_click_xy_natural(quantity_btn_pos[0], quantity_btn_pos[1])
                                    time.sleep(settings["global_wait_time"])
                                    _keyboard.type("25")
                                    time.sleep(settings["global_wait_time"])
                                    mkey.left_click_xy_natural(purchase_btn_pos[0], purchase_btn_pos[1])
                                    time.sleep(settings["global_wait_time"])
                                elif item == "Box 5":
                                    mkey.left_click_xy_natural(merch_item_pos_5_purchase[0], merch_item_pos_5_purchase[1], print_coords=False)
                                    time.sleep(0.2)
                                    mkey.left_click_xy_natural(quantity_btn_pos[0], quantity_btn_pos[1])
                                    time.sleep(settings["global_wait_time"])
                                    _keyboard.type("25")
                                    time.sleep(settings["global_wait_time"])
                                    mkey.left_click_xy_natural(purchase_btn_pos[0], purchase_btn_pos[1])
                                    time.sleep(settings["global_wait_time"])
                                emb = discord.Embed(
                                    title="Purchased Item from Mari",
                                    description=f"Item purchased: {detected_items[item]}",
                                    colour = discord.Color.from_rgb(255, 255, 255)
                                )
                                emb.set_thumbnail(url="https://static.wikia.nocookie.net/sol-rng/images/3/37/MARI_HIGH_QUALITYY.png/revision/latest")
                                self.webhook.send(avatar_url=WEBHOOK_ICON_URL, embed=emb)
                                GLOBAL_LOGGER.write_log(f"Item purchased from Mari: {detected_items[item]}")
                                time.sleep(5)
                    elif merchant_name == "Jester":
                        for item in detected_items.keys():
                            if settings["auto_purchase_items_jester"][detected_items[item]]:
                                if item == "Box 1":
                                    mkey.left_click_xy_natural(merch_item_pos_1_purchase[0], merch_item_pos_1_purchase[1], print_coords=False)
                                    time.sleep(0.2)
                                    mkey.left_click_xy_natural(quantity_btn_pos[0], quantity_btn_pos[1])
                                    time.sleep(settings["global_wait_time"])
                                    _keyboard.type("25")
                                    time.sleep(settings["global_wait_time"])
                                    mkey.left_click_xy_natural(purchase_btn_pos[0], purchase_btn_pos[1])
                                    time.sleep(settings["global_wait_time"])
                                elif item == "Box 2":
                                    mkey.left_click_xy_natural(merch_item_pos_2_purchase[0], merch_item_pos_2_purchase[1], print_coords=False)
                                    time.sleep(0.2)
                                    mkey.left_click_xy_natural(quantity_btn_pos[0], quantity_btn_pos[1])
                                    time.sleep(settings["global_wait_time"])
                                    _keyboard.type("25")
                                    time.sleep(settings["global_wait_time"])
                                    mkey.left_click_xy_natural(purchase_btn_pos[0], purchase_btn_pos[1])
                                    time.sleep(settings["global_wait_time"])
                                elif item == "Box 3":
                                    mkey.left_click_xy_natural(merch_item_pos_3_purchase[0], merch_item_pos_3_purchase[1], print_coords=False)
                                    time.sleep(0.2)
                                    mkey.left_click_xy_natural(quantity_btn_pos[0], quantity_btn_pos[1])
                                    time.sleep(settings["global_wait_time"])
                                    _keyboard.type("25")
                                    time.sleep(settings["global_wait_time"])
                                    mkey.left_click_xy_natural(purchase_btn_pos[0], purchase_btn_pos[1])
                                    time.sleep(settings["global_wait_time"])
                                elif item == "Box 4":
                                    mkey.left_click_xy_natural(merch_item_pos_4_purchase[0], merch_item_pos_4_purchase[1], print_coords=False)
                                    time.sleep(0.2)
                                    mkey.left_click_xy_natural(quantity_btn_pos[0], quantity_btn_pos[1])
                                    time.sleep(settings["global_wait_time"])
                                    _keyboard.type("25")
                                    time.sleep(settings["global_wait_time"])
                                    mkey.left_click_xy_natural(purchase_btn_pos[0], purchase_btn_pos[1])
                                    time.sleep(settings["global_wait_time"])
                                elif item == "Box 5":
                                    mkey.left_click_xy_natural(merch_item_pos_5_purchase[0], merch_item_pos_5_purchase[1], print_coords=False)
                                    time.sleep(0.2)
                                    mkey.left_click_xy_natural(quantity_btn_pos[0], quantity_btn_pos[1])
                                    time.sleep(settings["global_wait_time"])
                                    _keyboard.type("25")
                                    time.sleep(settings["global_wait_time"])
                                    mkey.left_click_xy_natural(purchase_btn_pos[0], purchase_btn_pos[1])
                                    time.sleep(settings["global_wait_time"])
                                emb = discord.Embed(
                                    title="Purchased Item from Jester",
                                    description=f"Item purchased: {detected_items[item]}",
                                    colour = discord.Color.from_rgb(176, 49, 255)
                                )
                                emb.set_thumbnail(url="https://static.wikia.nocookie.net/sol-rng/images/d/db/Headshot_of_Jester.png/revision/latest")
                                self.webhook.send(avatar_url=WEBHOOK_ICON_URL, embed=emb)
                                GLOBAL_LOGGER.write_log(f"Item purchased from Jester: {detected_items[item]}")
                                time.sleep(5)
                    detected_items = {}
                    time.sleep(180)
                except Exception as e:
                    GLOBAL_LOGGER.write_log(f"Error with Merchant Detection: {e}")

    def keep_alive(self):
        while not self.stop_event.is_set():
            with self.keyboard_lock:
                mkey.left_click_xy_natural(close_pos[0], close_pos[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(close_pos[0], close_pos[1])
                time.sleep(0.2)
            time.sleep(random.randint(550, 650))


    def disconnect_prevention(self):
        global rblx_log_dir
        while not self.stop_event.is_set():
            if not exists_procs_by_name("Windows10Universal.exe") and not exists_procs_by_name("RobloxPlayerBeta.exe"):
                GLOBAL_LOGGER.write_log("There are no instances of Roblox running, the macro will now stop.")
                sys.exit()
            if detect_client_disconnect(rblx_log_dir):
                if valid_ps:
                    if rblx_log_dir != ms_rblx_log_dir:
                        rblx_log_dir = ms_rblx_log_dir
                    _attempt = 1
                    os.system("taskkill /f /im RobloxPlayerBeta.exe /t")
                    with self.keyboard_lock:
                        while not detect_client_reconnect(rblx_log_dir):
                            GLOBAL_LOGGER.write_log(f"Attempting to rejoin private server (Attempt #{str(_attempt)})")
                            os.system("taskkill /f /im Windows10Universal.exe /t")
                            time.sleep(5)
                            asyncio.run(self.sniper._join_windows(ps_link_code))
                            time.sleep(5)                
                            ps_rblxms = get_process_by_name("Windows10Universal.exe")
                            rblxms_window = match_rblx_hwnd_to_pid(ps_rblxms.pid)
                            mkey.activate_window(rblxms_window.hwnd)
                            time.sleep(0.2)
                            mkey.left_click_xy_natural(ms_rblx_spawn_pos[0], ms_rblx_spawn_pos[1])
                            time.sleep(0.2)
                            mkey.left_click_xy_natural(ms_rblx_spawn_pos[0], ms_rblx_spawn_pos[1])
                            time.sleep(0.2)
                            _keyboard.press(Key.f11)
                            time.sleep(0.2)
                            _keyboard.release(Key.f11)
                            if detect_client_reconnect(rblx_log_dir):
                                break
                            time.sleep(45)
                            _attempt += 1
                    leave_main_menu()
                    GLOBAL_LOGGER.write_log("Successfully rejoined!")

    
    def storage_screenshot(self):
        while not self.stop_event.is_set():
            with self.keyboard_lock:
                mkey.left_click_xy_natural(inv_button_pos[0], inv_button_pos[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(items_pos[0], items_pos[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(search_pos[0], search_pos[1])
                time.sleep(0.2)
                storimg = pag.screenshot(f"{MACROPATH}/scr/screenshot_storage.png")
                time.sleep(0.2)
                mkey.left_click_xy_natural(close_pos[0], close_pos[1])
                emb = discord.Embed(
                    title="Aura Storage"
                )
                file=discord.File(f"{MACROPATH}/scr/screenshot_storage.png", filename="storage.png")
                emb.set_image(url="attachment://storage.png")
                self.webhook.send(embed=emb, file=file)
            time.sleep(1260)

    def inventory_screenshot(self):
        while not self.stop_event.is_set():
            with self.keyboard_lock:
                mkey.left_click_xy_natural(inv_button_pos[0], inv_button_pos[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(items_pos[0], items_pos[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(search_pos[0], search_pos[1])
                time.sleep(0.2)
                storimg = pag.screenshot(f"{MACROPATH}/scr/screenshot_inventory.png")
                time.sleep(0.2)
                mkey.left_click_xy_natural(close_pos[0], close_pos[1])
                emb = discord.Embed(
                    title="Inventory"
                )
                file=discord.File(f"{MACROPATH}/scr/screenshot_inventory.png", filename="inventory.png")
                emb.set_image(url="attachment://inventory.png")
                self.webhook.send(embed=emb, file=file)
            time.sleep(1140)

    def auto_br(self):
        while not self.stop_event.is_set():
            with self.keyboard_lock:
                use_item("Biome Random", 1, True)
            time.sleep(2100)
    
    def auto_sc(self):
        while not self.stop_event.is_set():
            with self.keyboard_lock:
                use_item("Strange Control", 1, True)
            time.sleep(1200)

    def auto_pop(self, biome : str):
        global ps_link_code, detected_snipe, rblx_log_dir
        _ended = False
        while not self.stop_event.is_set():
            if detected_snipe and rblx_log_dir == ms_rblx_log_dir:
                rblx_log_dir = ms_rblx_log_dir
                while not exists_procs_by_name("Windows10Universal.exe"):
                    pass # Wait for roblox to start
                ps_rblxms = get_process_by_name("Windows10Universal.exe")
                rblxms_window = match_rblx_hwnd_to_pid(ps_rblxms.pid)
                mkey.activate_window(rblxms_window.hwnd)
                time.sleep(0.2)
                mkey.left_click_xy_natural(ms_rblx_spawn_pos[0], ms_rblx_spawn_pos[1])
                time.sleep(0.2)
                mkey.left_click_xy_natural(ms_rblx_spawn_pos[0], ms_rblx_spawn_pos[1])
                time.sleep(0.2)
                _keyboard.press(Key.f11)
                time.sleep(0.2)
                _keyboard.release(Key.f11)
                leave_main_menu()
            if biome.lower() != get_latest_hovertext(rblx_log_dir).lower():
                _ended = True
                GLOBAL_LOGGER.write_log("Server appears to be bait, as the stated biome does not match the actual biome.")
            if settings["change_cutscene_on_pop"]:
                with self.keyboard_lock:
                    mkey.left_click_xy_natural(menu_btn_pos[0], menu_btn_pos[1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(settings_btn_pos[0], settings_btn_pos[1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(rolling_conf_pos[0], rolling_conf_pos[1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(cutscene_conf_pos[0], cutscene_conf_pos[1])
                    time.sleep(0.2)
                    _keyboard.press(Key.ctrl)
                    _keyboard.press("a")
                    time.sleep(0.2)
                    _keyboard.release("a")
                    _keyboard.release(Key.ctrl)
                    time.sleep(0.2)
                    _keyboard.type("9999999999")
                    time.sleep(0.2)
                    _keyboard.press(Key.enter)
                    time.sleep(0.2)
                    _keyboard.release(Key.enter)
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(menu_btn_pos[0], menu_btn_pos[1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(menu_btn_pos[0], menu_btn_pos[1])
                    time.sleep(0.2)
            if biome.lower() == "glitched" and settings["pop_in_glitch"]:
                original_hp2_amt = settings["auto_use_items_in_glitch"]["Heavenly Potion II"]["amount"]
                for item in reversed(settings["auto_use_items_in_glitch"].keys()):
                    with self.keyboard_lock:
                        if biome.lower() != get_latest_hovertext(rblx_log_dir).lower():
                            _ended = True
                        if _ended:
                            break
                        if not settings["auto_use_items_in_glitch"][item]["use"]:
                            continue
                        if item == "Heavenly Potion II" or item == "Oblivion Potion":
                            while not self.stop_event.is_set():
                                if get_latest_hovertext(rblx_log_dir).lower() != biome:
                                    GLOBAL_LOGGER.write_log("Biome has ended")
                                    GLOBAL_LOGGER.write_log("Stop autopop: Biome has ended")
                                    _ended = True
                                    break
                                else:
                                    if original_hp2_amt > 10:
                                        use_item(item, 10, True)
                                        original_hp2_amt -= 10
                                    elif original_hp2_amt > 1:
                                        use_item(item, 1, True)
                                        original_hp2_amt -= 1
                                    else:
                                        break
                                time.sleep(2)
                        else:
                            use_item(item, settings["auto_use_items_in_glitch"][item]["amount"], True)
            if _ended:
                break

    # THE FOLLOWING CODE IS A SLIGHTLY MODIFIED VERSION OF YAY JOINS SNIPER 1.2.10, WHICH IS OWNED BY Root1527. YOU CAN DOWNLOAD THE REGULAR VERSION OF YAY JOINS HERE: https://github.com/Root1527/yay-joins

    class Sniper:
        def __init__(self, macro, channel_id):
            self.macro = macro
            self.channel_id = channel_id
            self.config = self._load_config()
            self.roblox_session: typing.Optional[ClientSession] = None
            self._refresh_task = None
            self.output_list = []
            self.is_running = True
            self.webhook = macro.webhook

            self.words = ["Glitched", "Dreamspace"]

            self.link_pattern = re.compile(
                f"https://www.roblox.com/games/{PLACE_ID}/x1000000000-Sols-RNG\\?privateServerLinkCode="
            )
            self.link_pattern_2 = re.compile(r"https://.*&type=Server")

            self.blacklists = [
                re.compile(pattern)
                for pattern in [
                    "need|want|lf|look|stop|how|bait|ste|snip|fak|real|pl|hunt|sho|sea|wait|tho|gone|think|ago|prob|try|dev|adm|or|see|cap|tot|is|us|spa|giv|get|hav|and|str|sc|br|rai|wi|san|star|null|pm|gra|pump|moon|scr|mac|do|did|jk|no|rep|dm|farm|sum|who|if|imag|pro|bot|next|post|was|bae|fae",
                    "need|want|lf|look|stop|how|bait|ste|snip|fak|real|pl|hunt|sho|sea|wait|tho|gone|think|ago|prob|try|dev|adm|or|see|cap|tot|is|us|giv|get|hav|and|str|br|rai|wi|san|star|null|pm|gra|pump|moon|scr|mac|do|did|jk|no|rep|dm|farm|sum|who|if|imag|pro|bot|next|post|was|bae|fae",
                ]
            ]
            self.word_patterns = [
                re.compile(pattern)
                for pattern in [r"g[liotc]+h", r"d[rea]+ms"]
            ]

        def _load_config(self):
            with open(f"{MACROPATH}/settings.json", "r") as f:
                config = json.load(f)
            return config

        async def setup(self):
            self.roblox_session = ClientSession()
            self.roblox_session.cookie_jar.update_cookies(
                {".ROBLOSECURITY": self.config["ROBLOSECURITY_KEY"]}
            )

        async def _identify(self, ws):
            try:
                identify_payload = {
                    "op": 2,
                    "d": {
                        "token": self.config["DISCORD_TOKEN"],
                        "properties": {"$os": "windows", "$browser": "chrome", "$device": "pc"}
                    }
                }
                await ws.send(json.dumps(identify_payload))
            except Exception as e:
                if self.config["sniper_logs"]:
                    GLOBAL_LOGGER.write_log(f"[SNIPER] Error: {e}")
        
        def get_guild_id(self, channel_id):
            headers = {
                "Authorization": self.config['DISCORD_TOKEN']
            }
            response = requests.get(f"https://discord.com/api/v10/channels/{channel_id}", headers=headers)

            if response.status_code == 200:
                data = response.json()
                guild_id = data.get("guild_id")
                return guild_id
            else:
                GLOBAL_LOGGER.write_log(f"Failed to fetch channel. Status: {response.status_code}, Response: {response.text}")
                return None
            
        async def _subscribe(self, ws):
            subscription_payload = {
                "op": 14,
                "d": {
                        "guild_id": self.get_guild_id(self.channel_id),
                        "channels_ranges": {str(self.channel_id): [[0, 99]]},
                        "typing": True,
                        "threads": False,
                        "activities": False,
                        "members": [],
                        "thread_member_lists": []
                    }
                }
            await ws.send(json.dumps(subscription_payload))

        async def heartbeat(self, ws, interval):
            while True:
                try:
                    heartbeat_json= {
                        'op':1,
                        'd': 'null'
                    }
                    await ws.send(json.dumps(heartbeat_json))
                    time.sleep(interval)
                except Exception as e:
                    if self.config["sniper_logs"]:
                        GLOBAL_LOGGER.write_log(f"[SNIPER] Error: {e}")

        async def _on_message(self, ws):
            while True:
                event = json.loads(await ws.recv())
                try:
                    if event["t"] == "MESSAGE_CREATE":
                        channel_id = event["d"]["channel_id"]
                        content = event["d"]["content"]
                        for choice_id in self.cycle_index:
                            if int(channel_id) == [self.channel_id, self.channel_id][choice_id]:
                                await self.process_message(content, choice_id)
                except Exception as e:
                    if self.config["sniper_logs"]:
                        GLOBAL_LOGGER.write_log(f"[SNIPER] Error: {e}")

        def _should_process_message(self, message: str, choice_id: int) -> bool:          
            if not self.word_patterns[choice_id].search(message.lower()):
                return False

            if self.blacklists[choice_id].search(message.lower()):
                if self.config["sniper_logs"]:
                    GLOBAL_LOGGER.write_log(f"[SNIPER] Filtered message! content: {message}")
                return False

            return True

        async def _extract_server_code(self, message: str) -> typing.Optional[str]:
            if link_match := self.link_pattern.search(message):
                return link_match.group(0).split("LinkCode=")[-1]

            if link_match_2 := self.link_pattern_2.search(message):
                share_code = link_match_2.group(0).split("code=")[-1].split("&")[0]
                return await self._convert_link(share_code)
            
            if "locked" in message.lower():
                GLOBAL_LOGGER.write_log("The #biomes channel has been locked!")
            return None

        async def _convert_link(self, link_id: str) -> typing.Optional[str]:
            payload = {"linkId": link_id, "linkType": "Server"}

            async with self.roblox_session.post(SHARELINKS_API, json=payload) as response:
                if response.status == 403 and "X-CSRF-TOKEN" in response.headers:
                    self.roblox_session.headers["X-CSRF-TOKEN"] = response.headers[
                        "X-CSRF-TOKEN"
                    ]
                    async with self.roblox_session.post(
                        SHARELINKS_API, json=payload
                    ) as retry_response:
                        data = await retry_response.json()
                else:
                    data = await response.json()

            if data["privateServerInviteData"]["placeId"] != PLACE_ID:
                if self.config["sniper_logs"]:
                    GLOBAL_LOGGER.write_log("[SNIPER] Filtered non-sols link!")
                return None

            return data["privateServerInviteData"]["linkCode"]

        async def _handle_server_join(self, choice_id: int, server_code: str):
            global detected_snipe, rblx_log_dir
            detected_snipe = True
            await self._join_windows(server_code)
            if rblx_log_dir == rblx_player_log_dir:
                os.system("taskkill /f /im RobloxPlayerBeta.exe /t")
                rblx_log_dir = ms_rblx_log_dir
            GLOBAL_LOGGER.write_log(f"[SNIPER] {self.words[choice_id]} link found\nyay joins (modified for bazthedev/SolsRNGBot v{LOCALVERSION})")
            if settings["pop_in_glitch"] and self.words[choice_id] == "Glitched":
                self.macro.auto_pop(self.macro, "glitched")


        async def _join_windows(self, server_code: str):
            final_link = f"roblox://placeID={PLACE_ID}^&linkCode={server_code}"
            subprocess.Popen(["start", final_link], shell=True)

        async def _send_notification(self, choice_id: int, server_code: str):

            colors = [11206400, 16744703]

            embed_link = f"{BASE_ROBLOX_URL}?privateServerLinkCode={server_code}"
            embed = discord.Embed(
                title = f'[{datetime.now().strftime("%H:%M:%S")}] {self.words[choice_id]} Link Sniped!',
                colour = colors[choice_id],
            )
            embed.add_field(name =  f"{self.words[choice_id]} Link:", value = embed_link, inline=True)
            embed.set_footer(text=f"yay joins (modified for bazthedev/SolsRNGBot v{LOCALVERSION})")

            self.webhook.send(avatar_url=WEBHOOK_ICON_URL, content=f"<@{self.config['mention_id']}>", embed=embed)

        async def process_message(self, content: str, choice_id: int) -> None:
            try:
                if not self._should_process_message(content, choice_id):
                    return

                server_code = await self._extract_server_code(content)
                if not server_code:
                    return

                GLOBAL_LOGGER.write_log(f"[SNIPER] Found message! content: {content}")

                await self._handle_server_join(choice_id, server_code)
                await self._send_notification(choice_id, server_code)

            except Exception as e:
                if self.config["sniper_logs"]:
                    GLOBAL_LOGGER.write_log(f"[SNIPER] Error processing message: {str(e)}")

        async def run(self):
            global ps_link_code
            await self.setup()

            glitch = self.config["sniper_toggles"]["Glitched"]
            dream = self.config["sniper_toggles"]["Dreamspace"]
            snipe_list = [glitch, dream]

            self.cycle_index = [i for i, x in enumerate(snipe_list) if x]

            if not (glitch or dream):
                GLOBAL_LOGGER.write_log("[SNIPER] At least one option has to be True. Sniper has not been started.")
                return
                
            if not detect_client_disconnect(rblx_log_dir):
                GLOBAL_LOGGER.write_log(f"Started yay joins (sniper) for channel {str(self.channel_id)}")
                ps_link_code = await self._extract_server_code(settings["private_server_link"])
                emb = discord.Embed(
                    title=f"Started Sniper for channel <#{self.channel_id}>!",
                    description = f"Snipe Glitched: {str(glitch)}\nSnipe Dreamspace: {str(dream)}"
                )
                emb.set_footer(text=f"yay joins (modified for bazthedev/SolsRNGBot v{LOCALVERSION})")
                self.webhook.send(avatar_url=WEBHOOK_ICON_URL, embed=emb)
            else:
                GLOBAL_LOGGER.write_log("Attempting to reconnect sniper.")
            while not self.macro.stop_event.is_set():
                try:
                    async with connect(DISCORD_WS_BASE, max_size=None, ping_interval=None) as ws:
                        await self._identify(ws)
                        await self._subscribe(ws)
                        event = json.loads(await ws.recv())
                        interval = event["d"]["heartbeat_interval"] / 1000
                        async with asyncio.TaskGroup() as tg:
                            tg.create_task(self.heartbeat(ws, interval))
                            tg.create_task(self._on_message(ws))
                except Exception as e:
                    if self.config["sniper_logs"]:
                        GLOBAL_LOGGER.write_log(f"[SNIPER] Error: {e}")
            GLOBAL_LOGGER.write_log(f"Stopped scanning for channel with ID {str(self.channel_id)}")

# THE ABOVE CODE IS A SLIGHTLY MODIFIED VERSION OF YAY JOINS SNIPER 1.2.10, WHICH IS OWNED BY Root1527. YOU CAN DOWNLOAD THE REGULAR VERSION OF YAY JOINS HERE: https://github.com/Root1527/yay-joins


reload_settings()

root = tk.Tk()
app = Macro(root)
root.withdraw()

if PRERELEASE:
    GLOBAL_LOGGER.write_log(f"Warning! This is a prerelease version of SolsRNGBot, meaning you can expect bugs and some errors to occur!\nYou can find logs relating to events that occur during the prerelease in this folder: {MACROPATH}\n\nYou are currently running prerelease for version {LOCALVERSION}, are you sure you wish to continue?")
    messagebox.showwarning("Baz's Macro", f"Warning! This is a prerelease version of SolsRNGBot, meaning you can expect bugs and some errors to occur!\nYou can find logs relating to events that occur during the prerelease in this folder: {MACROPATH}\n\nYou are currently running prerelease for version {LOCALVERSION}, are you sure you wish to continue?")
if SERVERMACRO_EDITION or LOCALVERSION.endswith("SE"):
    GLOBAL_LOGGER.write_log("This is a stripped down version of SolsRNGBot designed for people who macro in Glitch Hunt Servers.")

migrate_settings()

if not os.path.exists(f"{MACROPATH}/scr/"):
    os.mkdir(f"{MACROPATH}/scr/")

if not os.path.exists(f"{MACROPATH}/plugins/"):
    os.mkdir(f"{MACROPATH}/plugins/")
    os.mkdir(f"{MACROPATH}/plugins/config/")

if not os.path.exists(f"{MACROPATH}/logs/"):
    os.mkdir(f"{MACROPATH}/logs/")

now = datetime.now()
_mouse = mouse.Controller()
_keyboard = keyboard.Controller()
screens = si.get_monitors()
monitor = None
for mon in screens:
    if mon.is_primary:
        monitor = mon
GLOBAL_LOGGER.write_log(f"Detected Resolution: {str(monitor.width)}x{str(monitor.height)}")
scale_w = monitor.width / 2560
scale_h = monitor.height / 1440 
merchant_box = (int(1140 * scale_w), int(434 * scale_h), int(1409 * scale_w), int(477 * scale_h))
manual_boxes = {
    "Box 1": (int(656 * scale_w), int(919 * scale_h), int(890 * scale_w), int(996 * scale_h)),
    "Box 2":         (int(908 * scale_w), int(919 * scale_h), int(1143 * scale_w), int(996 * scale_h)),
    "Box 3":   (int(1161 * scale_w), int(919 * scale_h), int(1396 * scale_w), int(996 * scale_h)),
    "Box 4":            (int(1416 * scale_w), int(919 * scale_h), int(1650 * scale_w), int(996 * scale_h)),
    "Box 5":       (int(1668 * scale_w), int(919 * scale_h), int(1903 * scale_w), int(996 * scale_h))
}
aura_button_pos = ((32 * scale_w), (595 * scale_h))
inv_button_pos = ((32 * scale_w), (692 * scale_h))
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
merch_item_pos_1 = (int(656 * scale_w), int(922 * scale_h))
merch_item_pos_1_end = (int(890 * scale_w), int(994 * scale_h))
merch_item_pos_1_purchase = ((766 * scale_w), (988 * scale_h))
merch_item_pos_2 = (int(908 * scale_w), int(922 * scale_h))
merch_item_pos_2_end = (int(1142 * scale_w), int(994 * scale_h))
merch_item_pos_2_purchase = ((1024 * scale_w), (986 * scale_h))
merch_item_pos_3 = (int(1160 * scale_w), int(922 * scale_h))
merch_item_pos_3_end = (int(1396 * scale_w), int(994 * scale_h))
merch_item_pos_3_purchase = ((1278 * scale_w), (988 * scale_h))
merch_item_pos_4 = (int(1416 * scale_w), int(922 * scale_h))
merch_item_pos_4_end = (int(1650 * scale_w), int(994 * scale_h))
merch_item_pos_4_purchase = ((1512 * scale_w), (988 * scale_h))
merch_item_pos_5 = (int(1666 * scale_w), int(922 * scale_h))
merch_item_pos_5_end = (int(1898 * scale_w), int(994 * scale_h))
merch_item_pos_5_purchase = ((1762 * scale_w), (986 * scale_h))
menu_btn_pos = ((32 * scale_w), (656 * scale_h))
settings_btn_pos = ((1278 * scale_w), (738 * scale_h))
rolling_conf_pos = ((888 * scale_w), (498 * scale_h))
cutscene_conf_pos = ((1518 * scale_w), (812 * scale_h))
craft_btn_pos = ((764 * scale_w), (764 * scale_h))
hp1_pos_potions = ((1064 * scale_w), (840 * scale_h)) # first add button (-110 * scale_w gives the item input)
hp1_pos_celestial = ((1064 * scale_w), (1024 * scale_h)) # very botton button
hp2_pos_potions = ((1064 * scale_w), (910 * scale_h)) # second add button
auto_btn_pos = ((940 * scale_w), (762 * scale_h))
auto_mode_swap = 5
auto_craft_index = 1
hp1_recipe_pos = ((1516 * scale_w), (684 * scale_h))
hp2_recipe_pos = ((1516 * scale_w), (836 * scale_h))
warp_recipe_pos = ((1516 * scale_w), (980 * scale_h))
merchant_face_pos_1 = (int(841 * scale_w), int(1056 * scale_h))
merchant_face_pos_2 = (int(855 * scale_w), int(1063 * scale_h))
collection_open_pos = ((32 * scale_w), (641 * scale_h))
exit_collection_pos = ((510 * scale_w), (146 * scale_h))
start_btn_pos = ((1252 * scale_w), (1206 * scale_h))
reconnect_btn_pos = ((1370 * scale_w), (800 * scale_h))
bound_recipe_pos = ((1524 * scale_w), (994 * scale_h))
potion_search_pos = ((1237 * scale_w), (449 * scale_h))
first_potion_pos = ((1520 * scale_w), (554 * scale_h))
biome_cols = {"windy" : (145, 247, 255), "snowy" : (196, 245, 246), "rainy" : (67, 133, 255), "hell" : (74, 23, 34), "starfall" : (103, 132, 224), "corruption" : (144, 66, 255), "null" : (7, 9, 16), "dreamspace" : (234, 108, 188), "glitched" : (100, 252, 100)}
previous_biome = None
previous_aura = None
popping = False
valid_ps = False
item_collection_index = 1
use_ms_rblx = False
rblx_player_log_dir = os.path.expandvars(r"%localappdata%\Roblox\logs") # This is for the Roblox Player
ms_rblx_log_dir = os.path.expandvars(r"%LOCALAPPDATA%\Packages\ROBLOXCorporation.ROBLOX_55nm5eh3cm0pr\LocalState\logs") # This is for the Microsoft Store version of Roblox
ms_rblx_spawn_pos = ((820 * scale_w), (548 * scale_h))
ps_link_code = 0
WINDY_MULTIPLIER = 3
SNOWY_MULTIPLIER = 3
RAINY_MULTIPLER = 4
SANDSTORM_MULTIPLIER = 4
HELL_MULTIPLIER = 6
STARFALL_MULTIPLIER = 5
CORRUPTION_MULTIPLIER = 5
NULL_MULTIPLIER = 1000
GLITCHED_MULTIPLIER = 1
DREAMSPACE_MULTIPLIER = 1
GLOBAL_LOGGER.write_log(f"Starting SolsRNGBot v{LOCALVERSION}")

if not os.path.exists(f"{MACROPATH}/settings.json"):
    x = open(f"{MACROPATH}/settings.json", "w")
    x.write('{}')
    x.close()
    with open(f"{MACROPATH}/settings.json", "w") as f:
        json.dump(DEFAULTSETTINGS, f, indent=4)
    GLOBAL_LOGGER.write_log("Settings have been created!")


reload_settings()


if settings["__version__"] < LOCALVERSION:
    settings["__version__"] = LOCALVERSION
    update_settings(settings)
    reload_settings()
    GLOBAL_LOGGER.write_log(f"The macro has been updated to version {LOCALVERSION}!")

if settings["__version__"] > LOCALVERSION:
    GLOBAL_LOGGER.write_log("You are running newer settings with an older version of this program. This may delete some of your settings. Are you sure you want to continue (y)? ")
    confirm = input("")
    if confirm[0].lower() != "y":
        sys.exit("You are running newer settings with an older version of this program.")
        
# Settings integrity check
validate_settings()

if settings["check_update"]:
    new_ver = requests.get(f"https://api.github.com/repos/bazthedev/SolsRNGBot/releases/latest")
    new_ver_str = new_ver.json()["name"]

    if LOCALVERSION < new_ver_str:
        DOWNLOADS_DIR = Path.home() / "Downloads"
        if not settings["auto_install_update"]:
            confirm_dl = messagebox.askyesno("Baz's Macro", f"A new version has been found ({new_ver_str}), would you like to install it?")
        else:
            confirm_dl = True
            GLOBAL_LOGGER.write_log("Automatically installing new version...")
        if confirm_dl.lower() == True:
            GLOBAL_LOGGER.write_log(f"Downloading v{new_ver_str}...")
            if not os.path.isfile(f"{DOWNLOADS_DIR}/SolsRNGBot_{new_ver_str}.zip"):
                toupd = requests.get(f"https://github.com/bazthedev/SolsRNGBot/releases/download/{new_ver_str}/SolsRNGBot_{new_ver_str}.zip")
                with open(f"{DOWNLOADS_DIR}/SolsRNGBot_{new_ver_str}.zip", "wb") as p:
                    p.write(toupd.content)
                    p.close()
                GLOBAL_LOGGER.write_log(f"Downloaded v{new_ver_str}")
            else:
                GLOBAL_LOGGER.write_log("New version zip appears to already be downloaded.")
            with zipfile.ZipFile(f"{DOWNLOADS_DIR}/SolsRNGBot_{new_ver_str}.zip", "r") as newverzip:
                if not os.path.exists(f"{DOWNLOADS_DIR}/SolsRNGBot_{new_ver_str}"):
                    os.mkdir(f"{DOWNLOADS_DIR}/SolsRNGBot_{new_ver_str}")
                newverzip.extractall(f"{DOWNLOADS_DIR}/SolsRNGBot_{new_ver_str}/")
                GLOBAL_LOGGER.write_log(f"Extracted v{new_ver_str} to directory {DOWNLOADS_DIR}\\SolsRNGBot_{new_ver_str}")
                GLOBAL_LOGGER.write_log("Cleaning up...")
                os.remove(f"{DOWNLOADS_DIR}/SolsRNGBot_{new_ver_str}.zip")
            sys.exit(f"Downloaded v{new_ver_str}")
    else:
        GLOBAL_LOGGER.write_log(f"You are running the latest version.")

if not os.path.exists(ms_rblx_log_dir):
    GLOBAL_LOGGER.write_log("The Microsoft Store Version of Roblox has not been detected as installed. This will break certain features of the macro, such as the Sniper and joining servers.")

if exists_procs_by_name("Windows10Universal.exe"):
    rblx_log_dir = ms_rblx_log_dir
    GLOBAL_LOGGER.write_log("Using Microsoft Store Roblox (detected as running)")
elif exists_procs_by_name("RobloxPlayerBeta.exe"):
    rblx_log_dir = rblx_player_log_dir
    GLOBAL_LOGGER.write_log("Using Roblox Player (detected as running)")
elif settings["use_roblox_player"]:
    GLOBAL_LOGGER.write_log("Using Roblox player (no Roblox instances were detected as running)")
    rblx_log_dir = rblx_player_log_dir
else:
    GLOBAL_LOGGER.write_log("Using Microsoft Store Roblox (no Roblox instances were detected as running)")
    rblx_log_dir = ms_rblx_log_dir

mkey.enable_failsafekill(settings["failsafe_key"])

if settings["WEBHOOK_URL"] == "":
    GLOBAL_LOGGER.write_log("You need to add your webhook link.")

validate_potions()
GLOBAL_LOGGER.write_log("Validating settings, then starting macro...")
validate_settings()

if settings["ROBLOSECURITY_KEY"] != "":
    format_roblosecurity()

if not settings["skip_aura_download"]:
    get_auras()

if not os.path.exists(f"{MACROPATH}/auras_new.json"):
    get_auras()

with open(f"{MACROPATH}/auras_new.json", "r", encoding="utf-8") as f:
    auras = json.load(f)

if settings["private_server_link"] != "":
    if not validate_pslink(settings["private_server_link"]):
        GLOBAL_LOGGER.write_log("Invalid Private Server Link")
        valid_ps = False
    else:
        valid_ps = True

__version__ = settings["__version__"]

root.deiconify()
root.mainloop()
