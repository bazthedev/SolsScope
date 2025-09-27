"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v2.0.0
Support server: https://discord.gg/6cuCu6ymkX
"""

import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))
import json
from PyQt6.QtWidgets import QLabel, QLineEdit, QCheckBox, QMessageBox
from PyQt6.QtCore import Qt
from packaging.version import parse as parse_version
import re
import pyautogui
import time
import datetime
from roblox_utils import get_latest_hovertext, get_active_log_directory

class Plugin:
    DEFAULTSETTINGS = {
        "enabled": True,
        "clipping_keycombo" : "alt+right",
        "clipping_rarity" : 99999999,
        "output_folder" : os.path.join(os.path.expandvars(r"%localappdata%\SolsScope"), "plugins", "rec"),
        "wait_after_end" : 10
    }

    DISPLAYSETTINGS = ["enabled", "clipping_keycombo", "clipping_rarity", "output_folder", "wait_after_end"]

    TOOLTIPS = {
        "enabled" : "Enable the plugin.",
        "clipping_keycombo" : "The key combo to activate your clipping software's clip feature.",
        "clipping_rarity" : "The minimum rarity of the aura rolled for it to be clipped.",
        "output_folder" : "The folder that a GLITCHED/DREAMSPACE recording goes to.",
        "wait_after_end" : "How many seconds to wait after biome ends to stop recording."
    }
    
    def __init__(self, macro):
        self.name = "Clipping"
        self.version = "1.0.2"
        self.authors = ["bazthedev"]
        self.requires = "2.0.0"
        self.requirements = ["pygetwindow"]
        self.autocraft_compatible = True
        self.macro = macro
        
        self.MACROPATH = os.path.expandvars(r"%localappdata%\SolsScope")
        self.config_path = os.path.join(
            self.MACROPATH, "plugins", "config", f"{self.name}.json"
        )
        
        # Initialize plugin config (completely separate from main settings)
        self.config = self.load_or_create_config()
        self.entries = {}



        self.LOG_FILE_PATH = self.MACROPATH + "\\solsscope.log"
        self.AURA_REGEX = re.compile(r"\[\s*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*-\s*INFO\s*\]\s*New aura detected:\s*(?P<name>.+)")
        self.BIOME_REGEX = re.compile(
            r"\[\s*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*-\s*INFO\s*\]\s*Biome change detected:\s*(?P<old_biome>[\w\s]+?)\s*->\s*(?P<new_biome>[\w\s]+)"
        )

        self.recorder = None
        
        macro.logger.write_log(f"[{self.name}] Plugin initialized (v{self.version})")

    def load_or_create_config(self):
        """Load only plugin-specific config, completely separate from main settings"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        if not os.path.exists(self.config_path):
            with open(self.config_path, "w") as f:
                json.dump(self.DEFAULTSETTINGS, f, indent=4)
            return self.DEFAULTSETTINGS.copy()

        try:
            with open(self.config_path, "r") as f:
                loaded_config = json.load(f)
                
                # Merge with defaults to ensure new settings are added
                merged_config = self.DEFAULTSETTINGS.copy()
                merged_config.update(loaded_config)
                return merged_config
                
        except Exception as e:
            QMessageBox.critical(
                None,
                f"{self.name} Plugin Error",
                f"Failed to load config: {e}\nUsing default settings."
            )
            return self.DEFAULTSETTINGS.copy()

    def init_tab(self, gui_tools):
        """
        Initialize UI using only plugin's own config - don't touch main settings
        """
        QtWidgets = gui_tools["QtWidgets"]
        parent_layout = gui_tools["parent_layout"]
        create_widgets = gui_tools["create_widgets"]
        
        # Use only this plugin's config, not main settings
        settings_to_display = {
            key: self.config.get(key, self.DEFAULTSETTINGS.get(key))
            for key in self.DISPLAYSETTINGS
        }
        
        # Create widgets using plugin's isolated config
        create_widgets(settings_to_display, parent_layout, self.entries, self.TOOLTIPS)
        
        label_text = f"{self.name} v{self.version} by"
        for author in self.authors:
            if self.authors.index(author) == len(self.authors) - 1:
                label_text += f" {author}."
            else:
                label_text += f" {author},"

        info_label = QLabel(
            f"<i>{label_text}</i>"
        )   
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_layout.addWidget(info_label)

    def save_config(self):
        """Save only to plugin's own config file, don't touch main settings"""
        updated_values = self.get_updated_values()
        
        if not updated_values:
            return False
            
        try:
            # Merge updates with existing PLUGIN config only
            current_config = self.load_or_create_config()
            self.merge_dicts(current_config, updated_values)
            
            # Save only to plugin's config file
            with open(self.config_path, "w") as f:
                json.dump(current_config, f, indent=4)
                
            # Update in-memory PLUGIN config only
            self.config.update(current_config)
            
            self.macro.logger.write_log(f"[{self.name}] Plugin config saved to {self.config_path}")
            return True
            
        except Exception as e:
            self.macro.logger.write_log(
                f"[{self.name}] Failed to save plugin config: {e}", 
                level="ERROR"
            )
            QMessageBox.critical(
                self.macro,
                f"{self.name} Plugin Error",
                f"Failed to save plugin config:\n{e}"
            )
            return False

    def get_updated_values(self):
        """Get values only from plugin's UI widgets"""
        updated_values = {}
        
        for key, widget in self.entries.items():
            if isinstance(widget, QLineEdit):
                value = widget.text()
                default_type = type(self.DEFAULTSETTINGS.get(key, ""))
                try:
                    if default_type == int:
                        value = int(value) if value else 0
                    elif default_type == float:
                        value = float(value) if value else 0.0
                    elif default_type == bool:
                        value = value.lower() in ("true", "1", "yes")
                except ValueError:
                    value = str(value)
                updated_values[key] = value

            elif isinstance(widget, QCheckBox):
                updated_values[key] = widget.isChecked()

            elif isinstance(widget, dict) and "list_widget" in widget:
                list_widget = widget["list_widget"]
                updated_values[key] = [list_widget.item(i).text() for i in range(list_widget.count())]

        return updated_values

    def merge_dicts(self, original, updates):
        """Recursively merges dictionaries."""
        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(original.get(key), dict):
                self.merge_dicts(original[key], value)
            else:
                original[key] = value

    def parse_key_combo(self, combo_str):
        combos = []
        for line in combo_str.strip().splitlines():
            keys = [key.strip().lower() for key in line.split("+")]
            combos.append(keys)
        return combos

    def execute_key_combo(self, combo_list):
        with self.macro.keyboard_lock:
            for combo in combo_list:
                pyautogui.hotkey(*combo)
                time.sleep(0.1)

    def get_roblox_window_pos(self):
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle("Roblox")
        for win in windows:
            if win.width > 100 and win.height > 100:
                return (win.left, win.top, win.width, win.height)
        return None

    def run(self, stop_event, sniped_event, pause_event):
        """
        Main plugin logic that runs in a separate thread.
        
        Args:
            stop_event (threading.Event): Set when macro is stopping
            sniped_event (threading.Event): Set when a snipe occurs
            pause_event (threading.Event): Set when something wants to pause the macro
            
        Note:
            - This method should regularly check stop_event.is_set()
            - Use self.macro.logger for logging
            - Access settings through self.config
            - Use self.macro.keyboard_lock for thread-safe input
        """
        try:
            import pyscreenrec
            self.recorder = pyscreenrec.ScreenRecorder()
            os.makedirs(os.path.join(self.MACROPATH, "plugins", "rec"), exist_ok=True)
            self.macro.logger.write_log(f"[{self.name}] Plugin thread started.")
            
            if not self.config["enabled"]:
                self.macro.logger.write_log("Clipping Auras is disabled and was not started.")
                return
            combo_list = self.parse_key_combo(self.config["clipping_keycombo"])
            with open(f"{self.MACROPATH}\\auras_new.json", "r") as _a:
                auras = json.load(_a)

            with open(self.LOG_FILE_PATH, "r", encoding="utf-8") as f:
                f.seek(0, 2)

                while not stop_event.is_set():
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue

                    line = line.strip()

                    block = [line]
                    for _ in range(2):
                        next_line = f.readline()
                        while not next_line:
                            time.sleep(0.1)
                            next_line = f.readline()
                        block.append(next_line.strip())

                    block_text = "\n".join(block)

                    biome_match = self.BIOME_REGEX.search(block_text)
                    
                    if biome_match:
                        biome = biome_match.group("new_biome").upper().strip("\n")
                        if biome == "GLITCHED" or biome == "DREAMSPACE":
                            _time = datetime.datetime.now().strftime("%d,%m,%Y_%H,%M,%S")
                            pos = self.get_roblox_window_pos()
                            self.macro.logger.write_log(f"[{self.name}] Started recording biome ({biome} to folder {self.config['output_folder']} with file name {biome}_{_time}.mp4)")
                            try:
                                self.recorder.start_recording(f"{self.config['output_folder']}/{biome}_{_time}.mp4", fps=30, monitor={"mon" : 1, "left" : pos[0], "top" : pos[1], "width" : pos[2], "height" : pos[3]})
                                while not stop_event.is_set():
                                    _ = get_latest_hovertext()
                                    if not _:
                                        continue

                                    if _ is None:
                                        continue

                                    if _.upper() != biome:
                                        time.sleep(self.config["wait_after_end"])
                                        break
                                    time.sleep(0.1)
                            except Exception as e:
                                print(e)
                            finally:
                                self.recorder.stop_recording()
                                time.sleep(1)
                                self.macro.logger.write_log(f"[{self.name}] Stopped recording biome ({biome}).")
                            time.sleep(5)
                            continue
                    
                    match = self.AURA_REGEX.search(block_text)
                    if match:
                        aura_name = match.group("name")
                        aura_key = auras.get(aura_name.lower(), "Not found")
                        if aura_key == "Not found":
                            continue
                        rarity_val = aura_key.get("rarity")

                        if int(rarity_val) >= int(self.config["clipping_rarity"]):
                            time.sleep(5)
                            self.execute_key_combo(combo_list)
            self.macro.logger.write_log("Clipping was stopped.")
                
        except Exception as e:
            self.macro.logger.write_log(
                f"[{self.name}] Plugin error: {e}", 
                level="ERROR"
            )
        finally:
            self.macro.logger.write_log(f"[{self.name}] Plugin thread stopped.")

    def unload(self):
        """Called when plugin is being unloaded/reloaded."""
        self.macro.logger.write_log(f"[{self.name}] Plugin unloaded.")