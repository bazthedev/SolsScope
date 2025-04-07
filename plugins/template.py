import os
import json
from tkinter import messagebox
import tkinter as tk

class Plugin:
    DEFAULTSETTINGS = {
        "enabled": True,
        "config1" : "Example",
        "config2" : 1
    }

    DISPLAYSETTINGS = ["enabled", "config1", "config2"]

    def __init__(self, macro):
        self.name = "Template"
        self.version = "1.0.0"
        self.author = "bazthedev"
        self.macro = macro
        self.config_path = os.path.join(os.path.expandvars(r"%localappdata%\Baz's Macro"), "plugins", "config", f"{self.name}.json")

        self.config = self.load_or_create_config()

        self.entries = {}
        macro.logger.write_log(f"[{self.name}] Plugin initialized with config: {self.config}")

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

    def run(self, stop_event, pause_event):
        pass # logic for the program to run
