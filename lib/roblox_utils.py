"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v1.2.5
Support server: https://discord.gg/6cuCu6ymkX
"""

import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))
import glob
import re
import json
import tempfile
import shutil
import time
import subprocess
import mousekey as mk 

from constants import MS_RBLX_LOG_DIR, RBLX_PLAYER_LOG_DIR, PLACE_ID, COORDS
from utils import get_logger, exists_procs_by_name, get_process_by_name, match_rblx_hwnd_to_pid
from pynput import keyboard 
from pynput import mouse 

_active_log_dir = None
_keyboard_controller = keyboard.Controller()
_mouse_controller = mouse.Controller()
_mkey_controller = mk.MouseKey()

def set_active_log_directory(use_ms_store_if_detected=False, force_player=False):
    """Determines and sets the active Roblox log directory based on running processes or settings."""
    global _active_log_dir
    logger = get_logger()

    ms_store_running = exists_procs_by_name("Windows10Universal.exe")
    player_running = exists_procs_by_name("RobloxPlayerBeta.exe")

    if force_player:
         _active_log_dir = RBLX_PLAYER_LOG_DIR
         logger.write_log("Forcing use of Roblox Player log directory.")
    elif ms_store_running and use_ms_store_if_detected:
        _active_log_dir = MS_RBLX_LOG_DIR
        logger.write_log("Using Microsoft Store Roblox log directory (detected as running).")
    elif player_running:
        _active_log_dir = RBLX_PLAYER_LOG_DIR
        logger.write_log("Using Roblox Player log directory (detected as running).")
    else:

        _active_log_dir = RBLX_PLAYER_LOG_DIR
        logger.write_log("No Roblox instance detected running, defaulting to Roblox Player log directory.")

    if not _active_log_dir or not os.path.exists(_active_log_dir):
        logger.write_log(f"Warning: Selected Roblox log directory does not exist: {_active_log_dir}")

    return _active_log_dir

def get_active_log_directory():
    """Returns the currently set active log directory."""
    if _active_log_dir is None:

        set_active_log_directory()
    return _active_log_dir

def _get_latest_log_content(purpose="generic"):
    """Safely copies and returns the content of the latest log file."""
    logger = get_logger()
    logs_dir = get_active_log_directory()
    if not logs_dir:
        logger.write_log(f"Error getting log content ({purpose}): Log directory not set.")
        return None

    try:
        log_files = glob.glob(os.path.join(logs_dir, "*.log"))
        if not log_files:

            return None

        latest_log_file = max(log_files, key=os.path.getctime)

        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, f"solsscope_{purpose}_{os.path.basename(latest_log_file)}")

        shutil.copy2(latest_log_file, temp_file_path)

        with open(temp_file_path, "r", encoding="utf-8", errors="ignore") as file:
            content = file.readlines()

        os.remove(temp_file_path)

        return content

    except PermissionError:
        logger.write_log(f"Permission error accessing log file for {purpose}. Check if Roblox is running with admin rights?")
    except FileNotFoundError:
         logger.write_log(f"Latest log file disappeared before copying for {purpose}.")
    except OSError as e:
         logger.write_log(f"OS error reading/copying log file for {purpose}: {e}")
    except Exception as e:
        logger.write_log(f"Unexpected error getting latest log content for {purpose}: {e}")

    return None

def get_latest_hovertext():
    """Extracts the latest biome name (hoverText) from Roblox logs."""
    log_content = _get_latest_log_content(purpose="biome_detection")
    if not log_content:
        return None

    json_pattern = re.compile(r'\{.*\}')
    last_hover_text = None

    try:
        for line in reversed(log_content):
            match = json_pattern.search(line)
            if match:
                try:
                    json_data = json.loads(match.group())

                    hover_text = json_data.get("message", {}).get("properties", {}).get("HoverText")

                    if not hover_text:
                         hover_text = json_data.get("data", {}).get("largeImage", {}).get("hoverText")

                    if hover_text:

                        hover_text = hover_text.strip()
                        return hover_text
                except json.JSONDecodeError:
                    continue 
    except Exception as e:
        get_logger().write_log(f"Error parsing hover text from logs: {e}")
        return None

    return last_hover_text 

def get_latest_equipped_aura():
    """Extracts the latest equipped aura name from Roblox logs."""
    log_content = _get_latest_log_content(purpose="aura_detection")
    if not log_content:
        return None

    json_pattern = re.compile(r'\{.*\}')

    try:
        for line in reversed(log_content):
            match = json_pattern.search(line)
            if match:
                try:
                    json_data = json.loads(match.group())

                    state = json_data.get("message", {}).get("properties", {}).get("State")

                    if not state:
                         state = json_data.get("data", {}).get("state")

                    if state:
                         state = state.strip()
                         if state == "In Main Menu":
                             return "In Main Menu"

                         if state.startswith('Equipped \"') and state.endswith('\"'):
                            aura = state[len('Equipped \"'):-1]
                            aura = aura.replace("_", ": ") 
                            return aura
                except json.JSONDecodeError:
                    continue
    except Exception as e:
         get_logger().write_log(f"Error parsing equipped aura from logs: {e}")
         return None

    return None

def detect_client_disconnect(lines_to_check=15):
    """Checks the last few log lines for disconnection messages."""
    log_content = _get_latest_log_content(purpose="disconnect_detection")
    if not log_content:
        return False 

    disconnect_patterns = [

        r"Lost connection with reason : Lost connection to the game server, please reconnect",
        r"disconnectErrorCode =",
        r"IDisconnecting from server:" 
    ]
    timestamp_pattern = re.compile(r"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}Z")

    try:
        last_lines = log_content[-lines_to_check:]
        for line in reversed(last_lines):
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in disconnect_patterns):
                timestamp_match = timestamp_pattern.search(line)
                timestamp_str = timestamp_match.group() if timestamp_match else "Unknown time"
                get_logger().write_log(f"Client disconnection detected in logs around {timestamp_str}.")
                return True
    except Exception as e:
        get_logger().write_log(f"Error checking for client disconnect: {e}")
        return False 

    return False

def detect_client_reconnect(lines_to_check=25):
    """Checks the last few log lines for reconnection messages."""
    log_content = _get_latest_log_content(purpose="reconnect_detection")
    if not log_content:
        return False

    reconnect_patterns = [
        r"NetworkClient:Create",
        r"Replicator::connect", 
        r"Connection accepted from",
        r"Joining server with placeID",
        r"Successfully joined game DataModel", 

    ]
    timestamp_pattern = re.compile(r"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}Z")

    try:
        last_lines = log_content[-lines_to_check:]
        for line in reversed(last_lines):
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in reconnect_patterns):
                timestamp_match = timestamp_pattern.search(line)
                timestamp_str = timestamp_match.group() if timestamp_match else "Unknown time"
                get_logger().write_log(f"Client reconnection detected in logs around {timestamp_str}.")
                return True
    except Exception as e:
        get_logger().write_log(f"Error checking for client reconnect: {e}")
        return False

    return False

def join_private_server_link(server_code):
    """Attempts to join a Roblox private server using the server code via protocol handler."""
    logger = get_logger()
    if not server_code:
        logger.write_log("Attempted to join private server with empty code.")
        return False
    try:

        final_link = f"roblox://placeID={PLACE_ID}^&linkCode={server_code}"
        logger.write_log(f"Attempting to join server with link code: {server_code[:5]}... (using {final_link[:30]}...)")

        subprocess.Popen(["start", "", final_link], shell=True) 
        logger.write_log(f"Issued command to join server.")
        return True
    except Exception as e:
        logger.write_log(f"Error executing command to join private server: {e}")
        return False

def leave_main_menu():
    """Clicks the start button if the latest log state is 'In Main Menu'."""
    logger = get_logger()
    try:
        if get_latest_equipped_aura() == "In Main Menu":
            logger.write_log("Detected 'In Main Menu'. Clicking start button...")
            if "start_btn_pos" in COORDS:
                 x, y = COORDS["start_btn_pos"]
                 _mkey_controller.left_click_xy_natural(x, y)
                 time.sleep(4) 

                 return True 
            else:
                 logger.write_log("Error leaving main menu: start_btn_pos not found in COORDS.")
    except Exception as e:
         logger.write_log(f"Error attempting to leave main menu: {e}")
    return False 

def reset_character():
    """Resets the Roblox character using keyboard shortcuts."""
    logger = get_logger()
    logger.write_log("Resetting character...")
    try:
        _keyboard_controller.press(keyboard.Key.esc)
        time.sleep(0.1)
        _keyboard_controller.release(keyboard.Key.esc)
        time.sleep(0.2)
        _keyboard_controller.press('r')
        time.sleep(0.1)
        _keyboard_controller.release('r')
        time.sleep(0.2)
        _keyboard_controller.press(keyboard.Key.enter)
        time.sleep(0.1)
        _keyboard_controller.release(keyboard.Key.enter)
        time.sleep(0.2)
        logger.write_log("Character reset initiated.")
    except Exception as e:
        logger.write_log(f"Error resetting character: {e}")

def align_camera(zoom_out_scrolls=80, zoom_in_scrolls=3):
    """Attempts to align the camera to a default view after reset."""
    logger = get_logger()
    logger.write_log("Aligning camera...")
    try:

        reset_character()
        time.sleep(3) 

        _keyboard_controller.press(keyboard.Key.shift)
        time.sleep(0.1)
        _keyboard_controller.release(keyboard.Key.shift)
        time.sleep(0.2)
        _keyboard_controller.press(keyboard.Key.shift)
        time.sleep(0.1)
        _keyboard_controller.release(keyboard.Key.shift)
        time.sleep(0.2)

        logger.write_log(f"Zooming out ({zoom_out_scrolls} scrolls)...")
        for _ in range(zoom_out_scrolls):
            _mouse_controller.scroll(0, 1) 
            time.sleep(0.01) 

        time.sleep(0.5) 

        logger.write_log(f"Zooming in slightly ({zoom_in_scrolls} scrolls)...")
        for _ in range(zoom_in_scrolls):
            _mouse_controller.scroll(0, -1) 
            time.sleep(0.05)

        time.sleep(0.5)
        logger.write_log("Camera alignment attempted.")

    except Exception as e:
        logger.write_log(f"Error aligning camera: {e}")

def activate_ms_store_roblox():
    logger = get_logger()
    logger.write_log("Attempting to activate MS Store Roblox window...")
    try:
        proc = get_process_by_name("Windows10Universal.exe")
        if proc:
            window = match_rblx_hwnd_to_pid(proc.pid)
            if window:
                _mkey_controller.activate_window(window.hwnd)
                time.sleep(0.5) 
                logger.write_log("MS Store Roblox window activated.")
                return True
            else:
                logger.write_log("Found MS Store process but couldn't find matching window.")
        else:
            logger.write_log("MS Store Roblox process not found.")
    except Exception as e:
        logger.write_log(f"Error activating MS Store Roblox window: {e}")
    return False

def click_ms_store_spawn_button():
    logger = get_logger()
    logger.write_log("Clicking MS Store spawn button...")
    try:
        if "ms_rblx_spawn_pos" in COORDS:
            x, y = COORDS["ms_rblx_spawn_pos"]
            _mkey_controller.left_click_xy_natural(x, y)
            time.sleep(0.1)
            _mkey_controller.left_click_xy_natural(x, y) 
            time.sleep(0.2)
            return True
        else:
             logger.write_log("Error clicking spawn: ms_rblx_spawn_pos not found in COORDS.")
    except Exception as e:
        logger.write_log(f"Error clicking MS Store spawn button: {e}")
    return False

def toggle_fullscreen_ms_store():
    logger = get_logger()
    logger.write_log("Toggling fullscreen (F11)...")
    try:
        _keyboard_controller.press(keyboard.Key.f11)
        time.sleep(0.1)
        _keyboard_controller.release(keyboard.Key.f11)
        time.sleep(0.2)
        return True
    except Exception as e:
        logger.write_log(f"Error toggling fullscreen: {e}")
    return False
