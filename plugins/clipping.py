"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v1.2.5
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

class Plugin:
    DEFAULTSETTINGS = {
        "enabled": True,
        "clipping_keycombo" : "alt+right",
        "clipping_rarity" : 99999999
    }

    DISPLAYSETTINGS = ["enabled", "clipping_keycombo", "clipping_rarity"]
    
    def __init__(self, macro):
        self.name = "Clipping"
        self.version = "1.0.1"
        self.author = "bazthedev"
        self.requires = "1.2.5"
        self.autocraft_compatible = False
        self.macro = macro
        
        self.MACROPATH = os.path.expandvars(r"%localappdata%\SolsScope")
        self.config_path = os.path.join(
            self.MACROPATH, "plugins", "config", f"{self.name}.json"
        )
        
        # Initialize plugin config (completely separate from main settings)
        self.config = self.load_or_create_config()
        self.entries = {}

        self.LOG_FILE_PATH = self.MACROPATH + "\\solsscope.log"
        self.AURA_REGEX = re.compile(r"\[(?P<timestamp>[\d\-:\s]+)\s-\sINFO\] New aura detected: (?P<name>.+)")
        
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
        create_widgets(settings_to_display, parent_layout, self.entries)
        
        info_label = QLabel(
            f"<i>{self.name} v{self.version} by {self.author}</i>"
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

    def run(self, stop_event, sniped_event):
        """
        Main plugin logic that runs in a separate thread.
        
        Args:
            stop_event (threading.Event): Set when macro is stopping
            sniped_event (threading.Event): Set when a snipe occurs
            
        Note:
            - This method should regularly check stop_event.is_set()
            - Use self.macro.logger for logging
            - Access settings through self.config
            - Use self.macro.keyboard_lock for thread-safe input
        """
        try:
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

                    if "GLITCHED has started" in line or "DREAMSPACE has started" in line:
                        time.sleep(5)
                        self.execute_key_combo(combo_list)
                        continue

                    if "Rolled Aura:" in line:
                        block = [line]
                        for _ in range(2):
                            next_line = f.readline()
                            while not next_line:
                                time.sleep(0.1)
                                next_line = f.readline()
                            block.append(next_line.strip())

                        block_text = "\n".join(block)
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
