import tkinter as tk
from tkinter import messagebox
import customtkinter
import threading
import time
import json
import os
import glob
import importlib.util
import shutil
import webbrowser 
import random 
import asyncio 

customtkinter.set_appearance_mode("Dark")  
customtkinter.set_default_color_theme("blue")  

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    import cv2 
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

from pynput import keyboard, mouse
import mousekey as mk

import discord

from constants import (
    MACROPATH, LOCALVERSION, WEBHOOK_ICON_URL, STARTUP_MSGS,
    GENERAL_KEYS, AURAS_KEYS, BIOMES_KEYS, MERCHANT_KEYS,
    AUTOCRAFT_KEYS, SNIPER_KEYS, OTHER_KEYS, COORDS, DEFAULTSETTINGS 
)
from utils import (
    get_logger, set_global_logger, Logger, format_key, rgb2hex, hex2rgb, 
    create_discord_file_from_path, left_click_drag, right_click_drag, validate_pslink 
)
from settings_manager import (
    load_settings, update_settings, get_settings_path, get_auras_path, get_biomes_path,
    validate_settings 
)
from roblox_utils import (
    set_active_log_directory, get_active_log_directory, exists_procs_by_name,
    get_latest_equipped_aura, get_latest_hovertext 
)
from discord_utils import forward_webhook_msg, start_snipers, stop_snipers 

from macro_logic import (
    aura_detection, biome_detection, keep_alive, merchant_detection, auto_craft,
    auto_br, auto_sc, inventory_screenshot, storage_screenshot, disconnect_prevention,
    do_obby, auto_pop, use_item 
)

class Macro:
    def __init__(self, root: customtkinter.CTk):
        self.root = root
        self.root.title(f"Baz's Macro v{LOCALVERSION}")
        self.root.geometry("700x500") 

        self.settings = load_settings() 
        self.original_settings = self.settings.copy() 
        self.logger = get_logger() 
        set_global_logger(self.logger) 

        self.webhook = None 
        self.threads = []
        self.sniper_task = None 
        self.running = False
        self.keyboard_lock = threading.Lock()
        self.stop_event = threading.Event() 
        self.sniped_event = threading.Event() 

        self.mkey = mk.MouseKey()
        self.keyboard = keyboard.Controller()
        self.mouse = mouse.Controller()

        if self.settings.get("always_on_top", False):
            self.root.lift()
            self.root.attributes("-topmost", True)

        try:
            icon_path = os.path.join(MACROPATH, "icon.ico")
            if os.path.exists(icon_path):

                self.root.iconbitmap(icon_path)
        except Exception as e:
            self.logger.write_log(f"Error setting window icon: {e}")

        self.notebook = customtkinter.CTkTabview(self.root, width=250, fg_color="transparent") 
        self.notebook.pack(expand=1, fill='both', padx=5, pady=5)

        self.tab_entries = {}

        tab_info = {
            "General": GENERAL_KEYS,
            "Auras": AURAS_KEYS,
            "Biomes": BIOMES_KEYS,
            "Merchant": MERCHANT_KEYS,
            "Auto Craft": AUTOCRAFT_KEYS,
            "Sniper": SNIPER_KEYS,
            "Other": OTHER_KEYS,
        }
        for tab_name, keys in tab_info.items():

            self.notebook.add(tab_name)
            tab_frame = self.notebook.tab(tab_name) 

            self.tab_entries[tab_name] = {}

            scrollable_frame = customtkinter.CTkScrollableFrame(tab_frame, fg_color="transparent")
            scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
            self.populate_tab(scrollable_frame, keys, self.tab_entries[tab_name]) 

            if tab_name == "Merchant":
                self.add_merchant_tab_extras(scrollable_frame) 
            if tab_name == "Other":
                self.add_other_tab_extras(scrollable_frame) 

        self.notebook.add("Logs")
        logs_frame = self.notebook.tab("Logs") 
        log_container = customtkinter.CTkFrame(logs_frame) 
        log_container.pack(fill='both', expand=True, padx=5, pady=5)

        self.log_widget = customtkinter.CTkTextbox(log_container, state='disabled', height=10, wrap=tk.WORD) 

        self.log_widget.pack(fill='both', expand=True)

        self.logger.text_widget = self.log_widget

        self.logger.write_log("GUI Logger initialized (CTkTextbox).")

        self.notebook.add("Credits")
        credits_frame = self.notebook.tab("Credits") 

        self.populate_credits_tab(credits_frame)

        self.plugins = []
        self.load_plugins() 

        self.start_key_listener()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close) 
        self.logger.write_log("GUI setup complete.")

        all_tab_names = list(tab_info.keys()) + ["Logs", "Credits"] 

        for tab_name in all_tab_names:
             tab_frame = self.notebook.tab(tab_name)
             self.create_bottom_buttons(tab_frame) 

    def populate_tab(self, frame, keys, entry_dict):
        "Populates a tab's scrollable frame with widgets based on settings keys."

        settings_subset = {k: self.settings.get(k, DEFAULTSETTINGS.get(k)) for k in keys}
        self.create_widgets(settings_subset, frame, entry_dict)

    def create_widgets(self, settings_subset, parent, entry_dict):
        "Recursively creates customtkinter widgets for settings items."
        for key, value in settings_subset.items():
            if key == "__version__": continue 

            formatted_key = format_key(key) 

            row_frame = customtkinter.CTkFrame(parent, fg_color="transparent") 
            row_frame.pack(fill=tk.X, pady=2, padx=5)

            label = customtkinter.CTkLabel(row_frame, text=formatted_key + ":", width=25, anchor="w") 
            label.pack(side=tk.LEFT, padx=(0, 5))

            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)

                checkbox = customtkinter.CTkCheckBox(row_frame, variable=var, text="")
                checkbox.pack(side=tk.LEFT)
                entry_dict[key] = var
            elif isinstance(value, dict):

                label_frame_container = customtkinter.CTkFrame(parent, fg_color="transparent") 
                label_frame_container.pack(fill=tk.X, padx=10, pady=5, expand=True)
                label = customtkinter.CTkLabel(label_frame_container, text=formatted_key, font=customtkinter.CTkFont(weight="bold"))
                label.pack(anchor="w", padx=5)

                subframe = customtkinter.CTkFrame(label_frame_container, border_width=1)
                subframe.pack(fill=tk.X, expand=True, padx=5, pady=(0,5))
                entry_dict[key] = {} 
                self.create_widgets(value, subframe, entry_dict[key])
            elif isinstance(value, list):

                self.create_list_widget(row_frame, key, value, entry_dict)
            else: 
                var = tk.StringVar(value=str(value))
                entry = customtkinter.CTkEntry(row_frame, textvariable=var) 

                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
                entry_dict[key] = var

    def create_list_widget(self, parent, key, items, entry_dict):
        "Creates a Listbox-like widget using CTkScrollableFrame, CTkButtons, Add/Remove CTkButtons."

        list_container_frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        list_container_frame.pack(fill=tk.X, expand=True, pady=(0,5)) 

        display_frame = customtkinter.CTkFrame(list_container_frame, fg_color="transparent")
        display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))

        list_scrollable_frame = customtkinter.CTkScrollableFrame(display_frame, label_text=f"Items for {format_key(key)}", fg_color="transparent")
        list_scrollable_frame.pack(fill=tk.BOTH, expand=True)

        button_frame = customtkinter.CTkFrame(list_container_frame, fg_color="transparent")
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

        add_entry = customtkinter.CTkEntry(button_frame, placeholder_text="New item...")
        add_entry.pack(pady=5, padx=5, fill=tk.X)

        add_button = customtkinter.CTkButton(button_frame, text="Add", width=80, 
                                command=lambda k=key, e=add_entry, sf=list_scrollable_frame: self.add_to_list(k, e, sf))
        add_button.pack(pady=5, padx=5)

        remove_button = customtkinter.CTkButton(button_frame, text="Remove Sel.", width=80, 
                                   command=lambda k=key, sf=list_scrollable_frame: self.remove_from_list(k, sf))
        remove_button.pack(pady=5, padx=5)

        entry_dict[key] = {
            "items": list(items),
            "item_widgets": {}, 
            "scroll_frame": list_scrollable_frame,
            "selected_widget": None 
        }

        self._populate_list_scrollframe(key, list_scrollable_frame)

    def _select_list_item(self, key, item_value, widget):
        "Handles selection visual and state for list items."

        list_data = None
        for tab_data in self.tab_entries.values():
            if key in tab_data and isinstance(tab_data[key], dict) and "item_widgets" in tab_data[key]:
                list_data = tab_data[key]
                break
        if not list_data: return

        if list_data["selected_widget"] and list_data["selected_widget"] != widget:
            try:

                list_data["selected_widget"].configure(fg_color=customtkinter.ThemeManager.theme["CTkButton"]["fg_color"])
            except Exception: pass 

        try:
            widget.configure(fg_color=customtkinter.ThemeManager.theme["CTkButton"]["hover_color"]) 
            list_data["selected_widget"] = widget
        except Exception:
             list_data["selected_widget"] = None 

    def _populate_list_scrollframe(self, key, scrollable_frame):
        "Adds item widgets to the scrollable frame based on the current item list."

        list_data = None
        for tab_data in self.tab_entries.values():
            if key in tab_data and isinstance(tab_data[key], dict) and "item_widgets" in tab_data[key]:
                list_data = tab_data[key]
                break
        if not list_data: return

        for widget in list_data["item_widgets"].values():
            widget.destroy()
        list_data["item_widgets"].clear()
        list_data["selected_widget"] = None

        for item in list_data["items"]:
            item_widget = customtkinter.CTkButton(
                scrollable_frame,
                text=item,
                fg_color="transparent", 
                border_width=1,
                text_color=("gray10", "gray90"), 
                anchor="w"
            )

            item_widget.configure(command=lambda k=key, val=item, w=item_widget: self._select_list_item(k, val, w))
            item_widget.pack(fill=tk.X, pady=2, padx=2)
            list_data["item_widgets"][item] = item_widget

    def add_to_list(self, key, entry_widget, scrollable_frame):
        new_item = entry_widget.get().strip()
        if not new_item: return

        list_data = None
        for tab_data in self.tab_entries.values():
            if key in tab_data and isinstance(tab_data[key], dict) and "items" in tab_data[key]:
                list_data = tab_data[key]
                break

        if list_data:
            item_list = list_data["items"]
            if new_item not in item_list:
                item_list.append(new_item)

                item_widget = customtkinter.CTkButton(
                    scrollable_frame,
                    text=new_item,
                    fg_color="transparent",
                    border_width=1,
                    text_color=("gray10", "gray90"),
                    anchor="w"
                )
                item_widget.configure(command=lambda k=key, val=new_item, w=item_widget: self._select_list_item(k, val, w))
                item_widget.pack(fill=tk.X, pady=2, padx=2)
                list_data["item_widgets"][new_item] = item_widget
                entry_widget.delete(0, tk.END)
            else:
                messagebox.showwarning("Duplicate Item", f"'{new_item}' is already in the list.")
        else:
            self.logger.write_log(f"Error adding to list: Could not find list data for key '{key}'.")

    def remove_from_list(self, key, scrollable_frame):
        list_data = None
        for tab_data in self.tab_entries.values():
            if key in tab_data and isinstance(tab_data[key], dict) and "items" in tab_data[key]:
                list_data = tab_data[key]
                break

        if list_data:
            if list_data["selected_widget"]:
                selected_widget = list_data["selected_widget"]
                item_to_remove = selected_widget.cget("text")

                if item_to_remove in list_data["items"]:
                    list_data["items"].remove(item_to_remove)

                if item_to_remove in list_data["item_widgets"]:
                    del list_data["item_widgets"][item_to_remove]
                selected_widget.destroy()
                list_data["selected_widget"] = None

            else:
                messagebox.showwarning("No Selection", "Please select an item from the list to remove.")
        else:
            self.logger.write_log(f"Error removing from list: Could not find list data for key '{key}'.")

    def add_merchant_tab_extras(self, parent_frame):
        "Adds Tesseract status and download button to the Merchant tab using CTk widgets."
        tesseract_installed = TESSERACT_AVAILABLE 
        status_text = "Tesseract OCR: Installed" if tesseract_installed else "Tesseract OCR: Not Installed (Merchant Detection Disabled)"
        status_color = "green" if tesseract_installed else "red"

        ocr_label = customtkinter.CTkLabel(parent_frame, text=status_text, text_color=status_color)
        ocr_label.pack(pady=(10, 2), anchor="w", padx=5)

        if not tesseract_installed:

            download_button = customtkinter.CTkButton(parent_frame, text="Download Tesseract (External Link)",
                                         command=lambda: webbrowser.open("https://github.com/tesseract-ocr/tesseract#installing-tesseract"))
            download_button.pack(pady=2, anchor="w", padx=5)

    def add_other_tab_extras(self, parent_frame):
         "Adds Plugin install button to the Other tab using CTkButton."
         install_btn = customtkinter.CTkButton(parent_frame, text="Install Plugin...", command=self.install_plugin)
         install_btn.pack(pady=10, anchor="w", padx=5)

    def populate_credits_tab(self, frame):
        "Populates the Credits tab with information using CTk widgets."

        customtkinter.CTkLabel(frame, text="Created by Baz", font=customtkinter.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))

        if PIL_AVAILABLE:
            try:
                image_path = os.path.join(MACROPATH, "baz.png")

                import requests 
                if not os.path.exists(image_path):
                     img_dl = requests.get("https://raw.githubusercontent.com/bazthedev/SolsRNGBot/main/img/baz.png", timeout=10)
                     img_dl.raise_for_status()
                     with open(image_path, "wb") as f:
                         f.write(img_dl.content)

                img = Image.open(image_path)

                img_ctk = customtkinter.CTkImage(light_image=img, dark_image=img, size=(100, 100))

                image_label = customtkinter.CTkLabel(frame, image=img_ctk, text="")

                image_label.pack(pady=10)
            except Exception as e:
                self.logger.write_log(f"Failed to load/display credits image: {e}")

        else:
            customtkinter.CTkLabel(frame, text="(Install Pillow to see images)").pack()

        customtkinter.CTkFrame(frame, height=1, fg_color="gray50").pack(fill='x', pady=10, padx=20)

        customtkinter.CTkLabel(frame, text="Acknowledgements:", font=customtkinter.CTkFont(size=12, weight="bold")).pack(pady=(0, 5))
        customtkinter.CTkLabel(frame, text="Root1527 for the original YAY Joins Sniper logic").pack(pady=2, anchor='w', padx=20)
        customtkinter.CTkLabel(frame, text="Mountain Shrine Path inspiration by AllanQute (_justalin)").pack(pady=2, anchor='w', padx=20)
        customtkinter.CTkLabel(frame, text="dolphSol for inspiration").pack(pady=2, anchor='w', padx=20)
        customtkinter.CTkLabel(frame, text="vex (vexthecoder) for ideas").pack(pady=2, anchor='w', padx=20)

    def create_bottom_buttons(self, parent_frame):
        "Creates the Start/Stop/Save CTkButtons at the bottom of a tab's main frame."

        button_frame = customtkinter.CTkFrame(parent_frame, fg_color="transparent")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 5), padx=10) 

        start_button = customtkinter.CTkButton(button_frame, text="Start (F1)", command=self.start_macro)
        start_button.pack(side=tk.LEFT, padx=5)

        stop_button = customtkinter.CTkButton(button_frame, text="Stop (F2)", command=self.stop_macro)
        stop_button.pack(side=tk.LEFT, padx=5)

        save_button = customtkinter.CTkButton(button_frame, text="Save Settings", command=self.save_settings)
        save_button.pack(side=tk.RIGHT, padx=5)

    def get_updated_values(self, original_settings_subset, entries_subset):
        "Compares current widget values (Vars or CTk list data) to original values."
        updated_subset = {}
        for key, widget_or_dict in entries_subset.items():
            original_value = original_settings_subset.get(key) 

            if isinstance(widget_or_dict, dict) and "items" in widget_or_dict and "item_widgets" in widget_or_dict:
                new_value = widget_or_dict["items"]

                if isinstance(original_value, list) and sorted(new_value) != sorted(original_value):
                    updated_subset[key] = new_value
                elif not isinstance(original_value, list): 
                     self.logger.write_log(f"Warning: Type mismatch for list setting '{key}' during update check (original type: {type(original_value)}).")
                     updated_subset[key] = new_value 

            elif isinstance(original_value, dict):

                 if isinstance(widget_or_dict, dict):
                    sub_updates = self.get_updated_values(original_value, widget_or_dict)
                    if sub_updates: 
                        updated_subset[key] = sub_updates
                 else:
                    self.logger.write_log(f"Warning: Mismatched type for dict setting '{key}' during update check.")

            else: 
                try:
                    if isinstance(widget_or_dict, tk.Variable):
                        new_value = widget_or_dict.get()
                    else:

                        self.logger.write_log(f"Warning: Unexpected widget type for '{key}' ({type(widget_or_dict)}).")
                        continue
                except tk.TclError as e:
                    self.logger.write_log(f"Error getting value from widget variable for '{key}': {e}")
                    continue 

                if original_value is None: 
                    if new_value != "": 
                        updated_subset[key] = new_value
                elif isinstance(original_value, bool):

                    new_value = bool(new_value)
                elif isinstance(original_value, int):
                    try: new_value = int(new_value)
                    except (ValueError, TypeError): pass 
                elif isinstance(original_value, float):
                    try: new_value = float(new_value)
                    except (ValueError, TypeError): pass

                try:
                    if new_value != original_value:
                        updated_subset[key] = new_value
                except TypeError:

                    if str(new_value) != str(original_value):
                        updated_subset[key] = new_value

        return updated_subset

    def save_settings(self):
        "Gathers updated values from all tabs and saves them to settings.json."
        self.logger.write_log("Gathering settings from UI (CTk)...")
        full_updated_values = {}

        for tab_name, tab_entries_dict in self.tab_entries.items():

            tab_info = {
                "General": GENERAL_KEYS, "Auras": AURAS_KEYS, "Biomes": BIOMES_KEYS,
                "Merchant": MERCHANT_KEYS, "Auto Craft": AUTOCRAFT_KEYS,
                "Sniper": SNIPER_KEYS, "Other": OTHER_KEYS
            }

            original_subset = {}
            if tab_name in tab_info:
                tab_keys = tab_info[tab_name]

                original_subset = {k: self.original_settings.get(k, DEFAULTSETTINGS.get(k)) for k in tab_keys}
            elif any(p.name == tab_name for p in self.plugins if hasattr(p, 'name')):

                plugin = next((p for p in self.plugins if p.name == tab_name), None)
                if plugin and hasattr(plugin, 'config'):
                     original_subset = plugin.config 
                else:
                     self.logger.write_log(f"Skipping settings save for plugin tab '{tab_name}': No config found.")
                     continue 
            else:
                 self.logger.write_log(f"Skipping settings save for unknown tab '{tab_name}'.")
                 continue 

            updated_subset = self.get_updated_values(original_subset, tab_entries_dict)
            full_updated_values.update(updated_subset)

        if not full_updated_values:
            self.logger.write_log("No setting changes detected.")
            messagebox.showinfo("Save Settings", "No changes to save.")
            return False

        self.logger.write_log(f"Detected changes: {list(full_updated_values.keys())}")

        current_file_settings = load_settings()

        def merge_dicts(target, updates):
            for key, value in updates.items():

                target_value = target.get(key)
                if isinstance(value, dict) and isinstance(target_value, dict):

                    merge_dicts(target_value, value)
                else:

                    target[key] = value

        merge_dicts(current_file_settings, full_updated_values)

        validated_settings, validation_errors = validate_settings(current_file_settings)
        if validation_errors:

             self.logger.write_log(f"Settings validation issues found: {validation_errors}")

        if update_settings(validated_settings):
            self.logger.write_log("Settings saved successfully.")
            messagebox.showinfo("Save Settings", "Settings saved successfully!")

            self.settings = validated_settings
            self.original_settings = self.settings.copy()

            for tab_name, updated_subset in full_updated_values.items():
                 plugin = next((p for p in self.plugins if hasattr(p, 'name') and p.name == tab_name), None)
                 if plugin and hasattr(plugin, 'config'):

                     if hasattr(plugin, 'update_config'):
                        plugin.update_config(validated_settings)

            return True
        else:
            self.logger.write_log("Failed to save settings to file.")
            messagebox.showerror("Save Settings Error", "Failed to save settings. Check logs.")
            return False

    def start_macro(self):
        if self.running:
            messagebox.showwarning("Macro Running", "Macro is already running!")
            return

        if not self.save_settings():

            if not messagebox.askyesno("Save Failed", "Failed to save settings. Continue starting the macro with potentially unsaved changes?"):
                self.logger.write_log("Macro start cancelled due to failed save.")
                return

            self.settings = load_settings()

        if not self.settings.get("WEBHOOK_URL") or not self.settings["WEBHOOK_URL"]:
            messagebox.showerror("Missing Webhook", "Please provide a primary Webhook URL in the General tab.")
            self.logger.write_log("Macro start failed: Missing Webhook URL.")
            return
        try:
            self.webhook = discord.Webhook.from_url(self.settings["WEBHOOK_URL"], adapter=discord.RequestsWebhookAdapter())
        except Exception as e:
            messagebox.showerror("Invalid Webhook", f"The primary Webhook URL is invalid:\n{e}")
            self.logger.write_log(f"Macro start failed: Invalid Webhook URL ({e}).")
            return

        if self.settings.get("sniper_enabled") and len(self.settings.get("scan_channels", [])) > 5:
            if not messagebox.askyesno("Sniper Channel Warning", "Sniping many channels (>5) can increase ratelimits. Continue anyway?"):
                self.logger.write_log("Macro start cancelled: Too many sniper channels.")
                return

        use_player = self.settings.get("use_roblox_player", True)
        set_active_log_directory(force_player=use_player)
        if not exists_procs_by_name("Windows10Universal.exe") and not exists_procs_by_name("RobloxPlayerBeta.exe"):
            if not messagebox.askyesno("Roblox Not Detected", "Roblox process not found. Start macro anyway?"):
                self.logger.write_log("Macro start cancelled: Roblox not running.")
                return

        self.running = True
        self.stop_event.clear()
        self.sniped_event.clear()
        self.threads = [] 
        self.logger.write_log("Starting Macro Threads...")

        is_autocraft_mode = self.settings.get("auto_craft_mode", False)

        MERCHANT_DETECTION_POSSIBLE = TESSERACT_AVAILABLE

        if is_autocraft_mode:
            self.logger.write_log("Starting in Auto Craft Mode.")

            enabled_crafts = [item for item, enabled in self.settings.get("auto_craft_item", {}).items() if enabled]
            if not enabled_crafts:
                messagebox.showerror("Auto Craft Error", "Auto Craft mode is enabled, but no potions are selected to craft.")
                self.logger.write_log("Auto Craft start failed: No items selected.")
                self.running = False
                return
            if not self.settings.get("skip_auto_mode_warning"):
                messagebox.showwarning("Auto Craft Mode", "Auto Craft mode is ON. Some features will be disabled. Ensure you are near the cauldron.")

            thread_targets = {
                "Auto Craft Logic": (auto_craft, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard, self.mouse]),
                "Aura Detection": (aura_detection, [self.settings, self.webhook, self.stop_event, self.keyboard_lock, self.mkey, self.keyboard]) if not self.settings.get("disable_aura_detection") else None,
                "Biome Detection": (biome_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event]) if not self.settings.get("disable_biome_detection") else None,

            }
        else: 
            self.logger.write_log("Starting in Normal Mode.")
            thread_targets = {
                "Aura Detection": (aura_detection, [self.settings, self.webhook, self.stop_event, self.keyboard_lock, self.mkey, self.keyboard]) if not self.settings.get("disable_aura_detection") else None,
                "Biome Detection": (biome_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event]) if not self.settings.get("disable_biome_detection") else None,
                "Keep Alive": (keep_alive, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey]) if not self.settings.get("disable_autokick_prevention") else None,
                "Disconnect Prevention": (disconnect_prevention, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard]) if self.settings.get("disconnect_prevention") else None,
                "Merchant Detection": (merchant_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard]) if self.settings.get("merchant_detection") and MERCHANT_DETECTION_POSSIBLE else None,
                "Auto Biome Randomizer": (auto_br, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard]) if self.settings.get("auto_biome_randomizer") else None,
                "Auto Strange Controller": (auto_sc, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard]) if self.settings.get("auto_strange_controller") else None,
                "Inventory Screenshots": (inventory_screenshot, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey]) if self.settings.get("periodic_screenshots", {}).get("inventory") else None,
                "Storage Screenshots": (storage_screenshot, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey]) if self.settings.get("periodic_screenshots", {}).get("storage") else None,
                "Obby": (do_obby, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard, self.mouse]) if self.settings.get("do_obby") else None,

            }

        for name, target_info in thread_targets.items():
            if target_info:
                func, args = target_info
                try:
                    thread = threading.Thread(target=func, args=args, daemon=True, name=name) 
                    thread.start()
                    self.threads.append(thread)
                    self.logger.write_log(f" > Started thread: {name}")
                except Exception as e:
                    self.logger.write_log(f" > Error starting thread {name}: {e}")

        if self.settings.get("sniper_enabled"):
            self.logger.write_log("Starting Sniper...")

            def run_sniper_loop():
                try:

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(start_snipers(self.settings, self.webhook, self.sniped_event, self.stop_event))
                    loop.close()
                except Exception as e:
                    self.logger.write_log(f"Error in sniper asyncio loop: {e}")
                self.logger.write_log("Sniper asyncio loop finished.")
            sniper_thread = threading.Thread(target=run_sniper_loop, daemon=True, name="SniperLoop")
            sniper_thread.start()
            self.threads.append(sniper_thread) 

        for plugin in self.plugins:
            try:

                can_run = True
                if is_autocraft_mode and not getattr(plugin, "autocraft_compatible", False):
                    can_run = False
                    self.logger.write_log(f"Skipping plugin {plugin.name}: Not compatible with Auto Craft mode.")

                if can_run and hasattr(plugin, "run"):

                    plugin_name = getattr(plugin, "name", "UnknownPlugin")
                    thread = threading.Thread(target=plugin.run, args=(self.stop_event, self.sniped_event), daemon=True, name=f"Plugin_{plugin_name}")
                    thread.start()
                    self.threads.append(thread)
                    self.logger.write_log(f" > Started plugin thread: {plugin.name}")
            except Exception as e:
                self.logger.write_log(f"Error starting plugin thread '{getattr(plugin, "name", "UnknownPlugin")}': {e}")

        self.logger.write_log("Macro started successfully.")
        mode_str = "Auto Craft" if is_autocraft_mode else "Normal"
        start_desc = f"**Mode:** {mode_str}\n"
        if is_autocraft_mode:
            enabled_crafts = [item for item, enabled in self.settings.get("auto_craft_item", {}).items() if enabled]
            start_desc += f"**Crafting:** {', '.join(enabled_crafts)}\n"
        else:
            try:
                start_desc += f"**Current Aura:** {get_latest_equipped_aura()}\n"
                start_desc += f"**Current Biome:** {get_latest_hovertext()}\n"
            except Exception as e:
                self.logger.write_log(f"Error getting initial aura/biome for start msg: {e}")

        from datetime import datetime 
        start_desc += f"**Started at:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        emb = discord.Embed(
            title="Macro Started",
            description=start_desc,
            colour=discord.Colour.green()
        )
        emb.set_footer(text=f"bazthedev/SolsRNGBot v{LOCALVERSION}")
        try:
            self.webhook.send(avatar_url=WEBHOOK_ICON_URL, embed=emb)
            forward_webhook_msg(self.webhook.url, self.settings.get("SECONDARY_WEBHOOK_URLS", []), embed=emb, avatar_url=WEBHOOK_ICON_URL)
        except Exception as e:
            self.logger.write_log(f"Error sending start notification: {e}")

    def stop_macro(self):
        if not self.running:
            messagebox.showwarning("Macro Not Running", "Macro is not currently running.")
            return

        self.logger.write_log("Stopping Macro... Signaling threads.")
        self.stop_event.set() 

        def run_stop_sniper():
            try:

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(stop_snipers())
                loop.close()
            except Exception as e:
                 self.logger.write_log(f"Error stopping sniper tasks: {e}")

        stop_sniper_thread = threading.Thread(target=run_stop_sniper, daemon=True, name="StopSniper")
        stop_sniper_thread.start()

        timeout_per_thread = 2 
        start_time = time.time()
        main_thread = threading.current_thread()

        threads_to_join = [t for t in self.threads if t != main_thread and t.is_alive()]
        self.logger.write_log(f"Waiting for {len(threads_to_join)} threads to stop...")

        for thread in threads_to_join:
            time_left = max(0.1, start_time + timeout_per_thread * len(threads_to_join) - time.time())
            thread.join(timeout=time_left)
            if thread.is_alive():
                self.logger.write_log(f"Warning: Thread {thread.name} did not stop gracefully within timeout.")

        if stop_sniper_thread.is_alive():
             stop_sniper_thread.join(timeout=2) 
             if stop_sniper_thread.is_alive():
                   self.logger.write_log(f"Warning: StopSniper thread did not finish.")

        self.logger.write_log("All threads signaled to stop. Macro execution finished.")
        self.running = False
        self.threads.clear()

        from datetime import datetime 
        emb = discord.Embed(
            title="Macro Stopped",
            colour=discord.Colour.red(),
            timestamp=datetime.now()
        )
        emb.set_footer(text=f"SolsRNGBot v{LOCALVERSION}")
        if self.webhook:
            try:
                self.webhook.send(avatar_url=WEBHOOK_ICON_URL, embed=emb)
                forward_webhook_msg(self.webhook.url, self.settings.get("SECONDARY_WEBHOOK_URLS", []), embed=emb, avatar_url=WEBHOOK_ICON_URL)
            except Exception as e:
                self.logger.write_log(f"Error sending stop notification: {e}")
        messagebox.showinfo("Macro Stopped", "Macro has been stopped.")

    def on_press(self, key):
        try:

            if key == keyboard.Key.f1:

                self.root.after(0, self.start_macro)
            elif key == keyboard.Key.f2:
                self.root.after(0, self.stop_macro)

        except Exception as e:
            self.logger.write_log(f"Hotkey listener error: {e}")

    def start_key_listener(self):

        try:
            listener = keyboard.Listener(on_press=self.on_press)

            listener_thread = threading.Thread(target=listener.run, daemon=True, name="HotkeyListener") 
            listener_thread.start()
            self.logger.write_log("Hotkey listener started (F1/F2).")

        except Exception as e:
            self.logger.write_log(f"Failed to start hotkey listener: {e}")
            messagebox.showerror("Hotkey Error", f"Could not start hotkey listener: {e}")

    def load_plugins(self):
        plugin_dir = os.path.join(MACROPATH, "plugins")
        config_dir = os.path.join(plugin_dir, "config")
        os.makedirs(config_dir, exist_ok=True) 

        plugin_files = glob.glob(os.path.join(plugin_dir, "*.py"))
        self.logger.write_log(f"Scanning for plugins in: {plugin_dir}")

        current_plugin_instances = {p.name: p for p in self.plugins if hasattr(p, "name")}

        for plugin_file in plugin_files:
            plugin_name_from_file = os.path.splitext(os.path.basename(plugin_file))[0]
            if plugin_name_from_file.startswith("__"): continue

            try:
                self.logger.write_log(f"Attempting to load plugin: {plugin_name_from_file}")
                spec = importlib.util.spec_from_file_location(plugin_name_from_file, plugin_file)
                if spec is None or spec.loader is None:
                     self.logger.write_log(f" > Could not create spec for plugin '{plugin_name_from_file}'. Skipping.")
                     continue
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if not hasattr(module, "Plugin"):
                    self.logger.write_log(f" > No 'Plugin' class found in {plugin_name_from_file}. Skipping.")
                    continue
                plugin_class = getattr(module, "Plugin")

                temp_instance = plugin_class(self)
                plugin_display_name = getattr(temp_instance, "name", plugin_name_from_file)
                plugin_version = getattr(temp_instance, "version", "0.0.0")
                plugin_author = getattr(temp_instance, "author", "Unknown")
                required_macro_version = getattr(temp_instance, "requires", "0.0.0")

                del temp_instance

                from packaging.version import parse as parse_version 
                if parse_version(required_macro_version) > parse_version(LOCALVERSION):
                    self.logger.write_log(f" > Skipped Plugin: '{plugin_display_name}' requires macro v{required_macro_version}, but current is v{LOCALVERSION}.")
                    continue

                existing_plugin = current_plugin_instances.get(plugin_display_name)
                if existing_plugin:
                    existing_version = getattr(existing_plugin, "version", "0.0.0")
                    if parse_version(plugin_version) <= parse_version(existing_version):
                        self.logger.write_log(f" > Skipped Plugin: '{plugin_display_name}' v{plugin_version} is older or same as loaded v{existing_version}.")
                        continue
                    else:
                        self.logger.write_log(f"Found newer version {plugin_version} for plugin '{plugin_display_name}'. Reloading...")

                        if hasattr(existing_plugin, "unload"): existing_plugin.unload() 
                        if hasattr(existing_plugin, "tab") and existing_plugin.tab:
                             try:

                                 self.notebook.delete(plugin_display_name)
                                 if plugin_display_name in self.tab_entries:
                                     del self.tab_entries[plugin_display_name]
                             except Exception as e_unload:
                                 self.logger.write_log(f"Error removing old tab for plugin {plugin_display_name}: {e_unload}")
                        self.plugins.remove(existing_plugin)
                        del current_plugin_instances[plugin_display_name]

                plugin_instance = plugin_class(self)
                plugin_instance.name = plugin_display_name
                plugin_instance.version = plugin_version
                plugin_instance.author = plugin_author
                plugin_instance.entries = {} 

                plugin_instance.config = plugin_instance.load_or_create_config() if hasattr(plugin_instance, "load_or_create_config") else {}

                self.notebook.add(plugin_display_name)
                plugin_tab_frame = self.notebook.tab(plugin_display_name) 
                plugin_instance.tab = plugin_tab_frame 

                self.tab_entries[plugin_display_name] = plugin_instance.entries

                if hasattr(plugin_instance, "init_tab"):

                    gui_tools = {
                        "customtkinter": customtkinter, 
                        "tk": tk, 
                        "create_widgets": self.create_widgets, 
                        "format_key": format_key,
                        "logger": self.logger,
                        "entries": plugin_instance.entries, 
                        "config": plugin_instance.config, 

                        "ScrollableFrame": customtkinter.CTkScrollableFrame,

                        "create_list_widget": self.create_list_widget, 
                        "parent_frame": plugin_tab_frame 
                    }

                    plugin_instance.init_tab(gui_tools) 
                else:
                    customtkinter.CTkLabel(plugin_tab_frame, text="Plugin has no UI to display.").pack(padx=10, pady=10)

                self.create_bottom_buttons(plugin_tab_frame)

                self.plugins.append(plugin_instance)
                current_plugin_instances[plugin_display_name] = plugin_instance 
                self.logger.write_log(f" > Successfully loaded plugin: {plugin_display_name} v{plugin_version} by {plugin_author}")

            except Exception as e:
                self.logger.write_log(f"Error loading plugin from '{plugin_file}': {e}")
                import traceback
                self.logger.write_log(traceback.format_exc())

    def install_plugin(self):
        plugin_path = filedialog.askopenfilename(
            title="Select Plugin File (.py)",
            filetypes=[("Python Files", "*.py")]
        )
        if not plugin_path:
            return

        try:
            dest_dir = os.path.join(MACROPATH, "plugins")
            filename = os.path.basename(plugin_path)
            dest_path = os.path.join(dest_dir, filename)

            if os.path.exists(dest_path):
                if not messagebox.askyesno("Plugin Exists", f"Plugin '{filename}' already exists. Overwrite?"):
                    return

            shutil.copy(plugin_path, dest_path)
            self.logger.write_log(f"Plugin '{filename}' copied to plugins directory.")

            self.load_plugins() 

            messagebox.showinfo("Plugin Installed", f"Plugin '{filename}' installed successfully. Restart may be needed for full effect.")
        except Exception as e:
            messagebox.showerror("Plugin Install Failed", f"Failed to install plugin:\n{e}")
            self.logger.write_log(f"Failed to install plugin '{plugin_path}': {e}")

    def on_close(self):
        if self.running:
            if messagebox.askyesno("Exit Confirmation", "Macro is running. Are you sure you want to stop and exit?"):
                self.stop_macro()
                self.root.destroy()
        else:
            if messagebox.askyesno("Exit Confirmation", "Are you sure you want to exit?"):

                self.root.destroy()