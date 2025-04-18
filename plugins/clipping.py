import os
import json
from tkinter import messagebox
import tkinter as tk
import time
import pyautogui
import re

class Plugin:
    DEFAULTSETTINGS = {
        "enabled": True,
        "clipping_keycombo" : "alt+right",
        "clipping_rarity" : 0
    }

    DISPLAYSETTINGS = ["enabled", "clipping_keycombo", "clipping_rarity"]


    def __init__(self, macro):
        self.name = "Clipping"
        self.version = "1.0.0"
        self.author = "bazthedev"
        self.requires = "1.2.3"
        self.macro = macro
        self.config_path = os.path.join(os.path.expandvars(r"%localappdata%\Baz's Macro"), "plugins", "config", f"{self.name}.json")
        self.WEBHOOK_ICON_URL = "https://raw.githubusercontent.com/bazthedev/SolsRNGBot/a93aaa9a42a7184047f12aa4135f3dab0857f05d/Server%20Edition/whicon.png"
        self.config = self.load_or_create_config()
        self.MACROPATH = os.path.expandvars(r"%localappdata%\Baz's Macro")
        self.entries = {}

        self.LOG_FILE_PATH = self.MACROPATH + "/solsrngbot.log"
        self.AURA_REGEX = re.compile(r"Rolled Aura: (?P<name>.+?)\nWith chances of 1/(?P<rarity>\d+)\nAt time: (?P<timestamp>.+)")

        macro.logger.write_log(f"[{self.name}] Plugin initialized.")

    def load_or_create_config(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        if not os.path.exists(self.config_path):
            with open(self.config_path, "w") as f:
                json.dump(self.DEFAULTSETTINGS, f, indent=4)

        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Baz's Macro", f"[{self.name}] Failed to load config: {e}")
            return self.DEFAULTSETTINGS.copy()

    def init_tab(self, tab_frame, gui):
        create_widgets = gui["create_widgets"]
        create_bottom_buttons = gui["create_bottom_buttons"]
        format_key = gui["format_key"]
        entries = gui["entries"]

        settings_to_display = {key: self.config.get(key) for key in self.DISPLAYSETTINGS}

        create_widgets(settings_to_display, tab_frame, entries)

        create_bottom_buttons(tab_frame)

    def save_config(self):
        updated_values = self.get_updated_values()

        if not updated_values:
            return

        try:
            with open(self.config_path, "r") as f:
                current_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            current_config = {}

        self.merge_dicts(current_config, updated_values)

        try:
            with open(self.config_path, "w") as f:
                json.dump(current_config, f, indent=4)
            self.macro.logger.write_log(f"[{self.name}] Plugin config saved.")
            
            self.macro.reload_plugin_config(self)

        except Exception as e:
            self.macro.logger.write_log(f"[{self.name}] Failed to save config: {e}")
            messagebox.showerror("Baz's Macro", f"[{self.name}] Failed to save config: {e}")


    def get_updated_values(self):
        updated_values = {}
        for key, entry_var in self.entries.items():
            if isinstance(entry_var, tk.StringVar):
                updated_values[key] = entry_var.get()
            elif isinstance(entry_var, tk.BooleanVar):
                updated_values[key] = entry_var.get()
        return updated_values

    def merge_dicts(self, original, updates):
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

    def run(self, stop_event, pause_event):
        if not self.config["enabled"]:
            self.macro.logger.write_log("Clipping Auras is disabled and was not started.")
            return
        combo_list = self.parse_key_combo(self.config["clipping_keycombo"])

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
                        rarity_val = int(match.group("rarity"))
                        timestamp = match.group("timestamp")

                        if rarity_val >= int(self.config["clipping_rarity"]):
                            time.sleep(5)
                            self.execute_key_combo(combo_list)
        self.macro.logger.write_log("Clipping was stopped.")
