"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v1.2.7
Support server: https://discord.gg/8khGXqG7nA
"""

import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))

import time 

import threading
import asyncio
from datetime import datetime
import webbrowser
import shutil 
import urllib.request 
import glob 
import importlib.util 
from packaging.version import parse as parse_version 
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QTabWidget, QLabel, QLineEdit, QCheckBox, QPushButton, QTextEdit,
    QScrollArea, QFrame, QMessageBox, QFileDialog, QListWidget, QListWidgetItem,
    QSizePolicy, QSpacerItem 
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QMetaObject, Q_ARG, pyqtSlot 
from PyQt6.QtGui import QIcon, QPixmap, QTextCursor 

from constants import (
    MACROPATH, LOCALVERSION, WEBHOOK_ICON_URL, STARTUP_MSGS,
    GENERAL_KEYS, AURAS_KEYS, BIOMES_KEYS, MERCHANT_KEYS,
    AUTOCRAFT_KEYS, SNIPER_KEYS, OTHER_KEYS, QUEST_KEYS, COORDS, DEFAULTSETTINGS, PATH_KEYS,
    DONOTDISPLAY, ALT_TESSERACT_DIR
)
from utils import (
    get_logger, set_global_logger, Logger, format_key, 
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
    do_obby, auto_pop, use_item, auto_questboard
)

try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract

    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

from pynput import keyboard, mouse
import mousekey as mk

import discord

class PyQtLogSignal(QObject):
    log_signal = pyqtSignal(str)

class PyQtLogger(Logger):
    """Logger implementation that emits a PyQt signal for GUI updates."""
    def __init__(self, log_file='macro.log'):

        super().__init__(log_file_path=log_file) 
        self.signal_emitter = PyQtLogSignal()

    def write_log(self, message, level='INFO'):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp} - {level}] {message}"

        if self.log_file_path:
            try:
                with open(self.log_file_path, "a", encoding='utf-8') as log_file:
                    log_file.write(formatted_message + '\n')
            except Exception as e:

                print(f"Error writing log to file {self.log_file_path}: {e}")
                print(formatted_message) 

        if self.signal_emitter:

            self.signal_emitter.log_signal.emit(formatted_message)

        return formatted_message

    def connect_log_widget(self, slot_function):
        """Connects the logger's signal to a GUI slot."""
        self.signal_emitter.log_signal.connect(slot_function)

class MainWindow(QMainWindow):

    start_macro_signal = pyqtSignal()
    stop_macro_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.logger = get_logger()

        self.settings = load_settings()
        self.original_settings = self.settings.copy()

        self.webhook = None
        self.threads = []
        self.sniper_task = None
        self.running = False
        self.keyboard_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.sniped_event = threading.Event()

        self.plugins = [] 

        self.plugin_file_paths = {}

        self.mkey = mk.MouseKey()
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()

        self.MACROPATH = os.path.expandvars(r"%localappdata%\SolsScope")

        self.setWindowTitle(f"SolsScope v{LOCALVERSION} (PyQt)")
        self.setGeometry(100, 100, 750, 550) 

        icon_path = os.path.join(MACROPATH, "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        if self.settings.get("always_on_top", False):
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint) 

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self.tab_entries = {}

        self.create_tabs()

        self.logger.write_log("GUI Logger initialized (PyQt).")

        self.plugin_settings = {}

        self.load_plugins() 

        self.start_key_listener()

        self.start_macro_signal.connect(self.start_macro)
        self.stop_macro_signal.connect(self.stop_macro)

        self.logger.write_log("GUI setup complete (PyQt).")

    def create_tabs(self):

        tab_info = {
            "General": GENERAL_KEYS,
            "Auras": AURAS_KEYS,
            "Biomes": BIOMES_KEYS,
            "Merchant": MERCHANT_KEYS,
            #"Quest" : QUEST_KEYS,
            "Path": PATH_KEYS,
            "Auto Craft": AUTOCRAFT_KEYS,
            "Sniper": SNIPER_KEYS,
            "Other": OTHER_KEYS,
        }

        for tab_name, keys in tab_info.items():
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget) 

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            tab_layout.addWidget(scroll_area)

            scroll_content_widget = QWidget()
            scroll_area.setWidget(scroll_content_widget)
            content_layout = QVBoxLayout(scroll_content_widget) 
            content_layout.setAlignment(Qt.AlignmentFlag.AlignTop) 

            self.tab_entries[tab_name] = {}
            self.populate_tab(content_layout, keys, self.tab_entries[tab_name])

            if tab_name == "Merchant":
                self.add_merchant_tab_extras(content_layout) 
            if tab_name == "Other":
                self.add_other_tab_extras(content_layout) 

            self.create_bottom_buttons(tab_layout) 

            self.tab_widget.addTab(tab_widget, tab_name)

        self.create_logs_tab()

        self.create_credits_tab()

    def populate_tab(self, layout, keys, entry_dict):
        """Populates a tab layout with widgets based on settings keys."""
        settings_subset = {k: self.settings.get(k, DEFAULTSETTINGS.get(k)) for k in keys}
        self.create_widgets(settings_subset, layout, entry_dict)

    def create_widgets(self, settings_subset, parent_layout, entry_dict):
        """Recursively creates widgets for settings items using PyQt layouts."""

        form_layout = QFormLayout()

        form_layout.setHorizontalSpacing(15) 
        form_layout.setVerticalSpacing(10)   
        parent_layout.addLayout(form_layout)

        for key, value in settings_subset.items():
            if key in DONOTDISPLAY:
                continue

            formatted_key = format_key(key)

            if isinstance(value, dict):

                group_box = QGroupBox(formatted_key) 
                group_box.setCheckable(False) 
                group_layout = QVBoxLayout(group_box) 
                group_layout.setContentsMargins(10, 15, 10, 10)

                form_layout.addRow(group_box) 

                entry_dict[key] = {}

                self.create_widgets(value, group_layout, entry_dict[key])

            elif isinstance(value, list):

                label = QLabel(formatted_key + ":")

                list_container_widget = QWidget()
                list_layout = QVBoxLayout(list_container_widget)
                list_layout.setContentsMargins(0,0,0,0) 

                list_widget_data = self.create_list_widget(list_layout, key, value, entry_dict)

                form_layout.addRow(label, list_container_widget)

                entry_dict[key] = list_widget_data

            elif isinstance(value, bool):

                widget = QCheckBox()
                widget.setChecked(value)
                form_layout.addRow(formatted_key + ":", widget)
                entry_dict[key] = widget

            else: 

                widget = QLineEdit(str(value))

                form_layout.addRow(formatted_key + ":", widget)
                entry_dict[key] = widget

    def create_list_widget(self, parent_layout, key, items, entry_dict_ignored):
        """Creates a QListWidget with Add/Remove buttons within the provided layout.
           Returns a dictionary containing the list widget and add entry widget.
        """

        list_widget = QListWidget()

        list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding) 
        list_widget.addItems([str(item) for item in items])
        parent_layout.addWidget(list_widget) 

        controls_layout = QHBoxLayout()
        parent_layout.addLayout(controls_layout) 

        add_entry = QLineEdit()
        add_entry.setPlaceholderText("Enter item to add...")
        controls_layout.addWidget(add_entry)

        add_button = QPushButton("Add")
        add_button.setFixedWidth(60)
        controls_layout.addWidget(add_button)

        remove_button = QPushButton("Remove")
        remove_button.setFixedWidth(60)
        controls_layout.addWidget(remove_button)

        add_button.clicked.connect(lambda _, k=key: self.add_to_list(k))
        remove_button.clicked.connect(lambda _, k=key: self.remove_from_list(k))

        list_widget_data = {"list_widget": list_widget, "add_entry": add_entry}

        return list_widget_data

    def add_to_list(self, key):
        list_data = self._find_list_data(key)
        if not list_data:
            self.logger.write_log(f"Error adding to list: Could not find list data for key '{key}'.")
            return

        list_widget = list_data["list_widget"]
        add_entry = list_data["add_entry"]
        new_item_text = add_entry.text().strip()

        if not new_item_text: return

        items = [list_widget.item(i).text() for i in range(list_widget.count())]
        if new_item_text in items:
            QMessageBox.warning(self, "Duplicate Item", f"'{new_item_text}' is already in the list.")
            return

        list_widget.addItem(new_item_text)
        add_entry.clear()

    def remove_from_list(self, key):
        list_data = self._find_list_data(key)
        if not list_data:
            self.logger.write_log(f"Error removing from list: Could not find list data for key '{key}'.")
            return

        list_widget = list_data["list_widget"]
        selected_items = list_widget.selectedItems()

        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an item to remove from the list.")
            return

        for item in selected_items:
            list_widget.takeItem(list_widget.row(item)) 

    def _find_list_data(self, key):
        """Helper to find list widget and add entry based on key."""

        def search_dict(d):
            if key in d and isinstance(d[key], dict) and "list_widget" in d[key]:
                return d[key]
            for sub_key, sub_data in d.items():
                if isinstance(sub_data, dict):
                    found = search_dict(sub_data)
                    if found:
                        return found
            return None

        for tab_name, tab_data in self.tab_entries.items():
            found = search_dict(tab_data)
            if found:
                return found

        return None 

    def add_merchant_tab_extras(self, layout):
        """Adds Tesseract status and download button to the Merchant tab layout."""
        status_text = "Tesseract OCR: Installed" if TESSERACT_AVAILABLE and (shutil.which("tesseract") is not None or os.path.exists(r'C:\Program Files\Tesseract-OCR') or os.path.exists(ALT_TESSERACT_DIR)) else "Tesseract OCR: Not Installed (Merchant Detection Disabled)"
        status_color = "green" if TESSERACT_AVAILABLE else "red"
        if TESSERACT_AVAILABLE and shutil.which("tesseract") is None and os.path.exists(r'C:\Program Files\Tesseract-OCR'):
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        elif os.path.exists(ALT_TESSERACT_DIR) and TESSERACT_AVAILABLE and shutil.which("tesseract") is None:
            pytesseract.pytesseract.tesseract_cmd = f"{ALT_TESSERACT_DIR}\\tesseract.exe"

        ocr_label = QLabel(status_text)
        ocr_label.setStyleSheet(f"color: {status_color};")
        layout.addWidget(ocr_label)

        if not TESSERACT_AVAILABLE:
            download_button = QPushButton("Download Tesseract (External Link)")
            download_button.clicked.connect(lambda: webbrowser.open("https://github.com/tesseract-ocr/tesseract#installing-tesseract"))
            download_button.setStyleSheet("text-align: left; padding: 2px;") 
            download_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed) 
            layout.addWidget(download_button)
            layout.addSpacing(10) 

    def add_other_tab_extras(self, layout):
         """Adds Plugin install button to the Other tab layout."""
         install_btn = QPushButton("Install Plugin...")
         install_btn.clicked.connect(self.install_plugin) 
         install_btn.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
         layout.addWidget(install_btn)
         layout.addSpacing(10)

    def create_bottom_buttons(self, layout):
        """Creates the Start/Stop/Save buttons at the bottom of a tab."""
        button_frame = QFrame() 
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 10, 0, 0) 

        start_button = QPushButton("Start (F1)")
        start_button.clicked.connect(self.start_macro)
        button_layout.addWidget(start_button)

        stop_button = QPushButton("Stop (F2)")
        stop_button.clicked.connect(self.stop_macro)
        button_layout.addWidget(stop_button)

        button_layout.addStretch(1) 

        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.press_save_button)
        button_layout.addWidget(save_button)

        layout.addWidget(button_frame) 

    def create_logs_tab(self):
        logs_tab = QWidget()
        layout = QVBoxLayout(logs_tab)

        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setStyleSheet("background-color: #f0f0f0;") 
        layout.addWidget(self.log_widget)

        self.logger.connect_log_widget(self.append_log_message)

        self.tab_widget.addTab(logs_tab, "Logs")

    @pyqtSlot(str) 
    def append_log_message(self, message):
        """Appends a message to the log widget (thread-safe)."""
        self.log_widget.moveCursor(QTextCursor.MoveOperation.End)
        self.log_widget.insertPlainText(message + '\n')
        self.log_widget.moveCursor(QTextCursor.MoveOperation.End) 

    def create_credits_tab(self):
        """Populates the Credits tab with information."""
        credits_tab = QWidget()
        layout = QVBoxLayout(credits_tab)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter) 

        title_label = QLabel("Created by Baz and Cresqnt")
        font = title_label.font()
        font.setPointSize(12)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        layout.addSpacing(10)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label2 = QLabel()
        image_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if PIL_AVAILABLE:
            try:
                image_path = os.path.join(MACROPATH, "baz.png")
                img_url = "https://raw.githubusercontent.com/bazthedev/SolsScope/main/img/baz.png"

                if not os.path.exists(image_path):
                    self.logger.write_log(f"Downloading credits image from {img_url}...")
                    try:

                        with urllib.request.urlopen(img_url, timeout=10) as response, open(image_path, 'wb') as out_file:
                            if response.status == 200:
                                shutil.copyfileobj(response, out_file)
                                self.logger.write_log("Credits image downloaded.")
                            else:
                                self.logger.write_log(f"Failed to download image: Status {response.status}")
                                raise Exception(f"HTTP Error {response.status}")
                    except Exception as dl_error:
                         self.logger.write_log(f"Error downloading credits image: {dl_error}")

                         raise dl_error 

                pixmap = QPixmap(image_path)
                if not pixmap.isNull():

                    scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    image_label.setPixmap(scaled_pixmap)
                else:
                    self.logger.write_log(f"Failed to load credits image from path: {image_path}")
                    image_label.setText("(Failed to load image)")

            except Exception as e:
                self.logger.write_log(f"Error processing credits image: {e}")
                image_label.setText("(Image unavailable)")
            try:
                image_path = os.path.join(MACROPATH, "cresqnt.png")
                img_url = "https://raw.githubusercontent.com/bazthedev/SolsScope/main/img/cresqnt.png"

                if not os.path.exists(image_path):
                    self.logger.write_log(f"Downloading credits image from {img_url}...")
                    try:

                        with urllib.request.urlopen(img_url, timeout=10) as response, open(image_path, 'wb') as out_file:
                            if response.status == 200:
                                shutil.copyfileobj(response, out_file)
                                self.logger.write_log("Credits image downloaded.")
                            else:
                                self.logger.write_log(f"Failed to download image: Status {response.status}")
                                raise Exception(f"HTTP Error {response.status}")
                    except Exception as dl_error:
                         self.logger.write_log(f"Error downloading credits image: {dl_error}")

                         raise dl_error 

                pixmap = QPixmap(image_path)
                if not pixmap.isNull():

                    scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    image_label2.setPixmap(scaled_pixmap)
                else:
                    self.logger.write_log(f"Failed to load credits image from path: {image_path}")
                    image_label2.setText("(Failed to load image)")

            except Exception as e:
                self.logger.write_log(f"Error processing credits image: {e}")
                image_label2.setText("(Image unavailable)")
        else:
            image_label.setText("(Install Pillow library to see images)")
            image_label2.setText("(Install Pillow library to see images)")
        
        donation_url = "https://raw.githubusercontent.com/bazthedev/SolsScope/main/donations.json"
        self.logger.write_log(f"Downloading donation data from {donation_url}...")
        try:

            with urllib.request.urlopen(donation_url, timeout=10) as response, open(image_path, 'wb') as out_file:
                if response.status == 200:
                    shutil.copyfileobj(response, out_file)
                    self.logger.write_log("Donation data downloaded.")
                else:
                    self.logger.write_log(f"Failed to download data: Status {response.status}")
                    raise Exception(f"HTTP Error {response.status}")
        except Exception as dl_error:
                self.logger.write_log(f"Error downloading data: {dl_error}")

                raise dl_error

        layout.addWidget(image_label)
        layout.addSpacing(15)

        layout.addWidget(image_label2)
        layout.addSpacing(15)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine) 
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        layout.addSpacing(15)

        ack_title = QLabel("Acknowledgements:")
        font = ack_title.font()
        font.setPointSize(10)
        font.setBold(True)
        ack_title.setFont(font)
        ack_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ack_title)
        layout.addSpacing(5)

        ack_texts = [
            "Root1527 for the original YAY Joins Sniper logic",
            "Mountain Shrine Path inspiration by AllanQute (_justalin)",
            "dolphSol for inspiration",
            "vex (vexthecoder) for ideas",
            "Doors_Daisukiman for helping with testing"
        ]
        for text in ack_texts:
            ack_label = QLabel(text)
            ack_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(ack_label)

        layout.addStretch(1)

        self.tab_widget.addTab(credits_tab, "Credits")

    def get_updated_values(self, original_settings_subset, entries_subset):
        """Compares current widget values to original values for a subset."""
        updated_subset = {}
        for key, widget_or_dict in entries_subset.items():
            original_value = original_settings_subset.get(key)

            if isinstance(original_value, dict) and isinstance(widget_or_dict, dict):

                sub_updates = self.get_updated_values(original_value, widget_or_dict)
                if sub_updates:
                    updated_subset[key] = sub_updates
            elif isinstance(original_value, list) and isinstance(widget_or_dict, dict) and "list_widget" in widget_or_dict:

                 list_widget = widget_or_dict["list_widget"]
                 new_value = [list_widget.item(i).text() for i in range(list_widget.count())]

                 if sorted(new_value) != sorted(map(str, original_value)):

                     converted_new_value = []
                     if original_value:
                         orig_type = type(original_value[0])
                         try:
                             converted_new_value = [orig_type(item) for item in new_value]
                         except (ValueError, TypeError):
                             converted_new_value = new_value 
                     else:
                         converted_new_value = new_value
                     updated_subset[key] = converted_new_value
            elif not isinstance(widget_or_dict, dict): 
                try:
                    if isinstance(widget_or_dict, QCheckBox):
                        new_value = widget_or_dict.isChecked()
                    elif isinstance(widget_or_dict, QLineEdit):
                        new_value_str = widget_or_dict.text()

                        if isinstance(original_value, bool): 
                            new_value = bool(new_value_str.lower() in ['true', '1', 'yes', 'y'])
                        elif isinstance(original_value, int):
                            try: new_value = int(new_value_str)
                            except (ValueError, TypeError): new_value = new_value_str 
                        elif isinstance(original_value, float):
                            try: new_value = float(new_value_str)
                            except (ValueError, TypeError): new_value = new_value_str
                        else: 
                            new_value = new_value_str
                    else:
                        self.logger.write_log(f"Warning: Unexpected widget type for '{key}' ({type(widget_or_dict)}).")
                        continue

                    if type(new_value) != type(original_value) and original_value is not None:

                         if str(new_value) != str(original_value):
                             updated_subset[key] = new_value
                    elif new_value != original_value:
                         updated_subset[key] = new_value

                except Exception as e:
                    self.logger.write_log(f"Error getting/comparing value for key '{key}': {e}")
                    continue 

        return updated_subset
    
    def press_save_button(self):
        save_successful, changes_were_present = self.save_settings()
        if save_successful:
            QMessageBox.information(self, "Settings Saved", "Settings were saved successfully!")

    def save_settings(self):
        """Gathers updated values from all tabs (including plugins) and saves them.
        Returns a tuple: (save_successful: bool, changes_detected: bool)
        """
        self.logger.write_log("Gathering settings from UI (PyQt)...")
        full_updated_values = {}
        changes_detected = False 

        tab_info = {
            "General": GENERAL_KEYS, "Auras": AURAS_KEYS, "Biomes": BIOMES_KEYS,
            "Merchant": MERCHANT_KEYS, "Path": PATH_KEYS, "Auto Craft": AUTOCRAFT_KEYS, #"Quest" : QUEST_KEYS, "Path": PATH_KEYS, "Auto Craft": AUTOCRAFT_KEYS,
            "Sniper": SNIPER_KEYS, "Other": OTHER_KEYS
        }

        for i in range(self.tab_widget.count()):
            tab_name = self.tab_widget.tabText(i)
            if tab_name in self.tab_entries:
                tab_entries_dict = self.tab_entries[tab_name]
                original_subset = {}

                if tab_name in tab_info:
                    # Standard tab
                    tab_keys = tab_info[tab_name]
                    original_subset = {
                        k: self.original_settings.get(k, DEFAULTSETTINGS.get(k))
                        for k in tab_keys if k != "__version__"
                    }
                    updated_subset = self.get_updated_values(original_subset, tab_entries_dict)
                    if updated_subset:
                        full_updated_values.update(updated_subset)
                        changes_detected = True
                else:
                    # Plugin tab
                    plugin = next((p for p in self.plugins if getattr(p, 'name', None) == tab_name), None)
                    if plugin and hasattr(plugin, 'config'):
                        updated_subset = self.get_updated_values(plugin.config, tab_entries_dict)
                        if updated_subset:
                            plugin.config.update(updated_subset)
                            changes_detected = True
                    continue  # Skip merging plugin config into full_updated_values

            elif tab_name not in ["Logs", "Credits"]:
                self.logger.write_log(f"Warning: Tab '{tab_name}' found in UI but not in tab_entries.")

        if not changes_detected:
            self.logger.write_log("No setting changes detected.")
            return True, False 

        self.logger.write_log(f"Detected changes: {list(full_updated_values.keys())}")

        current_file_settings = load_settings()

        def merge_dicts(target, updates):
            for key, value in updates.items():
                if isinstance(value, dict) and isinstance(target.get(key), dict):
                    merge_dicts(target[key], value)
                else:
                    target[key] = value

        merge_dicts(current_file_settings, full_updated_values)
        validated_settings, validation_errors = validate_settings(current_file_settings)

        if validation_errors:
            self.logger.write_log(f"Settings validation issues found: {validation_errors}")
            QMessageBox.warning(
                self, "Validation Warning",
                f"Settings validation found issues (check logs). Saving anyway.\nIssues: {validation_errors}"
            )

        if update_settings(validated_settings):
            for plugin in self.plugins:
                if hasattr(plugin, 'save_config'):
                    try:
                        plugin.save_config()
                        self.logger.write_log(f"Plugin config for '{plugin.name}' saved.")
                    except Exception as e:
                        self.logger.write_log(f"Error saving config for plugin '{plugin.name}': {e}", level="ERROR")

            self.logger.write_log("Settings saved successfully.")

            self.settings = validated_settings
            self.original_settings = self.settings.copy()

            for plugin in self.plugins:
                if hasattr(plugin, 'update_config'):
                    try:
                        plugin.update_config(validated_settings)
                        self.logger.write_log(f"Updated config for plugin '{plugin.name}'.")
                    except Exception as e:
                        self.logger.write_log(f"Error updating config for plugin '{plugin.name}': {e}")

            return True, True 
        else:
            self.logger.write_log("Failed to save settings to file.")
            QMessageBox.critical(self, "Save Settings Error", "Failed to save settings. Check logs.")
            return False, True


    def start_macro(self):
        if self.running:
            QMessageBox.warning(self, "Macro Running", "Macro is already running!")
            return

        save_successful, changes_were_present = self.save_settings()

        if not save_successful and changes_were_present:
             if QMessageBox.question(self, "Save Failed", "Failed to save settings. Continue starting the macro with potentially unsaved changes?") == QMessageBox.StandardButton.No:
                self.logger.write_log("Macro start cancelled due to failed save.")
                return
             self.logger.write_log("Continuing start despite failed save. Reloading settings from file.")
             self.settings = load_settings()

        if not self.settings.get("WEBHOOK_URL"):
            QMessageBox.critical(self, "Missing Webhook", "Please provide a primary Webhook URL in the General tab.")
            self.logger.write_log("Macro start failed: Missing Webhook URL.")
            return
        try:

            self.logger.write_log("Initializing webhook using discord.SyncWebhook.from_url...")
            self.webhook = discord.SyncWebhook.from_url(self.settings["WEBHOOK_URL"])
            self.logger.write_log("Successfully initialized webhook with discord.SyncWebhook.")

        except AttributeError as e:

            self.logger.write_log(f"AttributeError finding/using discord.SyncWebhook: {e}. Incompatible discord.py version or structure?", level="ERROR")
            import traceback
            self.logger.write_log(traceback.format_exc()) 
            QMessageBox.critical(
                self,
                "Webhook Creation Error",
                f"Failed to find or use discord.SyncWebhook.\nError: {e}\n"
                "Please ensure you have a compatible version of discord.py installed (e.g., v2.0+).\n"
                "Check logs for detailed traceback."
            )
            return 
        except Exception as e:

            QMessageBox.critical(self, "Invalid Webhook", f"The primary Webhook URL is invalid or initialization failed:\n{e}")
            self.logger.write_log(f"Macro start failed: Invalid Webhook URL or adapter issue ({e}).", level="ERROR")
            return 

        if self.settings.get("sniper_enabled") and len(self.settings.get("scan_channels", [])) > 5:
             if QMessageBox.question(self, "Sniper Channel Warning", "Sniping many channels (>5) can increase ratelimits. Continue anyway?") == QMessageBox.StandardButton.No:
                self.logger.write_log("Macro start cancelled: Too many sniper channels.")
                return

        use_player = self.settings.get("use_roblox_player", True)
        set_active_log_directory(force_player=use_player)
        if not exists_procs_by_name("Windows10Universal.exe") and not exists_procs_by_name("RobloxPlayerBeta.exe"):
            if QMessageBox.question(self, "Roblox Not Detected", "Roblox process not found. Start macro anyway?") == QMessageBox.StandardButton.No:
                self.logger.write_log("Macro start cancelled: Roblox not running.")
                return

        self.running = True
        self.stop_event.clear()
        self.sniped_event.clear()
        self.threads = []
        self.logger.write_log("Starting Macro Threads in 5 seconds...")

        is_autocraft_mode = self.settings.get("auto_craft_mode", False)
        is_idle_mode = self.settings.get("idle_mode", False)
        try:
            thread_targets = self._get_thread_targets(is_autocraft_mode, is_idle_mode)
        except ValueError as e: 
             self.running = False 
             return

        for name, target_info in thread_targets.items():
            if target_info:
                func, args = target_info
                try:
                    adjusted_args = list(args)

                    if self.keyboard_controller in adjusted_args:
                        adjusted_args[adjusted_args.index(self.keyboard_controller)] = self.keyboard_controller
                    if self.mouse_controller in adjusted_args:
                         adjusted_args[adjusted_args.index(self.mouse_controller)] = self.mouse_controller

                    thread = threading.Thread(target=func, args=adjusted_args, daemon=True, name=name)
                    thread.start()
                    self.threads.append(thread)
                    self.logger.write_log(f" > Started thread: {name}")
                except Exception as e:
                    self.logger.write_log(f" > Error starting thread {name}: {e}")

        if self.settings.get("sniper_enabled"):
            self.logger.write_log("Starting Sniper...")
            self._start_sniper_thread() 

        self.logger.write_log("Starting Plugin Threads...")
        for plugin in self.plugins:
            try:
                can_run = True
                plugin_name = getattr(plugin, "name", "UnknownPlugin")
                if is_autocraft_mode and not getattr(plugin, "autocraft_compatible", False):
                    can_run = False
                    self.logger.write_log(f"Skipping plugin {plugin_name}: Not compatible with Auto Craft mode.")

                if can_run and hasattr(plugin, "run"):

                    plugin_args = (self.stop_event, self.sniped_event)
                    thread = threading.Thread(target=plugin.run, args=plugin_args, daemon=True, name=f"Plugin_{plugin_name}")
                    thread.start()
                    self.threads.append(thread)
                    self.logger.write_log(f" > Started plugin thread: {plugin_name}")
                elif can_run:
                     self.logger.write_log(f"Plugin {plugin_name} has no run method.")
            except Exception as e:
                self.logger.write_log(f"Error starting plugin thread '{plugin_name}': {e}", level="ERROR")

        self._send_start_notification(is_autocraft_mode, is_idle_mode)
        self.logger.write_log("Macro started successfully.")

    def _get_thread_targets(self, is_autocraft_mode, is_idle_mode):
        """Helper to determine which threads to start based on mode."""

        MERCHANT_DETECTION_POSSIBLE = TESSERACT_AVAILABLE 

        if is_idle_mode:
            self.logger.write_log("Starting in IDLE Mode.")
            targets = {
                "Aura Detection": (aura_detection, [self.settings, self.webhook, self.stop_event, self.keyboard_lock, self.mkey, self.keyboard_controller]) if not self.settings.get("disable_aura_detection") else None,
                "Biome Detection": (biome_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event]) if not self.settings.get("disable_biome_detection") else None,
            }
        elif is_autocraft_mode:
            self.logger.write_log("Starting in Auto Craft Mode.")
            enabled_crafts = [item for item, enabled in self.settings.get("auto_craft_item", {}).items() if enabled]
            if not enabled_crafts:
                QMessageBox.critical(self, "Auto Craft Error", "Auto Craft mode is enabled, but no potions are selected to craft.")
                self.logger.write_log("Auto Craft start failed: No items selected.")

                raise ValueError("No items selected for auto-craft")
            if not self.settings.get("skip_auto_mode_warning"):
                self.logger.write_log("Auto Craft mode is ON. Some features will be disabled. Ensure you are near the cauldron.")

            targets = {
                "Auto Craft Logic": (auto_craft, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.mouse_controller]),
                "Aura Detection": (aura_detection, [self.settings, self.webhook, self.stop_event, self.keyboard_lock, self.mkey, self.keyboard_controller]) if not self.settings.get("disable_aura_detection") else None,
                "Biome Detection": (biome_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event]) if not self.settings.get("disable_biome_detection") else None,
                "Keep Alive": (keep_alive, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey]) if not self.settings.get("disable_autokick_prevention") else None,
                "Disconnect Prevention": (disconnect_prevention, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller]) if self.settings.get("disconnect_prevention") else None,
                #"Merchant Detection": (merchant_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller]) if (self.settings.get("merchant_detection") or self.settings.get("auto_sell_to_jester")) and MERCHANT_DETECTION_POSSIBLE else None,
                "Auto Biome Randomizer": (auto_br, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller]) if self.settings.get("auto_biome_randomizer") else None,
                "Auto Strange Controller": (auto_sc, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller]) if self.settings.get("auto_strange_controller") else None,
                "Inventory Screenshots": (inventory_screenshot, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey]) if self.settings.get("periodic_screenshots", {}).get("inventory") else None,
                "Storage Screenshots": (storage_screenshot, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey]) if self.settings.get("periodic_screenshots", {}).get("storage") else None,
                "Obby": (do_obby, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.mouse_controller]) if self.settings.get("do_obby") else None,
                #"Auto Quest Board": (auto_questboard, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.mouse_controller]) if self.settings.get("enable_auto_quest_board") else None,
            }
        else: 
            self.logger.write_log("Starting in Normal Mode.")
            targets = {
                "Aura Detection": (aura_detection, [self.settings, self.webhook, self.stop_event, self.keyboard_lock, self.mkey, self.keyboard_controller]) if not self.settings.get("disable_aura_detection") else None,
                "Biome Detection": (biome_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event]) if not self.settings.get("disable_biome_detection") else None,
                "Keep Alive": (keep_alive, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey]) if not self.settings.get("disable_autokick_prevention") else None,
                "Disconnect Prevention": (disconnect_prevention, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller]) if self.settings.get("disconnect_prevention") else None,
                "Merchant Detection": (merchant_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller]) if (self.settings.get("merchant_detection") or self.settings.get("auto_sell_to_jester")) and MERCHANT_DETECTION_POSSIBLE else None,
                "Auto Biome Randomizer": (auto_br, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller]) if self.settings.get("auto_biome_randomizer") else None,
                "Auto Strange Controller": (auto_sc, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller]) if self.settings.get("auto_strange_controller") else None,
                "Inventory Screenshots": (inventory_screenshot, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey]) if self.settings.get("periodic_screenshots", {}).get("inventory") else None,
                "Storage Screenshots": (storage_screenshot, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey]) if self.settings.get("periodic_screenshots", {}).get("storage") else None,
                "Obby": (do_obby, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.mouse_controller]) if self.settings.get("do_obby") else None,
                #"Auto Quest Board": (auto_questboard, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.mouse_controller]) if self.settings.get("enable_auto_quest_board") else None,
            }
        return targets

    def _start_sniper_thread(self):
        """Starts the sniper asyncio loop in a separate thread."""
        def run_sniper_loop():

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:

                loop.run_until_complete(start_snipers(self.settings, self.webhook, self.sniped_event, self.stop_event))
            except Exception as e:

                self.logger.write_log(f"Error in sniper asyncio loop: {e}")
            finally:
                loop.close()
            self.logger.write_log("Sniper asyncio loop finished.")

        sniper_thread = threading.Thread(target=run_sniper_loop, daemon=True, name="SniperThread")
        sniper_thread.start()
        self.threads.append(sniper_thread)

    def _send_start_notification(self, is_autocraft_mode, is_idle_mode):
        """Sends the start notification webhook."""
        if is_idle_mode:
            mode_str = "IDLE"
        elif is_autocraft_mode:
            if self.settings.get("merchant_detection", False):
                mode_str = "Auto Craft, with Merchant Detection"
            else:
                mode_str = "Auto Craft"
        else:
            mode_str = "Normal"
        start_desc = "" 

        emb = discord.Embed(
            title="Macro Started",
            description=start_desc, 
            colour=discord.Colour.green(),
            timestamp=datetime.now() 
        )
        emb.set_footer(text=f"SolsScope v{LOCALVERSION}")
        emb.add_field(name="Mode", value=mode_str, inline=True)

        if is_autocraft_mode:
            enabled_crafts = [item for item, enabled in self.settings.get("auto_craft_item", {}).items() if enabled]
            craft_list = ', '.join(enabled_crafts) if enabled_crafts else "None Selected"
            emb.add_field(name="Crafting", value=craft_list, inline=False)
        else:
            try:
                aura = get_latest_equipped_aura()
                emb.add_field(name="Current Aura", value=aura if aura else "Unknown", inline=True)
            except Exception as e:
                self.logger.write_log(f"Error sending start aura notification: {e}")
                emb.add_field(name="Current Aura", value="Unknown", inline=True) 
            try:
                biome = get_latest_hovertext()
                emb.add_field(name="Current Biome", value=biome if biome else "Unknown", inline=True)
            except Exception:
                self.logger.write_log(f"Error sending start biome notification: {e}")
                emb.add_field(name="Current Biome", value="Unknown", inline=True)
        emb.add_field(name="Active Webhooks:", value=f"{len(self.settings.get('SECONDARY_WEBHOOK_URLS', [])) + 1}")

        try:
            if self.webhook:
                self.webhook.send(embed=emb)
                forward_webhook_msg(self.webhook.url, self.settings.get("SECONDARY_WEBHOOK_URLS", []), embed=emb)
        except Exception as e:
            self.logger.write_log(f"Error sending start notification: {e}")

    def stop_macro(self):
        if not self.running:
            QMessageBox.warning(self, "Macro Not Running", "Macro is not currently running.")
            return

        self.logger.write_log("Stopping Macro... Signaling threads.")
        self.stop_event.set() 

        stop_sniper_thread = None
        if any(t.name == "SniperThread" for t in self.threads if t.is_alive()): 
            self.logger.write_log(" > Attempting to stop sniper tasks explicitly...")
            def run_stop_sniper():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    loop.run_until_complete(stop_snipers())
                    loop.close()
                    self.logger.write_log(" > stop_snipers() executed.")
                except RuntimeError as e:

                    self.logger.write_log(f" > Info during stop_snipers execution: {e}")
                except Exception as e:
                    self.logger.write_log(f" > Error stopping sniper tasks: {e}", level="ERROR")
                    import traceback
                    self.logger.write_log(traceback.format_exc())

            stop_sniper_thread = threading.Thread(target=run_stop_sniper, daemon=True, name="StopSniperThread")
            stop_sniper_thread.start()

        timeout_per_thread = 2 
        start_time = time.time()

        threads_to_join = [t for t in self.threads if t != threading.current_thread() and t.is_alive()]

        if stop_sniper_thread:
            threads_to_join = [t for t in threads_to_join if t != stop_sniper_thread]

        self.logger.write_log(f"Waiting for {len(threads_to_join)} core/plugin threads to stop...")
        total_timeout = start_time + timeout_per_thread * len(threads_to_join)
        for thread in threads_to_join:
            if thread.is_alive():
                try:

                    time_left = max(0.1, total_timeout - time.time())
                    thread.join(timeout=time_left)
                    if thread.is_alive():
                        self.logger.write_log(f"Warning: Thread {thread.name} did not stop gracefully within timeout.")
                except Exception as e:
                    self.logger.write_log(f"Error joining thread {thread.name}: {e}")

        if stop_sniper_thread and stop_sniper_thread.is_alive():
            self.logger.write_log("Waiting for StopSniperThread to finish...")
            stop_sniper_thread.join(timeout=5) 
            if stop_sniper_thread.is_alive():
                 self.logger.write_log("Warning: StopSniperThread did not finish within its timeout.")

        self.logger.write_log("All threads signaled/joined.")
        self.running = False
        self.threads.clear() 
        self.stop_event.clear() 

        emb = discord.Embed(
            title="Macro Stopped",
            colour=discord.Colour.red(),
            timestamp=datetime.now() 
        )
        emb.set_footer(text=f"SolsScope v{LOCALVERSION}")
        if self.webhook:
            try:
                self.webhook.send(embed=emb)
                forward_webhook_msg(self.webhook.url, self.settings.get("SECONDARY_WEBHOOK_URLS", []), embed=emb)
            except Exception as e:
                self.logger.write_log(f"Error sending stop notification: {e}")
        QMessageBox.information(self, "Macro Stopped", "Macro has been stopped.")

    def on_press(self, key):
        try:
            if key == keyboard.Key.f1:

                self.start_macro_signal.emit()
            elif key == keyboard.Key.f2:

                self.stop_macro_signal.emit()
        except Exception as e:
            self.logger.write_log(f"Hotkey listener error: {e}")

    def start_key_listener(self):

        try:
            listener = keyboard.Listener(on_press=self.on_press)
            listener_thread = threading.Thread(target=listener.run, daemon=True, name="HotkeyListener")
            listener_thread.start()
            self.logger.write_log("Hotkey listener started (F1/F2 - PyQt).")

        except Exception as e:
            self.logger.write_log(f"Failed to start hotkey listener: {e}")
            QMessageBox.critical(self, "Hotkey Error", f"Could not start hotkey listener: {e}")

    def load_plugins(self):
        plugin_dir = os.path.join(self.MACROPATH, "plugins") 
        config_dir = os.path.join(plugin_dir, "config")
        os.makedirs(plugin_dir, exist_ok=True)
        os.makedirs(config_dir, exist_ok=True)

        plugin_files = glob.glob(os.path.join(plugin_dir, "*.py"))
        self.logger.write_log(f"Scanning for plugins in: {plugin_dir}")

        current_plugin_instances = {p.name: p for p in self.plugins if hasattr(p, "name")}

        loaded_plugin_files = set(os.path.abspath(p) for p in self.plugin_file_paths.values())
        found_plugin_files_this_scan = set() 

        for plugin_file in plugin_files:
            plugin_name_from_file = os.path.splitext(os.path.basename(plugin_file))[0]
            if plugin_name_from_file.startswith("__"): continue
            abs_plugin_file = os.path.abspath(plugin_file)
            found_plugin_files_this_scan.add(abs_plugin_file) 

            try:

                self.logger.write_log(f"Attempting to load plugin module: {plugin_name_from_file}")
                spec = importlib.util.spec_from_file_location(plugin_name_from_file, abs_plugin_file)
                if spec is None or spec.loader is None:
                     self.logger.write_log(f" > Could not create spec for plugin '{plugin_name_from_file}'. Skipping.")
                     continue
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if not hasattr(module, "Plugin"):
                    self.logger.write_log(f" > No 'Plugin' class found in {plugin_name_from_file}. Skipping.")
                    continue
                plugin_class = getattr(module, "Plugin")

                try:
                    temp_instance = plugin_class(self)
                    plugin_display_name = getattr(temp_instance, "name", plugin_name_from_file)
                    plugin_version = getattr(temp_instance, "version", "0.0.0")
                    plugin_author = getattr(temp_instance, "author", "Unknown")
                    required_macro_version = getattr(temp_instance, "requires", "0.0.0")

                    plugin_autocraft_compatible = getattr(temp_instance, "autocraft_compatible", False)
                    del temp_instance 
                except Exception as meta_e:
                    self.logger.write_log(f" > Error getting metadata from temporary instance of {plugin_name_from_file}: {meta_e}", level="ERROR")
                    continue 

                if parse_version(required_macro_version) > parse_version(LOCALVERSION):
                    self.logger.write_log(f" > Skipped Plugin: '{plugin_display_name}' requires macro v{required_macro_version}, but current is v{LOCALVERSION}.")
                    continue

                existing_plugin = current_plugin_instances.get(plugin_display_name)
                if existing_plugin:
                    existing_version = getattr(existing_plugin, "version", "0.0.0")
                    if parse_version(plugin_version) <= parse_version(existing_version):
                        continue
                    else:
                        self.logger.write_log(f"Found newer version {plugin_version} for plugin '{plugin_display_name}'. Reloading...")
                        self._unload_plugin(plugin_display_name)

                self.logger.write_log(f"Initializing final plugin instance: {plugin_display_name}")
                try:
                    plugin_instance = plugin_class(self)

                    plugin_instance.name = plugin_display_name
                    plugin_instance.version = plugin_version
                    plugin_instance.author = plugin_author

                    plugin_instance.autocraft_compatible = plugin_autocraft_compatible
                    plugin_instance.file_path = abs_plugin_file
                    plugin_instance.entries = {}
                    self.plugin_settings[plugin_instance.name] = plugin_instance.config
                except Exception as init_e:
                    self.logger.write_log(f" > Error initializing plugin '{plugin_display_name}': {init_e}", level="ERROR")
                    continue

                self.logger.write_log(f"Loading config for plugin: {plugin_display_name}")
                try:
                    if hasattr(plugin_instance, "load_or_create_config"):
                        plugin_instance.config = plugin_instance.load_or_create_config()
                    else:
                        plugin_instance.config = {}
                except Exception as config_e:
                    self.logger.write_log(f" > Error loading  config for plugin '{plugin_display_name}': {config_e}", level="WARN")
                    plugin_instance.config = {} 

                self.logger.write_log(f"Creating UI tab for plugin: {plugin_display_name}")
                plugin_tab = QWidget()
                plugin_tab_layout = QVBoxLayout(plugin_tab)

                self.tab_widget.addTab(plugin_tab, plugin_display_name)

                self.tab_entries[plugin_display_name] = plugin_instance.entries

                if hasattr(plugin_instance, "init_tab"):
                    gui_tools = {
                        "QtWidgets": __import__('PyQt6.QtWidgets'),
                        "QtCore": __import__('PyQt6.QtCore'),
                        "QtGui": __import__('PyQt6.QtGui'),
                        "QLabel": QLabel, "QLineEdit": QLineEdit, "QCheckBox": QCheckBox,
                        "QPushButton": QPushButton, "QTextEdit": QTextEdit, "QFrame": QFrame,
                        "QListWidget": QListWidget, "QScrollArea": QScrollArea, "QGroupBox": QGroupBox,
                        "QVBoxLayout": QVBoxLayout, "QHBoxLayout": QHBoxLayout, "QFormLayout": QFormLayout,
                        "QSpacerItem": QSpacerItem, "QSizePolicy": QSizePolicy,
                        "AlignmentFlag": Qt.AlignmentFlag,
                        "logger": self.logger,
                        "format_key": format_key,
                        "config": plugin_instance.config,
                        "entries": plugin_instance.entries,
                        "parent_layout": plugin_tab_layout,
                        "create_widgets": self.create_widgets,
                        "create_list_widget": self.create_list_widget,
                        "main_window": self
                    }
                    try:
                        plugin_instance.init_tab(gui_tools)
                    except Exception as tab_e:
                         self.logger.write_log(f" > Error running init_tab for plugin '{plugin_display_name}': {tab_e}", level="ERROR")
                         error_label = QLabel(f"Error loading plugin UI for {plugin_display_name}.\nCheck logs for details.")
                         error_label.setStyleSheet("color: red;")
                         plugin_tab_layout.addWidget(error_label)

                else:
                    default_label = QLabel("Plugin has no UI defined.")
                    plugin_tab_layout.addWidget(default_label)

                self.create_bottom_buttons(plugin_tab_layout)

                self.plugins.append(plugin_instance)
                self.plugin_file_paths[plugin_display_name] = plugin_instance.file_path
                self.logger.write_log(f" > Successfully loaded plugin: {plugin_display_name} v{plugin_version} from {os.path.basename(plugin_file)}")

            except Exception as e:
                self.logger.write_log(f"Error processing plugin file '{plugin_file}': {e}", level="ERROR")
                import traceback
                self.logger.write_log(traceback.format_exc()) 

        removed_plugin_files = loaded_plugin_files - found_plugin_files_this_scan
        if removed_plugin_files:
             self.logger.write_log(f"Detected removed plugin files: {removed_plugin_files}")
        for removed_file_path in removed_plugin_files:

            plugin_name_to_remove = None
            for name, path in self.plugin_file_paths.items():

                if os.path.abspath(path) == os.path.abspath(removed_file_path):
                    plugin_name_to_remove = name
                    break
            if plugin_name_to_remove:
                 self.logger.write_log(f"Unloading plugin '{plugin_name_to_remove}' as its file ({os.path.basename(removed_file_path)}) seems to be removed.")
                 self._unload_plugin(plugin_name_to_remove) 
            else:
                 self.logger.write_log(f"Could not find loaded plugin associated with removed file: {removed_file_path}", level="WARN")

    def _unload_plugin(self, plugin_name):
        """Handles the removal of a plugin instance and its UI by name."""
        plugin_instance = next((p for p in self.plugins if hasattr(p, 'name') and p.name == plugin_name), None)

        if not plugin_instance:
            self.logger.write_log(f"Cannot unload plugin '{plugin_name}': Instance not found.", level="WARN")
            return

        self.logger.write_log(f"Attempting to unload plugin: {plugin_name}")
        try:

            if hasattr(plugin_instance, "unload"):
                 self.logger.write_log(f" > Calling unload() method for {plugin_name}...")
                 plugin_instance.unload()

            tab_removed = False
            for i in range(self.tab_widget.count()):
                 if self.tab_widget.tabText(i) == plugin_name:
                     self.logger.write_log(f" > Removing tab '{plugin_name}' at index {i}...")
                     widget_to_remove = self.tab_widget.widget(i)
                     self.tab_widget.removeTab(i)
                     if widget_to_remove:
                          widget_to_remove.deleteLater() 
                          self.logger.write_log(f" > Scheduled deletion for tab widget of {plugin_name}.")
                     tab_removed = True
                     break 
            if not tab_removed:
                self.logger.write_log(f" > Tab for '{plugin_name}' not found in UI.", level="WARN")

            if plugin_name in self.tab_entries:
                del self.tab_entries[plugin_name]
                self.logger.write_log(f" > Removed '{plugin_name}' from tab_entries.")
            if plugin_name in self.plugin_file_paths:
                del self.plugin_file_paths[plugin_name]
                self.logger.write_log(f" > Removed '{plugin_name}' from plugin_file_paths.")
            if plugin_instance in self.plugins:
                self.plugins.remove(plugin_instance)
                self.logger.write_log(f" > Removed '{plugin_name}' instance from plugins list.")

            del plugin_instance
            self.logger.write_log(f"Successfully unloaded and deleted instance for plugin: {plugin_name}")

        except Exception as e:
             self.logger.write_log(f"Error during unload process for plugin '{plugin_name}': {e}", level="ERROR")
             import traceback
             self.logger.write_log(traceback.format_exc())

    def install_plugin(self):
        """Handles copying a plugin file and reloading plugins."""
        plugin_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Plugin File (.py)",
            ",".join(MACROPATH), 
            "Python Files (*.py)"
        )

        if not plugin_path:
            return 

        try:
            dest_dir = os.path.join(MACROPATH, "plugins")
            filename = os.path.basename(plugin_path)
            dest_path = os.path.join(dest_dir, filename)

            os.makedirs(dest_dir, exist_ok=True)

            if os.path.exists(dest_path):
                reply = QMessageBox.question(self, "Plugin Exists",
                                             f"Plugin '{filename}' already exists. Overwrite?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                             QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    return

            shutil.copy(plugin_path, dest_path)
            self.logger.write_log(f"Plugin '{filename}' copied to plugins directory.")

            self.load_plugins()

            QMessageBox.information(self, "Plugin Installed", f"Plugin '{filename}' installed successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Plugin Install Failed", f"Failed to install plugin:\n{e}")
            self.logger.write_log(f"Failed to install plugin '{plugin_path}': {e}")

    def closeEvent(self, event):
        """Handles the window close event."""
        confirm_exit = True
        if self.running:
            reply = QMessageBox.question(self, "Exit Confirmation",
                                         "Macro is running. Are you sure you want to stop and exit?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_macro() 

            else:
                confirm_exit = False
        else:
             reply = QMessageBox.question(self, "Exit Confirmation",
                                         "Are you sure you want to exit?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.Yes)
             if reply == QMessageBox.StandardButton.No:
                 confirm_exit = False

        if confirm_exit:
            self.logger.write_log("Exiting application.")

            event.accept() 
        else:
            event.ignore()
