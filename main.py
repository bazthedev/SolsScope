import sys
import os
import tkinter as tk
from tkinter import messagebox
import requests
import json
import zipfile
from pathlib import Path
import importlib 
import screeninfo as si 
import mousekey as mk 
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui import MainWindow
from gui import PyQtLogger

CORE_MODULES = [
    'discord', 'requests', 'pynput', 'mousekey', 'screeninfo',
    'psutil', 'websockets', 'aiohttp', 'PIL'
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
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Missing Core Dependencies", error_message)
    except Exception:
        pass 
    sys.exit(1)

try:
    from constants import MACROPATH, LOCALVERSION, PRERELEASE, DEFAULTSETTINGS, COORDS
    from utils import calculate_coords, set_global_logger, parse_version, Logger, get_logger 
    from settings_manager import (
        migrate_settings_from_legacy_location, load_settings, update_settings,
        get_auras, get_biomes, get_settings_path, get_auras_path, get_biomes_path,
        validate_settings 
    )
    from roblox_utils import set_active_log_directory 
except ImportError as e:
    error_message = (
        f"Failed to load a required project module.\n"
        f"Ensure all .py files (constants, utils, etc.) are present.\n"
        f"Error: {e}"
    )
    print(f"ERROR: {error_message}")
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Module Load Error", error_message)
    except Exception:
        pass
    sys.exit(1)
except Exception as e:

    error_message = f"An unexpected error occurred during startup: {e}"
    print(f"FATAL ERROR: {error_message}")
    import traceback
    traceback.print_exc()
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Fatal Startup Error", error_message)
    except Exception:
        pass
    sys.exit(1)

def run_initial_setup(logger): 
    """Performs all necessary setup before starting the GUI."""

    logger.write_log(f"--- SolsRNGBot v{LOCALVERSION} Startup Sequence --- Using {type(logger).__name__} ---")

    logger.write_log("Ensuring core directories exist...")
    try:
        os.makedirs(MACROPATH, exist_ok=True)
        os.makedirs(os.path.join(MACROPATH, "scr"), exist_ok=True)
        os.makedirs(os.path.join(MACROPATH, "plugins"), exist_ok=True)
        os.makedirs(os.path.join(MACROPATH, "plugins", "config"), exist_ok=True)
        logger.write_log(f"Core directories ensured in: {MACROPATH}")
    except OSError as e:
        logger.write_log(f"Error creating directories: {e}")
        messagebox.showerror("Directory Error", f"Could not create necessary directories in {MACROPATH}. Check permissions.")
        return False 

    if migrate_settings_from_legacy_location():
        logger.write_log("Settings migrated from legacy location (./settings.json).")

    logger.write_log("Loading settings...")
    settings = load_settings()

    logger.write_log("Initial settings loaded and validated.")

    current_settings_version = settings.get("__version__", "0.0.0")
    if parse_version(current_settings_version) != parse_version(LOCALVERSION):
        logger.write_log(f"Settings version ({current_settings_version}) differs from macro version ({LOCALVERSION}). Settings were updated/validated during load.")

    if PRERELEASE:
        logger.write_log(f"Warning: Running PRERELEASE version {LOCALVERSION}.")
        messagebox.showwarning("Prerelease Version", f"Warning! This is a prerelease version (v{LOCALVERSION}) of SolsRNGBot. Expect potential bugs or errors.\nLogs are stored in: {MACROPATH}")

    icon_path = os.path.join(MACROPATH, "icon.ico")
    icon_url = "https://raw.githubusercontent.com/bazthedev/SolsRNGBot/main/icon.ico"
    if not os.path.exists(icon_path):
        logger.write_log("Icon file missing, attempting download...")
        try:
            dl = requests.get(icon_url, timeout=10)
            dl.raise_for_status()
            with open(icon_path, "wb") as f:
                f.write(dl.content)
            logger.write_log("Icon downloaded successfully.")
        except requests.RequestException as e:
            logger.write_log(f"Failed to download icon: {e}") 
        except OSError as e:
            logger.write_log(f"Error saving icon file: {e}") 
        except Exception as e:
            logger.write_log(f"Unexpected error downloading/saving icon: {e}") 

    if not settings.get("skip_aura_download", False):
        if not os.path.exists(get_auras_path()):
            logger.write_log("Auras file missing.")
            if not get_auras():
                logger.write_log("Failed to download auras data.") 

    else:
        logger.write_log("Skipping aura download based on settings.")

    if not settings.get("skip_biome_download", False):
        if not os.path.exists(get_biomes_path()):
            logger.write_log("Biomes file missing.")
            if not get_biomes():
                logger.write_log("Failed to download biomes data.") 

    else:
        logger.write_log("Skipping biome download based on settings.")

    if not os.path.exists(get_auras_path()):
        messagebox.showwarning("Data Missing", f"Auras data file missing and could not be downloaded:\n{get_auras_path()}\n\nAura-related features may not work correctly.")
    if not os.path.exists(get_biomes_path()):
        messagebox.showwarning("Data Missing", f"Biomes data file missing and could not be downloaded:\n{get_biomes_path()}\n\nBiome-related features may not work correctly.")

    if settings.get("check_update", True):
        logger.write_log("Checking for updates...")
        try:
            api_url = "https://api.github.com/repos/bazthedev/SolsRNGBot/releases/latest"
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()
            release_data = response.json()
            latest_version_str = release_data.get("tag_name") or release_data.get("name") 
            if not latest_version_str:
                logger.write_log("Could not determine latest version from GitHub API response.")
            else:
                if latest_version_str.startswith('v'): 
                    latest_version_str = latest_version_str[1:]

                if parse_version(latest_version_str) > parse_version(LOCALVERSION):
                    logger.write_log(f"New version found: {latest_version_str}")
                    DOWNLOADS_DIR = Path.home() / "Downloads"
                    zip_filename = f"SolsRNGBot_{latest_version_str}.zip"
                    zip_filepath = DOWNLOADS_DIR / zip_filename
                    extract_dirname = f"SolsRNGBot_{latest_version_str}"
                    extract_path = DOWNLOADS_DIR / extract_dirname

                    do_install = settings.get("auto_install_update", False)
                    if not do_install:
                        do_install = messagebox.askyesno("Update Found", f"A new version ({latest_version_str}) is available. Download and extract to Downloads folder?")

                    if do_install:
                        logger.write_log(f"Downloading v{latest_version_str}...")

                        asset_url = None
                        for asset in release_data.get("assets", []):

                            asset_name = asset.get("name", "")
                            if asset_name.lower().endswith('.zip') and latest_version_str in asset_name:
                                asset_url = asset.get("browser_download_url")
                                break
                        if not asset_url:
                            logger.write_log(f"Error: Could not find download URL for '{latest_version_str}' zip in latest release.")
                            messagebox.showerror("Update Error", f"Could not find the download link for version {latest_version_str}.")
                        else:
                            try:

                                update_resp = requests.get(asset_url, timeout=120) 
                                update_resp.raise_for_status()
                                with open(zip_filepath, "wb") as p:
                                    p.write(update_resp.content)
                                logger.write_log(f"Downloaded v{latest_version_str} to {zip_filepath}")

                                logger.write_log(f"Extracting v{latest_version_str}...")
                                with zipfile.ZipFile(zip_filepath, "r") as newverzip:
                                    newverzip.extractall(extract_path)
                                logger.write_log(f"Extracted to {extract_path}")

                                os.remove(zip_filepath)
                                logger.write_log("Update complete. Please close this version and run the new one from your Downloads folder.")
                                messagebox.showinfo("Update Complete", f"Version {latest_version_str} downloaded and extracted to:\n{extract_path}\n\nPlease close this program and run the new version.")
                                return False 

                            except requests.RequestException as download_e:
                                logger.write_log(f"Error downloading update: {download_e}")
                                messagebox.showerror("Update Download Error", f"Failed to download the update: {download_e}")
                            except zipfile.BadZipFile:
                                logger.write_log("Error: Downloaded update file is not a valid zip.")
                                messagebox.showerror("Update Error", "Downloaded update file is corrupted.")
                            except OSError as install_e:
                                logger.write_log(f"Error extracting/saving update: {install_e}")
                                messagebox.showerror("Update Install Error", f"Failed to extract/save the update: {install_e}")
                            except Exception as install_e:
                                logger.write_log(f"Unexpected error installing update: {install_e}")
                                messagebox.showerror("Update Install Error", f"An unexpected error occurred during update: {install_e}")
                else:
                    logger.write_log("Macro is up to date.")

        except requests.RequestException as e:
            logger.write_log(f"Failed to check for updates (Network Error): {e}")
        except json.JSONDecodeError:
            logger.write_log("Failed to check for updates (Invalid response from GitHub API).")
        except Exception as e:
            logger.write_log(f"An unexpected error occurred during update check: {e}")

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
                logger.write_log(f"Screen coordinates calculated for {primary_monitor.width}x{primary_monitor.height} (Scale W:{COORDS['scale_w']:.2f}, H:{COORDS['scale_h']:.2f})")
            else:
                logger.write_log("Coordinate calculation failed. Using default coordinates.")

                messagebox.showerror("Coordinate Error", "Failed to calculate screen coordinates. Macro may not function correctly. Using defaults.")

                if 'scale_w' not in COORDS: COORDS['scale_w'] = 1.0
                if 'scale_h' not in COORDS: COORDS['scale_h'] = 1.0
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

    set_active_log_directory(use_ms_store_if_detected=not settings.get("use_roblox_player", True))

    logger.write_log("Initial setup complete.")
    return True 

if __name__ == '__main__':

    log_file = os.path.join(MACROPATH, "solsrngbot.log")
    pyqt_logger = PyQtLogger(log_file=log_file)
    set_global_logger(pyqt_logger) 
    logger = get_logger() 
    logger.write_log("Global logger set to PyQtLogger. Running initial setup...")

    if not run_initial_setup(logger):

        logger.write_log("Initial setup failed. Exiting.")
        sys.exit(0)

    logger.write_log("Initial setup complete. Initializing GUI...")

    try:
        app = QApplication(sys.argv)
        main_window = MainWindow() 

        if hasattr(main_window, 'log_widget') and hasattr(main_window, 'append_log_message'):
            logger.connect_log_widget(main_window.append_log_message)
        else:
            logger.write_log("Could not connect PyQtLogger signal to MainWindow log widget.")

        failsafe = None 

        main_window.show()
        logger.write_log("Starting PyQt event loop...")
        exit_code = app.exec()

        logger.write_log("--- SolsRNGBot Exiting --- ")
        sys.exit(exit_code)

    except Exception as e:

        logger = get_logger()

        logger.write_log(f"[CRITICAL] --- !!! UNHANDLED FATAL GUI ERROR: {e} !!! ---")
        import traceback
        logger.write_log(f"[CRITICAL] {traceback.format_exc()}")
        try:

            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Icon.Critical)
            msgBox.setWindowTitle("Fatal GUI Error")
            msgBox.setText(f"An unhandled error occurred:\n{e}\n\nPlease check the log file for details:\n{os.path.join(MACROPATH, 'solsrngbot.log')}")
            msgBox.exec()
        except Exception:
            print(f"FATAL ERROR: {e}\n{traceback.format_exc()}") 
        sys.exit(1)