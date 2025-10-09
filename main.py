"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v2.0.2
Support server: https://discord.gg/8khGXqG7nA
"""

import sys
import os
import requests
import json
import tkinter as tk
from tkinter import messagebox
from webbrowser import open as wbopen
import glob
import shutil
import ctypes
import datetime
import traceback

WORK_DIR = os.path.expandvars(r"%localappdata%\SolsScope")
THEME_DIR = os.path.expandvars(r"%localappdata%\SolsScope\theme")
PATH_DIR = os.path.expandvars(r"%localappdata%\SolsScope\path")
LIB_DIR = os.path.expandvars(r"%localappdata%\SolsScope\lib")
LEGACY_DIR = os.path.expandvars(r"%localappdata%\Baz's Macro")
PACKAGES_DIR = os.path.expandvars(r"%localappdata%/SolsScope/py/Lib/site-packages")
ASSET_DIR = os.path.expandvars(r"%localappdata%\SolsScope\assets")
CALIBRATIONS_DIR = os.path.expandvars(r"%localappdata%\SolsScope\calibrations")


def log_uncaught_exception(exc_type, exc_value, exc_traceback):
    """Log uncaught exceptions to a file with timestamped name."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    log_dir = os.path.join(WORK_DIR, "temp")
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_path = os.path.join(log_dir, f"error_{timestamp}.log")

    with open(dump_path, "w", encoding="utf-8") as f:
        f.write("=== SolsScope Unhandled Exception ===\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)

    if "--debug" in sys.argv:
        print(f"\nUnhandled exception logged to: {dump_path}")

sys.excepthook = log_uncaught_exception

def enable_console():
    """Attach a console window for debugging."""
    kernel32 = ctypes.windll.kernel32
    if not kernel32.GetConsoleWindow():
        kernel32.AllocConsole()
        sys.stdout = open('CONOUT$', 'w')
        sys.stderr = open('CONOUT$', 'w')
        sys.stdin = open('CONIN$', 'r')

MAIN_VER = "2.0.2"
PRERELEASE = False
BUILTINPKGS = True
IS_EXE = True

if "--debug" in sys.argv and IS_EXE:
    enable_console()


print("======== SolsScope ========")
print(f"Launcher version: {MAIN_VER}\nPrerelease: {PRERELEASE}\nPackages Built In: {BUILTINPKGS}")


GITHUB_USERNAMES = {
    "primary" : "bazthedev",
    "mirror" : "ScopeDevelopment"
}

IS_SS_UP = {
    "primary" : "DOWN",
    "mirror" : "DOWN"
}

try:
    riu = requests.get(f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/main/requirements.txt", timeout=10)
    if riu.status_code == 200:
        IS_SS_UP["primary"] = "OK"
except Exception as e:
    print(f"Error: {e}")

try:
    riu = requests.get(f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('mirror')}/SolsScope/main/requirements.txt", timeout=10)
    if riu.status_code == 200:
        IS_SS_UP["mirror"] = "OK"
except Exception as e:
    print(f"Error: {e}")

print(f"Primary: {IS_SS_UP.get('primary')}")
print(f"Mirror: {IS_SS_UP.get('mirror')}")

def download_folder(url, local_dir, overwrite=True):
    os.makedirs(local_dir, exist_ok=True)
    if IS_SS_UP.get("primary") == "OK" or IS_SS_UP.get("mirror") == "OK":
        response = requests.get(url)
        response.raise_for_status()
        items = response.json()
        
        for item in items:
            if item['type'] == 'file':
                file_url = item['download_url']
                file_path = os.path.join(local_dir, item['name'])
                if overwrite or not os.path.exists(file_path):
                    print(f"Downloading {file_path} from {item['download_url']}...")
                    r = requests.get(file_url)
                    r.raise_for_status()
                    with open(file_path, 'wb') as f:
                        f.write(r.content)
            elif item['type'] == 'dir':
                download_folder(item['url'], os.path.join(local_dir, item['name']))
    else:
        print("SolsScope is currently DOWN.")


def get_script_location():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))
    
def resource_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller exe """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = get_script_location()
    return os.path.join(base_path, relative_path)

if PRERELEASE:
    LIB_DOWNLOAD_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/Preview/lib/"
    LIBS_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('primary')}/SolsScope/contents/lib?ref=Preview"
    REQ_TXT_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/Preview/requirements.txt"
    print("Pre-Release Version! Thank you for being a tester!")
    PATH_DOWNLOAD_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/refs/heads/main/path/"
    PATH_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('primary')}/SolsScope/contents/path?ref=main"
    THEME_DOWNLOAD_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/refs/heads/main/theme/"
    THEME_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('primary')}/SolsScope/contents/theme?ref=main"
    ASSETS_DOWNLOAD_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/refs/heads/main/img/assets/"
    ASSETS_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('primary')}/SolsScope/contents/img/assets?ref=main"
    LATEST_VERSION_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('primary')}/SolsScope/releases/latest"
    THEME_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('primary')}/SolsScope/contents/theme"
    VIDEO_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/refs/heads/main/video_url"
elif IS_SS_UP.get("primary") == "OK":
    LIB_DOWNLOAD_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/Preview/lib/"
    LIBS_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('primary')}/SolsScope/contents/lib?ref=main"
    REQ_TXT_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/main/requirements.txt"
    PATH_DOWNLOAD_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/refs/heads/main/path/"
    PATH_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('primary')}/SolsScope/contents/path?ref=main"
    THEME_DOWNLOAD_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/refs/heads/main/theme/"
    THEME_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('primary')}/SolsScope/contents/theme?ref=main"
    ASSETS_DOWNLOAD_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/refs/heads/main/img/assets/"
    ASSETS_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('primary')}/SolsScope/contents/img/assets?ref=main"
    LATEST_VERSION_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('primary')}/SolsScope/releases/latest"
    THEME_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('primary')}/SolsScope/contents/theme"
    VIDEO_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/refs/heads/main/video_url"
else:
    LIB_DOWNLOAD_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('mirror')}/SolsScope/main/lib/"
    LIBS_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('mirror')}/SolsScope/contents/lib?ref=main"
    REQ_TXT_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('mirror')}/SolsScope/main/requirements.txt"
    PATH_DOWNLOAD_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('mirror')}/SolsScope/refs/heads/main/path/"
    PATH_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('mirror')}/SolsScope/contents/path?ref=main"
    THEME_DOWNLOAD_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('mirror')}/SolsScope/refs/heads/main/theme/"
    THEME_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('mirror')}/SolsScope/contents/theme?ref=main"
    ASSETS_DOWNLOAD_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('mirror')}/SolsScope/refs/heads/main/img/assets/"
    ASSETS_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('mirror')}/SolsScope/contents/img/assets?ref=main"
    LATEST_VERSION_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('mirror')}/SolsScope/releases/latest"
    THEME_URL = f"https://api.github.com/repos/{GITHUB_USERNAMES.get('mirror')}/SolsScope/contents/theme"
    VIDEO_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('mirror')}/SolsScope/refs/heads/main/video_url"

EXTRACTED_DATA = False

if not os.path.exists(WORK_DIR):
    os.mkdir(WORK_DIR)
    if IS_EXE:
        try:
            shutil.copytree(resource_path("data/"), WORK_DIR, dirs_exist_ok=True)
            print("Successfully extracted data.")
            EXTRACTED_DATA = True
        except Exception as e:
            print(f"Error occured copying data: {e}")

if not os.path.exists(os.path.join(WORK_DIR, "player_logs")):
    os.mkdir(os.path.join(WORK_DIR, "player_logs"))

if not os.path.exists(ASSET_DIR):
    os.mkdir(ASSET_DIR)
    download_folder(ASSETS_API_URL, ASSET_DIR)
    print("All assets have been downloaded, proceeding...")

if not os.path.exists(THEME_DIR):
    os.mkdir(THEME_DIR)
    print("All themes have been downloaded, proceeding...")

if not os.path.exists(LIB_DIR):
    os.mkdir(LIB_DIR)
    print("Lib folder not found, downloading libraries...")
    download_folder(LIBS_API_URL, LIB_DIR)

if not os.path.exists(PATH_DIR):
    os.mkdir(PATH_DIR)
    download_folder(PATH_API_URL, PATH_DIR)
    print("All required paths were downloaded, proceeding...")


if not os.path.isfile(f"{WORK_DIR}\\settings.json") and os.path.isfile(f"{LEGACY_DIR}\\settings.json"):
    os.system(f"xcopy {LEGACY_DIR}\\settings.json {WORK_DIR}")
elif not os.path.isfile(f"{WORK_DIR}\\settings.json"):
    _temp = open(f"{WORK_DIR}\\settings.json", "w")
    _temp.write("{}")
    _temp.close()
    if messagebox.askyesno("SolsScope", "As this is your first time using SolsScope, would you like to watch a video guide on how to use it?"):
        try:
            video = requests.get(VIDEO_URL, timeout=10)
            video.raise_for_status()
            wbopen(video.text)
        except Exception as e:
            wbopen("https://www.youtube.com/watch?v=Y12uiAbqMDc")

root = tk.Tk(); root.withdraw(); root.attributes('-topmost', True)

try:
    print("Checking latest version...")
    r = requests.get(LATEST_VERSION_URL, timeout=10)
    r.raise_for_status()
    data = r.json()
    LATEST_VERSION = data["name"]   
    print(f"The latest version is {LATEST_VERSION}")
except Exception as e:
    LATEST_VERSION = "2.0.2"


UPDATE = False

try:
    with open(f"{WORK_DIR}\\settings.json", "r") as s:
        _tempsettings = json.load(s)
        def parse_version(v):
            try:
                return tuple(map(int, v.split('.')))
            except ValueError:
                print(f"Invalid version format: '{v}'. Returning (1,0,0).")
                return (1, 0, 0)
        
        if parse_version(MAIN_VER) > parse_version(_tempsettings.get("__version__", "1.0.0")):
            UPDATE = True
            print("Macro update detected, redownloading required libraries...")
            download_folder(LIBS_API_URL, LIB_DIR)
            download_folder(PATH_API_URL, PATH_DIR)
            download_folder(ASSETS_API_URL, ASSET_DIR)
            print("All required libraries were updated, proceeding...")
            _tempsettings["__version__"] = MAIN_VER
            with open(f"{WORK_DIR}\\settings.json", "w", encoding="utf-8") as f:
                json.dump(_tempsettings, f, indent=4)
            messagebox.showinfo("SolsScope", "If you paid for this software, then you have been scammed and should demand a refund. The only official download page for this software is https://github.com/bazthedev/SolsScope and https://github.com/ScopeDevelopment/SolsScope")
        elif parse_version(LATEST_VERSION) > parse_version(_tempsettings.get("__version__", "1.0.0")):
            UPDATE = True
            if messagebox.askyesno("SolsScope", f"A new version ({LATEST_VERSION}) of SolsScope has been detected, would you like to download it?"):
                print("Macro update detected, redownloading required libraries...")
                download_folder(LIBS_API_URL, LIB_DIR)
                download_folder(PATH_API_URL, PATH_DIR)
                download_folder(ASSETS_API_URL, ASSET_DIR)
                print("All required libraries were updated, proceeding...")
                _tempsettings["__version__"] = LATEST_VERSION
                with open(f"{WORK_DIR}\\settings.json", "w", encoding="utf-8") as f:
                    json.dump(_tempsettings, f, indent=4)
                messagebox.showinfo("SolsScope", "If you paid for this software, then you have been scammed and should demand a refund. The only official download page for this software is https://github.com/bazthedev/SolsScope and https://github.com/ScopeDevelopment/SolsScope")
        elif _tempsettings.get("redownload_libs_on_run", False) or PRERELEASE:
            print("Manual redownload/prerelease initiated download.")
            download_folder(LIBS_API_URL, LIB_DIR)
            download_folder(PATH_API_URL, PATH_DIR)
            download_folder(ASSETS_API_URL, ASSET_DIR)
            _tempsettings["redownload_libs_on_run"] = False
            with open(f"{WORK_DIR}\\settings.json", "w", encoding="utf-8") as f:
                json.dump(_tempsettings, f, indent=4)
        else:
            print("No updates were detected.")

except Exception as e:
    messagebox.showerror("SolsScope", f"Error whilst downloading required libraries: {e}")

sys.path.insert(1, LIB_DIR)

import importlib
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer

import packager

packager.download_python()

icon_path = os.path.join(WORK_DIR, "icon.ico")
if IS_SS_UP['primary'] == "OK":
    icon_url = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/main/icon.ico"
elif IS_SS_UP['mirror'] == "OK":
    icon_url = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('mirror')}/SolsScope/main/icon.ico"
else:
    icon_url = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/main/icon.ico"


if not os.path.exists(icon_path):
    try:
        dl = requests.get(icon_url, timeout=10)
        dl.raise_for_status()
        with open(icon_path, "wb") as f:
            f.write(dl.content)
        print("Icon downloaded successfully.")
    except requests.RequestException as e:
        print(f"Failed to download icon: {e}") 
    except OSError as e:
        print(f"Error saving icon file: {e}") 
    except Exception as e:
        print(f"Unexpected error downloading/saving icon: {e}") 

if not BUILTINPKGS:
    _requirements = []
    try:
        reqs_txt_resp = requests.get(REQ_TXT_URL, timeout=10)
        reqs_txt_resp.raise_for_status()
        _requirements = reqs_txt_resp.text.split("\n")
        print(_requirements)
        if _requirements[-1] == "":
            _requirements.pop()

    except Exception as e:
        print(f"Error whilst querying requirements: {e}")

    if _requirements:
        temp_app = QApplication.instance()
        owns_app = temp_app is None
        if owns_app:
            temp_app = QApplication(sys.argv)
        try:
            installer = packager.PackageInstallerGUI(_requirements)
            QTimer.singleShot(0, installer.start_install)
            installer.exec()
        finally:
            if owns_app:
                temp_app.quit()
                del temp_app
                
sys.path.insert(0, PACKAGES_DIR)
sys.path.insert(0, os.path.expandvars(r"%localappdata%/SolsScope/py/Scripts"))
sys.path.insert(0, os.path.expandvars(r"%localappdata%/SolsScope/py/Lib/"))


import screeninfo as si 
import mousekey as mk
from gui import MainWindow
from gui import PyQtLogger

CORE_MODULES = [
    'discord', 'requests', 'pynput', 'mousekey', 'screeninfo',
    'psutil', 'PIL'
]
missing_core = []
for module_name in CORE_MODULES:
    try:
        importlib.import_module(module_name)
    except ImportError:
        missing_core.append(module_name)

if missing_core:

    error_message = (
        f"The following essential modules are missing:\n"
        f"{', '.join(missing_core)}\n\n"
        f"Please install them, e.g., using:\n"
        f"pip install -r requirements.txt"
    )
    print(f"ERROR: {error_message}")
    try:
        messagebox.showerror("Missing Core Dependencies", error_message)
    except Exception:
        pass 
    sys.exit(1)

try:
    from constants import MACROPATH, LOCALVERSION, DEFAULTSETTINGS, COORDS, USERDATA
    from utils import calculate_coords, set_global_logger, parse_version, Logger, get_logger, apply_roblox_fastflags
    from settings_manager import (
        migrate_settings_from_legacy_location, load_settings, update_settings,
        get_auras, get_biomes, get_settings_path, get_auras_path, get_biomes_path,
        get_merchant, get_merchant_path, get_questboard_path, get_questboard,
        validate_settings, get_fish_path, get_fishdata, get_autocraftdata_path,
        get_autocraft_data, get_ratios_path, get_ratios, get_valid_list_path,
        get_valid_list
    )
    from roblox_utils import set_active_log_directory, get_username, get_active_log_directory
    from stats import create_stats, init_stats
except ImportError as e:
    error_message = (
        f"Failed to load a required project module.\n"
        f"Ensure all .py files (constants, utils, etc.) are present.\n"
        f"Error: {e}"
    )
    print(f"ERROR: {error_message}")
    try:
        messagebox.showerror("Module Load Error", error_message)
    except Exception:
        pass
    sys.exit(1)
except Exception as e:

    error_message = f"An unexpected error occurred during startup: {e}"
    print(f"FATAL ERROR: {error_message}")
    traceback.print_exc()
    try:
        messagebox.showerror("Fatal Startup Error", error_message)
    except Exception:
        pass
    sys.exit(1)

def run_initial_setup(logger): 
    """Performs all necessary setup before starting the GUI."""

    logger.write_log(f"--- SolsScope v{LOCALVERSION} Startup Sequence --- Using {type(logger).__name__} ---")

    logger.write_log("Ensuring core directories exist...")
    try:
        os.makedirs(MACROPATH, exist_ok=True)
        os.makedirs(os.path.join(MACROPATH, "scr"), exist_ok=True)
        os.makedirs(os.path.join(MACROPATH, "theme"), exist_ok=True)
        os.makedirs(os.path.join(MACROPATH, "plugins"), exist_ok=True)
        os.makedirs(os.path.join(MACROPATH, "plugins", "config"), exist_ok=True)            
        os.makedirs(os.path.join(MACROPATH, "temp"), exist_ok=True)
        logger.write_log(f"Core directories ensured in: {MACROPATH}")
    except OSError as e:
        logger.write_log(f"Error creating directories: {e}")
        messagebox.showerror("Directory Error", f"Could not create necessary directories in {MACROPATH}. Check permissions.")
        return False

    if migrate_settings_from_legacy_location():
        logger.write_log("Settings migrated from legacy location (./settings.json).")

    print("Clearing temp directory")
    for file in os.listdir(f"{MACROPATH}/temp"):
        try:
            os.remove(f"{MACROPATH}/temp/{file}")
            print(f"Delete: {MACROPATH}/temp/{file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}")

    logger.write_log("Loading settings...")
    settings = load_settings()

    logger.write_log("Initial settings loaded and validated.")

    current_settings_version = settings.get("__version__", "0.0.0")
    if parse_version(current_settings_version) != parse_version(LOCALVERSION):
        logger.write_log(f"Settings version ({current_settings_version}) differs from macro version ({LOCALVERSION}). Settings were updated/validated during load.")

    if PRERELEASE:
        logger.write_log(f"Warning: Running PRERELEASE version {LOCALVERSION}.")
        messagebox.showwarning("Prerelease Version", f"Warning! This is a prerelease version (v{LOCALVERSION}) of SolsScope. Expect potential bugs or errors.\nLogs are stored in: {MACROPATH}")

    print("Downloading data files...")

    if not settings.get("skip_aura_download", False):
        if not get_auras():
            logger.write_log("Failed to download auras data.")
    elif not os.path.exists(get_auras_path()):
        logger.write_log("Auras file missing.")
        if not get_auras():
            logger.write_log("Failed to download auras data.")

    else:
        logger.write_log("Skipping aura download based on settings.")

    if not settings.get("skip_biome_download", False):
        if not get_biomes():
            logger.write_log("Failed to download biomes data.")

    elif not os.path.exists(get_biomes_path()):
        logger.write_log("Biomes file missing.")
        if not get_biomes():
            logger.write_log("Failed to download biomes data.")

    else:
        logger.write_log("Skipping biome download based on settings.")

    if not settings.get("skip_merchant_download", False):
        if not get_merchant():
            logger.write_log("Failed to download merchant data.")

    elif not os.path.exists(get_merchant_path()):
        logger.write_log("Merchant file missing.")
        if not get_merchant():
            logger.write_log("Failed to download merchant data.")

    else:
        logger.write_log("Skipping merchant download based on settings.")

    if not settings.get("skip_questboard_download", False):
        if not get_questboard():
            logger.write_log("Failed to download quest board data.")

    elif not os.path.exists(get_questboard_path()):
        logger.write_log("Quest board file missing.")
        if not get_questboard():
            logger.write_log("Failed to download quest board data.")

    else:
        logger.write_log("Skipping quest board download based on settings.")

    if not settings.get("skip_fishdata_download", False):
        if not get_fishdata():
            logger.write_log("Failed to download fish data.")

    elif not os.path.exists(get_fish_path()):
        logger.write_log("Fish Data file missing.")
        if not get_fishdata():
            logger.write_log("Failed to download fish data.")

    else:
        logger.write_log("Skipping fish data download based on settings.")

    if not settings.get("skip_autocraft_download", False):
        if not get_autocraft_data():
            logger.write_log("Failed to download auto craft data.")

    elif not os.path.exists(get_autocraftdata_path()):
        logger.write_log("Auto craft file missing.")
        if not get_autocraft_data():
            logger.write_log("Failed to download auto craft data.")

    else:
        logger.write_log("Skipping auto craft download based on settings.")

    if not os.path.exists(get_ratios_path()) or UPDATE:
        logger.write_log("Ratios file missing/needs download.")
        if not get_ratios():
            logger.write_log("Failed to download ratios data.")

    if not os.path.exists(get_valid_list_path()) or UPDATE:
        logger.write_log("Valid list file missing/needs download.")
        if not get_valid_list():
            logger.write_log("Failed to download valid list.")

    print("Done!")

    if not os.path.exists(get_auras_path()):
        messagebox.showwarning("Data Missing", f"Auras data file missing and could not be downloaded:\n{get_auras_path()}\n\nAura-related features may not work correctly.")
    if not os.path.exists(get_biomes_path()):
        messagebox.showwarning("Data Missing", f"Biomes data file missing and could not be downloaded:\n{get_biomes_path()}\n\nBiome-related features may not work correctly.")
    if not os.path.exists(get_merchant_path()):
        messagebox.showwarning("Data Missing", f"Merchant data file missing and could not be downloaded:\n{get_merchant_path()}\n\nMerchant-related features may not work correctly.")
    if not os.path.exists(get_questboard_path()):
        messagebox.showwarning("Data Missing", f"Quest board data file missing and could not be downloaded:\n{get_questboard_path()}\n\nQuest board related features may not work correctly.")
    if not os.path.exists(get_fish_path()):
        messagebox.showwarning("Data Missing", f"Fish data file missing and could not be downloaded:\n{get_fish_path()}\n\nFishing related features may not work correctly.")
    if not os.path.exists(get_autocraftdata_path()):
        messagebox.showwarning("Data Missing", f"Auto Craft data file missing and could not be downloaded:\n{get_autocraftdata_path()}\n\nAuto craft related features may not work correctly.")

    apply_roblox_fastflags(logger.write_log)

    try:
        create_stats()
        init_stats()
    except Exception as e:
        print(f"Unknown exception whilst creating stats: {e}")

    print(f"Setting up SolsScope v{LOCALVERSION}")

    logger.write_log("Detecting screen resolution and calculating coordinates...")
    primary_monitor = None
    try:
        monitors = si.get_monitors()
        for mon in monitors:
            if mon.is_primary:
                primary_monitor = mon
                break
        if not primary_monitor and monitors: 
            primary_monitor = monitors[0]
            logger.write_log("No primary monitor detected, using first available monitor.")

        if primary_monitor:
            calculated_coords = calculate_coords(primary_monitor)
            if calculated_coords:

                COORDS.update(calculated_coords)

                base_w, base_h = 2560, 1440
                COORDS['scale_w'] = primary_monitor.width / base_w
                COORDS['scale_h'] = primary_monitor.height / base_h
                COORDS['scr_wid'] = primary_monitor.width
                COORDS['scr_hei'] = primary_monitor.height
                logger.write_log(f"Screen coordinates calculated for {primary_monitor.width}x{primary_monitor.height} (Scale W:{COORDS['scale_w']:.2f}, H:{COORDS['scale_h']:.2f})")
            else:
                logger.write_log("Coordinate calculation failed. Using default coordinates.")

                messagebox.showerror("Coordinate Error", "Failed to calculate screen coordinates. Macro may not function correctly. Using defaults.")

                if 'scale_w' not in COORDS: COORDS['scale_w'] = 1.0
                if 'scale_h' not in COORDS: COORDS['scale_h'] = 1.0
                if 'scr_wid' not in COORDS: COORDS['scr_wid'] = 2560
                if 'scr_hei' not in COORDS: COORDS['scr_hei'] = 1440
        else:
            logger.write_log("No monitors detected. Cannot calculate coordinates. Exiting.")
            messagebox.showerror("Monitor Error", "Could not detect any monitors. Cannot calculate coordinates.")
            return False
        
        

    except Exception as e:
        logger.write_log(f"Error during screen detection or coordinate calculation: {e}")
        messagebox.showerror("Screen Error", f"Error getting monitor info or calculating coordinates: {e}")
        return False 

    try:

        mkey_instance = mk.MouseKey()
        failsafe_key = settings.get("failsafe_key", "ctrl+e")
        mkey_instance.enable_failsafekill(failsafe_key)
        logger.write_log(f"Failsafe kill switch enabled ({failsafe_key}). Press this combination to force-stop.")
    except Exception as e:
        logger.write_log(f"Failed to enable failsafe kill switch: {e}")
        messagebox.showwarning("Failsafe Error", f"Could not enable failsafe key ({failsafe_key}):\n{e}\n\nManual termination may be required if macro freezes.")

    try:
        set_active_log_directory(use_ms_store_if_detected=not settings.get("use_roblox_player", True))
        userdata = get_username(max(glob.glob(os.path.join(get_active_log_directory(), "*.log")), key=os.path.getctime))

        if userdata:
            USERDATA.update(userdata)
    except Exception as e:
        print(f"Error fetching username: {e}")
        return False
    logger.write_log("Initial setup complete.")
    return True

if __name__ == '__main__':

    log_file = os.path.join(MACROPATH, "solsscope.log")
    pyqt_logger = PyQtLogger(log_file=log_file)
    set_global_logger(pyqt_logger) 
    logger = get_logger() 
    logger.write_log("Global logger set to PyQtLogger. Running initial setup...")

    if not run_initial_setup(logger):

        logger.write_log("Initial setup failed. Exiting.")
        sys.exit(0)

    logger.write_log("Initial setup complete. Initializing GUI...")

    if PRERELEASE:
        logger.write_log("This is a prerelease version!")

    try:
        root.destroy()
        app = QApplication(sys.argv)
        main_window = MainWindow() 

        failsafe = None 

        main_window.show()
        logger.write_log("Starting PyQt event loop...")
        exit_code = app.exec()

        logger.write_log("--- SolsScope Exiting --- ")
        sys.exit(exit_code)

    except Exception as e:

        logger = get_logger()

        logger.write_log(f"[CRITICAL] --- !!! UNHANDLED FATAL GUI ERROR: {e} !!! ---")
        logger.write_log(f"[CRITICAL] {traceback.format_exc()}")
        try:

            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Icon.Critical)
            msgBox.setWindowTitle("Fatal GUI Error")
            msgBox.setText(f"An unhandled error occurred:\n{e}\n\nPlease check the log file for details:\n{os.path.join(MACROPATH, 'solsscope.log')}")
            msgBox.exec()
        except Exception:
            print(f"FATAL ERROR: {e}\n{traceback.format_exc()}") 
        sys.exit(1)