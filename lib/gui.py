"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v2.0.0
Support server: https://discord.gg/8khGXqG7nA
"""

import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))

import time 
import json
import threading
from datetime import datetime, timedelta
import webbrowser
import shutil 
import urllib.request 
import glob 
import importlib.util
from packaging.version import parse as parse_version
import random
import requests

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QTabWidget, QLabel, QLineEdit, QCheckBox, QPushButton, QTextEdit,
    QScrollArea, QFrame, QMessageBox, QFileDialog, QListWidget, QListWidgetItem,
    QSizePolicy, QSpacerItem, QDialog, QDialogButtonBox, QGraphicsDropShadowEffect,
    QComboBox, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QMetaObject, Q_ARG, pyqtSlot, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QTextCursor, QPalette, QColor, QFont, QPainter, QLinearGradient, QBrush, QPainterPath 

from constants import (
    MACROPATH, LOCALVERSION, WEBHOOK_ICON_URL, STARTUP_MSGS,
    GENERAL_KEYS, AURAS_KEYS, BIOMES_KEYS, MERCHANT_KEYS,
    AUTOCRAFT_KEYS, OTHER_KEYS, QUEST_KEYS, COORDS, DEFAULTSETTINGS, PATH_KEYS,
    ACTIONS_KEYS, MARI_MERCHANT_KEYS, JESTER_MERCHANT_KEYS, AUTOCRAFT_ITEM_KEYS,
    BIOME_CONFIG_KEYS, GLITCHED_ITEMS_KEYS, DREAMSPACE_ITEMS_KEYS,
    DONOTDISPLAY, LIMBO_KEYS, DONOTACCEPTRESET, TOOLTIPS, SKIP_DLS_KEYS,
    MACRO_OVERRIDES, ACTIONS_CONFIG, USERDATA
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
from discord_utils import forward_webhook_msg

from macro_logic import (
    aura_detection, biome_detection, keep_alive, merchant_detection, auto_craft,
    auto_br, auto_sc, inventory_screenshot, storage_screenshot, disconnect_prevention,
    do_obby, auto_pop, use_item, auto_questboard, portable_crack, eden_detection,
    vok_taran
)

from stats import load_stats, load_all_biomes

from packager import PackageInstallerGUI

from calibrations import get_available_calibrations, CalibrationEditor, download_all_calibrations, get_best_calibration, get_screen_info

import pyautoscope

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from easyocr import Reader
    import cv2
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from pynput import keyboard, mouse
import mousekey as mk

import discord

from manager import ManagerGUI

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

from PyQt6.QtCore import pyqtProperty

class NumberAnimator(QObject):
    def __init__(self, start, end, update_func):
        super().__init__()
        self._value = start
        self.update_func = update_func
        self.anim = QPropertyAnimation(self, b"value")
        self.anim.setDuration(500)
        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        self.anim.valueChanged.connect(self.on_value_changed)

    def on_value_changed(self, value):
        self.update_func(int(value))

    def start(self):
        self.anim.start()

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    value = pyqtProperty(int, fget=get_value, fset=set_value)


class MainWindow(QMainWindow):

    start_macro_signal = pyqtSignal()
    stop_macro_signal = pyqtSignal()
    biomeStatChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.easter_eggs = self.generate_easter_eggs()

        self.settings = load_settings()

        # Apply custom styling first
        if "--no-theme" not in sys.argv:
            self.setup_custom_styling()

        self.logger = get_logger()

        self.original_settings = self.settings.copy()

        self.webhook = None
        self.threads = []
        self.running = False
        self.keyboard_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.sniped_event = threading.Event()
        self.pause_event = threading.Event()

        self.ignore_next_detection = set()
        self.ignore_lock = threading.Lock()
        self.items_crafted = 0
        self.start_time = 0

        # Initialize log storage for filtering
        self.all_log_messages = []

        self.plugins = []

        self.plugin_file_paths = {}

        self.mkey = mk.MouseKey()
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()

        self.MACROPATH = os.path.expandvars(r"%localappdata%\SolsScope")

        if self.easter_eggs["InvertedScope"]:
            self.setWindowTitle(f"InvertedScope v{LOCALVERSION} (PyQt)")
        else:
            self.setWindowTitle(f"SolsScope v{LOCALVERSION} (PyQt)")
        self.setGeometry(100, 100, 900, 650)  # Made slightly larger for better appearance

        # Remove window frame and add custom styling
        if "--no-theme" not in sys.argv:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Create main container with rounded corners
        self.main_container = QWidget()
        self.main_container.setObjectName("mainContainer")
        self.setCentralWidget(self.main_container)
        
        # Add drop shadow effect
        if "--no-theme" not in sys.argv:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 160))
            shadow.setOffset(0, 5)
            self.main_container.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(self.main_container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Add custom title bar
        if "--no-theme" not in sys.argv:
            self.create_title_bar(main_layout)

        icon_path = os.path.join(MACROPATH, "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        if self.settings.get("always_on_top", False):
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("customTabWidget")
        main_layout.addWidget(self.tab_widget)

        self.tab_entries = {}
        self.biome_stat_labels = {}
        self.biomeStatChanged.connect(self.update_biome_stats)

        self.create_tabs()

        self.logger.write_log("GUI Logger initialized (PyQt).")

        self.plugin_settings = {}

        if "--no-plugins" not in sys.argv:
            self.load_plugins()
        else:
            self.logger.write_log("Plugins skipped loading (--no-plugins).")

        self.start_key_listener()

        self.start_macro_signal.connect(self.start_macro)
        self.stop_macro_signal.connect(self.stop_macro)

        self.logger.write_log("GUI setup complete (PyQt).")

        self.logger.write_log(f"Detected username: {USERDATA.get('username')}")

    def generate_easter_eggs(self):
        ee = {}
        if random.randint(1, 1000) == 1:
            ee["InvertedScope"] = True
        else:
            ee["InvertedScope"] = False

        return ee


    def refresh_theme_dropdown(self):
        if hasattr(self, "theme_dropdown") and isinstance(self.theme_dropdown, QComboBox):
            self.theme_dropdown.clear()
            themes = [theme for theme in self.settings.get("themes", {})]
            self.theme_dropdown.addItems(themes)
            self.theme_dropdown.setCurrentText(self.settings.get("current_theme", "Default"))

    def refresh_calibrations_dropdown(self):
        if hasattr(self, "calibrations_dropdown") and isinstance(self.calibrations_dropdown, QComboBox):
            self.calibrations_dropdown.clear()
            self.calibrations_dropdown.addItems(get_available_calibrations())
            screen_info = get_screen_info()
            if self.settings.get("calibration", "") != "":
                self.calibrations_dropdown.setCurrentText(self.settings.get("calibration"))
            else:
                self.calibrations_dropdown.setCurrentText(get_best_calibration(screen_info["width"], screen_info["height"], screen_info["scale"], screen_info["windowed"]))

    def apply_theme_button(self, path = None):
        self.logger.write_log("Presenting user with theme file dialog prompt.")
        default_dir = os.path.join(MACROPATH, "theme")

        if not path:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Theme File",
                default_dir,
                "SolsScope Theme Files (*.ssthm)"
            )
        else:
            file_path = path

        if not file_path:
            self.logger.write_log("No theme selected.")
            return
        
        self.logger.write_log("Changing and saving new theme path to config.")

        try:
            dest_dir = os.path.join(MACROPATH, "theme")
            filename = os.path.basename(file_path)
            dest_path = os.path.join(dest_dir, filename)

            theme_name = filename.split(".")[0].capitalize()

            os.makedirs(dest_dir, exist_ok=True)

            try:
                shutil.copy(file_path, dest_path)
            except shutil.SameFileError:
                self.logger.write_log("Files are identical, skipping copying.")
            self.settings["current_theme"] = theme_name
            if not self.settings.get("themes", {}).get(theme_name):
                self.settings["themes"][theme_name] = dest_path
            self.logger.write_log(f"Theme '{theme_name}' copied to theme directory.")

        except Exception as e:
            QMessageBox.critical(self, "Theme Installation Failed", f"Failed to install theme:\n{e}")
            self.logger.write_log(f"Failed to install theme '{theme_name}': {e}")
        
        try:
            with open(get_settings_path(), "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            self.logger.write_log(f"Error whilst saving configuration: {e}")

        self.setup_custom_styling()
        self.refresh_theme_dropdown()
        self.logger.write_log(f"Applied theme {theme_name}.")

        if not path:
            QMessageBox.information(self, "Theme Applied", f"The theme {theme_name} has been applied.")

    def setup_custom_styling(self):
        """Apply custom theme styling to the application"""

        print("Applying custom theme to application.")
        style = self.load_theme(self.settings.get("themes", {}).get(self.settings.get("current_theme", "Default"), os.path.join(MACROPATH, "theme", "default.ssthm")))
        self.setStyleSheet(style)

    def load_theme(self, theme_path : str):

        DEFAULT_THEME = """
        /* Main Container */
        #mainContainer {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #2b2b2b, stop: 1 #1e1e1e);
            border-radius: 15px;
            border: 1px solid #404040;
        }

        /* Title Bar */
        #titleBar {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #3a3a3a, stop: 1 #2b2b2b);
            border-radius: 10px;
            border: 1px solid #505050;
            padding: 10px;
            min-height: 40px;
        }

        #titleLabel {
            color: #ffffff;
            font-size: 18px;
            font-weight: bold;
            background: transparent;
        }

        #titleButtons QPushButton {
            background: #404040;
            color: #ffffff;
            border: 1px solid #606060;
            border-radius: 8px;
            padding: 5px 15px;
            font-weight: bold;
            min-width: 40px;
        }

        #titleButtons QPushButton:hover {
            background: #505050;
            border-color: #707070;
        }

        #titleButtons QPushButton:pressed {
            background: #353535;
        }

        #closeButton {
            background: #e74c3c;
            border: 1px solid #c0392b;
        }

        #closeButton:hover {
            background: #c0392b;
        }

        #minimizeButton {
            background: #f39c12;
            border: 1px solid #e67e22;
        }

        #minimizeButton:hover {
            background: #e67e22;
        }

        /* Custom Tab Widget */
        #customTabWidget::pane {
            border: 1px solid #404040;
            background: #252525;
            border-radius: 10px;
            margin-top: 5px;
        }

        #customTabWidget::tab-bar {
            alignment: center;
        }

        #customTabWidget QTabBar::tab {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #404040, stop: 1 #353535);
            color: #cccccc;
            border: 1px solid #505050;
            border-bottom: none;
            padding: 12px 25px;
            margin-right: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: bold;
            font-size: 12px;
        }

        #customTabWidget QTabBar::tab:selected {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #0078d4, stop: 1 #005a9e);
            color: #ffffff;
            border-color: #0078d4;
        }

        #customTabWidget QTabBar::tab:hover:!selected {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #4a4a4a, stop: 1 #3a3a3a);
            color: #ffffff;
        }

        /* tab background */
        QWidget#tabContentWidget {
            background: #252525;
        }


        /* Scroll Areas */
        QScrollArea {
            border: none;
            background: transparent;
        }

        QScrollBar:vertical {
            background: #2b2b2b;
            border: none;
            width: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background: #505050;
            border-radius: 6px;
            min-height: 20px;
        }

        QScrollBar::handle:vertical:hover {
            background: #606060;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0;
        }

        /* Group Boxes */
        QGroupBox {
            color: #ffffff;
            font-weight: bold;
            font-size: 13px;
            border: 2px solid #404040;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #2f2f2f, stop: 1 #252525);
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 5px 10px;
            background: #0078d4;
            border-radius: 5px;
            color: #ffffff;
        }

        /* Labels */
        QLabel {
            color: #ffffff;
            font-size: 11px;
            background: transparent;
        }

        /* Input Fields */
        QLineEdit {
            background: #3a3a3a;
            border: 1px solid #505050;
            border-radius: 6px;
            padding: 8px 12px;
            color: #ffffff;
            font-size: 11px;
            selection-background-color: #0078d4;
        }

        QLineEdit:focus {
            border: 2px solid #0078d4;
            background: #404040;
        }

        QLineEdit:disabled {
            background: #2a2a2a;
            color: #666666;
        }

        /* Checkboxes */
        QCheckBox {
            color: #ffffff;
            font-size: 11px;
            spacing: 8px;
        }

        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 2px solid #505050;
            border-radius: 3px;
            background: #3a3a3a;
        }

        QCheckBox::indicator:checked {
            background: #0078d4;
            border-color: #0078d4;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTQiIGhlaWdodD0iMTQiIHZpZXdCb3g9IjAgMCAxNCAxNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTExLjMzMzMgMy41TDUuMjQ5OTkgOS41ODMzM0wyLjY2NjY2IDciIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
        }

        QCheckBox::indicator:hover {
            border-color: #0078d4;
        }

        /* Buttons */
        QPushButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #0078d4, stop: 1 #005a9e);
            color: #ffffff;
            border: 1px solid #005a9e;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 11px;
            min-height: 15px;
            min-width: 100px;
        }

        QPushButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #1084da, stop: 1 #0d70c4);
            border-color: #0d70c4;
        }

        QPushButton:pressed {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #005a9e, stop: 1 #004578);
        }

        QPushButton:disabled {
            background: #404040;
            color: #666666;
            border-color: #303030;
        }

        /* Special button styles */
        #startButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #27ae60, stop: 1 #1e8449);
            border: 1px solid #1e8449;
        }

        #startButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #2ecc71, stop: 1 #27ae60);
        }

        #stopButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #e74c3c, stop: 1 #c0392b);
            border: 1px solid #c0392b;
        }

        #stopButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #ec7063, stop: 1 #e74c3c);
        }

        #donateButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #f39c12, stop: 1 #e67e22);
            border: 1px solid #e67e22;
        }

        #donateButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #f5b041, stop: 1 #f39c12);
        }

        /* List Widgets */
        QListWidget {
            background: #3a3a3a;
            border: 1px solid #505050;
            border-radius: 6px;
            color: #ffffff;
            padding: 5px;
            selection-background-color: #0078d4;
        }

        QListWidget::item {
            padding: 8px;
            border-radius: 4px;
            margin: 1px;
        }

        QListWidget::item:selected {
            background: #0078d4;
        }

        QListWidget::item:hover {
            background: #505050;
        }

        /* Text Edit */
        QTextEdit {
            background: #2a2a2a;
            border: 1px solid #505050;
            border-radius: 6px;
            color: #ffffff;
            padding: 10px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 10px;
            selection-background-color: #0078d4;
        }

        /* Log Widget Special Styling */
        #logWidget {
            background: #1e1e1e;
            border: 2px solid #404040;
            border-radius: 8px;
            color: #ffffff;
            padding: 12px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 11px;
            line-height: 1.4;
        }

        /* Filter Frame */
        #filterFrame {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #3a3a3a, stop: 1 #2b2b2b);
            border: 1px solid #505050;
            border-radius: 8px;
            padding: 5px;
        }

        /* Combo Box Styling */
        QComboBox {
            background: #3a3a3a;
            border: 1px solid #505050;
            border-radius: 6px;
            padding: 6px 12px;
            color: #ffffff;
            font-size: 11px;
            min-height: 20px;
        }

        QComboBox:hover {
            background: #404040;
            border-color: #0078d4;
        }

        QComboBox:focus {
            border: 2px solid #0078d4;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: #505050;
            border-left-style: solid;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
            background: #404040;
        }

        QComboBox::down-arrow {
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDFMNiA2TDExIDEiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            width: 12px;
            height: 8px;
        }

        QComboBox QAbstractItemView {
            background: #3a3a3a;
            border: 1px solid #505050;
            border-radius: 6px;
            color: #ffffff;
            selection-background-color: #0078d4;
            outline: none;
        }

        QComboBox QAbstractItemView::item {
            padding: 8px 12px;
            border: none;
        }

        QComboBox QAbstractItemView::item:selected {
            background: #0078d4;
        }

        /* Frames */
        QFrame {
            background: transparent;
        }

        /* Message Boxes */
        QMessageBox {
            background: #2b2b2b;
            color: #ffffff;
        }

        QMessageBox QPushButton {
            min-width: 100px;
            padding: 8px 15px;
        }

        /* Credits Tab Styling */
        #creditsContainer {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #2f2f2f, stop: 1 #252525);
            border-radius: 10px;
            border: 1px solid #404040;
        }

        #developerCard {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #3a3a3a, stop: 1 #2b2b2b);
            border: 2px solid #505050;
            border-radius: 12px;
            padding: 15px;
            margin: 5px;
        }

        #developerCard:hover {
            border-color: #0078d4;
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #404040, stop: 1 #303030);
        }

        #sectionCard {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #353535, stop: 1 #282828);
            border: 1px solid #505050;
            border-radius: 8px;
            padding: 12px;
            margin: 3px;
        }

        #versionLabel {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                        stop: 0 #0078d4, stop: 1 #005a9e);
            color: #ffffff;
            border-radius: 15px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 12px;
        }

        #donateCardButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #f39c12, stop: 1 #e67e22);
            border: 2px solid #e67e22;
            border-radius: 10px;
            color: #ffffff;
            font-weight: bold;
            font-size: 12px;
            padding: 12px 20px;
            min-height: 20px;
        }

        #donateCardButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #f5b041, stop: 1 #f39c12);
            border-color: #f39c12;
        }

        #donateCardButton:pressed {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #e67e22, stop: 1 #d68910);
        }

        QWidget#popoutConfigBox {
            background: #252525;
        }

        QDialog#popoutWindow {
            background: #252525;
        }

        /* Main CalibrationEditor window */
        QWidget#CalibrationEditor {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #2f2f2f, stop:1 #252525);
        }

        /* Scroll area content widget */
        QWidget#CalibrationEditorContent {
            background: transparent;  /* inherit from parent */
        }

        QDialog#screenRegionDialog {
            background: #2f2f2f;
            border: 2px solid #404040;
            border-radius: 10px;
            padding: 15px;
        }
        QDialog#screenRegionDialogContent {
            background: transparent;
        }

        /* =========================
        Manager Window Styling
        ========================= */
        QWidget#ManagerGUI {
            background: qlineargradient(
                x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #2f2f2f, stop: 1 #1e1e1e
            );
            border: 1px solid #404040;
            border-radius: 12px;
            color: #ffffff;
            padding: 8px;
        }

        QWidget#ManagerGUI QLabel {
            color: #e0e0e0;
            font-weight: bold;
        }

        QWidget#ManagerGUI QTextEdit {
            background: #1a1a1a;
            color: #dcdcdc;
            border: 1px solid #3c3c3c;
            border-radius: 6px;
            padding: 6px;
        }

        QWidget#ManagerGUI QPushButton {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #3c3c3c, stop:1 #2a2a2a
            );
            border: 1px solid #555555;
            border-radius: 6px;
            color: #ffffff;
            padding: 4px 12px;
        }

        QWidget#ManagerGUI QPushButton:hover {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #505050, stop:1 #3a3a3a
            );
        }

        QWidget#ManagerGUI QListWidget {
            background: #1f1f1f;
            border: 1px solid #3c3c3c;
            border-radius: 6px;
            color: #dcdcdc;
        }

        /* Package Installer - Default Theme */
        QDialog#PackageInstallerGUI {
            background: #f0f0f0;
            border: 1px solid #aaa;
            border-radius: 10px;
            padding: 12px;
        }

        QDialog#PackageInstallerGUI QLabel {
            color: #222;
            font-size: 12px;
            font-weight: bold;
        }

        QDialog#PackageInstallerGUI QProgressBar {
            border: 1px solid #aaa;
            border-radius: 6px;
            background: #ddd;
            text-align: center;
            color: #222;
        }

        QDialog#PackageInstallerGUI QProgressBar::chunk {
            background: #5aa0f0;
            border-radius: 6px;
        }
        """

        def validate_theme(theme_text: str) -> bool:
            theme_text = theme_text.lower()
            found_selectors = []

            required_selectors = {
                "#maincontainer", "#titlebar", "#titlelabel",
                "#titlebuttons qpushbutton", "#closebutton", "#minimizebutton",
                "#customtabwidget::pane", "#customtabwidget::tab-bar",
                "#customtabwidget qtabbar::tab", "#customtabwidget qtabbar::tab:selected",
                "#customtabwidget qtabbar::tab:hover:!selected",
                "qwidget#tabcontentwidget", "qscrollarea", "qscrollbar:vertical",
                "qscrollbar::handle:vertical", "qscrollbar::handle:vertical:hover",
                "qscrollbar::add-line:vertical", "qscrollbar::sub-line:vertical",
                "qgroupbox", "qgroupbox::title", "qlabel", "qlineedit",
                "qlineedit:focus", "qlineedit:disabled", "qcheckbox",
                "qcheckbox::indicator", "qcheckbox::indicator:checked",
                "qcheckbox::indicator:hover", "qpushbutton", "qpushbutton:hover",
                "qpushbutton:pressed", "qpushbutton:disabled", "#startbutton",
                "#startbutton:hover", "#stopbutton", "#stopbutton:hover",
                "#donatebutton", "#donatebutton:hover", "qlistwidget",
                "qlistwidget::item", "qlistwidget::item:selected",
                "qlistwidget::item:hover", "qtextedit", "#logwidget",
                "#filterframe", "qcombobox", "qcombobox:hover", "qcombobox:focus",
                "qcombobox::drop-down", "qcombobox::down-arrow",
                "qcombobox qabstractitemview", "qcombobox qabstractitemview::item",
                "qcombobox qabstractitemview::item:selected", "qframe", "qmessagebox",
                "qmessagebox qpushbutton", "#creditscontainer", "#developercard",
                "#developercard:hover", "#sectioncard", "#versionlabel",
                "#donatecardbutton", "#donatecardbutton:hover", "#donatecardbutton:pressed",
                "qdialog#popoutwindow", "qwidget#popoutconfigbox", "qwidget#calibrationeditor",
                "qwidget#calibrationeditorcontent", "qdialog#screenregiondialog",
                "qdialog#screenregiondialogcontent"
            }

            for sel in required_selectors:
                if sel in theme_text:
                    found_selectors.append(sel)

            missing = sorted(req for req in required_selectors if req not in found_selectors)

            if missing:
                print(f"Theme validation failed. Missing selectors:\n" + "\n".join(missing))
                return False

            if theme_text.count('{') != theme_text.count('}'):
                print("Theme validation failed: mismatched curly braces.")
                return False

            return True

        try:
            if not os.path.exists(theme_path) or not theme_path.lower().endswith(".ssthm"):
                print("Theme does not exist or is not a .ssthm file.")
                return DEFAULT_THEME

            with open(theme_path, "r", encoding="utf-8") as f:
                theme_content = f.read()

            if validate_theme(theme_content):
                print("Theme was valid!")
                return theme_content
            else:
                print("Theme was not valid (did not contain all required items)")
                return DEFAULT_THEME

        except Exception as e:
            print(f"Error whilst loading theme: {e}")
            return DEFAULT_THEME

    def create_title_bar(self, layout):
        """Create a custom title bar with close and minimize buttons"""
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(60)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 10, 15, 10)
        
        # Title label
        title_label = QLabel(f"SolsScope v{LOCALVERSION}")
        title_label.setObjectName("titleLabel")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # Window control buttons
        button_container = QWidget()
        button_container.setObjectName("titleButtons")
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(5)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Minimize button
        minimize_btn = QPushButton("−")
        minimize_btn.setObjectName("minimizeButton")
        minimize_btn.setFixedSize(45, 25)
        minimize_btn.clicked.connect(self.showMinimized)
        button_layout.addWidget(minimize_btn)
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setObjectName("closeButton")
        close_btn.setFixedSize(45, 25)
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        title_layout.addWidget(button_container)
        layout.addWidget(title_bar)

        # Make title bar draggable
        self.title_bar = title_bar
        self.drag_position = None

    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.title_bar.geometry().contains(event.position().toPoint()):
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release to stop dragging"""
        self.drag_position = None

    def create_tabs(self):

        tab_info = {
            "General": GENERAL_KEYS,
            "Auras": AURAS_KEYS,
            "Biomes": BIOMES_KEYS,
            "Actions": ACTIONS_KEYS,
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
            scroll_content_widget.setObjectName("tabContentWidget")
            scroll_area.setWidget(scroll_content_widget)
            content_layout = QVBoxLayout(scroll_content_widget) 
            content_layout.setAlignment(Qt.AlignmentFlag.AlignTop) 

            self.tab_entries[tab_name] = {}

            self.populate_tab(content_layout, keys, self.tab_entries[tab_name])

            if tab_name == "General":
                self.add_general_tab_extras(content_layout) 
            if tab_name == "Actions":
                self.add_actions_tab_extras(content_layout) 
            if tab_name == "Biomes":
                self.add_biomes_tab_extras(content_layout)
            if tab_name == "Other":
                self.add_other_tab_extras(content_layout) 

            self.create_bottom_buttons(tab_layout, tab_name) 

            self.tab_widget.addTab(tab_widget, tab_name)

        self.create_logs_tab()

        self.create_credits_tab()

    def populate_tab(self, layout, keys, entry_dict):
        """Populates a tab layout with widgets based on settings keys."""
        settings_subset = {k: self.settings.get(k, DEFAULTSETTINGS.get(k)) for k in keys}
        self.create_widgets(settings_subset, layout, entry_dict)

    def apply_selected_theme(self, dropdown):
        selected_theme = dropdown.currentText()
        theme_path = self.settings.get("themes", {}).get(selected_theme)

        if not theme_path or not os.path.exists(theme_path):
            QMessageBox.warning(self, "Theme Error", f"Theme file for '{selected_theme}' not found.")
            return

        self.settings["current_theme"] = selected_theme

        try:
            with open(get_settings_path(), "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            self.logger.write_log(f"Error whilst saving configuration: {e}")

        self.setup_custom_styling()
        self.logger.write_log(f"Applied theme {selected_theme} from dropdown.")
        QMessageBox.information(self, "Theme Applied", f"Theme '{selected_theme}' has been applied.")

    def start_calibration(self, calibration_name):
        self.hide()
        editor = CalibrationEditor(calibration_name=calibration_name, theme_style=self.load_theme(self.settings.get("themes", {}).get(self.settings.get("current_theme", "Default"), os.path.join(MACROPATH, "theme", "default.ssthm"))), parent=self)
        editor.setWindowFlags(editor.windowFlags() | Qt.WindowType.Window)
        editor.show()

    def dl_calibrations(self):
        download_all_calibrations()
        self.refresh_calibrations_dropdown()

    
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

            tooltip_text = TOOLTIPS.get(key)
            if not isinstance(tooltip_text, str):
                tooltip_text = None

            label = QLabel(formatted_key + ":")
            if tooltip_text:
                label.setToolTip(tooltip_text)
            else:
                label.setToolTip("No tooltip for this.")

            if key == "calibration":
                h_layout = QHBoxLayout()

                calibrations_dropdown = QComboBox()
                self.calibrations_dropdown = calibrations_dropdown
                options = get_available_calibrations()
                calibrations_dropdown.addItems(options)
                if value in options:
                    calibrations_dropdown.setCurrentText(value)
                h_layout.addWidget(calibrations_dropdown)
                entry_dict[key] = calibrations_dropdown

                cal_button = QPushButton("Calibrate")
                cal_button.setFixedWidth(100)
                cal_button.clicked.connect(lambda _, w=calibrations_dropdown: self.start_calibration(w.currentText()))
                h_layout.addWidget(cal_button)

                dl_button = QPushButton("Download Calibrations")
                dl_button.setFixedWidth(250)
                dl_button.clicked.connect(self.dl_calibrations)
                h_layout.addWidget(dl_button)

                form_layout.addRow(label, h_layout)
                self.refresh_calibrations_dropdown()
                continue

            if key == "mode":
                widget = QComboBox()
                modes = ["Normal", "Auto Craft", "Limbo", "IDLE"]
                if os.path.exists(os.path.join(self.MACROPATH, "plugins", "fishing.py")):
                    modes.append("Fishing")
                widget.addItems(modes)
                if value in modes:
                    widget.setCurrentText(value)
                form_layout.addRow(label, widget)
                entry_dict[key] = widget
                continue

            if key == "themes":
                themes_layout = QHBoxLayout()
                theme_dropdown = QComboBox()
                self.theme_dropdown = theme_dropdown
                
                themes = []
                todel = []
                for theme in self.settings.get("themes", {}):
                    if not os.path.exists(self.settings.get("themes", {}).get(theme, os.path.join(MACROPATH, "theme", "default.ssthm"))):
                        print(f"File for {theme} no longer exists, deleting.")
                        todel.append(theme)
                        continue
                    themes.append(theme)

                for tdl in todel:
                    del self.settings["themes"][tdl]
                try:
                    with open(get_settings_path(), "w", encoding="utf-8") as f:
                        json.dump(self.settings, f, indent=4)
                except Exception as e:
                    print(f"Error whilst saving configuration: {e}")
                theme_dropdown.addItems(themes)
                theme_dropdown.setCurrentText(self.settings.get("current_theme", "Default"))
                
                apply_button = QPushButton("Apply")
                apply_button.clicked.connect(lambda: self.apply_selected_theme(theme_dropdown))
                
                themes_layout.addWidget(theme_dropdown, stretch=4)
                themes_layout.addWidget(apply_button, stretch=1)
                
                form_layout.addRow(label, themes_layout)
                entry_dict[key] = theme_dropdown
                continue

            if key == "reset_aura":
                with open(get_auras_path(), "r", encoding="utf-8") as f:
                    auras_data = json.load(f)
                    _auras = []
                    for aura in auras_data:
                        if "★" in aura or "\u00e2\u02dc\u2026" in aura or aura in DONOTACCEPTRESET or ":" in aura or "__TIMESTAMP__" in aura:
                            continue
                        _auras.append(aura)
                widget = QComboBox()
                widget.addItems(_auras)
                if value in _auras:
                    widget.setCurrentText(value)
                form_layout.addRow(label, widget)
                entry_dict[key] = widget
                continue

            if key == "vip_status":
                widget = QComboBox()
                options = ["No VIP", "VIP", "VIP+"]
                widget.addItems(options)
                if value in options:
                    widget.setCurrentText(value)
                form_layout.addRow(label, widget)
                entry_dict[key] = widget
                continue

            if key == "merchant_detection_type":
                widget = QComboBox()
                options = ["Legacy", "Logs"]
                widget.addItems(options)
                if value in options:
                    widget.setCurrentText(value)
                form_layout.addRow(label, widget)
                entry_dict[key] = widget
                continue

            if key == "interaction_type":
                widget = QComboBox()
                options = ["Mouse", "UI Navigation"]
                widget.addItems(options)
                if value in options:
                    widget.setCurrentText(value)
                form_layout.addRow(label, widget)
                entry_dict[key] = widget
                continue

            if isinstance(value, dict):
                group_box = QGroupBox(formatted_key) 
                group_box.setCheckable(False) 
                group_layout = QVBoxLayout(group_box) 
                group_layout.setContentsMargins(10, 15, 10, 10)
                if tooltip_text:
                    group_box.setToolTip(tooltip_text)
                else:
                    group_box.setToolTip("No tooltip for this.")
                form_layout.addRow(group_box) 
                entry_dict[key] = {}
                self.create_widgets(value, group_layout, entry_dict[key])

            elif isinstance(value, list):
                list_container_widget = QWidget()
                list_layout = QVBoxLayout(list_container_widget)
                list_layout.setContentsMargins(0, 0, 0, 0) 
                list_widget_data = self.create_list_widget(list_layout, key, value, entry_dict)
                form_layout.addRow(label, list_container_widget)
                entry_dict[key] = list_widget_data

            elif isinstance(value, bool):
                widget = QCheckBox()
                widget.setChecked(value)
                form_layout.addRow(label, widget)
                entry_dict[key] = widget

            else:
                widget = QLineEdit(str(value))
                form_layout.addRow(label, widget)
                entry_dict[key] = widget

    def create_widgets_plugin(self, settings_subset, parent_layout, entry_dict, TOOLTIPS):
        """Recursively creates widgets for plugin items using PyQt layouts."""

        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(15) 
        form_layout.setVerticalSpacing(10)   
        parent_layout.addLayout(form_layout)

        for key, value in settings_subset.items():
            if key in DONOTDISPLAY:
                continue

            formatted_key = format_key(key)

            tooltip_text = TOOLTIPS.get(key)
            if not isinstance(tooltip_text, str):
                tooltip_text = None

            label = QLabel(formatted_key + ":")
            if tooltip_text:
                label.setToolTip(tooltip_text)
            else:
                label.setToolTip("No tooltip for this.")

            if isinstance(value, dict):
                group_box = QGroupBox(formatted_key) 
                group_box.setCheckable(False) 
                group_layout = QVBoxLayout(group_box) 
                group_layout.setContentsMargins(10, 15, 10, 10)
                if tooltip_text:
                    group_box.setToolTip(tooltip_text)
                else:
                    group_box.setToolTip("No tooltip for this.")
                form_layout.addRow(group_box) 
                entry_dict[key] = {}
                self.create_widgets(value, group_layout, entry_dict[key])

            elif isinstance(value, list):
                list_container_widget = QWidget()
                list_layout = QVBoxLayout(list_container_widget)
                list_layout.setContentsMargins(0, 0, 0, 0) 
                list_widget_data = self.create_list_widget(list_layout, key, value, entry_dict)
                form_layout.addRow(label, list_container_widget)
                entry_dict[key] = list_widget_data

            elif isinstance(value, bool):
                widget = QCheckBox()
                widget.setChecked(value)
                form_layout.addRow(label, widget)
                entry_dict[key] = widget

            else:
                widget = QLineEdit(str(value))
                form_layout.addRow(label, widget)
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
        controls_layout.setSpacing(10)
        parent_layout.addLayout(controls_layout) 

        add_entry = QLineEdit()
        add_entry.setPlaceholderText("Enter item to add...")
        add_entry.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        controls_layout.addWidget(add_entry)

        add_button = QPushButton("Add")
        add_button.setMinimumWidth(100)
        add_button.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        controls_layout.addWidget(add_button)

        remove_button = QPushButton("Remove")
        remove_button.setMinimumWidth(100)
        remove_button.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
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
    
    def add_general_tab_extras(self, layout):

        button_frame = QFrame()
        button_layout = QVBoxLayout(button_frame)
        button_layout.setSpacing(10)

        # Data Download Settings Button
        skip_ddl_button = QPushButton("Data Download Settings")
        skip_ddl_button.setToolTip("Configure settings relating to the downloading of data from Github.")
        skip_ddl_button.clicked.connect(self.open_skip_ddl_settings)
        skip_ddl_button.setStyleSheet("text-align: left; padding: 8px; font-size: 11px;")
        skip_ddl_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout.addWidget(skip_ddl_button)

        layout.addWidget(button_frame)

    def add_other_tab_extras(self, layout):

        button_frame = QFrame()
        button_layout = QVBoxLayout(button_frame)
        button_layout.setSpacing(10)

        # Macro Overrides Settings Button
        overrides_button = QPushButton("Macro Overrides")
        overrides_button.setToolTip("Toggle macro overrides (Not Recommended).")
        overrides_button.clicked.connect(self.open_overrides_settings)
        overrides_button.setStyleSheet("text-align: left; padding: 8px; font-size: 11px;")
        overrides_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout.addWidget(overrides_button)

        layout.addWidget(button_frame)

    def add_actions_tab_extras(self, layout):
        """Adds action configuration buttons to the Actions tab layout."""
        
        # Add a section header
        header_label = QLabel("Action Configuration")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0px;")
        layout.addWidget(header_label)
        
        # Create a frame for the buttons
        button_frame = QFrame()
        button_layout = QVBoxLayout(button_frame)
        button_layout.setSpacing(10)
        
        uinav_button = QPushButton("Actions Controls")
        uinav_button.setToolTip("Toggle Actions options.")
        uinav_button.clicked.connect(self.open_uinav_controls_settings)
        uinav_button.setStyleSheet("text-align: left; padding: 8px; font-size: 11px;")
        uinav_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout.addWidget(uinav_button)

        # Mari Merchant Settings Button
        mari_button = QPushButton("Mari Merchant Settings")
        mari_button.setToolTip("Configure Mari merchant auto-purchase and ping settings")
        mari_button.clicked.connect(self.open_mari_settings)
        mari_button.setStyleSheet("text-align: left; padding: 8px; font-size: 11px;")
        mari_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout.addWidget(mari_button)
        
        # Jester Merchant Settings Button  
        jester_button = QPushButton("Jester Merchant Settings")
        jester_button.setToolTip("Configure Jester merchant auto-purchase, auto-sell, and ping settings")
        jester_button.clicked.connect(self.open_jester_settings)
        jester_button.setStyleSheet("text-align: left; padding: 8px; font-size: 11px;")
        jester_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout.addWidget(jester_button)
        
        # Auto Craft Settings Button
        craft_button = QPushButton("Auto Craft Item Settings")
        craft_button.setToolTip("Configure which items to auto-craft and craft settings")
        craft_button.clicked.connect(self.open_autocraft_settings)
        craft_button.setStyleSheet("text-align: left; padding: 8px; font-size: 11px;")
        craft_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout.addWidget(craft_button)

        # Auto Quest Settings Button
        quest_button = QPushButton("Auto Quest Settings")
        quest_button.setToolTip("Configure settings relating to Auto Quest")
        quest_button.clicked.connect(self.open_autoquest_settings)
        quest_button.setStyleSheet("text-align: left; padding: 8px; font-size: 11px;")
        quest_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout.addWidget(quest_button)
        
        layout.addWidget(button_frame)

    def update_biome_stats(self, biome_name):
        """Reload from file and animate stat change."""
        stats = load_stats()
        if biome_name in self.biome_stat_labels:
            label = self.biome_stat_labels[biome_name]

            old_value = int(label.text().split(":")[1])
            new_value = stats[biome_name.lower()]["amount"]

            self.animate_stat_change(label, biome_name, old_value, new_value)

    def animate_stat_change(self, label, biome_name, start, end):
        def update_label(val):
            label.setText(f"{biome_name.upper()}: {val}")

        animator = NumberAnimator(start, end, update_label)
        animator.start()

    def setup_glitched_animation(self):
        self.glitched_chars = ['▓', '▒', '░', '█', '▌', '▐', '▖', '▗']
        self.glitched_index = 0

        self.glitched_label = self.biome_stat_labels.get("glitched")
        if not self.glitched_label:
            return

        self.glitched_timer = QTimer()
        self.glitched_timer.timeout.connect(self.update_glitched_animation)
        self.glitched_timer.start(100)

    def update_glitched_animation(self):
        base_word = "GLITCHED"
        glitch_chars = ['%', '$', '@', '#', '*', '&', '!', '?', '▓', '▒', '░']
        glitch_chance = 0.3

        glitched_word_chars = []
        for c in base_word:
            if c.isalpha() and random.random() < glitch_chance:
                glitched_char = random.choice(glitch_chars)
                glitched_word_chars.append(glitched_char)
            else:
                glitched_word_chars.append(c)

        glitched_word = "".join(glitched_word_chars)

        amount = self.stats.get("glitched", {}).get("amount", 0) if hasattr(self, 'stats') else 0
        self.glitched_label.setText(f"{glitched_word}: {amount}")


    def add_biomes_tab_extras(self, layout):
        """Adds biome statistics and configuration buttons to the Biomes tab layout."""

        stats_frame = QFrame()
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setSpacing(5)
        stats_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        stats_header = QLabel("Biome Statistics")
        stats_header.setStyleSheet("""
            font-weight: bold;
            font-size: 14px;
            margin-top: 0px;   /* Raise */
            margin-bottom: 5px;
        """)
        stats_layout.addWidget(stats_header)

        self.biome_stat_labels = {}

        biomes = load_all_biomes()

        for biome_name, biome_data in load_stats().items():
            stat_row = QHBoxLayout()

            color_label = QLabel()
            color_label.setFixedSize(12, 12)
            color_label.setStyleSheet(f"background-color: {biome_data['colour']}; border: 1px solid black;")
            stat_row.addWidget(color_label)
            if biomes.get(biome_name):
                if biomes.get(biome_name).get("display_name"):
                    count_label = QLabel(f"{biomes.get(biome_name).get("display_name").upper()}: {biome_data['amount']}")
                else:
                    count_label = QLabel(f"{biome_name.upper()}: {biome_data['amount']}")
            else:
                count_label = QLabel(f"{biome_name.upper()}: {biome_data['amount']}")
            count_label.setStyleSheet("font-size: 11px; margin-left: 5px;")
            stat_row.addWidget(count_label)

            self.biome_stat_labels[biome_name] = count_label

            stat_row.addStretch()
            stats_layout.addLayout(stat_row)

        self.setup_glitched_animation()

        top_row_frame = QFrame()
        top_row_layout = QHBoxLayout(top_row_frame)
        top_row_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        left_side_frame = QFrame()
        left_side_layout = QVBoxLayout(left_side_frame)

        header_label = QLabel("Biome Configuration")
        header_label.setStyleSheet("""
            font-weight: bold;
            font-size: 14px;
            margin-top: 0px;   /* Align with stats header */
            margin-bottom: 10px;
        """)
        left_side_layout.addWidget(header_label)

        top_row_layout.addWidget(left_side_frame, stretch=2)
        top_row_layout.addWidget(stats_frame, stretch=1)

        layout.addWidget(top_row_frame)

        button_frame = QFrame()
        button_layout = QVBoxLayout(button_frame)
        button_layout.setSpacing(10)

        biome_config_button = QPushButton("Biome Notification Settings")
        biome_config_button.setToolTip("Configure which biomes to send notifications for")
        biome_config_button.clicked.connect(self.open_biome_config_settings)
        biome_config_button.setStyleSheet("text-align: left; padding: 8px; font-size: 11px;")
        biome_config_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout.addWidget(biome_config_button)

        limbo_config_button = QPushButton("Limbo Mode Settings")
        limbo_config_button.setToolTip("Configure settings relating to limbo mode")
        limbo_config_button.clicked.connect(self.open_limbo_settings)
        limbo_config_button.setStyleSheet("text-align: left; padding: 8px; font-size: 11px;")
        limbo_config_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout.addWidget(limbo_config_button)

        glitched_button = QPushButton("Auto Use Items In Glitched Settings")
        glitched_button.setToolTip("Configure which items to automatically use when in Glitched biome")
        glitched_button.clicked.connect(self.open_glitched_items_settings)
        glitched_button.setStyleSheet("text-align: left; padding: 8px; font-size: 11px;")
        glitched_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout.addWidget(glitched_button)

        dreamspace_button = QPushButton("Auto Use Items In Dreamspace Settings")
        dreamspace_button.setToolTip("Configure which items to automatically use when in Dreamspace biome")
        dreamspace_button.clicked.connect(self.open_dreamspace_items_settings)
        dreamspace_button.setStyleSheet("text-align: left; padding: 8px; font-size: 11px;")
        dreamspace_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout.addWidget(dreamspace_button)

        left_side_layout.addWidget(button_frame)
        layout.addSpacing(10)


    def open_biome_config_settings(self):
        """Open biome configuration settings dialog."""
        current_settings = load_settings()
        dialog = BiomeConfigDialog(current_settings, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_settings = dialog.get_updated_settings()
            # Update the current settings
            for key, value in updated_settings.items():
                current_settings[key] = value
            # Save settings
            update_settings(current_settings)
            self.show_status_message("Biome configuration settings saved successfully!", 3000)
    
    def open_glitched_items_settings(self):
        """Open glitched items settings dialog."""
        current_settings = load_settings()
        dialog = GlitchedItemsDialog(current_settings, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_settings = dialog.get_updated_settings()
            # Update the current settings
            for key, value in updated_settings.items():
                current_settings[key] = value
            # Save settings
            update_settings(current_settings)
            self.show_status_message("Glitched items settings saved successfully!", 3000)
    
    def open_dreamspace_items_settings(self):
        """Open dreamspace items settings dialog."""
        current_settings = load_settings()
        dialog = DreamspaceItemsDialog(current_settings, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_settings = dialog.get_updated_settings()
            # Update the current settings
            for key, value in updated_settings.items():
                current_settings[key] = value
            # Save settings
            update_settings(current_settings)
            self.show_status_message("Dreamspace items settings saved successfully!", 3000)

    def open_mari_settings(self):
        """Open Mari merchant settings dialog."""
        current_settings = load_settings()
        dialog = MariMerchantDialog(current_settings, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_settings = dialog.get_updated_settings()
            # Update the current settings
            for key, value in updated_settings.items():
                current_settings[key] = value
            # Save settings
            update_settings(current_settings)
            self.show_status_message("Mari merchant settings saved successfully!", 3000)
    
    def open_jester_settings(self):
        """Open Jester merchant settings dialog."""
        current_settings = load_settings()
        dialog = JesterMerchantDialog(current_settings, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_settings = dialog.get_updated_settings()
            # Update the current settings
            for key, value in updated_settings.items():
                current_settings[key] = value
            # Save settings
            update_settings(current_settings)
            self.show_status_message("Jester merchant settings saved successfully!", 3000)
    
    def open_autocraft_settings(self):
        """Open Auto Craft settings dialog."""
        current_settings = load_settings()
        dialog = AutoCraftDialog(current_settings, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_settings = dialog.get_updated_settings()
            # Update the current settings
            for key, value in updated_settings.items():
                current_settings[key] = value
            # Save settings
            update_settings(current_settings)
            self.show_status_message("Auto craft settings saved successfully!", 3000)

    def open_autoquest_settings(self):
        """Open Auto Quest settings dialog."""
        current_settings = load_settings()
        dialog = AutoQuestDialog(current_settings, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_settings = dialog.get_updated_settings()
            # Update the current settings
            for key, value in updated_settings.items():
                current_settings[key] = value
            # Save settings
            update_settings(current_settings)
            self.show_status_message("Auto Quest settings saved successfully!", 3000)

    def open_limbo_settings(self):
        """Open Limbo settings dialog."""
        current_settings = load_settings()
        dialog = LimboDialog(current_settings, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_settings = dialog.get_updated_settings()
            # Update the current settings
            for key, value in updated_settings.items():
                current_settings[key] = value
            # Save settings
            update_settings(current_settings)
            self.show_status_message("Limbo Mode settings saved successfully!", 3000)

    def open_skip_ddl_settings(self):
        """Open Skip Data Download settings dialog."""
        current_settings = load_settings()
        dialog = SkipDownloadsDialog(current_settings, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_settings = dialog.get_updated_settings()
            # Update the current settings
            for key, value in updated_settings.items():
                current_settings[key] = value
            # Save settings
            update_settings(current_settings)
            self.show_status_message("Data Download settings saved successfully!", 3000)

    def open_overrides_settings(self):
        """Open Macro Overrides dialog."""
        current_settings = load_settings()
        dialog = MacroOverrides(current_settings, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_settings = dialog.get_updated_settings()
            # Update the current settings
            for key, value in updated_settings.items():
                current_settings[key] = value
            # Save settings
            update_settings(current_settings)
            self.show_status_message("Macro Overrides saved successfully!", 3000)

    def open_uinav_controls_settings(self):
        """Open Actions Controls dialog."""
        current_settings = load_settings()
        dialog = UINavControls(current_settings, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_settings = dialog.get_updated_settings()
            # Update the current settings
            for key, value in updated_settings.items():
                current_settings[key] = value
            # Save settings
            update_settings(current_settings)
            self.show_status_message("Action Controls saved successfully!", 3000)

    def show_status_message(self, message, timeout=2000):
        """Show a temporary status message."""
        # For now, just show a simple message box
        # In a more advanced implementation, this could be a status bar message
        msg = QMessageBox(self)
        msg.setWindowTitle("SolsScope")
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def create_bottom_buttons(self, layout, tab_name):
        """Creates the Start/Stop/Save buttons at the bottom of a tab."""
        button_frame = QFrame() 
        button_frame.setObjectName("buttonFrame")
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 15, 0, 0) 
        button_layout.setSpacing(10)

        start_button = QPushButton("Start (F1)")
        start_button.setObjectName("startButton")
        start_button.clicked.connect(self.start_macro)
        button_layout.addWidget(start_button)

        stop_button = QPushButton("Stop (F2)")
        stop_button.setObjectName("stopButton")
        stop_button.clicked.connect(self.stop_macro)
        button_layout.addWidget(stop_button)

        button_layout.addStretch(1) 

        if tab_name.lower() == "other":
            theme_button = QPushButton("Open Extras")
            theme_button.clicked.connect(self.start_downloader)
            button_layout.addWidget(theme_button)
        else:
            save_button = QPushButton("Save Settings")
            save_button.clicked.connect(self.press_save_button)
            button_layout.addWidget(save_button)

        if tab_name.lower() == "other":
            rdl_button = QPushButton("Redownload Libraries")
            rdl_button.setObjectName("donateButton")
            rdl_button.clicked.connect(self.toggle_redownload)
            button_layout.addWidget(rdl_button)
        else:
            donate_button = QPushButton("Donate")
            donate_button.setObjectName("donateButton")
            donate_button.clicked.connect(self.open_donation_url)
            button_layout.addWidget(donate_button)

        layout.addWidget(button_frame)

    def toggle_redownload(self):
        
        save_success, error_occured = self.save_settings()
        
        if save_success:
            self.logger.write_log("Settings were saved")
        else:
            self.logger.write_log(f"Error Occured saving settings: {error_occured}")

        if not self.settings.get("redownload_libs_on_run", False):
            self.settings["redownload_libs_on_run"] = True
            QMessageBox.information(self, "SolsScope", "Required Libraries and paths will be redownloaded the next time the macro is run.")
            self.logger.write_log("Required Libraries and paths will be redownloaded the next time the macro is run.")
        else:
            self.settings["redownload_libs_on_run"] = False
            self.logger.write_log("Required Libraries and paths will not be redownloaded the next time the macro is run.")

        with open(get_settings_path(), "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4)
            self.logger.write_log("Updated config to decide redownload.")

    def start_downloader(self):
        try:
            pd_req = requests.get("https://raw.githubusercontent.com/bazthedev/SolsScope/refs/heads/main/plugins/plugin_index.json", timeout=10)
            plugin_data = pd_req.json()
        except Exception as e:
            plugin_data = {
                "Remote Bot": {
                    "name": "Remote Bot",
                    "description": "Control SolsScope remotely via a discord bot.",
                    "version": "1.0.4",
                    "authors": ["bazthedev"],
                    "requires_version": "2.0.0",
                    "plugin_requirements": [],
                    "download_url": "https://raw.githubusercontent.com/bazthedev/SolsScope/refs/heads/main/plugins/remote.py"
                },
                "Clipping": {
                    "name": "Clipping",
                    "description": "Clip Global rolls or record rare biomes.",
                    "version": "1.0.2",
                    "authors": ["bazthedev"],
                    "requires_version": "2.0.0",
                    "plugin_requirements": ["pygetwindow"],
                    "download_url": "https://raw.githubusercontent.com/bazthedev/SolsScope/refs/heads/main/plugins/clipping.py"
                }
            }

        try:
            th_req = requests.get("https://raw.githubusercontent.com/bazthedev/SolsScope/refs/heads/main/theme/theme_index.json", timeout=10)
            theme_data = th_req.json()
        except Exception as e:
            theme_data = {
                "Remote Bot": {
                    "name": "Remote Bot",
                    "description": "Control SolsScope remotely via a discord bot.",
                    "version": "1.0.4",
                    "authors": ["bazthedev"],
                    "requires_version": "2.0.0",
                    "plugin_requirements": [],
                    "download_url": "https://raw.githubusercontent.com/bazthedev/SolsScope/refs/heads/main/plugins/remote.py"
                },
                "Clipping": {
                    "name": "Clipping",
                    "description": "Clip Global rolls or record rare biomes.",
                    "version": "1.0.2",
                    "authors": ["bazthedev"],
                    "requires_version": "2.0.0",
                    "plugin_requirements": ["pygetwindow"],
                    "download_url": "https://raw.githubusercontent.com/bazthedev/SolsScope/refs/heads/main/plugins/clipping.py"
                }
            }

        self.manager_window = ManagerGUI(self, plugin_data, theme_data)
        self.manager_window.setModal(True)
        self.manager_window.exec()


    def create_logs_tab(self):
        logs_tab = QWidget()
        layout = QVBoxLayout(logs_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Create filter controls
        filter_frame = QFrame()
        filter_frame.setObjectName("filterFrame")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(10, 10, 10, 10)
        filter_layout.setSpacing(10)

        # Filter label
        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet("font-weight: bold; color: #ffffff;")
        filter_layout.addWidget(filter_label)

        # Level filter dropdown
        self.log_level_filter = QComboBox()
        self.log_level_filter.addItems(["All Levels", "INFO", "WARNING", "ERROR", "DEBUG"])
        self.log_level_filter.setMinimumWidth(120)
        self.log_level_filter.currentTextChanged.connect(self.filter_logs)
        filter_layout.addWidget(self.log_level_filter)

        # Search filter
        search_label = QLabel("Search:")
        search_label.setStyleSheet("font-weight: bold; color: #ffffff;")
        filter_layout.addWidget(search_label)

        self.log_search_filter = QLineEdit()
        self.log_search_filter.setPlaceholderText("Enter search term...")
        self.log_search_filter.textChanged.connect(self.filter_logs)
        self.log_search_filter.setMinimumWidth(200)
        filter_layout.addWidget(self.log_search_filter)

        filter_layout.addStretch()

        # Clear logs button
        clear_button = QPushButton("Clear Logs")
        clear_button.clicked.connect(self.clear_logs)
        clear_button.setMinimumWidth(100)
        filter_layout.addWidget(clear_button)

        # Export logs button
        export_button = QPushButton("Export Logs")
        export_button.clicked.connect(self.export_logs)
        export_button.setMinimumWidth(100)
        filter_layout.addWidget(export_button)

        layout.addWidget(filter_frame)

        # Create log display
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setObjectName("logWidget")
        layout.addWidget(self.log_widget)

        self.logger.connect_log_widget(self.append_log_message)

        self.tab_widget.addTab(logs_tab, "Logs")

    @pyqtSlot(str) 
    def append_log_message(self, message):
        """Appends a message to the log widget (thread-safe)."""
        # Add timestamp if not already present
        if not message.startswith('['):
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"[{timestamp}] {message}"
        
        # Store message for filtering
        self.all_log_messages.append(message)
        
        # Apply current filters and update display
        self.filter_logs()

    def filter_logs(self):
        """Filter logs based on current filter settings."""
        level_filter = self.log_level_filter.currentText()
        search_filter = self.log_search_filter.text().lower()
        
        filtered_messages = []
        
        for message in self.all_log_messages:
            # Apply level filter
            if level_filter != "All Levels":
                if level_filter not in message:
                    continue
            
            # Apply search filter
            if search_filter and search_filter not in message.lower():
                continue
                
            filtered_messages.append(message)
        
        # Update display
        self.log_widget.clear()
        for message in filtered_messages:
            self.log_widget.append(self.format_log_message(message))
        
        # Auto-scroll to bottom
        self.log_widget.moveCursor(QTextCursor.MoveOperation.End)

    def format_log_message(self, message):
        """Format log message with color coding based on level."""
        if "ERROR" in message:
            return f'<span style="color: #ff6b6b;">{message}</span>'
        elif "WARNING" in message:
            return f'<span style="color: #ffd93d;">{message}</span>'
        elif "DEBUG" in message:
            return f'<span style="color: #74c0fc;">{message}</span>'
        elif "INFO" in message:
            return f'<span style="color: #51cf66;">{message}</span>'
        else:
            return f'<span style="color: #ffffff;">{message}</span>'

    def clear_logs(self):
        """Clear all log messages."""
        reply = QMessageBox.question(
            self, "Clear Logs", 
            "Are you sure you want to clear all logs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.all_log_messages.clear()
            self.log_widget.clear()

    def export_logs(self):
        """Export logs to a text file."""
        if not self.all_log_messages:
            QMessageBox.information(self, "Export Logs", "No logs to export.")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"solsscope_logs_{timestamp}.txt"
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", default_filename, "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"SolsScope v{LOCALVERSION} Logs\n")
                    f.write(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for message in self.all_log_messages:
                        f.write(message + "\n")
                
                QMessageBox.information(self, "Export Complete", f"Logs exported to:\n{filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export logs:\n{str(e)}") 

    def create_credits_tab(self):
        """Populates the Credits tab with modern, compact design."""
        credits_tab = QWidget()
        credits_tab.setObjectName("creditsContainer")
        
        # Create scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Main layout for the tab
        tab_layout = QVBoxLayout(credits_tab)
        tab_layout.setContentsMargins(15, 15, 15, 15)
        tab_layout.addWidget(scroll_area)
        
        # Content widget inside scroll area
        content_widget = QWidget()
        content_widget.setObjectName("tabContentWidget")
        scroll_area.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Header section with title and version
        header_frame = QFrame()
        header_frame.setObjectName("sectionCard")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 15, 15, 15)
        header_layout.setSpacing(10)

        if self.easter_eggs["InvertedScope"]:
            title_label = QLabel("InvertedScope")
        else:
            title_label = QLabel("SolsScope")
            
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            margin: 0px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)

        version_label = QLabel(f"v{LOCALVERSION}")
        version_label.setObjectName("versionLabel")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(version_label)

        subtitle_label = QLabel("A powerful macro tool for Sol's RNG")
        subtitle_label.setStyleSheet("""
            font-size: 12px;
            color: #cccccc;
            font-style: italic;
        """)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle_label)

        layout.addWidget(header_frame)

        # Developers section in a grid layout
        developers_frame = QFrame()
        developers_frame.setObjectName("sectionCard")
        developers_layout = QVBoxLayout(developers_frame)
        developers_layout.setContentsMargins(15, 15, 15, 15)
        developers_layout.setSpacing(15)

        dev_title = QLabel("Developers")
        dev_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #0078d4;
            margin-bottom: 5px;
        """)
        developers_layout.addWidget(dev_title)

        # Developer cards in horizontal layout with proper alignment
        dev_cards_container = QWidget()
        dev_cards_layout = QGridLayout(dev_cards_container)
        dev_cards_layout.setSpacing(20)
        dev_cards_layout.setContentsMargins(0, 0, 0, 0)

        devs = [
            ("Baz", {"image": "baz.png", "role": "Lead Developer"}),
            ("cresqnt", {"image": "cresqnt.png", "role": "Lead Developer"}),
            ("Meklows", {"image": "meklows.jpg", "role" : "Developer"}),
            ("ManasAarohi", {"image": "manasaarohi.png", "role": "Lead Path Developer"}),
            ("Cyclate", {"image": "cyclate.png", "role": "Developer"})
        ]

        # Create developer cards
        for i, (dev_name, dev_info) in enumerate(devs):
            row = i // 2
            col = i % 2
            dev_card = self.create_developer_card(dev_name, dev_info)
            dev_cards_layout.addWidget(dev_card, row, col)

        # Add stretch to center the cards
        developers_layout.addWidget(dev_cards_container)
        layout.addWidget(developers_frame)

        # Acknowledgements section - more compact
        ack_frame = QFrame()
        ack_frame.setObjectName("sectionCard")
        ack_layout = QVBoxLayout(ack_frame)
        ack_layout.setContentsMargins(10, 10, 10, 10)
        ack_layout.setSpacing(8)

        ack_title = QLabel("Special Thanks")
        ack_title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #51cf66;
            margin-bottom: 5px;
        """)
        ack_layout.addWidget(ack_title)

        # Compact acknowledgements in a grid
        ack_grid = QHBoxLayout()
        ack_grid.setSpacing(20)
        
        left_acks = [
            "AllanQute (_justalin) - Path inspiration",
            "dolphSol - Creative inspiration",
            "Mr. Void - Helping with the logic for the new auto craft",
            "ethan03228 - Helping create calibrations",
            "gemz0649 - Helping create calibrations",
            "senatorarmstrong4017 - Helping create calibrations",
            "square.ow - Helping create calibrations"
        ]
        
        right_acks = [
            "vex (vexthecoder) - Feature ideas", 
            "Doors_Daisukiman - Testing help",
            "C (criticize) - For helping Scope to get to where it is today",
            "gummyballer - Helping create calibrations",
            "honzahomecoming - Helping create calibrations",
            "im_a_cro - Helping create calibrations"
        ]

        for ack_list in [left_acks, right_acks]:
            ack_column = QVBoxLayout()
            for ack in ack_list:
                ack_label = QLabel(f"• {ack}")
                ack_label.setStyleSheet("""
                    font-size: 10px;
                    color: #cccccc;
                    padding: 2px 0px;
                """)
                ack_column.addWidget(ack_label)
            ack_grid.addLayout(ack_column)

        ack_layout.addLayout(ack_grid)
        layout.addWidget(ack_frame)

        # Donations section
        self.create_donations_section(layout)

        # Support section with donate button
        support_frame = QFrame()
        support_frame.setObjectName("sectionCard")
        support_layout = QVBoxLayout(support_frame)
        support_layout.setContentsMargins(15, 15, 15, 15)
        support_layout.setSpacing(10)

        support_title = QLabel("Support the Project")
        support_title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #f39c12;
            text-align: center;
        """)
        support_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        support_layout.addWidget(support_title)

        support_desc = QLabel("Help us continue developing SolsScope!")
        support_desc.setStyleSheet("""
            font-size: 11px;
            color: #cccccc;
            text-align: center;
        """)
        support_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        support_layout.addWidget(support_desc)

        donate_btn = QPushButton("Donate Now")
        donate_btn.setObjectName("donateCardButton")
        donate_btn.clicked.connect(self.open_donation_url)
        support_layout.addWidget(donate_btn)

        layout.addWidget(support_frame)

        layout.addStretch()
        self.tab_widget.addTab(credits_tab, "Credits")

    def create_developer_card(self, name, info):
        """Create a modern developer card widget."""
        card = QFrame()
        card.setObjectName("developerCard")
        card.setFixedHeight(140)  # Slightly increased height to accommodate proper layout
        card.setMinimumWidth(280)  # Set minimum width for consistency
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(20, 15, 20, 15)
        card_layout.setSpacing(20)

        # Profile image container - properly added to layout
        image_container = QWidget()
        image_container.setFixedSize(90, 90)
        image_container_layout = QVBoxLayout(image_container)
        image_container_layout.setContentsMargins(0, 0, 0, 0)
        image_container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        image_label = QLabel()
        image_label.setFixedSize(80, 80)  # Slightly smaller for better proportion
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet("""
            background: transparent;
            border: none;
        """)

        # Load and set image
        self.load_developer_image(image_label, info["image"])
        image_container_layout.addWidget(image_label)
        
        # Add image container to main layout
        card_layout.addWidget(image_container)

        # Info section with proper spacing
        info_container = QWidget()
        info_container_layout = QVBoxLayout(info_container)
        info_container_layout.setContentsMargins(0, 0, 0, 0)
        info_container_layout.setSpacing(8)
        info_container_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # Center vertically

        name_label = QLabel(name)
        name_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
            margin: 0px;
        """)
        info_container_layout.addWidget(name_label)

        role_label = QLabel(info["role"])
        role_label.setStyleSheet("""
            font-size: 12px;
            color: #0078d4;
            font-weight: bold;
            margin: 0px;
        """)
        info_container_layout.addWidget(role_label)
        
        card_layout.addWidget(info_container, 1)

        return card

    def load_developer_image(self, image_label, image_filename):
        """Load developer image with fallback and create circular mask."""
        if PIL_AVAILABLE:
            try:
                image_path = os.path.join(MACROPATH, "img", image_filename)  # Updated path to img folder
                img_url = f"https://raw.githubusercontent.com/bazthedev/SolsScope/main/img/{image_filename}"

                if not os.path.exists(image_path):
                    self.logger.write_log(f"Downloading developer image: {image_filename}")
                    try:
                        # Ensure img directory exists
                        img_dir = os.path.join(MACROPATH, "img")
                        os.makedirs(img_dir, exist_ok=True)
                        
                        with urllib.request.urlopen(img_url, timeout=5) as response, open(image_path, 'wb') as out_file:
                            if response.status == 200:
                                shutil.copyfileobj(response, out_file)
                            else:
                                raise Exception(f"HTTP Error {response.status}")
                    except Exception as dl_error:
                        self.logger.write_log(f"Error downloading {image_filename}: {dl_error}")
                        self.set_fallback_image(image_label, image_filename.split('.')[0])
                        return

                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # Create circular image with proper size for new layout
                    circular_pixmap = self.create_circular_image(pixmap, 70)  # Adjusted size
                    image_label.setPixmap(circular_pixmap)
                else:
                    self.set_fallback_image(image_label, image_filename.split('.')[0])
                    
            except Exception as e:
                self.logger.write_log(f"Error processing developer image {image_filename}: {e}")
                self.set_fallback_image(image_label, image_filename.split('.')[0])
        else:
            self.set_fallback_image(image_label, "No PIL")

    def create_circular_image(self, source_pixmap, size):
        """Create a circular image from a square pixmap with shadow effect."""
        source_size = min(source_pixmap.width(), source_pixmap.height())
        
        if source_pixmap.width() > source_pixmap.height():
            x_offset = (source_pixmap.width() - source_size) // 2
            y_offset = 0
        else:
            x_offset = 0
            y_offset = (source_pixmap.height() - source_size) // 2
            
        square_pixmap = source_pixmap.copy(x_offset, y_offset, source_size, source_size)
        
        scaled_pixmap = square_pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        shadow_size = 4
        total_size = size + shadow_size * 2
        circular_pixmap = QPixmap(total_size, total_size)
        circular_pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(circular_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        shadow_path = QPainterPath()
        shadow_path.addEllipse(shadow_size + 2, shadow_size + 2, size, size)
        painter.fillPath(shadow_path, QBrush(QColor(0, 0, 0, 60)))  
        

        path = QPainterPath()
        path.addEllipse(shadow_size, shadow_size, size, size)
        

        painter.setClipPath(path)
        painter.drawPixmap(shadow_size, shadow_size, scaled_pixmap)
        
        # Add subtle border
        painter.setClipping(False)
        painter.setPen(QColor(80, 80, 80, 100))  
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(shadow_size, shadow_size, size, size)
        
        painter.end()
        
        return circular_pixmap

    def set_fallback_image(self, image_label, name):
        """Set a fallback text when image is not available."""
        # Create a circular fallback image with shadow
        size = 70  # Updated to match new image size
        shadow_size = 4
        total_size = size + shadow_size * 2
        fallback_pixmap = QPixmap(total_size, total_size)
        fallback_pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(fallback_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw shadow
        shadow_path = QPainterPath()
        shadow_path.addEllipse(shadow_size + 2, shadow_size + 2, size, size)
        painter.fillPath(shadow_path, QBrush(QColor(0, 0, 0, 60)))
        
        # Draw circular background
        painter.setBrush(QBrush(QColor(64, 64, 64)))  # #404040
        painter.setPen(QColor(80, 80, 80, 100))  # Semi-transparent border
        painter.drawEllipse(shadow_size, shadow_size, size, size)
        
        # Draw text
        painter.setPen(QColor(255, 255, 255))  # White text
        painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))  # Slightly smaller font
        
        # Center the name text
        text_rect = (shadow_size, shadow_size, size, size)
        painter.drawText(*text_rect, Qt.AlignmentFlag.AlignCenter, name)
        
        painter.end()
        
        image_label.setPixmap(fallback_pixmap)
        image_label.setStyleSheet("background: transparent; border: none;")

    def create_donations_section(self, layout):
        """Create the donations section."""
        try:
            # Download donation data
            donation_url = "https://raw.githubusercontent.com/bazthedev/SolsScope/main/donations.json"
            try:
                with urllib.request.urlopen(donation_url, timeout=3) as response, open(f"{MACROPATH}/donations.json", 'wb') as out_file:
                    if response.status == 200:
                        shutil.copyfileobj(response, out_file)
                    else:
                        raise Exception(f"HTTP Error {response.status}")
            except Exception as dl_error:
                self.logger.write_log(f"Error downloading donation data: {dl_error}")
                return

            # Load and display donors
            with open(f"{MACROPATH}/donations.json", "r", encoding="utf-8") as f:
                donors = json.load(f)
                
                if donors and len(donors) > 0:
                    donors_frame = QFrame()
                    donors_frame.setObjectName("sectionCard")
                    donors_layout = QVBoxLayout(donors_frame)
                    donors_layout.setContentsMargins(10, 10, 10, 10)
                    donors_layout.setSpacing(8)

                    donors_title = QLabel("❤️ Amazing Supporters")
                    donors_title.setStyleSheet("""
                        font-size: 14px;
                        font-weight: bold;
                        color: #e74c3c;
                        margin-bottom: 5px;
                    """)
                    donors_layout.addWidget(donors_title)

                    # Create compact donor list
                    donors_text = " • ".join(donors[:10])  # Show max 10 donors
                    if len(donors) > 10:
                        donors_text += f" • and {len(donors) - 10} more..."
                    
                    donors_label = QLabel(donors_text)
                    donors_label.setStyleSheet("""
                        font-size: 10px;
                        color: #cccccc;
                        padding: 5px;
                        background: #2a2a2a;
                        border-radius: 5px;
                    """)
                    donors_label.setWordWrap(True)
                    donors_layout.addWidget(donors_label)

                    layout.addWidget(donors_frame)
                    
        except Exception as e:
            self.logger.write_log(f"Failed to create donations section: {e}")

    def open_donation_url(self):
        """Show donation prompt and open appropriate donation URL based on user choice."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Choose Developer to Support")
        msg.setText("Which developer would you like to donate to?")
        msg.setIcon(QMessageBox.Icon.Question)
        
        # Create custom buttons
        baz_button = msg.addButton("Baz", QMessageBox.ButtonRole.AcceptRole)
        cresqnt_button = msg.addButton("Cresqnt", QMessageBox.ButtonRole.AcceptRole)
        cancel_button = msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        
        msg.exec()
        
        if msg.clickedButton() == baz_button:
            webbrowser.open("https://www.roblox.com/games/4998237654/GeoffDoes90ss-Place#!/store")
        elif msg.clickedButton() == cresqnt_button:
            webbrowser.open("https://www.roblox.com/games/1980495071/Donations-D#!/store")

    def get_updated_values(self, original_settings_subset, entries_subset):
        """Compares current widget values to original values for a subset."""
        updated_subset = {}
        for key, widget_or_dict in entries_subset.items():

            if key.lower() == "themes":
                continue

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

                    elif isinstance(widget_or_dict, QComboBox):
                        new_value = widget_or_dict.currentText()

                    elif isinstance(widget_or_dict, QLineEdit):
                        new_value_str = widget_or_dict.text()

                        if isinstance(original_value, bool): 
                            new_value = new_value_str.lower() in ['true', '1', 'yes', 'y']
                        elif isinstance(original_value, int):
                            try:
                                new_value = int(new_value_str)
                            except (ValueError, TypeError):
                                new_value = new_value_str 
                        elif isinstance(original_value, float):
                            try:
                                new_value = float(new_value_str)
                            except (ValueError, TypeError):
                                new_value = new_value_str
                        else: 
                            new_value = new_value_str

                    else:
                        self.logger.write_log(f"Warning: Unexpected widget type for '{key}' (type={type(widget_or_dict)}, value={widget_or_dict}).")
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
            "General": GENERAL_KEYS,
            "Auras": AURAS_KEYS,
            "Biomes": BIOMES_KEYS,
            "Actions": ACTIONS_KEYS,
            "Other": OTHER_KEYS,
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

        use_player = self.settings.get("use_roblox_player", True)
        if OCR_AVAILABLE:
            self.reader = Reader(['en'], gpu=False)
        else:
            self.reader = None
            QMessageBox.warning(self, "SolsScope", "OCR Modules are not installed.")
            return
        set_active_log_directory(force_player=use_player)
        if not exists_procs_by_name("Windows10Universal.exe") and not exists_procs_by_name("RobloxPlayerBeta.exe"):
            if QMessageBox.question(self, "Roblox Not Detected", "Roblox process not found. Start macro anyway?") == QMessageBox.StandardButton.No:
                self.logger.write_log("Macro start cancelled: Roblox not running.")
                return

        self.running = True
        self.stop_event.clear()
        self.sniped_event.clear()
        self.pause_event.clear()
        self.ignore_next_detection.clear()
        self.threads = []
        self.logger.write_log("Starting Macro Threads in 5 seconds...")
        pyautoscope.refresh_clients()

        is_autocraft_mode = self.settings.get("mode", "Normal") == "Auto Craft"
        is_idle_mode = self.settings.get("mode", "Normal") == "IDLE"
        is_limbo_mode = self.settings.get("mode", "Normal") == "Limbo"
        is_fishing_mode = self.settings.get("mode", "Normal") == "Fishing"
        vip_status = self.settings.get("vip_status", "No VIP")
        if vip_status == "No VIP":
            QMessageBox.warning(self, "No VIP Warning", "You are currently using No VIP, which means that walking to Stella and Eden will not work.")
        try:
            thread_targets = self._get_thread_targets(is_autocraft_mode, is_idle_mode, is_limbo_mode, is_fishing_mode)
        except ValueError as e: 
             self.running = False 
             return
        
        if self.settings.get("ignore_fastflags_disabled_check", False):
            import macro_logic
            macro_logic.FAST_FLAGS_DISABLED = False

        for name, target_info in thread_targets.items():
            if target_info:
                func, args = target_info
                try:
                    adjusted_args = list(args)

                    thread = threading.Thread(target=func, args=adjusted_args, daemon=True, name=name)
                    thread.start()
                    self.threads.append(thread)
                    self.logger.write_log(f" > Started thread: {name}")
                except Exception as e:
                    self.logger.write_log(f" > Error starting thread {name}: {e}")

        self.logger.write_log("Starting Plugin Threads...")
        for plugin in self.plugins:
            try:
                can_run = True
                plugin_name = getattr(plugin, "name", "UnknownPlugin")
                if is_autocraft_mode and not getattr(plugin, "autocraft_compatible", False):
                    can_run = False
                    self.logger.write_log(f"Skipping plugin {plugin_name}: Not compatible with Auto Craft mode.")

                if can_run and hasattr(plugin, "run"):

                    plugin_args = (self.stop_event, self.sniped_event, self.pause_event)
                    thread = threading.Thread(target=plugin.run, args=plugin_args, daemon=True, name=f"Plugin_{plugin_name}")
                    thread.start()
                    self.threads.append(thread)
                    self.logger.write_log(f" > Started plugin thread: {plugin_name}")
                elif can_run:
                     self.logger.write_log(f"Plugin {plugin_name} has no run method.")
            except Exception as e:
                self.logger.write_log(f"Error starting plugin thread '{plugin_name}': {e}", level="ERROR")

        self._send_start_notification()
        self.start_time = time.time()
        self.logger.write_log("Macro started successfully.")

    def _get_thread_targets(self, is_autocraft_mode, is_idle_mode, is_limbo_mode, is_fishing_mode):
        """Helper to determine which threads to start based on mode."""

        MERCHANT_DETECTION_POSSIBLE = OCR_AVAILABLE 

        if is_idle_mode:
            self.logger.write_log("Starting in IDLE Mode.")
            targets = {
                "Aura Detection": (aura_detection, [self.settings, self.webhook, self.stop_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.ignore_lock, self.ignore_next_detection, self.pause_event, self.reader, self.mouse_controller]) if not self.settings.get("disable_aura_detection") else None,
                "Biome Detection": (biome_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.mkey, self.keyboard_controller, self.keyboard_lock, self.pause_event, self, self.reader, self.mouse_controller]) if not self.settings.get("disable_biome_detection") else None,
                "Merchant Detection": (merchant_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.ignore_lock, self.ignore_next_detection, self.reader, self.pause_event, self.mouse_controller]) if self.settings.get("merchant_detection") else None,
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
                "Auto Craft Logic": (auto_craft, [self.webhook, self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.mouse_controller, self.ignore_lock, self.ignore_next_detection, self.reader, self.pause_event, self.items_crafted]),
                "Aura Detection": (aura_detection, [self.settings, self.webhook, self.stop_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.ignore_lock, self.ignore_next_detection, self.pause_event, self.reader, self.mouse_controller]) if not self.settings.get("disable_aura_detection") else None,
                "Biome Detection": (biome_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.mkey, self.keyboard_controller, self.keyboard_lock, self.pause_event, self, self.reader, self.mouse_controller]) if not self.settings.get("disable_biome_detection") else None,
                "Keep Alive": (keep_alive, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock,  self.keyboard_controller, self.pause_event, self.mkey]) if not self.settings.get("disable_autokick_prevention") else None,
                "Disconnect Prevention": (disconnect_prevention, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event]) if self.settings.get("disconnect_prevention") else None,
                "Merchant Detection": (merchant_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.ignore_lock, self.ignore_next_detection, self.reader, self.pause_event, self.mouse_controller]) if (self.settings.get("merchant_detection") or self.settings.get("auto_sell_to_jester")) and MERCHANT_DETECTION_POSSIBLE else None,
                "Auto Strange Controller": (auto_sc, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event, self.reader, self.mouse_controller]) if self.settings.get("auto_strange_controller") else None,
                "Auto Biome Randomizer": (auto_br, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event, self.reader, self.mouse_controller]) if self.settings.get("auto_biome_randomizer") else None,
                "Inventory Screenshots": (inventory_screenshot, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event, self.reader]) if self.settings.get("periodic_screenshots", {}).get("inventory") else None,
                "Storage Screenshots": (storage_screenshot, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event, self.reader]) if self.settings.get("periodic_screenshots", {}).get("storage") else None,
                "Obby": (do_obby, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.ignore_lock, self.ignore_next_detection, self.pause_event, self.reader, self.mouse_controller]) if self.settings.get("do_obby") and not self.settings.get("do_not_walk_to_stella", False) else None,
                "Auto Quest Board": (auto_questboard, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.mouse_controller, self.ignore_lock, self.ignore_next_detection, self.pause_event, self.reader,]) if self.settings.get("enable_auto_quest_board") else None,
                #"vok taran": (vok_taran, [self.settings, self.webhook, self.stop_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event]) if self.settings.get("vok_taran") else None,
            }
        elif is_limbo_mode:
            self.logger.write_log("Starting in Limbo Mode.")
            targets = {
                "Aura Detection": (aura_detection, [self.settings, self.webhook, self.stop_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.ignore_lock, self.ignore_next_detection, self.pause_event, self.reader, self.mouse_controller]) if not self.settings.get("disable_aura_detection") else None,
                "Eden Detection": (eden_detection, [self.settings, self.webhook, self.stop_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.mouse_controller, self.pause_event, self.reader]) if not self.settings.get("disable_eden_detection_in_limbo") else None,
                "Biome Detection": (biome_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.mkey, self.keyboard_controller, self.keyboard_lock, self.pause_event, self, self.reader, self.mouse_controller]) if not self.settings.get("disable_biome_detection") else None,
                "Keep Alive": (keep_alive, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.keyboard_controller, self.pause_event, self.mkey]) if not self.settings.get("disable_autokick_prevention") else None,
                "Disconnect Prevention": (disconnect_prevention, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event]) if self.settings.get("disconnect_prevention") else None,
                "Merchant Detection": (merchant_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.ignore_lock, self.ignore_next_detection, self.reader, self.pause_event, self.mouse_controller]) if (self.settings.get("merchant_detection") or self.settings.get("auto_sell_to_jester")) and MERCHANT_DETECTION_POSSIBLE else None,
                "Auto Strange Controller": (auto_sc, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event, self.reader, self.mouse_controller]) if self.settings.get("auto_strange_controller") else None,
                "Auto Biome Randomizer": (auto_br, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event, self.reader, self.mouse_controller]) if self.settings.get("auto_biome_randomizer") else None,
                "Inventory Screenshots": (inventory_screenshot, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event, self.reader]) if self.settings.get("periodic_screenshots", {}).get("inventory") else None,
                "Storage Screenshots": (storage_screenshot, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event, self.reader]) if self.settings.get("periodic_screenshots", {}).get("storage") else None,
                "Obby": (do_obby, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.ignore_lock, self.ignore_next_detection, self.pause_event, self.reader, self.mouse_controller]) if self.settings.get("do_obby") else None,
                "Portable Crack": (portable_crack, [self.settings, self.stop_event, self.sniped_event, self.mkey, self.keyboard_controller, self.keyboard_lock, self.pause_event, self.reader, self.mouse_controller]) if is_limbo_mode and not is_idle_mode else None,
                "Auto Quest Board": (auto_questboard, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.mouse_controller, self.ignore_lock, self.ignore_next_detection, self.pause_event, self.reader,]) if self.settings.get("enable_auto_quest_board") else None,
            }
        elif is_fishing_mode:
            self.logger.write_log("Starting in Fishing Mode.")
            targets = {
                "Aura Detection": (aura_detection, [self.settings, self.webhook, self.stop_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.ignore_lock, self.ignore_next_detection, self.pause_event, self.reader, self.mouse_controller]) if not self.settings.get("disable_aura_detection") else None,
                "Biome Detection": (biome_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.mkey, self.keyboard_controller, self.keyboard_lock, self.pause_event, self, self.reader, self.mouse_controller]) if not self.settings.get("disable_biome_detection") else None,
                "Keep Alive": (keep_alive, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.keyboard_controller, self.pause_event, self.mkey]) if not self.settings.get("disable_autokick_prevention") else None,
                "Auto Strange Controller": (auto_sc, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event, self.reader, self.mouse_controller]) if self.settings.get("auto_strange_controller") else None,
                "Auto Biome Randomizer": (auto_br, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event, self.reader, self.mouse_controller]) if self.settings.get("auto_biome_randomizer") else None,
                "Inventory Screenshots": (inventory_screenshot, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event, self.reader]) if self.settings.get("periodic_screenshots", {}).get("inventory") else None,
                "Storage Screenshots": (storage_screenshot, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event, self.reader]) if self.settings.get("periodic_screenshots", {}).get("storage") else None,
                #"vok taran": (vok_taran, [self.settings, self.webhook, self.stop_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event]) if self.settings.get("vok_taran") else None,
                "Merchant Detection": (merchant_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.ignore_lock, self.ignore_next_detection, self.reader, self.pause_event, self.mouse_controller]) if (self.settings.get("merchant_detection") or self.settings.get("auto_sell_to_jester")) and MERCHANT_DETECTION_POSSIBLE else None,
            }
        else:
            self.logger.write_log("Starting in Normal Mode.")
            targets = {
                "Aura Detection": (aura_detection, [self.settings, self.webhook, self.stop_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.ignore_lock, self.ignore_next_detection, self.pause_event, self.reader, self.mouse_controller]) if not self.settings.get("disable_aura_detection") else None,
                "Biome Detection": (biome_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.mkey, self.keyboard_controller, self.keyboard_lock, self.pause_event, self, self.reader, self.mouse_controller]) if not self.settings.get("disable_biome_detection") else None,
                "Keep Alive": (keep_alive, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.keyboard_controller, self.pause_event, self.mkey]) if not self.settings.get("disable_autokick_prevention") else None,
                "Disconnect Prevention": (disconnect_prevention, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event]) if self.settings.get("disconnect_prevention") else None,
                "Merchant Detection": (merchant_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.ignore_lock, self.ignore_next_detection, self.reader, self.pause_event, self.mouse_controller]) if (self.settings.get("merchant_detection") or self.settings.get("auto_sell_to_jester")) and MERCHANT_DETECTION_POSSIBLE else None,
                "Auto Strange Controller": (auto_sc, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event, self.reader, self.mouse_controller]) if self.settings.get("auto_strange_controller") else None,
                "Auto Biome Randomizer": (auto_br, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event, self.reader, self.mouse_controller]) if self.settings.get("auto_biome_randomizer") else None,
                "Inventory Screenshots": (inventory_screenshot, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event, self.reader]) if self.settings.get("periodic_screenshots", {}).get("inventory") else None,
                "Storage Screenshots": (storage_screenshot, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event, self.reader]) if self.settings.get("periodic_screenshots", {}).get("storage") else None,
                "Obby": (do_obby, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.ignore_lock, self.ignore_next_detection, self.pause_event, self.reader, self.mouse_controller]) if self.settings.get("do_obby") else None,
                "Auto Quest Board": (auto_questboard, [self.settings, self.webhook, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.mouse_controller, self.ignore_lock, self.ignore_next_detection, self.pause_event, self.reader,]) if self.settings.get("enable_auto_quest_board") else None,
                #"vok taran": (vok_taran, [self.settings, self.webhook, self.stop_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.pause_event]) if self.settings.get("vok_taran") else None,
            }
        return targets

    def _send_start_notification(self):
        """Sends the start notification webhook."""
        mode_str = self.settings.get("mode", "Normal")
        start_desc = "" 

        emb = discord.Embed(
            title="Macro Started",
            description=start_desc, 
            colour=discord.Colour.green(),
            timestamp=datetime.now() 
        )
        if self.easter_eggs["InvertedScope"]:
            emb.set_footer(text=f"InvertedScope v{LOCALVERSION}")
        else:
            emb.set_footer(text=f"SolsScope v{LOCALVERSION}")
        emb.add_field(name="Mode", value=mode_str, inline=True)
        emb.set_thumbnail(url="https://raw.githubusercontent.com/bazthedev/SolsScope/main/img/solsscope.png")

        if mode_str == "Auto Craft":
            enabled_crafts = [item for item, enabled in self.settings.get("auto_craft_item", {}).items() if enabled]
            craft_list = ', '.join(enabled_crafts) if enabled_crafts else "None Selected"
            emb.add_field(name="Crafting", value=craft_list, inline=False)
        else:
            try:
                aura = get_latest_equipped_aura()
                emb.add_field(name="Current Aura", value=aura if aura else "Unknown (not the aura)", inline=True)
            except Exception as e:
                self.logger.write_log(f"Error sending start aura notification: {e}")
                emb.add_field(name="Current Aura", value="Unknown (not the aura)", inline=True) 
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
        self.pause_event.clear()
        self.stop_event.set()

        timeout_per_thread = 2 
        start_time = time.time()

        threads_to_join = [t for t in self.threads if t != threading.current_thread() and t.is_alive()]

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

        self.logger.write_log("All threads signaled/joined.")
        self.running = False
        self.threads.clear()
        self.ignore_next_detection.clear()
        self.stop_event.clear()

        session_duration = start_time - self.start_time

        td = timedelta(seconds=session_duration)

        days = td.days
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        description = f"Session Duration: **{days}:{hours:02}:{minutes:02}:{seconds:02}**"

        if self.settings.get("mode", "Normal") == "Auto Craft" and self.settings.get("send_item_crafted_notification", True):
            description += f"\nNumber of Potions Crafted: **{str(self.items_crafted)}**"

        emb = discord.Embed(
            title="Macro Stopped",
            description=description,
            colour=discord.Colour.red(),
            timestamp=datetime.now() 
        )
        if self.easter_eggs["InvertedScope"]:
            emb.set_footer(text=f"InvertedScope v{LOCALVERSION}")
        else:
            emb.set_footer(text=f"SolsScope v{LOCALVERSION}")
        emb.set_thumbnail(url="https://raw.githubusercontent.com/bazthedev/SolsScope/main/img/solsscope.png")
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
                    plugin_authors = getattr(temp_instance, "authors", ["Unknown"])
                    plugin_requirements = getattr(temp_instance, "requirements", [])
                    required_macro_version = getattr(temp_instance, "requires", "0.0.0")
                    silent = getattr(temp_instance, "silent", False)
                    plugin_autocraft_compatible = getattr(temp_instance, "autocraft_compatible", False)

                    del temp_instance 
                except Exception as meta_e:
                    self.logger.write_log(f" > Error getting metadata from temporary instance of {plugin_name_from_file}: {meta_e}", level="ERROR")
                    continue 
                
                installer = PackageInstallerGUI(plugin_requirements, parent=self)
                QTimer.singleShot(0, installer.start_install)
                installer.exec()

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
                    plugin_instance.authors = plugin_authors

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

                if not silent:
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
                            "create_widgets": self.create_widgets_plugin,
                            "create_list_widget": self.create_list_widget,
                            "main_window": self
                        }
                        try:
                            plugin_instance.init_tab(gui_tools)
                        except Exception as tab_e:
                            self.logger.write_log(f" > Error running init_tab for plugin '{plugin_display_name}': {tab_e}", level="ERROR")
                            error_label = QLabel(f"Error loading plugin UI for {plugin_display_name}.\nCheck logs for details.\nIf you recently updated the macro, then the plugin may also require updating.")
                            error_label.setStyleSheet("color: red;")
                            plugin_tab_layout.addWidget(error_label)

                    else:
                        default_label = QLabel("Plugin has no UI defined.")
                        plugin_tab_layout.addWidget(default_label)

                    self.create_bottom_buttons(plugin_tab_layout, plugin_display_name)

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

    def install_plugin(self, path = None):
        """Handles copying a plugin file and reloading plugins."""
        if not path:
            plugin_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Plugin File (.py)",
                "Plugin.py", 
                "Python Files (*.py)"
            )
        else:
            plugin_path = path

        if not plugin_path:
            return 

        try:
            dest_dir = os.path.join(MACROPATH, "plugins")
            filename = os.path.basename(plugin_path)
            dest_path = os.path.join(dest_dir, filename)

            os.makedirs(dest_dir, exist_ok=True)

            shutil.copy(plugin_path, dest_path)
            self.logger.write_log(f"Plugin '{filename}' copied to plugins directory.")

            self.load_plugins()

            if not path:
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

class SettingsDialog(QDialog):
    """Base class for settings popup dialogs."""
    
    def __init__(self, title, keys, settings, parent=None):
        super().__init__(parent)
        self.keys = keys
        self.settings = settings
        self.entries = {}
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(400, 500)
        self.setObjectName("popoutWindow")
        
        layout = QVBoxLayout(self)
        
        # Create scroll area for settings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(scroll_area)
        
        scroll_content = QWidget()
        scroll_content.setObjectName("popoutConfigBox")
        scroll_area.setWidget(scroll_content)
        content_layout = QVBoxLayout(scroll_content)
        
        # Populate settings
        self.populate_settings(content_layout)
        
        # Add dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.adjustSize()
        self.setMaximumSize(self.size())
    
    def populate_settings(self, layout):
        """Populate the settings in the dialog."""
        from utils import format_key, get_logger
        
        for key in self.keys:
            if key in DONOTDISPLAY:
                continue
                
            current_value = self.settings.get(key, DEFAULTSETTINGS.get(key))

            tooltip_text = TOOLTIPS.get(key)

            if not isinstance(tooltip_text, str):
                tooltip_text = None
            
            if isinstance(current_value, bool):
                checkbox = QCheckBox(format_key(key))
                checkbox.setChecked(current_value)
                if tooltip_text:
                    checkbox.setToolTip(tooltip_text)
                else:
                    checkbox.setToolTip("No tooltip for this.")
                layout.addWidget(checkbox)
                self.entries[key] = checkbox
                
            elif isinstance(current_value, (int, float, str)):
                if key.endswith("_id") and current_value == 0:
                    current_value = ""
                elif isinstance(current_value, (int, float)):
                    current_value = str(current_value)
                    
                label = QLabel(format_key(key))
                line_edit = QLineEdit(str(current_value))
                if tooltip_text:
                    line_edit.setToolTip(tooltip_text)
                else:
                    line_edit.setToolTip("No tooltip for this.")
                layout.addWidget(label)
                layout.addWidget(line_edit)
                self.entries[key] = line_edit
                
            elif isinstance(current_value, dict):
                group_box = QGroupBox(format_key(key))
                group_layout = QVBoxLayout(group_box)
                
                self.entries[key] = {}
                
                for sub_key, sub_value in current_value.items():
                    tooltip_text = TOOLTIPS.get(key)
                    if not isinstance(tooltip_text, str):
                        tooltip_text = None
                    
                    if isinstance(sub_value, bool):
                        sub_checkbox = QCheckBox(sub_key)
                        sub_checkbox.setChecked(sub_value)
                        if tooltip_text:
                            sub_checkbox.setToolTip(tooltip_text)
                        else:
                            sub_checkbox.setToolTip("No tooltip for this.")
                        group_layout.addWidget(sub_checkbox)
                        self.entries[key][sub_key] = sub_checkbox
                    elif isinstance(sub_value, dict):
                        # Handle nested dictionaries (like purchase items)
                        sub_group = QGroupBox(sub_key)
                        sub_group_layout = QFormLayout(sub_group)
                        if tooltip_text:
                            sub_group.setToolTip(tooltip_text)
                        else:
                            sub_group.setToolTip("No tooltip for this.")
                        
                        self.entries[key][sub_key] = {}
                        
                        for nested_key, nested_value in sub_value.items():
                            if isinstance(nested_value, bool):
                                nested_checkbox = QCheckBox()
                                nested_checkbox.setChecked(nested_value)
                                sub_group_layout.addRow(nested_key, nested_checkbox)
                                self.entries[key][sub_key][nested_key] = nested_checkbox
                            else:
                                nested_line_edit = QLineEdit(str(nested_value))
                                sub_group_layout.addRow(nested_key, nested_line_edit)
                                self.entries[key][sub_key][nested_key] = nested_line_edit
                        
                        group_layout.addWidget(sub_group)
                    else:
                        sub_label = QLabel(sub_key)
                        sub_line_edit = QLineEdit(str(sub_value))
                        group_layout.addWidget(sub_label)
                        group_layout.addWidget(sub_line_edit)
                        self.entries[key][sub_key] = sub_line_edit
                
                layout.addWidget(group_box)
    
    def get_updated_settings(self):
        """Get the updated settings from the dialog."""
        updated_settings = {}
        
        for key, widget in self.entries.items():
            if isinstance(widget, QCheckBox):
                updated_settings[key] = widget.isChecked()
            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                original_value = self.settings.get(key, DEFAULTSETTINGS.get(key))
                
                if key.endswith("_id") and text == "":
                    updated_settings[key] = 0
                elif isinstance(original_value, int):
                    try:
                        updated_settings[key] = int(text) if text else 0
                    except ValueError:
                        updated_settings[key] = 0
                elif isinstance(original_value, float):
                    try:
                        updated_settings[key] = float(text) if text else 0.0
                    except ValueError:
                        updated_settings[key] = 0.0
                else:
                    updated_settings[key] = text
            elif isinstance(widget, dict):
                # Handle dictionary settings
                updated_settings[key] = {}
                original_dict = self.settings.get(key, DEFAULTSETTINGS.get(key, {}))
                
                for sub_key, sub_widget in widget.items():
                    if isinstance(sub_widget, QCheckBox):
                        updated_settings[key][sub_key] = sub_widget.isChecked()
                    elif isinstance(sub_widget, QLineEdit):
                        text = sub_widget.text().strip()
                        original_sub_value = original_dict.get(sub_key, "")
                        
                        if isinstance(original_sub_value, int):
                            try:
                                updated_settings[key][sub_key] = int(text) if text else 0
                            except ValueError:
                                updated_settings[key][sub_key] = 0
                        elif isinstance(original_sub_value, float):
                            try:
                                updated_settings[key][sub_key] = float(text) if text else 0.0
                            except ValueError:
                                updated_settings[key][sub_key] = 0.0
                        else:
                            updated_settings[key][sub_key] = text
                    elif isinstance(sub_widget, dict):
                        # Handle nested dictionaries
                        updated_settings[key][sub_key] = {}
                        original_nested = original_dict.get(sub_key, {})
                        
                        for nested_key, nested_widget in sub_widget.items():
                            if isinstance(nested_widget, QCheckBox):
                                updated_settings[key][sub_key][nested_key] = nested_widget.isChecked()
                            elif isinstance(nested_widget, QLineEdit):
                                text = nested_widget.text().strip()
                                original_nested_value = original_nested.get(nested_key, "")
                                
                                if isinstance(original_nested_value, int):
                                    try:
                                        updated_settings[key][sub_key][nested_key] = int(text) if text else 0
                                    except ValueError:
                                        updated_settings[key][sub_key][nested_key] = 0
                                elif isinstance(original_nested_value, float):
                                    try:
                                        updated_settings[key][sub_key][nested_key] = float(text) if text else 0.0
                                    except ValueError:
                                        updated_settings[key][sub_key][nested_key] = 0.0
                                else:
                                    updated_settings[key][sub_key][nested_key] = text
        
        return updated_settings


class MariMerchantDialog(SettingsDialog):
    """Dialog for Mari merchant settings."""
    
    def __init__(self, settings, parent=None):
        super().__init__("Mari Merchant Settings", MARI_MERCHANT_KEYS, settings, parent)


class JesterMerchantDialog(SettingsDialog):
    """Dialog for Jester merchant settings."""
    
    def __init__(self, settings, parent=None):
        super().__init__("Jester Merchant Settings", JESTER_MERCHANT_KEYS, settings, parent)


class AutoCraftDialog(SettingsDialog):
    """Dialog for Auto Craft item settings."""
    
    def __init__(self, settings, parent=None):
        super().__init__("Auto Craft Settings", AUTOCRAFT_ITEM_KEYS, settings, parent)

    def show_status_message(self, message, timeout=2000):
        """Show a temporary status message."""
        msg = QMessageBox(self)
        msg.setWindowTitle("SolsScope")
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()


class BiomeConfigDialog(SettingsDialog):
    """Dialog for biome configuration settings."""
    
    def __init__(self, settings, parent=None):
        super().__init__("Biome Notification Settings", BIOME_CONFIG_KEYS, settings, parent)


class GlitchedItemsDialog(SettingsDialog):
    """Dialog for auto use items in glitched settings."""
    
    def __init__(self, settings, parent=None):
        super().__init__("Auto Use Items In Glitched Settings", GLITCHED_ITEMS_KEYS, settings, parent)


class DreamspaceItemsDialog(SettingsDialog):
    """Dialog for auto use items in dreamspace settings."""
    
    def __init__(self, settings, parent=None):
        super().__init__("Auto Use Items In Dreamspace Settings", DREAMSPACE_ITEMS_KEYS, settings, parent)

class AutoQuestDialog(SettingsDialog):
    """Dialog for auto quest settings."""
    
    def __init__(self, settings, parent=None):
        super().__init__("Auto Quest Settings", QUEST_KEYS, settings, parent)

class LimboDialog(SettingsDialog):
    """Dialog for Limbo settings."""
    
    def __init__(self, settings, parent=None):
        super().__init__("Limbo Mode Settings", LIMBO_KEYS, settings, parent)

class SkipDownloadsDialog(SettingsDialog):
    """Dialog for Data Download settings."""
    
    def __init__(self, settings, parent=None):
        super().__init__("Skip Data Download Settings", SKIP_DLS_KEYS, settings, parent)

class MacroOverrides(SettingsDialog):
    """Dialog for Macro Overrides."""
    
    def __init__(self, settings, parent=None):
        super().__init__("Macro Overrides", MACRO_OVERRIDES, settings, parent)

class UINavControls(SettingsDialog):
    """Dialog for Macro Overrides."""
    
    def __init__(self, settings, parent=None):
        super().__init__("Actions Configuration", ACTIONS_CONFIG, settings, parent)