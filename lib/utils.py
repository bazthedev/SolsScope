"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v2.0.0
Support server: https://discord.gg/8khGXqG7nA
"""

import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))

import psutil
import time
from difflib import SequenceMatcher
import mousekey as mk 
import io 
import discord
import datetime
import json
import pyautogui as pag
import re
from gc import collect
import psutil
import platform
import cv2
import random

from constants import MACROPATH, COORDS_PERCENT1610, COORDS_PERCENT169, COORDS_PERCENT43

GLOBAL_LOGGER = None

def set_global_logger(logger_instance):
    global GLOBAL_LOGGER
    GLOBAL_LOGGER = logger_instance

def get_logger():
    """Returns the globally accessible logger instance."""

    if GLOBAL_LOGGER is None:
        print("WARNING: get_logger() called before logger was set!")

        class DummyLogger:
            def write_log(self, message):
                print(f"[DUMMY LOG]: {message}")
        return DummyLogger()
    return GLOBAL_LOGGER

class Logger:
    def __init__(self, log_file_path=None):
        self.log_file_path = log_file_path
        if self.log_file_path:
            try:
                with open(self.log_file_path, "a", encoding='utf-8') as log_file:
                    log_file.write("\n\n--------------------------- Starting new instance of SolsScope ---------------------------\n\n")
            except Exception as e:
                print(f"Error initializing log file {self.log_file_path}: {e}")
                self.log_file_path = None 

    def write_log(self, message):
        try:
            message = str(message)
        except Exception:
            print("Failed to convert log message to string.")
            return

        if self.log_file_path:
            try:
                with open(self.log_file_path, "a", encoding='utf-8') as log_file:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_message = f"[{timestamp}] {message}"
                    log_file.write(log_message)
            except Exception as e:
                print(f"Error writing to log file {self.log_file_path}: {e}")

def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def hex2rgb(_hex):
    _hex = _hex.lstrip("#")
    if len(_hex) != 6:
        get_logger().write_log(f"Invalid hex color format: '{_hex}'. Returning black.")
        return (0, 0, 0) 
    try:
        return tuple(int(_hex[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
         get_logger().write_log(f"Invalid hex color value: '{_hex}'. Returning black.")
         return (0, 0, 0)

def fuzzy_match(text, known_items, threshold=0.5):
    """Finds the best match for text within a list of known_items using sequence matching."""
    best_match = None
    best_score = 0
    text_lower = text.lower()
    for item in known_items:
        item_lower = item.lower()
        score = SequenceMatcher(None, text_lower, item_lower).ratio()
        if score > best_score:
            best_score = score
            best_match = item

    if best_score >= threshold:
        return best_match

    get_logger().write_log(f"Fuzzy match for '{text}' below threshold ({best_score:.2f} < {threshold}). No match found.")
    return text 

def fuzzy_match_merchant(text, options, threshold=0.6):
    """Similar to fuzzy_match, specifically for merchant names."""
    best_match = None
    best_score = 0
    text_lower = text.lower()
    for name in options:
        name_lower = name.lower()
        score = SequenceMatcher(None, text_lower, name_lower).ratio()
        if score > best_score:
            best_match = name
            best_score = score
    return best_match if best_score >= threshold else None

def fuzzy_match_auto_sell(text, sellable_items, threshold=0.6):
    """Similar to fuzzy_match, specifically for Jester's sellable items."""
    best_match = None
    best_score = 0
    text_lower = text.lower()
    for name in sellable_items:
        name_lower = name.lower()
        score = SequenceMatcher(None, text_lower, name_lower).ratio()
        if score > best_score:
            best_match = name
            best_score = score
    return best_match if best_score >= threshold else None

def fuzzy_match_qb(text, quests, threshold=0.6):
    """Similar to fuzzy_match, specifically for the Quest Board."""
    best_match = None
    best_score = 0
    text_lower = text.lower()
    for name in quests:
        name_lower = name.lower()
        score = SequenceMatcher(None, text_lower, name_lower).ratio()
        if score > best_score:
            best_match = name
            best_score = score
    return best_match if best_score >= threshold else None

def parse_version(v):
    """Converts a version string (e.g., "1.2.3") into a tuple of integers for comparison."""
    try:
        return tuple(map(int, v.split('.')))
    except ValueError:
        get_logger().write_log(f"Invalid version format: '{v}'. Returning (0,0,0).")
        return (0, 0, 0) 

def exists_procs_by_name(name):
    """Checks if a process with the given name exists."""
    proc_name = name.lower()
    for p in psutil.process_iter(['name']):
        try:
            if p.info['name'].lower() == proc_name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue 
    return False

def get_process_by_name(name):
    """Returns the first psutil.Process object matching the name."""
    proc_name = name.lower()
    for p in psutil.process_iter(['name']):
        try:
            if p.info['name'].lower() == proc_name:
                return p
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None 

def match_rblx_hwnd_to_pid(pid):
    """Finds the window handle (hwnd) associated with a given process ID."""
    try:

        local_mkey = mk.MouseKey()
        for w in local_mkey.get_all_windows():
            if w.pid == pid:
                return w
    except Exception as e:
        get_logger().write_log(f"Error matching HWND to PID {pid}: {e}")
    return None 

def validate_pslink(ps_server_link : str):
    """Checks if a string looks like a valid Roblox private server share link."""
    if not isinstance(ps_server_link, str):
        return False

    return "https://www.roblox.com/share?code=" in ps_server_link and "&type=Server" in ps_server_link

def create_discord_file_from_path(path, filename):
    """Creates a discord.File object from a local file path."""
    try:

        if not os.path.exists(path):
            get_logger().write_log(f"Error creating discord file: Source file not found at {path}")
            return None
        with open(path, "rb") as f:
            file_bytes = f.read()
        return discord.File(io.BytesIO(file_bytes), filename=filename)
    except FileNotFoundError:
         get_logger().write_log(f"Error creating discord file: File not found at {path}")
    except IOError as e:
        get_logger().write_log(f"Error reading file {path} for discord upload: {e}")
    except Exception as e:
        get_logger().write_log(f"Unexpected error creating discord file from {path}: {e}")
    return None

def left_click_drag(x, y, delay=0.1):
    """Performs a left mouse button drag relative of the current position based on (x, y)."""
    try:
        mk._mouse_click(mk.MOUSEEVENTF_LEFTDOWN)
        time.sleep(delay)
        mk.MouseKey().move_relative(x, y)
        time.sleep(delay)
        mk._mouse_click(mk.MOUSEEVENTF_LEFTUP)
    except Exception as e:
        get_logger().write_log(f"Error during left_click_drag: {e}")

def right_click_drag(x, y, delay=0.1):
    """Performs a right mouse button drag relative of the current position based on (x, y)."""
    try:
        mk._mouse_click(mk.MOUSEEVENTF_RIGHTDOWN)
        time.sleep(delay)
        mk.MouseKey().move_relative(x, y)
        time.sleep(delay)
        mk._mouse_click(mk.MOUSEEVENTF_RIGHTUP)
    except Exception as e:
        get_logger().write_log(f"Error during right_click_drag: {e}")

def calculate_coords(primary_monitor):
    """Calculates scaled coordinates based on primary monitor resolution."""
    if not primary_monitor:
        get_logger().write_log("Error: No primary monitor provided for coordinate calculation.")
        return None

    try:

        base_w, base_h = 2560, 1440
        current_w, current_h = primary_monitor.width, primary_monitor.height
        get_logger().write_log(f"Calculating coordinates based on primary monitor: {current_w}x{current_h} (Base: {base_w}x{base_h})")

        scale_w = current_w / base_w
        scale_h = current_h / base_h

        try:
            from constants import COORDS as BASE_COORDS
        except ImportError:
            get_logger().write_log("Error: Could not import BASE_COORDS from constants for calculation.")
            return None

        calculated = {}
        for key, value in BASE_COORDS.items():
            if key == "manual_boxes": 
                calculated[key] = {}
                for box_name, (x1, y1, x2, y2) in value.items():
                    calculated[key][box_name] = (
                        int(x1 * scale_w),
                        int(y1 * scale_h),
                        int(x2 * scale_w),
                        int(y2 * scale_h)
                    )
            elif key == "merchant_box": 
                 x1, y1, x2, y2 = value
                 calculated[key] = (
                    int(x1 * scale_w),
                    int(y1 * scale_h),
                    int(x2 * scale_w),
                    int(y2 * scale_h)
                 )
            elif isinstance(value, tuple) and len(value) == 2: 
                x, y = value
                calculated[key] = (int(x * scale_w), int(y * scale_h))
            else:
                 calculated[key] = value 

        return calculated

    except Exception as e:
        get_logger().write_log(f"Error calculating coordinates: {e}")
        return None

def format_key(key: str) -> str:
    """Converts a snake_case key into a Title Case string with spaces."""
    
    custom_labels = {
        "merchant_detection": "Auto Detect And Buy From Merchants",
        #"vok_taran" : "Spawn Sand Storm using \"vok taran\"",
        "use_gpu_for_ocr" : "Use GPU for OCR processing",
        "enable_ui_nav_key" : "Turn on UI Navigation key bind",
        "delay" : "Actions Delay",
        "typing_delay" : "Typing character delay",
        "typing_hold" : "Hold key duration",
        "typing_jitter" : "Typing Jitter"
    }

    if key in custom_labels:
        return custom_labels[key]    

    return key.replace("_", " ").title()

def resolve_full_aura_name(partial_name: str, aura_dict : dict) -> str:
   
    partial_lower = partial_name.lower()
    matches = [full_name for full_name in aura_dict if full_name.lower().startswith(partial_lower)]

    if not matches:
        return partial_name
    if len(matches) == 1:
        return matches[0]

    return min(matches, key=len)

def apply_roblox_fastflags(update_status_callback=None):
    """Apply Roblox FastFlag settings for logging"""
    local_app_data = os.getenv('LOCALAPPDATA')
    if not local_app_data:
        if update_status_callback:
            update_status_callback("Error: LOCALAPPDATA environment variable not found.")
        return

    required_flags = {
        "FStringDebugLuaLogLevel": "trace",
        "FStringDebugLuaLogPattern": "ExpChat/mountClientApp"
    }
    applied_count = 0
    updated_count = 0

    def update_json_file(json_file_path, launcher_info_str):
        nonlocal applied_count, updated_count
        current_settings = {}
        needs_update = False
        file_existed = False
        file_dir = os.path.dirname(json_file_path)

        try:
            os.makedirs(file_dir, exist_ok=True)

            if os.path.exists(json_file_path):
                file_existed = True
                try:
                    with open(json_file_path, 'r', encoding="utf-8") as f:
                        content = f.read()
                        if content.strip(): 
                            current_settings = json.loads(content)
                        else:
                            current_settings = {} 
                except json.JSONDecodeError:
                    if update_status_callback:
                        update_status_callback(f"Warning: Corrupt JSON found at {json_file_path}. Overwriting for {launcher_info_str}.")
                    current_settings = {}
                    needs_update = True
                except Exception as read_err:
                    if update_status_callback:
                        update_status_callback(f"Warning: Error reading {json_file_path}: {read_err}. Overwriting for {launcher_info_str}.")
                    current_settings = {}
                    needs_update = True
            else:
                needs_update = True

            for key, value in required_flags.items():
                if key not in current_settings or current_settings[key] != value:
                    current_settings[key] = value
                    needs_update = True

            if needs_update:
                with open(json_file_path, 'w', encoding="utf-8") as f:
                    json.dump(current_settings, f, indent=2)
                if file_existed:
                    updated_count += 1
                    if update_status_callback:
                        update_status_callback(f"Updated FastFlags in {launcher_info_str} file")
                else:
                    applied_count += 1
                    if update_status_callback:
                        update_status_callback(f"Applied FastFlags to new file in {launcher_info_str}")

        except Exception as e:
            if update_status_callback:
                update_status_callback(f"Error processing FastFlags for {launcher_info_str}: {e}")

    mod_launchers_config_files = {
        'Bloxstrap': os.path.join(local_app_data, 'Bloxstrap', 'Modifications', 'ClientSettings', 'ClientAppSettings.json'),
        'Fishstrap': os.path.join(local_app_data, 'Fishstrap', 'Modifications', 'ClientSettings', 'ClientAppSettings.json')
    }

    for launcher_name, target_json_path in mod_launchers_config_files.items():
        launcher_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(target_json_path)))
        if os.path.isdir(launcher_base_dir):
            update_json_file(target_json_path, f"{launcher_name} Modifications")

    roblox_versions_path = os.path.join(local_app_data, 'Roblox', 'Versions')
    if os.path.isdir(roblox_versions_path):
        try:
            for item_name in os.listdir(roblox_versions_path):
                item_path = os.path.join(roblox_versions_path, item_name)

                if os.path.isdir(item_path) and item_name.startswith("version-"):
                    version_folder_path = item_path
                    client_settings_path = os.path.join(version_folder_path, 'ClientSettings')
                    json_file_path = os.path.join(client_settings_path, 'ClientAppSettings.json')

                    update_json_file(json_file_path, f"Roblox/{item_name}")
        except OSError as e:
            if update_status_callback:
                update_status_callback(f"Error accessing Roblox versions directory: {e}")

    if applied_count > 0 or updated_count > 0:
        if update_status_callback:
            update_status_callback(f"Finished applying/updating FastFlags ({applied_count} new, {updated_count} updated)." )
    else:
        if update_status_callback:
            update_status_callback("FastFlags check complete. No changes needed or relevant folders found.")

def is_quest_accepted(quest_name : str) -> bool:

    with open(os.path.join(MACROPATH, "quest_tracker.json"), "r", encoding="utf-8") as f:
        tracked_quests = json.load(f)

        if quest_name in tracked_quests["quest_board"]:
            return True
        else:
            return False
        
def get_coords_percent(coords):
    ratio = coords["scr_wid"] / coords["scr_hei"]
    if abs(ratio - (16/9)) < 0.01:
        return COORDS_PERCENT169
    elif abs(ratio - (16/10)) < 0.01:
        return COORDS_PERCENT1610
    elif abs(ratio - (4/3)) < 0.01:
        return COORDS_PERCENT43
    else:
        print("Could not determine screen ratio, exiting.")
        return None
    
def convert_boxes(percent_boxes, scr_wid, scr_hei):
    pixel_boxes = {}
    for name, (x1, y1, x2, y2) in percent_boxes.items():
        pixel_boxes[name] = (
            round(x1 * scr_wid),
            round(y1 * scr_hei),
            round(x2 * scr_wid),
            round(y2 * scr_hei)
        )
    return pixel_boxes

def check_tab_menu_open(reader, COORDS_PERCENT, COORDS) -> bool:

    screenshot_path = os.path.join(MACROPATH, "scr", "screenshot_tab_menu.png")

    time.sleep(0.6)

    pag.screenshot(screenshot_path)
    time.sleep(0.2)

    image = cv2.imread(screenshot_path)

    if image is None:
        return False

    x1p, y1p, x2p, y2p = COORDS_PERCENT["check_tab_menu"]
    x1 = round(x1p * COORDS["scr_wid"])
    y1 = round(y1p * COORDS["scr_hei"])
    x2 = round(x2p * COORDS["scr_wid"])
    y2 = round(y2p * COORDS["scr_hei"])
    add_crop = image[y1:y2, x1:x2]
    
    ocr_results = reader.readtext(add_crop, detail=0)
    ocr_add_raw = " ".join(ocr_results).strip()

    if ocr_add_raw:

        ocr_add_clean = re.sub(r"[^a-zA-Z']", "", ocr_add_raw).lower()
        final_text = fuzzy_match_merchant(ocr_add_clean, ["rolls"])

        if final_text and final_text.lower() == "rolls":
            del image, x1p, y1p, x2p, y2p, add_crop, x1, y1, x2, y2, ocr_results, ocr_add_raw, ocr_add_clean, final_text
            collect()
            return True
        elif not final_text:
            del image, x1p, y1p, x2p, y2p, add_crop, x1, y1, x2, y2, ocr_results, ocr_add_raw
            collect()
            return False
        
    del image, x1p, y1p, x2p, y2p, add_crop, x1, y1, x2, y2, ocr_results, ocr_add_raw
    collect()
    return False


def get_autocraft_path(nonscrolled: tuple, scrolled: tuple = (), position: int = 4) -> int:

    nonscrolled = tuple(nonscrolled)
    scrolled = tuple(scrolled)

    if position == 5 and scrolled:
        scrolled = (nonscrolled[2],) + scrolled[1:]

    lookup = {
        6: {
            ((False, False, False), (False, False, False)): 5,
            ((False, False, False), (False, True, False)): 4,
            ((False, False, False), (True, False, False)): 4,
            ((False, False, False), (True, True, False)): 3,
            ((False, False, True), (False, False, False)): 4,
            ((False, False, True), (False, True, False)): 3,
            ((False, False, True), (True, False, False)): 3,
            ((False, False, True), (True, True, False)): 2,
            ((False, True, False), (False, False, False)): 4,
            ((False, True, False), (False, True, False)): 3,
            ((False, True, False), (True, False, False)): 3,
            ((False, True, False), (True, True, False)): 2,
            ((False, True, True), (False, False, False)): 3,
            ((False, True, True), (False, True, False)): 2,
            ((False, True, True), (True, False, False)): 2,
            ((False, True, True), (True, True, False)): 1,
            ((True, False, False), (False, False, False)): 4,
            ((True, False, False), (False, True, False)): 3,
            ((True, False, False), (True, False, False)): 3,
            ((True, False, False), (True, True, False)): 2,
            ((True, False, True), (False, False, False)): 3,
            ((True, False, True), (False, True, False)): 2,
            ((True, False, True), (True, False, False)): 2,
            ((True, False, True), (True, True, False)): 1,
            ((True, True, False), (False, False, False)): 3,
            ((True, True, False), (False, True, False)): 2,
            ((True, True, False), (True, False, False)): 2,
            ((True, True, False), (True, True, False)): 1,
            ((True, True, True), (False, False, False)): 2,
            ((True, True, True), (False, True, False)): 1,
            ((True, True, True), (True, False, False)): 1,
            ((True, True, True), (True, True, False)): 0
        },
        5: {
            ((False, False, False), (False,)): 4,
            ((False, False, True), (True,)): 3,
            ((False, True, False), (False,)): 3,
            ((False, True, True), (True,)): 2,
            ((True, False, False), (False,)): 3,
            ((True, False, True), (True,)): 2,
            ((True, True, False), (False,)): 2,
            ((True, True, True), (True,)): 1
        },
        4: {
            ((False, False, False), (False, False, False)): 3,
            ((False, False, False), (False, True, False)): 3,
            ((False, False, False), (True, False, False)): 3,
            ((False, False, False), (True, True, False)): 3,
            ((False, False, True), (False, False, False)): 2,
            ((False, False, True), (False, True, False)): 2,
            ((False, False, True), (True, False, False)): 2,
            ((False, False, True), (True, True, False)): 2,
            ((False, True, False), (False, False, False)): 2,
            ((False, True, False), (False, True, False)): 2,
            ((False, True, False), (True, False, False)): 2,
            ((False, True, False), (True, True, False)): 2,
            ((False, True, True), (False, False, False)): 1,
            ((False, True, True), (False, True, False)): 1,
            ((False, True, True), (True, False, False)): 1,
            ((False, True, True), (True, True, False)): 1,
            ((True, False, False), (False, False, False)): 2,
            ((True, False, False), (False, True, False)): 2,
            ((True, False, False), (True, False, False)): 2,
            ((True, False, False), (True, True, False)): 2,
            ((True, False, True), (False, False, False)): 1,
            ((True, False, True), (False, True, False)): 1,
            ((True, False, True), (True, False, False)): 1,
            ((True, False, True), (True, True, False)): 1,
            ((True, True, False), (False, False, False)): 1,
            ((True, True, False), (False, True, False)): 1,
            ((True, True, False), (True, False, False)): 1,
            ((True, True, False), (True, True, False)): 1,
            ((True, True, True), (False, False, False)): 0,
            ((True, True, True), (False, True, False)): 0,
            ((True, True, True), (True, False, False)): 0,
            ((True, True, True), (True, True, False)): 0
        },
        3: {
            ((False, False, False), ()): 2,
            ((False, True, False), ()): 1,
            ((True, False, False), ()): 1,
            ((True, True, False), ()): 0
        },
        2: {
            ((False, False), ()): 1,
            ((True, False), ()): 0
        }
    }

    return lookup.get(position, {}).get((nonscrolled, scrolled), -1)


def get_hardware_profile():
    info = {
        "cpu_name": platform.processor(),
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_threads": psutil.cpu_count(logical=True),
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 1),
        "os": platform.system() + " " + platform.release()
    }
    return info

def get_device_score():
    cores = psutil.cpu_count(logical=True)
    ram_gb = psutil.virtual_memory().total / (1024**3)

    score = (cores * 1.5) + (ram_gb * 0.5)
    return score 
    
def _type(kb, jitter, delay, hold, text : str):

    for character in text:

        kb.press(character)
        time.sleep(hold)
        kb.release(character)
        time.sleep(delay + random.uniform(0, jitter))