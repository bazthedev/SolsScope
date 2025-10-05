"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v2.0.0
Support server: https://discord.gg/8khGXqG7nA
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

from constants import MS_RBLX_LOG_DIR, RBLX_PLAYER_LOG_DIR, PLACE_ID, COORDS, MACROPATH, LOCALVERSION, USERDATA
from utils import get_logger, exists_procs_by_name, get_process_by_name, match_rblx_hwnd_to_pid
from uinav import load_delay, load_keybind
from pynput import keyboard 
from pynput import mouse
from PIL import ImageGrab
import pygetwindow as gw
from datetime import datetime, timezone
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import re
import json
import discord
from collections import defaultdict
from discord_utils import forward_webhook_msg
from utils import hex2rgb
import requests
import queue
import threading

_active_log_dir = None
_keyboard_controller = keyboard.Controller()
_mouse_controller = mouse.Controller()
_mkey_controller = mk.MouseKey()

# Global variable to track last permission error time to reduce spam
_last_permission_error_time = {}

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
        # Throttle permission error logging to reduce spam
        current_time = time.time()
        if purpose not in _last_permission_error_time or current_time - _last_permission_error_time[purpose] > 30:
            logger.write_log(f"Permission error accessing log file for {purpose}. Check if Roblox is running with admin rights?")
            _last_permission_error_time[purpose] = current_time
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
                            continue

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


def check_for_eden_spawn():
    """Checks if Eden has spawned in the server."""
    
    EDEN_REGEX = (
        r'<font color="rgb\(\d{1,3},\d{1,3},\d{1,3}\)">'
        r'<stroke color="rgb\(\d{1,3},\d{1,3},\d{1,3}\)" thickness="\d+" transparency="\d+">'
        r'The Devourer of the Void, <b>(.*?)</b> has appeared somewhere in <i>(.*?)</i>\.'
        r'</stroke></font>'
    )

    EDEN_SIGNS = [
        r"\[expchat/mountclientapp \(debug\)\]",
        r"incoming messagereceived status: success text:"
    ]

    log_content = _get_latest_log_content(purpose="eden_detection")
    if not log_content:
        return None, int(time.time() * 1000)

    try:
        for line in reversed(log_content):
            ts_match = re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", line)
            if not ts_match:
                continue
            timestamp_str = ts_match.group()
            dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            dt = dt.replace(tzinfo=timezone.utc)
            unix_millis = int(dt.timestamp() * 1000)

            eden_match = re.search(EDEN_REGEX, line, re.IGNORECASE)
            if not eden_match:
                continue

            if all(re.search(sign, line, re.IGNORECASE) for sign in EDEN_SIGNS):
                return True, unix_millis

        return False, int(time.time() * 1000)

    except Exception as e:
        get_logger().write_log(f"Error finding Eden from logs: {e}")
        return None, int(time.time() * 1000)
    

def get_latest_merchant_info(previous_timestamp : float):
    """
    Extracts the latest merchant info from Roblox logs.
    Returns a tuple: (merchant_name, unix_timestamp) or None if not found.
    """
    log_content = _get_latest_log_content(purpose="merchant_detection")
    if not log_content:
        return None

    merchant_pattern = re.compile(
        r'^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z),.*'
        r'\[FLog::Output\]\s+\[ExpChat/mountClientApp\s+\(Debug\)\]\s+-\s+Incoming MessageReceived Status: Success Text:\s*'
        r'(?:<.*?>)?\[Merchant\]:\s*(?P<name>[A-Za-z]+)\s+has arrived on the island',
        re.IGNORECASE
    )

    try:
        for line in reversed(log_content):
            match = merchant_pattern.search(line)
            if match:
                name = match.group("name").strip()
                timestamp_str = match.group("timestamp").strip()

                dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                unix_ts = dt.timestamp()

                if unix_ts > previous_timestamp:
                    return name, unix_ts
    except Exception as e:
        get_logger().write_log(f"Error parsing merchant info from logs: {e}")
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
    if not server_code:
        return False
    try:

        final_link = f"roblox://placeID={PLACE_ID}^&linkCode={server_code}"

        subprocess.Popen(["start", "", final_link], shell=True)
        return True
    except Exception as e:
        return False
    
def join_private_share_link(server_code):
    """Attempts to join a Roblox private server using the share code via protocol handler."""
    if not server_code:
        return False
    try:

        final_link = f"roblox://navigation/share_links?code={server_code}^&type=Server"
        subprocess.Popen(["start", "", final_link], shell=True) 
        return True
    except Exception as e:
        return False
    
def leave_main_menu():
    """Clicks the start button if the latest log state is 'In Main Menu'."""
    logger = get_logger()
    try:
        keybind = load_keybind()
        delay = load_delay()
        
        logger.write_log("Detected 'In Main Menu'. Clicking start button...")
        _keyboard_controller.press(keybind)
        time.sleep(delay)
        _keyboard_controller.release(keybind)
        time.sleep(delay)
        _keyboard_controller.press(keyboard.Key.enter)
        time.sleep(delay)
        _keyboard_controller.release(keyboard.Key.enter)
        time.sleep(delay)
        _keyboard_controller.press(keybind)
        time.sleep(delay)
        _keyboard_controller.release(keybind)
        time.sleep(delay)
        time.sleep(4)

        return True
    except Exception as e:
         logger.write_log(f"Error attempting to leave main menu: {e}")
    return False 

def reset_character():
    """Resets the Roblox character using keyboard shortcuts."""
    logger = get_logger()
    logger.write_log("Resetting character...")
    try:
        delay = load_delay()
        _keyboard_controller.press(keyboard.Key.esc)
        time.sleep(delay)
        _keyboard_controller.release(keyboard.Key.esc)
        time.sleep(0.2)
        _keyboard_controller.press('r')
        time.sleep(delay)
        _keyboard_controller.release('r')
        time.sleep(0.2)
        _keyboard_controller.press(keyboard.Key.enter)
        time.sleep(delay)
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
        delay = load_delay()

        reset_character()
        time.sleep(3) 

        _keyboard_controller.press(keyboard.Key.shift)
        time.sleep(delay)
        _keyboard_controller.release(keyboard.Key.shift)
        time.sleep(0.2)
        _keyboard_controller.press(keyboard.Key.shift)
        time.sleep(delay)
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
        leave_main_menu()
        return True
    except Exception as e:
        logger.write_log(f"Error clicking MS Store spawn button: {e}")
    return False

def toggle_fullscreen_ms_store():
    logger = get_logger()
    logger.write_log("Toggling fullscreen (F11)...")
    try:
        delay = load_delay()
        _keyboard_controller.press(keyboard.Key.f11)
        time.sleep(delay)
        _keyboard_controller.release(keyboard.Key.f11)
        time.sleep(0.2)
        return True
    except Exception as e:
        logger.write_log(f"Error toggling fullscreen: {e}")
    return False

def detect_ui_nav(bbox):
    px = ImageGrab.grab(bbox).load()
    for x in range(0, bbox[2] - bbox[0]):
        for y in range(0, bbox[3] - bbox[1]):
            if px[x, y] == (255, 255, 255):
                return True
    return False

def get_roblox_window_bbox():
    windows = gw.getWindowsWithTitle("Roblox")
    for win in windows:
        if win.width > 100 and win.height > 100:
            return (win.left, win.top, win.left + win.width, win.top + win.height)
    return None

def extract_server_code(url: str):
    """Extracts the server link/share code from a URL."""

    link_pattern = re.compile(
        f"https://www\\.roblox\\.com/games/{PLACE_ID}[^?]*\\?privateServerLinkCode=([^&]+)"
    )
    link_pattern_2 = re.compile(r"https://.*&type=Server")

    if link_match := link_pattern.search(url):
        try:
            code = link_match.group(1)
            return code, 1
        except IndexError:
            return None, None

    if link_match_2 := link_pattern_2.search(url):
        try:
            share_code = link_match_2.group(0).split("code=")[-1].split("&")[0]
            return share_code, 2
        except IndexError:
            return None, None

    return None, None

class PlayerLogHandler(FileSystemEventHandler):
    def __init__(self, logger, log_file, pylogger):
        self.logger = logger
        self.pylogger = pylogger
        self.log_file = log_file
        self.previous_player_join = None
        self.previous_player_leave = None
        self.started_logging = time.time()
        self.file_positions = {}

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".log"):
            return

        last_pos = self.file_positions.get(event.src_path, 0)

        try:
            with open(event.src_path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(last_pos)
                new_lines = f.readlines()
                self.file_positions[event.src_path] = f.tell()

            for line in new_lines:
                player_join = self.logger.parse_join_line(line)
                player_leave = self.logger.parse_leave_line(line)

                if player_join:
                    self.logger.process_player_event(player_join, self.log_file,
                                                     joined=True, prev_event=self.previous_player_join)
                    self.previous_player_join = player_join

                if player_leave:
                    self.logger.process_player_event(player_leave, self.log_file,
                                                     joined=False, prev_event=self.previous_player_leave)
                    self.previous_player_leave = player_leave
        except Exception as e:
            self.pylogger.write_log(f"Error reading log file {event.src_path}: {e}")


class PlayerLogger:
    
    def __init__(self, logs_dir, webhook, settings, pylogger):
        self.logs_dir = logs_dir
        self.pylogger = pylogger
        self.webhook = webhook
        self.settings = settings
        self.biome = None
        self.player_log_data = []
        self.to_send = queue.Queue()
        self._stop_event = threading.Event()
        self.ignore_userdata = USERDATA

        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()

    def _process_queue(self):
        while not self._stop_event.is_set():
            try:
                embed, content = self.to_send.get(timeout=0.5)
                self.send_embed(embed, content)
                time.sleep(5)
                self.to_send.task_done()
            except queue.Empty:
                continue

    def stop_worker(self):
        self._stop_event.set()
        self.worker_thread.join()

    def _send_embed(self, embed, content=None):
        self.to_send.put((embed, content))

    def init_player_logs(self, biome):
        file_name = f"{biome}_{datetime.now().strftime('%H-%M-%S')}_{datetime.now().strftime('%d-%m-%Y')}.log"
        os.makedirs(f"{MACROPATH}/player_logs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = (
            f"[{timestamp}] Starting Player logger for {biome}\n"
        )
        with open(f"{MACROPATH}/player_logs/{file_name}", "w", encoding="utf-8") as f:
            f.write(header + "\n")
        return file_name

    def log_player(self, file_name, content):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {content}"
        with open(f"{MACROPATH}/player_logs/{file_name}", "a", encoding="utf-8") as f:
            f.write(formatted_message + "\n")

    def send_player_msg(self, event, joined):
        ts = event.get("timestamp")
        title = f"Player Joined: {event.get('username', 'Unknown')}" if joined else f"Player Left: {event.get('username', 'Unknown')}"
        emb_rgb = hex2rgb(self.get_biome_colour(self.biome.lower()))
        
        _emb = discord.Embed(
            title=title,
            description=f"The user **{event.get('username', 'Unknown')}** (**{event.get('player_id', 'Unknown')}**) {'joined' if joined else 'left'} at <t:{str(int(ts))}>",
            colour=discord.Colour.from_rgb(*emb_rgb),
            url=f"https://www.roblox.com/users/{event.get('player_id', 'Unknown')}/profile"
        )
        img_url = self.get_user_headshot_from_id(event.get('player_id', 'Unknown'))
        if img_url:
            _emb.set_thumbnail(url=img_url)
        _emb.set_footer(text=f"SolsScope v{LOCALVERSION}")
        self._send_embed(_emb)

    def process_player_event(self, event, log_file_name, joined=True, prev_event=None):
        ts = event.get("timestamp")
        if not ts or (prev_event and ts <= prev_event.get("timestamp")) or ts < self.started_logging - 20:
            return

        ts_str = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
        if self.ignore_userdata.get("userId") != event.get("player_id", "Unknown"):
            self.player_log_data.append(event)
            msg = (
                f"Player {'Joined' if joined else 'Left'} Server: {event.get('username', 'Unknown')}, "
                f"ID: {event.get('player_id', 'Unknown')} at time {ts_str}"
            )
            self.send_player_msg(event, joined)
            self.pylogger.write_log(msg)
            self.log_player(log_file_name, msg)
        else:
            self.log_player(log_file_name, f"Owner {self.ignore_userdata.get('username')} {'joined' if joined else 'left'} the server.")

    def get_user_headshot_from_id(self, userid: str) -> str:
        try:
            if not userid:
                return None
            
            url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=150x150&format=Png"
            
            response = requests.get(url)
            return response.json()["data"][0]["imageUrl"]
        except Exception as e:
            return None

    def send_embed(self, embed, content=None):
        try:
            self.webhook.send(content=content, embed=embed)
            forward_webhook_msg(
                primary_webhook_url=self.webhook.url,
                secondary_urls=self.settings.get("SECONDARY_WEBHOOK_URLS", []),
                content=content,
                embed=embed
            )
        except Exception as e:
            self.pylogger.write_log(f"Error sending/forwarding webhooks: {e}")


    def parse_join_line(self, line):
        match = re.match(
            r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z).*?Player added: (\S+) (\d+)", line
        )
        if match:
            timestamp_str, username, player_id = match.groups()
            dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            return {"timestamp": dt.timestamp(), "username": username, "player_id": player_id, "joined_server": True}
        return None

    def parse_leave_line(self, line):
        match = re.match(
            r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z).*?Player removed: (\S+) (\d+)", line
        )
        if match:
            timestamp_str, username, player_id = match.groups()
            dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            return {"timestamp": dt.timestamp(), "username": username, "player_id": player_id, "joined_server": False}
        return None

    def start_logging(self, biome, end_event):
        self.biome = biome
        self.started_logging = time.time()
        self.player_log_data = []
        log_file_name = self.init_player_logs(biome)
        self.pylogger.write_log(f"Logging players to file: {log_file_name}")

        event_handler = PlayerLogHandler(self, log_file_name, self.pylogger)
        observer = Observer()
        observer.schedule(event_handler, self.logs_dir, recursive=False)
        observer.start()

        try:
            start_time = time.time()
            while not end_event.is_set():
                time.sleep(0.5)

            self.pylogger.write_log("Stopping player logs...")
            self.log_player(log_file_name, "Stopped logging players.")
            self.send_wait_time_report(self.player_log_data, biome)
            observer.stop()
        except KeyboardInterrupt:
            observer.stop()
        finally:
            observer.stop()

        observer.join()
        self.check_logs(log_file_name)

    def check_logs(self, log_file):
        should_remove = False
        with open(f"{MACROPATH}/player_logs/{log_file}", "r") as f:
            if len(f.readlines()) <= 3:
                should_remove = True
        
        if should_remove:
            try:
                os.remove(f"{MACROPATH}/player_logs/{log_file}")
                self.pylogger.write_log(f"Removed log file {log_file} as nobody joined/left")
            except Exception as e:
                self.pylogger.write_log(f"Failed to delete log file: {e}")

    def get_biome_colour(self, biome):
        with open(f"{MACROPATH}/biomes.json", "r") as f:
            _ = json.load(f)
            if _.get(biome):
                return _.get(biome).get("colour", "#000000")
        return "#000000"

    def send_wait_time_report(self, data, match_type) -> None:
        current_time = round(time.time())
        self.pylogger.write_log("Generating player report...")

        user_events = defaultdict(list)
        for event in data:
            user_id = event.get("player_id", "Unknown")
            user_events[user_id].append(event)

        description = ""
        emb_rgb = hex2rgb(self.get_biome_colour(match_type.lower()))

        for user_id, events in user_events.items():
            events.sort(key=lambda e: e.get("timestamp") or 0)

            total_duration = 0
            first_join = None
            last_leave = None
            username = "Unknown"
            in_server = False

            session_stack = []
            for event in events:
                ts = event.get("timestamp")
                if not ts:
                    continue
                joined = event.get("joined_server")
                username = event.get("username", username)

                if joined:
                    if first_join is None:
                        first_join = ts
                    session_stack.append(ts)
                    in_server = True
                else:
                    if session_stack:
                        join_ts = session_stack.pop()
                        total_duration += ts - join_ts
                        last_leave = ts
                        in_server = False
                    else:
                        last_leave = ts

            if session_stack:
                join_ts = session_stack.pop()
                total_duration += current_time - join_ts
                in_server = True

            formatted_join = f"<t:{str(int(first_join))}>" if first_join else "Unknown"
            if in_server:
                formatted_leave = "Still in server"
            else:
                formatted_leave = f"<t:{str(int(first_join))}>" if last_leave else "Unknown"

            duration_fmt = datetime.utcfromtimestamp(total_duration).strftime("%H:%M:%S")

            description += (
                f"Username: [**{username}**](https://www.roblox.com/users/{user_id}/profile), UserID: **{user_id}**, "
                f"Joined at **{formatted_join}**, Left at **{formatted_leave}**, "
                f"Total Time: **{duration_fmt}**\n"
            )

        MAX_DESC_LEN = 4096
        embeds = []
        chunks = [description[i:i+MAX_DESC_LEN] for i in range(0, len(description), MAX_DESC_LEN)]
        total = len(chunks)

        for i, chunk in enumerate(chunks, start=1):
            embed = discord.Embed(
                title=f"Player report for {match_type} at {datetime.now().strftime('%H:%M:%S')} ({i}/{total})",
                description=chunk,
                colour=discord.Colour.from_rgb(*emb_rgb)
            )
            embed.set_footer(text=f"SolsScope v{LOCALVERSION}")
            embeds.append(embed)

        try:
            for emb in embeds:
                self.send_embed(emb)
            self.pylogger.write_log("Sent player log report.")
        except Exception as e:
            self.pylogger.write_log(f"Error sending report to webhook: {e}")


def get_username(log_path):
    """
    Parses Roblox log to extract username, userId, and displayName.
    Returns a dict: {"username": ..., "userId": ..., "displayName": ...} or None if not found.
    """
    if not os.path.exists(log_path):
        print(f"Debug: Log path does not exist: {log_path}")
        return None

    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(1048576)

        match = re.search(
            r'Application did receive notification, type\(DID_LOG_IN,[^\)]*\), data\((\{.*?\})\)',
            content,
            re.DOTALL
        )
        if match:
            json_str = match.group(1)
            try:
                data = json.loads(json_str)
                username = data.get("username")
                user_id = data.get("userId")
                display_name = data.get("displayName")
                print(f"Debug: Extracted username={username}, userId={user_id}, displayName={display_name}")
                return {"username": username, "userId": user_id, "displayName": display_name}
            except json.JSONDecodeError:
                print(f"Error: Failed to parse JSON from log: {json_str}")
                return None
        else:
            print(f"Debug: DID_LOG_IN pattern not found in {log_path}")
            return None

    except Exception as e:
        print(f"Error reading log {log_path}: {e}")
        return None