"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v1.2.6
Support server: https://discord.gg/8khGXqG7nA
"""

import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))
import psutil
import time
import tkinter as tk
from difflib import SequenceMatcher
import mousekey as mk 
import io 
import discord
import datetime
import codecs

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
                with codecs.open(self.log_file_path, "a", encoding='utf-8') as log_file:
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
                with codecs.open(self.log_file_path, "a", encoding='utf-8') as log_file:
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
    """Performs a left mouse button drag from current position to (x, y)."""
    try:
        local_mkey = mk.MouseKey()
        local_mkey._mouse_click(mk.MOUSEEVENTF_LEFTDOWN)
        time.sleep(delay)
        local_mkey.move(x, y)
        time.sleep(delay)
        local_mkey._mouse_click(mk.MOUSEEVENTF_LEFTUP)
    except Exception as e:
        get_logger().write_log(f"Error during left_click_drag: {e}")

def right_click_drag(x, y, delay=0.1):
    """Performs a right mouse button drag from current position to (x, y)."""
    try:
        local_mkey = mk.MouseKey()
        local_mkey._mouse_click(mk.MOUSEEVENTF_RIGHTDOWN)
        time.sleep(delay)
        local_mkey.move(x, y)
        time.sleep(delay)
        local_mkey._mouse_click(mk.MOUSEEVENTF_RIGHTUP)
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
    return key.replace("_", " ").title()