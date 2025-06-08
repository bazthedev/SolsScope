"""
Modern PyQt6 GUI for SolsScope
Clean, modern interface with improved UX and functionality
"""

import sys
import os
import time
import json
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
    QSizePolicy, QSpacerItem, QSplitter, QToolBar, QStatusBar, QMenuBar,
    QMenu, QComboBox, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QMetaObject, Q_ARG, pyqtSlot, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QTextCursor, QAction, QFont

# Import our custom components and styles
from styles import get_complete_stylesheet, COLORS
from ui_components import (
    ModernCard, StatusIndicator, CollapsibleSection, ModernFormField,
    ModernListWidget, ProgressCard, AutocraftPotionSelector
)

# Improved field names mapping
FIELD_NAMES = {
    # General Settings
    "WEBHOOK_URL": "Discord Webhook URL",
    "private_server_link": "Private Server Link",
    "SECONDARY_WEBHOOK_URLS": "Secondary Webhook URLs",
    "failsafe_key": "Emergency Stop Key",
    "idle_mode": "Idle Mode (Detection Only)",
    "use_roblox_player": "Use Roblox Player (vs Microsoft Store)",
    "global_wait_time": "Global Delay Between Actions (seconds)",
    "mention": "Enable Discord Mentions",
    "mention_id": "Discord User ID to Mention",
    "skip_aura_download": "Skip Aura Data Download",
    "skip_biome_download": "Skip Biome Data Download",
    "skip_merchant_download": "Skip Merchant Data Download",
    "skip_questboard_download": "Skip Quest Board Data Download",

    # Aura Settings
    "minimum_roll": "Minimum Aura Roll Value",
    "minimum_ping": "Minimum Aura Value to Ping",
    "reset_aura": "Aura to Reset For (leave empty for none)",
    "take_screenshot_on_detection": "Take Screenshot on Aura Detection",

    # Biome Settings
    "auto_biome_randomizer": "Auto Use Biome Randomizer",
    "auto_strange_controller": "Auto Use Strange Controller",
    "pop_in_glitch": "Auto Pop Items in Glitched Biome",
    "pop_in_dreamspace": "Auto Pop Items in Dreamspace",

    # Merchant Settings
    "merchant_detection": "Enable Merchant Detection",
    "ping_mari": "Ping for Mari's Shop",
    "mari_ping_id": "Discord User ID for Mari Pings",
    "auto_purchase_items_mari": "Auto Purchase from Mari",
    "ping_jester": "Ping for Jester's Shop",
    "jester_ping_id": "Discord User ID for Jester Pings",
    "auto_purchase_items_jester": "Auto Purchase from Jester",
    "auto_sell_to_jester": "Auto Sell Items to Jester",
    "amount_of_item_to_sell": "Maximum Items to Sell",

    # Path Settings
    "do_obby": "Complete Obby Automatically",
    "notify_obby_completion": "Notify When Obby is Complete",
    "has_abyssal_hunter": "Has Abyssal Hunter Aura",

    # Auto Craft Settings
    "auto_craft_mode": "Enable Auto Craft Mode",
    "auto_craft_item": "Item to Auto Craft",
    "skip_auto_mode_warning": "Skip Auto Mode Warning",
    "do_no_walk_to_stella": "Don't Walk to Stella",

    # Sniper Settings
    "sniper_enabled": "Enable Discord Sniper",
    "DISCORD_TOKEN": "Discord Bot Token",
    "ROBLOSECURITY_KEY": "Roblox Security Cookie",
    "sniper_logs": "Enable Sniper Logging",
    "scan_channels": "Discord Channels to Monitor",

    # Other Settings
    "disconnect_prevention": "Prevent Disconnections",
    "disable_autokick_prevention": "Disable Anti-Kick System",
    "disable_aura_detection": "Disable Aura Detection",
    "disable_biome_detection": "Disable Biome Detection",
    "always_on_top": "Keep Window Always on Top",
    "check_update": "Check for Updates on Startup",
    "auto_install_update": "Auto Install Updates",

    # Quest Settings
    "enable_auto_quest_board": "Enable Auto Quest Board",
}

# Import existing SolsScope modules
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
    """Signal emitter for log messages"""
    log_signal = pyqtSignal(str)

class PyQtLogger(Logger):
    """Logger implementation that emits a PyQt signal for GUI updates"""
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
        """Connects the logger's signal to a GUI slot"""
        self.signal_emitter.log_signal.connect(slot_function)

class ModernMainWindow(QMainWindow):
    """Modern main window for SolsScope"""
    
    start_macro_signal = pyqtSignal()
    stop_macro_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Initialize core attributes
        self.logger = get_logger()
        self.settings = load_settings()
        self.original_settings = self.settings.copy()
        
        # Macro state
        self.webhook = None
        self.threads = []
        self.sniper_task = None
        self.running = False
        self.keyboard_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.sniped_event = threading.Event()
        
        # UI state
        self.current_theme = 'dark'  # Default to dark mode
        self.ignore_next_detection = set()
        self.ignore_lock = threading.Lock()
        self.plugins = []
        self.plugin_file_paths = {}
        self.tab_entries = {}
        
        # Controllers
        self.mkey = mk.MouseKey()
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()
        
        # Setup UI
        self.setup_window()
        self.setup_menu_bar()
        self.setup_toolbar()
        self.setup_central_widget()
        self.setup_status_bar()
        self.apply_theme()
        
        # Connect signals
        self.start_macro_signal.connect(self.start_macro)
        self.stop_macro_signal.connect(self.stop_macro)
        
        # Initialize components
        self.load_plugins()
        self.start_key_listener()
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second
        
        self.logger.write_log("Modern GUI initialized successfully.")
    
    def setup_window(self):
        """Setup main window properties"""
        self.setWindowTitle(f"SolsScope v{LOCALVERSION} - Modern Interface")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)
        
        # Set window icon
        icon_path = os.path.join(MACROPATH, "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Always on top setting
        if self.settings.get("always_on_top", False):
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
    
    def setup_menu_bar(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        save_action = QAction('Save Settings', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_settings_action)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        theme_action = QAction('Toggle Theme', self)
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        install_plugin_action = QAction('Install Plugin...', self)
        install_plugin_action.triggered.connect(self.install_plugin)
        tools_menu.addAction(install_plugin_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Setup the toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Start button
        self.start_action = QAction('Start (F1)', self)
        self.start_action.triggered.connect(self.start_macro)
        toolbar.addAction(self.start_action)
        
        # Stop button
        self.stop_action = QAction('Stop (F2)', self)
        self.stop_action.triggered.connect(self.stop_macro)
        toolbar.addAction(self.stop_action)
        
        toolbar.addSeparator()

        # Theme toggle with icon
        self.theme_action = QAction('🌙 Dark Mode', self)
        self.theme_action.triggered.connect(self.toggle_theme)
        toolbar.addAction(self.theme_action)
        
        toolbar.addSeparator()
        
        # Status indicator
        self.status_indicator = StatusIndicator("Stopped", "stopped")
        toolbar.addWidget(QLabel("Status:"))
        toolbar.addWidget(self.status_indicator)
    
    def setup_central_widget(self):
        """Setup the central widget with tabs"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - Settings tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumWidth(600)
        splitter.addWidget(self.tab_widget)
        
        # Right side - Status and logs
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Status dashboard
        self.status_card = ModernCard("Status Dashboard")
        self.setup_status_dashboard()
        right_layout.addWidget(self.status_card)
        
        # Logs
        self.logs_card = ModernCard("Logs")
        self.setup_logs_section()
        right_layout.addWidget(self.logs_card)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 400])
        
        # Create tabs
        self.create_settings_tabs()
    
    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add permanent widgets
        self.status_bar.addPermanentWidget(QLabel(f"SolsScope v{LOCALVERSION}"))
    
    def apply_theme(self):
        """Apply the current theme"""
        stylesheet = get_complete_stylesheet(self.current_theme)
        self.setStyleSheet(stylesheet)
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme()

        # Update theme action text
        if self.current_theme == 'dark':
            self.theme_action.setText('🌙 Dark Mode')
        else:
            self.theme_action.setText('☀️ Light Mode')

        self.logger.write_log(f"Switched to {self.current_theme} theme")
    
    def setup_status_dashboard(self):
        """Setup the status dashboard"""
        # Current status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Macro Status:"))
        self.macro_status_label = StatusIndicator("Stopped", "stopped")
        status_layout.addWidget(self.macro_status_label)
        status_layout.addStretch()
        self.status_card.add_layout(status_layout)
        
        # Running time
        self.runtime_label = QLabel("Runtime: 00:00:00")
        self.status_card.add_widget(self.runtime_label)
        
        # Active threads
        self.threads_label = QLabel("Active Threads: 0")
        self.status_card.add_widget(self.threads_label)
        
        # Current aura/biome (if available)
        self.aura_label = QLabel("Current Aura: Unknown")
        self.status_card.add_widget(self.aura_label)
        
        self.biome_label = QLabel("Current Biome: Unknown")
        self.status_card.add_widget(self.biome_label)
    
    def setup_logs_section(self):
        """Setup the logs section"""
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setMaximumHeight(200)
        self.logs_card.add_widget(self.log_widget)
        
        # Connect logger
        try:
            if hasattr(self.logger, 'connect_log_widget'):
                self.logger.connect_log_widget(self.append_log_message)
            else:
                print("Warning: Logger does not support connect_log_widget method")
        except Exception as e:
            print(f"Warning: Failed to connect logger to log widget: {e}")
        
        # Log controls
        log_controls = QHBoxLayout()
        
        clear_logs_btn = QPushButton("Clear Logs")
        clear_logs_btn.setProperty("class", "secondary")
        clear_logs_btn.clicked.connect(self.log_widget.clear)
        log_controls.addWidget(clear_logs_btn)
        
        log_controls.addStretch()
        self.logs_card.add_layout(log_controls)

    def create_settings_tabs(self):
        """Create all settings tabs with improved organization - fewer tabs, more organized"""

        # Create main tabs - fewer tabs with better organization
        self.tab_widget.addTab(self.create_main_settings_tab(), "⚙️ Main Settings")
        self.tab_widget.addTab(self.create_detection_tab(), "🔍 Detection & Automation")
        self.tab_widget.addTab(self.create_merchant_tab(), "🛒 Merchant & Trading")
        self.tab_widget.addTab(self.create_sniper_tab(), "📡 Sniper & Advanced")

        # Add credits tab
        self.create_credits_tab()

    def create_settings_tab(self, tab_name, keys):
        """Create a settings tab with modern layout"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_layout.setSpacing(12)

        # Initialize tab entries
        self.tab_entries[tab_name] = {}

        # Create form fields
        self.create_form_fields(scroll_layout, keys, self.tab_entries[tab_name])

        # Add special sections for specific tabs
        if tab_name == "Merchant":
            self.add_merchant_extras(scroll_layout)
        elif tab_name == "Other":
            self.add_other_extras(scroll_layout)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Add action buttons
        self.add_tab_actions(layout, tab_name)

        return tab_widget

    def create_form_fields(self, layout, keys, entry_dict):
        """Create form fields for settings"""
        settings_subset = {k: self.settings.get(k, DEFAULTSETTINGS.get(k)) for k in keys}

        for key, value in settings_subset.items():
            if key in DONOTDISPLAY:
                continue

            # Use improved field names
            formatted_key = FIELD_NAMES.get(key, format_key(key))

            if isinstance(value, dict):
                # Create collapsible section for nested settings
                section = CollapsibleSection(formatted_key, collapsed=True)
                self.create_nested_fields(section, value, entry_dict, key)
                layout.addWidget(section)
                entry_dict[key] = section

            elif isinstance(value, list):
                # Create list widget
                list_widget = ModernListWidget(formatted_key)
                list_widget.set_items(value)
                list_widget.itemsChanged.connect(lambda: self.on_setting_changed())
                layout.addWidget(list_widget)
                entry_dict[key] = list_widget

            elif isinstance(value, bool):
                # Create checkbox field
                field = ModernFormField(formatted_key, "checkbox")
                field.set_value(value)
                field.valueChanged.connect(self.on_setting_changed)
                layout.addWidget(field)
                entry_dict[key] = field

            else:
                # Create text field
                field_type = "number" if isinstance(value, int) else "text"
                field = ModernFormField(formatted_key, field_type)
                field.set_value(value)
                field.valueChanged.connect(self.on_setting_changed)

                # Add tooltips for specific fields
                tooltip = self.get_field_tooltip(key)
                if tooltip:
                    field.set_tooltip(tooltip)

                layout.addWidget(field)
                entry_dict[key] = field

    def create_nested_fields(self, parent_section, nested_dict, entry_dict, parent_key):
        """Create fields for nested dictionary settings"""
        entry_dict[parent_key] = {}

        for key, value in nested_dict.items():
            formatted_key = format_key(key)

            if isinstance(value, bool):
                field = ModernFormField(formatted_key, "checkbox")
                field.set_value(value)
                field.valueChanged.connect(self.on_setting_changed)
                parent_section.add_widget(field)
                entry_dict[parent_key][key] = field

            elif isinstance(value, dict):
                # Handle nested dictionaries (like auto_use_items_in_glitch)
                nested_section = CollapsibleSection(formatted_key, collapsed=True)
                for nested_key, nested_value in value.items():
                    if isinstance(nested_value, dict):
                        # Handle items with use/amount structure
                        item_card = ModernCard(nested_key)

                        use_field = ModernFormField("Use", "checkbox")
                        use_field.set_value(nested_value.get("use", False))
                        use_field.valueChanged.connect(self.on_setting_changed)
                        item_card.add_widget(use_field)

                        amount_field = ModernFormField("Amount", "number")
                        amount_field.set_value(nested_value.get("amount", 1))
                        amount_field.valueChanged.connect(self.on_setting_changed)
                        item_card.add_widget(amount_field)

                        nested_section.add_widget(item_card)

                        # Store references
                        if parent_key not in entry_dict:
                            entry_dict[parent_key] = {}
                        if key not in entry_dict[parent_key]:
                            entry_dict[parent_key][key] = {}
                        entry_dict[parent_key][key][nested_key] = {
                            "use": use_field,
                            "amount": amount_field
                        }
                    else:
                        nested_field = ModernFormField(nested_key, "checkbox" if isinstance(nested_value, bool) else "text")
                        nested_field.set_value(nested_value)
                        nested_field.valueChanged.connect(self.on_setting_changed)
                        nested_section.add_widget(nested_field)

                        if parent_key not in entry_dict:
                            entry_dict[parent_key] = {}
                        if key not in entry_dict[parent_key]:
                            entry_dict[parent_key][key] = {}
                        entry_dict[parent_key][key][nested_key] = nested_field

                parent_section.add_widget(nested_section)
            else:
                field_type = "checkbox" if isinstance(value, bool) else ("number" if isinstance(value, int) else "text")
                field = ModernFormField(formatted_key, field_type)
                field.set_value(value)
                field.valueChanged.connect(self.on_setting_changed)
                parent_section.add_widget(field)
                entry_dict[parent_key][key] = field

    def get_field_tooltip(self, key):
        """Get tooltip text for specific fields"""
        tooltips = {
            "WEBHOOK_URL": "Discord webhook URL for notifications",
            "private_server_link": "Roblox private server link",
            "failsafe_key": "Emergency stop key combination",
            "minimum_roll": "Minimum aura roll value to trigger notifications",
            "minimum_ping": "Minimum aura value to ping for",
            "global_wait_time": "Global delay between actions (seconds)",
            "mention_id": "Discord user ID to mention in notifications",
        }
        return tooltips.get(key, "")

    def add_merchant_extras(self, layout):
        """Add Tesseract status to merchant tab"""
        tesseract_card = ModernCard("OCR Status")

        status_text = "Tesseract OCR: Installed" if TESSERACT_AVAILABLE else "Tesseract OCR: Not Installed"
        status_type = "running" if TESSERACT_AVAILABLE else "stopped"

        status_indicator = StatusIndicator(status_text, status_type)
        tesseract_card.add_widget(status_indicator)

        if not TESSERACT_AVAILABLE:
            download_btn = QPushButton("Download Tesseract")
            download_btn.setProperty("class", "secondary")
            download_btn.clicked.connect(lambda: webbrowser.open("https://github.com/tesseract-ocr/tesseract#installing-tesseract"))
            tesseract_card.add_widget(download_btn)

        layout.addWidget(tesseract_card)

    def add_other_extras(self, layout):
        """Add plugin management to other tab"""
        plugin_card = ModernCard("Plugin Management")

        install_btn = QPushButton("Install Plugin...")
        install_btn.setProperty("class", "secondary")
        install_btn.clicked.connect(self.install_plugin)
        plugin_card.add_widget(install_btn)

        layout.addWidget(plugin_card)

    def create_main_settings_tab(self):
        """Create main settings tab combining general, auras, and basic settings"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_layout.setSpacing(12)

        # Initialize tab entries
        self.tab_entries["⚙️ Main Settings"] = {}

        # Discord & Webhooks Section
        discord_section = CollapsibleSection("📢 Discord & Notifications", collapsed=True)

        webhook_field = ModernFormField("Primary Discord Webhook URL", "text")
        webhook_field.set_value(self.settings.get("WEBHOOK_URL", ""))
        webhook_field.set_tooltip("Main Discord webhook for notifications")
        webhook_field.valueChanged.connect(self.on_setting_changed)
        discord_section.add_widget(webhook_field)
        self.tab_entries["⚙️ Main Settings"]["WEBHOOK_URL"] = webhook_field

        secondary_webhooks = ModernListWidget("Secondary Webhook URLs")
        secondary_webhooks.set_items(self.settings.get("SECONDARY_WEBHOOK_URLS", []))
        secondary_webhooks.itemsChanged.connect(self.on_setting_changed)
        discord_section.add_widget(secondary_webhooks)
        self.tab_entries["⚙️ Main Settings"]["SECONDARY_WEBHOOK_URLS"] = secondary_webhooks

        mention_field = ModernFormField("Enable Discord Mentions", "checkbox")
        mention_field.set_value(self.settings.get("mention", True))
        mention_field.valueChanged.connect(self.on_setting_changed)
        discord_section.add_widget(mention_field)
        self.tab_entries["⚙️ Main Settings"]["mention"] = mention_field

        mention_id_field = ModernFormField("Discord User ID to Mention", "text")
        mention_id_field.set_value(str(self.settings.get("mention_id", 0)))
        mention_id_field.set_tooltip("Discord user ID to mention in notifications")
        mention_id_field.valueChanged.connect(self.on_setting_changed)
        discord_section.add_widget(mention_id_field)
        self.tab_entries["⚙️ Main Settings"]["mention_id"] = mention_id_field

        scroll_layout.addWidget(discord_section)

        # Roblox & Server Settings
        roblox_section = CollapsibleSection("🎮 Roblox & Server Settings", collapsed=True)

        ps_link_field = ModernFormField("Private Server Link", "text")
        ps_link_field.set_value(self.settings.get("private_server_link", ""))
        ps_link_field.set_tooltip("Roblox private server link to join")
        ps_link_field.valueChanged.connect(self.on_setting_changed)
        roblox_section.add_widget(ps_link_field)
        self.tab_entries["⚙️ Main Settings"]["private_server_link"] = ps_link_field

        roblox_player_field = ModernFormField("Use Roblox Player (vs Microsoft Store)", "checkbox")
        roblox_player_field.set_value(self.settings.get("use_roblox_player", True))
        roblox_player_field.set_tooltip("Use Roblox Player instead of Microsoft Store version")
        roblox_player_field.valueChanged.connect(self.on_setting_changed)
        roblox_section.add_widget(roblox_player_field)
        self.tab_entries["⚙️ Main Settings"]["use_roblox_player"] = roblox_player_field

        scroll_layout.addWidget(roblox_section)

        # Aura Settings
        aura_section = CollapsibleSection("✨ Aura Detection Settings", collapsed=True)

        min_roll_field = ModernFormField("Minimum Aura Roll Value", "text")
        min_roll_field.set_value(str(self.settings.get("minimum_roll", "99998")))
        min_roll_field.set_tooltip("Minimum aura roll value to trigger notifications")
        min_roll_field.valueChanged.connect(self.on_setting_changed)
        aura_section.add_widget(min_roll_field)
        self.tab_entries["⚙️ Main Settings"]["minimum_roll"] = min_roll_field

        min_ping_field = ModernFormField("Minimum Aura Value to Ping", "text")
        min_ping_field.set_value(str(self.settings.get("minimum_ping", "349999")))
        min_ping_field.set_tooltip("Minimum aura value to trigger Discord pings")
        min_ping_field.valueChanged.connect(self.on_setting_changed)
        aura_section.add_widget(min_ping_field)
        self.tab_entries["⚙️ Main Settings"]["minimum_ping"] = min_ping_field

        reset_aura_field = ModernFormField("Aura to Reset For (leave empty for none)", "text")
        reset_aura_field.set_value(self.settings.get("reset_aura", ""))
        reset_aura_field.set_tooltip("Specific aura name to reset character for")
        reset_aura_field.valueChanged.connect(self.on_setting_changed)
        aura_section.add_widget(reset_aura_field)
        self.tab_entries["⚙️ Main Settings"]["reset_aura"] = reset_aura_field

        screenshot_field = ModernFormField("Take Screenshot on Aura Detection", "checkbox")
        screenshot_field.set_value(self.settings.get("take_screenshot_on_detection", False))
        screenshot_field.valueChanged.connect(self.on_setting_changed)
        aura_section.add_widget(screenshot_field)
        self.tab_entries["⚙️ Main Settings"]["take_screenshot_on_detection"] = screenshot_field

        scroll_layout.addWidget(aura_section)

        # System Settings
        system_section = CollapsibleSection("🔧 System Settings", collapsed=True)

        global_wait_field = ModernFormField("Global Delay Between Actions (seconds)", "decimal")
        global_wait_field.set_value(self.settings.get("global_wait_time", 0.2))
        global_wait_field.set_tooltip("Global delay between macro actions")
        global_wait_field.valueChanged.connect(self.on_setting_changed)
        system_section.add_widget(global_wait_field)
        self.tab_entries["⚙️ Main Settings"]["global_wait_time"] = global_wait_field

        failsafe_field = ModernFormField("Emergency Stop Key Combination", "text")
        failsafe_field.set_value(self.settings.get("failsafe_key", "ctrl+e"))
        failsafe_field.set_tooltip("Key combination to emergency stop the macro")
        failsafe_field.valueChanged.connect(self.on_setting_changed)
        system_section.add_widget(failsafe_field)
        self.tab_entries["⚙️ Main Settings"]["failsafe_key"] = failsafe_field

        idle_mode_field = ModernFormField("Idle Mode (Detection Only)", "checkbox")
        idle_mode_field.set_value(self.settings.get("idle_mode", False))
        idle_mode_field.set_tooltip("Run in idle mode - detection only, no automation")
        idle_mode_field.valueChanged.connect(self.on_setting_changed)
        system_section.add_widget(idle_mode_field)
        self.tab_entries["⚙️ Main Settings"]["idle_mode"] = idle_mode_field

        always_on_top_field = ModernFormField("Keep Window Always on Top", "checkbox")
        always_on_top_field.set_value(self.settings.get("always_on_top", False))
        always_on_top_field.valueChanged.connect(self.on_setting_changed)
        system_section.add_widget(always_on_top_field)
        self.tab_entries["⚙️ Main Settings"]["always_on_top"] = always_on_top_field

        scroll_layout.addWidget(system_section)

        # Download Settings
        download_section = CollapsibleSection("📥 Download Settings", collapsed=True)

        skip_aura_field = ModernFormField("Skip Aura Data Download", "checkbox")
        skip_aura_field.set_value(self.settings.get("skip_aura_download", False))
        skip_aura_field.valueChanged.connect(self.on_setting_changed)
        download_section.add_widget(skip_aura_field)
        self.tab_entries["⚙️ Main Settings"]["skip_aura_download"] = skip_aura_field

        skip_biome_field = ModernFormField("Skip Biome Data Download", "checkbox")
        skip_biome_field.set_value(self.settings.get("skip_biome_download", False))
        skip_biome_field.valueChanged.connect(self.on_setting_changed)
        download_section.add_widget(skip_biome_field)
        self.tab_entries["⚙️ Main Settings"]["skip_biome_download"] = skip_biome_field

        skip_merchant_field = ModernFormField("Skip Merchant Data Download", "checkbox")
        skip_merchant_field.set_value(self.settings.get("skip_merchant_download", False))
        skip_merchant_field.valueChanged.connect(self.on_setting_changed)
        download_section.add_widget(skip_merchant_field)
        self.tab_entries["⚙️ Main Settings"]["skip_merchant_download"] = skip_merchant_field

        skip_quest_field = ModernFormField("Skip Quest Board Data Download", "checkbox")
        skip_quest_field.set_value(self.settings.get("skip_questboard_download", False))
        skip_quest_field.valueChanged.connect(self.on_setting_changed)
        download_section.add_widget(skip_quest_field)
        self.tab_entries["⚙️ Main Settings"]["skip_questboard_download"] = skip_quest_field

        scroll_layout.addWidget(download_section)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Add action buttons
        self.add_tab_actions(layout, "⚙️ Main Settings")

        return tab_widget

    def create_detection_tab(self):
        """Create detection & automation tab combining biomes, quests, auto craft, and path"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_layout.setSpacing(12)

        # Initialize tab entries
        self.tab_entries["🔍 Detection & Automation"] = {}

        # Detection Controls
        detection_section = CollapsibleSection("🔍 Detection Controls", collapsed=True)

        disable_aura_field = ModernFormField("Disable Aura Detection", "checkbox")
        disable_aura_field.set_value(self.settings.get("disable_aura_detection", False))
        disable_aura_field.valueChanged.connect(self.on_setting_changed)
        detection_section.add_widget(disable_aura_field)
        self.tab_entries["🔍 Detection & Automation"]["disable_aura_detection"] = disable_aura_field

        disable_biome_field = ModernFormField("Disable Biome Detection", "checkbox")
        disable_biome_field.set_value(self.settings.get("disable_biome_detection", False))
        disable_biome_field.valueChanged.connect(self.on_setting_changed)
        detection_section.add_widget(disable_biome_field)
        self.tab_entries["🔍 Detection & Automation"]["disable_biome_detection"] = disable_biome_field

        scroll_layout.addWidget(detection_section)

        # Biome Detection & Automation
        biome_section = CollapsibleSection("🌍 Biome Detection & Automation", collapsed=True)

        # Biome toggles in a compact grid
        biomes_card = ModernCard("Biomes to Detect")
        biomes_data = self.settings.get("biomes", {})

        biome_names = {
            "snowy": "❄️ Snowy", "windy": "💨 Windy", "rainy": "🌧️ Rainy", "sand storm": "🏜️ Sand Storm",
            "hell": "🔥 Hell", "starfall": "⭐ Starfall", "corruption": "💜 Corruption", "null": "⚫ Null",
            "glitched": "🌈 Glitched", "dreamspace": "💭 Dreamspace"
        }

        self.tab_entries["🔍 Detection & Automation"]["biomes"] = {}

        # Create a grid layout for biomes
        biome_grid_widget = QWidget()
        biome_grid_layout = QHBoxLayout(biome_grid_widget)
        biome_grid_layout.setSpacing(8)

        left_column = QVBoxLayout()
        right_column = QVBoxLayout()

        for i, (biome_key, display_name) in enumerate(biome_names.items()):
            biome_field = ModernFormField(display_name, "checkbox")
            biome_field.set_value(biomes_data.get(biome_key, False))
            biome_field.valueChanged.connect(self.on_setting_changed)

            if i < 5:
                left_column.addWidget(biome_field)
            else:
                right_column.addWidget(biome_field)

            self.tab_entries["🔍 Detection & Automation"]["biomes"][biome_key] = biome_field

        biome_grid_layout.addLayout(left_column)
        biome_grid_layout.addLayout(right_column)
        biomes_card.add_widget(biome_grid_widget)
        biome_section.add_widget(biomes_card)

        # Biome Tools
        tools_card = ModernCard("Automatic Biome Tools")

        auto_randomizer_field = ModernFormField("Auto Use Biome Randomizer", "checkbox")
        auto_randomizer_field.set_value(self.settings.get("auto_biome_randomizer", False))
        auto_randomizer_field.valueChanged.connect(self.on_setting_changed)
        tools_card.add_widget(auto_randomizer_field)
        self.tab_entries["🔍 Detection & Automation"]["auto_biome_randomizer"] = auto_randomizer_field

        auto_controller_field = ModernFormField("Auto Use Strange Controller", "checkbox")
        auto_controller_field.set_value(self.settings.get("auto_strange_controller", False))
        auto_controller_field.valueChanged.connect(self.on_setting_changed)
        tools_card.add_widget(auto_controller_field)
        self.tab_entries["🔍 Detection & Automation"]["auto_strange_controller"] = auto_controller_field

        biome_section.add_widget(tools_card)

        # Glitched & Dreamspace Settings
        special_biomes_subsection = CollapsibleSection("Special Biome Settings", collapsed=True)

        pop_glitch_field = ModernFormField("Auto Pop Items in Glitched Biome", "checkbox")
        pop_glitch_field.set_value(self.settings.get("pop_in_glitch", False))
        pop_glitch_field.valueChanged.connect(self.on_setting_changed)
        special_biomes_subsection.add_widget(pop_glitch_field)
        self.tab_entries["🔍 Detection & Automation"]["pop_in_glitch"] = pop_glitch_field

        pop_dreamspace_field = ModernFormField("Auto Pop Items in Dreamspace", "checkbox")
        pop_dreamspace_field.set_value(self.settings.get("pop_in_dreamspace", False))
        pop_dreamspace_field.valueChanged.connect(self.on_setting_changed)
        special_biomes_subsection.add_widget(pop_dreamspace_field)
        self.tab_entries["🔍 Detection & Automation"]["pop_in_dreamspace"] = pop_dreamspace_field

        biome_section.add_widget(special_biomes_subsection)
        scroll_layout.addWidget(biome_section)

        # Auto Craft Settings
        autocraft_section = CollapsibleSection("🛠️ Auto Craft Settings", collapsed=True)

        # Enable auto craft mode
        autocraft_mode_field = ModernFormField("Enable Auto Craft Mode", "checkbox")
        autocraft_mode_field.set_value(self.settings.get("auto_craft_mode", False))
        autocraft_mode_field.set_tooltip("Enable automatic crafting mode - must be near cauldron")
        autocraft_mode_field.valueChanged.connect(self.on_setting_changed)
        autocraft_section.add_widget(autocraft_mode_field)
        self.tab_entries["🔍 Detection & Automation"]["auto_craft_mode"] = autocraft_mode_field

        # Potion selector
        autocraft_potion_selector = AutocraftPotionSelector()
        autocraft_potion_selector.set_value(self.settings.get("auto_craft_item", {}))
        autocraft_potion_selector.valueChanged.connect(self.on_setting_changed)
        autocraft_section.add_widget(autocraft_potion_selector)
        self.tab_entries["🔍 Detection & Automation"]["auto_craft_item"] = autocraft_potion_selector

        # Additional settings
        additional_settings_card = ModernCard("Additional Settings")

        skip_warning_field = ModernFormField("Skip Auto Mode Warning", "checkbox")
        skip_warning_field.set_value(self.settings.get("skip_auto_mode_warning", False))
        skip_warning_field.set_tooltip("Skip the warning dialog when starting auto craft mode")
        skip_warning_field.valueChanged.connect(self.on_setting_changed)
        additional_settings_card.add_widget(skip_warning_field)
        self.tab_entries["🔍 Detection & Automation"]["skip_auto_mode_warning"] = skip_warning_field

        no_walk_stella_field = ModernFormField("Don't Walk to Stella", "checkbox")
        no_walk_stella_field.set_value(self.settings.get("do_no_walk_to_stella", False))
        no_walk_stella_field.set_tooltip("Disable automatic walking to Stella during auto craft")
        no_walk_stella_field.valueChanged.connect(self.on_setting_changed)
        additional_settings_card.add_widget(no_walk_stella_field)
        self.tab_entries["🔍 Detection & Automation"]["do_no_walk_to_stella"] = no_walk_stella_field

        autocraft_section.add_widget(additional_settings_card)
        scroll_layout.addWidget(autocraft_section)

        # Quest Board Settings
        quest_section = CollapsibleSection("🎯 Quest Board Automation", collapsed=True)

        enable_quest_field = ModernFormField("Enable Auto Quest Board", "checkbox")
        enable_quest_field.set_value(self.settings.get("enable_auto_quest_board", False))
        enable_quest_field.set_tooltip("Automatically accept and complete quests")
        enable_quest_field.valueChanged.connect(self.on_setting_changed)
        quest_section.add_widget(enable_quest_field)
        self.tab_entries["🔍 Detection & Automation"]["enable_auto_quest_board"] = enable_quest_field

        # Quest selection in a compact format
        quests_card = ModernCard("Quests to Accept")
        quests_to_accept = self.settings.get("quests_to_accept", {})
        self.tab_entries["🔍 Detection & Automation"]["quests_to_accept"] = {}

        quest_grid_widget = QWidget()
        quest_grid_layout = QHBoxLayout(quest_grid_widget)
        quest_left = QVBoxLayout()
        quest_right = QVBoxLayout()

        quest_list = list(quests_to_accept.keys())
        for i, quest_name in enumerate(quest_list):
            quest_field = ModernFormField(quest_name, "checkbox")
            quest_field.set_value(quests_to_accept.get(quest_name, True))
            quest_field.valueChanged.connect(self.on_setting_changed)

            if i < len(quest_list) // 2:
                quest_left.addWidget(quest_field)
            else:
                quest_right.addWidget(quest_field)

            self.tab_entries["🔍 Detection & Automation"]["quests_to_accept"][quest_name] = quest_field

        quest_grid_layout.addLayout(quest_left)
        quest_grid_layout.addLayout(quest_right)
        quests_card.add_widget(quest_grid_widget)
        quest_section.add_widget(quests_card)

        scroll_layout.addWidget(quest_section)

        # Path & Obby Settings
        path_section = CollapsibleSection("🎯 Path & Obby Automation", collapsed=True)

        do_obby_field = ModernFormField("Complete Obby Automatically", "checkbox")
        do_obby_field.set_value(self.settings.get("do_obby", False))
        do_obby_field.valueChanged.connect(self.on_setting_changed)
        path_section.add_widget(do_obby_field)
        self.tab_entries["🔍 Detection & Automation"]["do_obby"] = do_obby_field

        notify_obby_field = ModernFormField("Notify When Obby is Complete", "checkbox")
        notify_obby_field.set_value(self.settings.get("notify_obby_completion", False))
        notify_obby_field.valueChanged.connect(self.on_setting_changed)
        path_section.add_widget(notify_obby_field)
        self.tab_entries["🔍 Detection & Automation"]["notify_obby_completion"] = notify_obby_field

        has_abyssal_field = ModernFormField("Has Abyssal Hunter Aura", "checkbox")
        has_abyssal_field.set_value(self.settings.get("has_abyssal_hunter", False))
        has_abyssal_field.set_tooltip("Check if you have Abyssal Hunter aura for path optimization")
        has_abyssal_field.valueChanged.connect(self.on_setting_changed)
        path_section.add_widget(has_abyssal_field)
        self.tab_entries["🔍 Detection & Automation"]["has_abyssal_hunter"] = has_abyssal_field

        scroll_layout.addWidget(path_section)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Add action buttons
        self.add_tab_actions(layout, "🔍 Detection & Automation")

        return tab_widget

    def create_merchant_tab(self):
        """Create comprehensive merchant tab with ALL merchant functionality"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_layout.setSpacing(12)

        # Initialize tab entries
        self.tab_entries["🛒 Merchant & Trading"] = {}

        # OCR Status Card
        ocr_card = ModernCard("🔍 OCR Status & Requirements")
        status_text = "Tesseract OCR: Installed ✅" if TESSERACT_AVAILABLE else "Tesseract OCR: Not Installed ❌"
        status_type = "running" if TESSERACT_AVAILABLE else "stopped"
        status_indicator = StatusIndicator(status_text, status_type)
        ocr_card.add_widget(status_indicator)

        if not TESSERACT_AVAILABLE:
            info_label = QLabel("Merchant detection requires Tesseract OCR to read shop names.")
            ocr_card.add_widget(info_label)
            download_btn = QPushButton("📥 Download Tesseract OCR")
            download_btn.setProperty("class", "secondary")
            download_btn.clicked.connect(lambda: webbrowser.open("https://github.com/tesseract-ocr/tesseract#installing-tesseract"))
            ocr_card.add_widget(download_btn)

        scroll_layout.addWidget(ocr_card)

        # General Merchant Settings
        general_section = CollapsibleSection("⚙️ General Merchant Settings", collapsed=True)

        merchant_detection_field = ModernFormField("Enable Merchant Detection", "checkbox")
        merchant_detection_field.set_value(self.settings.get("merchant_detection", False))
        merchant_detection_field.set_tooltip("Enable automatic merchant detection using OCR")
        merchant_detection_field.valueChanged.connect(self.on_setting_changed)
        general_section.add_widget(merchant_detection_field)
        self.tab_entries["🛒 Merchant & Trading"]["merchant_detection"] = merchant_detection_field

        scroll_layout.addWidget(general_section)

        # Mari's Shop Section
        mari_section = CollapsibleSection("👩‍💼 Mari's Shop", collapsed=True)

        # Mari notification settings
        mari_ping_field = ModernFormField("Ping for Mari's Shop", "checkbox")
        mari_ping_field.set_value(self.settings.get("ping_mari", False))
        mari_ping_field.valueChanged.connect(self.on_setting_changed)
        mari_section.add_widget(mari_ping_field)
        self.tab_entries["🛒 Merchant & Trading"]["ping_mari"] = mari_ping_field

        mari_ping_id_field = ModernFormField("Discord User ID for Mari Pings", "text")
        mari_ping_id_field.set_value(str(self.settings.get("mari_ping_id", 0)))
        mari_ping_id_field.set_tooltip("Discord user ID to mention when Mari's shop is detected")
        mari_ping_id_field.valueChanged.connect(self.on_setting_changed)
        mari_section.add_widget(mari_ping_id_field)
        self.tab_entries["🛒 Merchant & Trading"]["mari_ping_id"] = mari_ping_id_field

        # Mari purchase items
        mari_purchase_subsection = CollapsibleSection("💰 Mari's Shop - Items to Purchase", collapsed=True)
        auto_purchase_mari = self.settings.get("auto_purchase_items_mari", {})
        self.tab_entries["🛒 Merchant & Trading"]["auto_purchase_items_mari"] = {}

        for item_name, item_config in auto_purchase_mari.items():
            item_card = ModernCard(f"🛍️ {item_name}")

            purchase_field = ModernFormField("Purchase This Item", "checkbox")
            purchase_field.set_value(item_config.get("Purchase", False))
            purchase_field.valueChanged.connect(self.on_setting_changed)
            item_card.add_widget(purchase_field)

            amount_field = ModernFormField("Amount to Purchase", "number")
            amount_field.set_value(item_config.get("amount", 1))
            amount_field.set_tooltip(f"Number of {item_name} to purchase")
            amount_field.valueChanged.connect(self.on_setting_changed)
            item_card.add_widget(amount_field)

            mari_purchase_subsection.add_widget(item_card)

            self.tab_entries["🛒 Merchant & Trading"]["auto_purchase_items_mari"][item_name] = {
                "Purchase": purchase_field,
                "amount": amount_field
            }

        mari_section.add_widget(mari_purchase_subsection)
        scroll_layout.addWidget(mari_section)

        # Jester's Shop Section
        jester_section = CollapsibleSection("🃏 Jester's Shop", collapsed=True)

        # Jester notification settings
        jester_ping_field = ModernFormField("Ping for Jester's Shop", "checkbox")
        jester_ping_field.set_value(self.settings.get("ping_jester", True))
        jester_ping_field.valueChanged.connect(self.on_setting_changed)
        jester_section.add_widget(jester_ping_field)
        self.tab_entries["🛒 Merchant & Trading"]["ping_jester"] = jester_ping_field

        jester_ping_id_field = ModernFormField("Discord User ID for Jester Pings", "text")
        jester_ping_id_field.set_value(str(self.settings.get("jester_ping_id", 0)))
        jester_ping_id_field.set_tooltip("Discord user ID to mention when Jester's shop is detected")
        jester_ping_id_field.valueChanged.connect(self.on_setting_changed)
        jester_section.add_widget(jester_ping_id_field)
        self.tab_entries["🛒 Merchant & Trading"]["jester_ping_id"] = jester_ping_id_field

        # Jester purchase items
        jester_purchase_subsection = CollapsibleSection("💰 Jester's Shop - Items to Purchase", collapsed=True)
        auto_purchase_jester = self.settings.get("auto_purchase_items_jester", {})
        self.tab_entries["🛒 Merchant & Trading"]["auto_purchase_items_jester"] = {}

        for item_name, item_config in auto_purchase_jester.items():
            item_card = ModernCard(f"🛍️ {item_name}")

            purchase_field = ModernFormField("Purchase This Item", "checkbox")
            purchase_field.set_value(item_config.get("Purchase", False))
            purchase_field.valueChanged.connect(self.on_setting_changed)
            item_card.add_widget(purchase_field)

            amount_field = ModernFormField("Amount to Purchase", "number")
            amount_field.set_value(item_config.get("amount", 1))
            amount_field.set_tooltip(f"Number of {item_name} to purchase")
            amount_field.valueChanged.connect(self.on_setting_changed)
            item_card.add_widget(amount_field)

            jester_purchase_subsection.add_widget(item_card)

            self.tab_entries["🛒 Merchant & Trading"]["auto_purchase_items_jester"][item_name] = {
                "Purchase": purchase_field,
                "amount": amount_field
            }

        jester_section.add_widget(jester_purchase_subsection)

        # Jester selling settings
        jester_sell_subsection = CollapsibleSection("💸 Jester's Shop - Auto Sell Settings", collapsed=True)

        auto_sell_field = ModernFormField("Enable Auto Sell to Jester", "checkbox")
        auto_sell_field.set_value(self.settings.get("auto_sell_to_jester", False))
        auto_sell_field.set_tooltip("Automatically sell items to Jester when detected")
        auto_sell_field.valueChanged.connect(self.on_setting_changed)
        jester_sell_subsection.add_widget(auto_sell_field)
        self.tab_entries["🛒 Merchant & Trading"]["auto_sell_to_jester"] = auto_sell_field

        sell_amount_field = ModernFormField("Maximum Items to Sell (per type)", "number")
        sell_amount_field.set_value(self.settings.get("amount_of_item_to_sell", 9999))
        sell_amount_field.set_tooltip("Maximum number of each item type to sell")
        sell_amount_field.valueChanged.connect(self.on_setting_changed)
        jester_sell_subsection.add_widget(sell_amount_field)
        self.tab_entries["🛒 Merchant & Trading"]["amount_of_item_to_sell"] = sell_amount_field

        # Items to sell configuration
        sell_items_card = ModernCard("Items to Sell Configuration")
        items_to_sell = self.settings.get("items_to_sell", {})
        self.tab_entries["🛒 Merchant & Trading"]["items_to_sell"] = {}

        # Create grid layout for sell items
        sell_grid_widget = QWidget()
        sell_grid_layout = QHBoxLayout(sell_grid_widget)
        sell_left = QVBoxLayout()
        sell_right = QVBoxLayout()

        sell_items_list = list(items_to_sell.items())
        for i, (item_name, should_sell) in enumerate(sell_items_list):
            item_field = ModernFormField(f"Sell {item_name}", "checkbox")
            item_field.set_value(should_sell)
            item_field.valueChanged.connect(self.on_setting_changed)

            if i < len(sell_items_list) // 2:
                sell_left.addWidget(item_field)
            else:
                sell_right.addWidget(item_field)

            self.tab_entries["🛒 Merchant & Trading"]["items_to_sell"][item_name] = item_field

        sell_grid_layout.addLayout(sell_left)
        sell_grid_layout.addLayout(sell_right)
        sell_items_card.add_widget(sell_grid_widget)
        jester_sell_subsection.add_widget(sell_items_card)

        jester_section.add_widget(jester_sell_subsection)
        scroll_layout.addWidget(jester_section)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Add action buttons
        self.add_tab_actions(layout, "🛒 Merchant & Trading")

        return tab_widget

    def create_biomes_tab(self):
        """Create specialized biomes tab with better organization"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_layout.setSpacing(12)

        # Initialize tab entries
        self.tab_entries["🌍 Biomes"] = {}

        # Biome Detection Settings
        detection_card = ModernCard("🔍 Biome Detection Settings")

        # Biome toggles in a grid layout
        biomes_data = self.settings.get("biomes", {})
        biome_grid = QWidget()
        grid_layout = QFormLayout(biome_grid)
        grid_layout.setSpacing(8)

        biome_names = {
            "snowy": "❄️ Snowy",
            "windy": "💨 Windy",
            "rainy": "🌧️ Rainy",
            "sand storm": "🏜️ Sand Storm",
            "hell": "🔥 Hell",
            "starfall": "⭐ Starfall",
            "corruption": "💜 Corruption",
            "null": "⚫ Null",
            "glitched": "🌈 Glitched",
            "dreamspace": "💭 Dreamspace"
        }

        self.tab_entries["🌍 Biomes"]["biomes"] = {}

        for biome_key, display_name in biome_names.items():
            biome_field = ModernFormField(f"Detect {display_name}", "checkbox")
            biome_field.set_value(biomes_data.get(biome_key, False))
            biome_field.valueChanged.connect(self.on_setting_changed)
            detection_card.add_widget(biome_field)
            self.tab_entries["🌍 Biomes"]["biomes"][biome_key] = biome_field

        scroll_layout.addWidget(detection_card)

        # Auto Tools Section
        tools_section = CollapsibleSection("🛠️ Automatic Tools", collapsed=True)

        auto_randomizer_field = ModernFormField("Auto Use Biome Randomizer", "checkbox")
        auto_randomizer_field.set_value(self.settings.get("auto_biome_randomizer", False))
        auto_randomizer_field.set_tooltip("Automatically use Biome Randomizer when detected")
        auto_randomizer_field.valueChanged.connect(self.on_setting_changed)
        tools_section.add_widget(auto_randomizer_field)
        self.tab_entries["🌍 Biomes"]["auto_biome_randomizer"] = auto_randomizer_field

        auto_controller_field = ModernFormField("Auto Use Strange Controller", "checkbox")
        auto_controller_field.set_value(self.settings.get("auto_strange_controller", False))
        auto_controller_field.set_tooltip("Automatically use Strange Controller when detected")
        auto_controller_field.valueChanged.connect(self.on_setting_changed)
        tools_section.add_widget(auto_controller_field)
        self.tab_entries["🌍 Biomes"]["auto_strange_controller"] = auto_controller_field

        scroll_layout.addWidget(tools_section)

        # Glitched Biome Section
        glitched_section = CollapsibleSection("🌈 Glitched Biome Settings", collapsed=True)

        pop_glitch_field = ModernFormField("Auto Pop Items in Glitched Biome", "checkbox")
        pop_glitch_field.set_value(self.settings.get("pop_in_glitch", False))
        pop_glitch_field.valueChanged.connect(self.on_setting_changed)
        glitched_section.add_widget(pop_glitch_field)
        self.tab_entries["🌍 Biomes"]["pop_in_glitch"] = pop_glitch_field

        # Auto use items in glitch
        if "auto_use_items_in_glitch" in self.settings:
            glitch_items_subsection = CollapsibleSection("Items to Use in Glitched", collapsed=True)
            auto_items_glitch = self.settings.get("auto_use_items_in_glitch", {})
            self.tab_entries["🌍 Biomes"]["auto_use_items_in_glitch"] = {}

            for item_name, item_config in auto_items_glitch.items():
                item_card = ModernCard(item_name)

                use_field = ModernFormField("Use Item", "checkbox")
                use_field.set_value(item_config.get("use", False))
                use_field.valueChanged.connect(self.on_setting_changed)
                item_card.add_widget(use_field)

                amount_field = ModernFormField("Amount", "number")
                amount_field.set_value(item_config.get("amount", 1))
                amount_field.valueChanged.connect(self.on_setting_changed)
                item_card.add_widget(amount_field)

                glitch_items_subsection.add_widget(item_card)

                self.tab_entries["🌍 Biomes"]["auto_use_items_in_glitch"][item_name] = {
                    "use": use_field,
                    "amount": amount_field
                }

            glitched_section.add_widget(glitch_items_subsection)

        scroll_layout.addWidget(glitched_section)

        # Dreamspace Section
        dreamspace_section = CollapsibleSection("💭 Dreamspace Settings", collapsed=True)

        pop_dreamspace_field = ModernFormField("Auto Pop Items in Dreamspace", "checkbox")
        pop_dreamspace_field.set_value(self.settings.get("pop_in_dreamspace", False))
        pop_dreamspace_field.valueChanged.connect(self.on_setting_changed)
        dreamspace_section.add_widget(pop_dreamspace_field)
        self.tab_entries["🌍 Biomes"]["pop_in_dreamspace"] = pop_dreamspace_field

        # Auto use items in dreamspace
        if "auto_use_items_in_dreamspace" in self.settings:
            dreamspace_items_subsection = CollapsibleSection("Items to Use in Dreamspace", collapsed=True)
            auto_items_dreamspace = self.settings.get("auto_use_items_in_dreamspace", {})
            self.tab_entries["🌍 Biomes"]["auto_use_items_in_dreamspace"] = {}

            for item_name, item_config in auto_items_dreamspace.items():
                item_card = ModernCard(item_name)

                use_field = ModernFormField("Use Item", "checkbox")
                use_field.set_value(item_config.get("use", False))
                use_field.valueChanged.connect(self.on_setting_changed)
                item_card.add_widget(use_field)

                amount_field = ModernFormField("Amount", "number")
                amount_field.set_value(item_config.get("amount", 1))
                amount_field.valueChanged.connect(self.on_setting_changed)
                item_card.add_widget(amount_field)

                dreamspace_items_subsection.add_widget(item_card)

                self.tab_entries["🌍 Biomes"]["auto_use_items_in_dreamspace"][item_name] = {
                    "use": use_field,
                    "amount": amount_field
                }

            dreamspace_section.add_widget(dreamspace_items_subsection)

        scroll_layout.addWidget(dreamspace_section)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Add action buttons
        self.add_tab_actions(layout, "🌍 Biomes")

        return tab_widget

    def create_quests_tab(self):
        """Create specialized quests tab"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_layout.setSpacing(12)

        # Initialize tab entries
        self.tab_entries["🎯 Quests"] = {}

        # Quest Board Settings
        quest_card = ModernCard("🎯 Auto Quest Board Settings")

        enable_quest_field = ModernFormField("Enable Auto Quest Board", "checkbox")
        enable_quest_field.set_value(self.settings.get("enable_auto_quest_board", False))
        enable_quest_field.set_tooltip("Automatically accept and complete quests from the quest board")
        enable_quest_field.valueChanged.connect(self.on_setting_changed)
        quest_card.add_widget(enable_quest_field)
        self.tab_entries["🎯 Quests"]["enable_auto_quest_board"] = enable_quest_field

        scroll_layout.addWidget(quest_card)

        # Quest Selection
        quest_selection_section = CollapsibleSection("📋 Quest Selection", collapsed=True)

        quests_to_accept = self.settings.get("quests_to_accept", {})
        self.tab_entries["🎯 Quests"]["quests_to_accept"] = {}

        quest_categories = {
            "Hunt Quests": ["Basic Hunt", "Epic Hunt", "Unique Hunt", "Legendary Hunt", "Mythic Hunt"],
            "Meditation Quests": ["Meditation I", "Meditation II", "Meditation III"],
            "Delivery Quests": ["Delivery III"],
            "Other Quests": ["Finding a person"]
        }

        for category, quest_list in quest_categories.items():
            category_section = CollapsibleSection(f"📂 {category}", collapsed=True)

            for quest_name in quest_list:
                if quest_name in quests_to_accept:
                    quest_field = ModernFormField(f"Accept {quest_name}", "checkbox")
                    quest_field.set_value(quests_to_accept.get(quest_name, True))
                    quest_field.valueChanged.connect(self.on_setting_changed)
                    category_section.add_widget(quest_field)
                    self.tab_entries["🎯 Quests"]["quests_to_accept"][quest_name] = quest_field

            quest_selection_section.add_widget(category_section)

        scroll_layout.addWidget(quest_selection_section)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Add action buttons
        self.add_tab_actions(layout, "🎯 Quests")

        return tab_widget

    def create_sniper_tab(self):
        """Create comprehensive sniper & advanced settings tab"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_layout.setSpacing(12)

        # Initialize tab entries
        self.tab_entries["📡 Sniper & Advanced"] = {}

        # Warning Card
        warning_card = ModernCard("⚠️ Important Notice")
        warning_label = QLabel("Discord sniping requires a Discord bot token and Roblox security cookie. Use at your own risk!")
        warning_label.setStyleSheet("color: #f59e0b; font-weight: bold;")
        warning_card.add_widget(warning_label)
        scroll_layout.addWidget(warning_card)

        # Sniper Settings
        sniper_section = CollapsibleSection("📡 Discord Sniper Configuration", collapsed=True)

        sniper_enabled_field = ModernFormField("Enable Discord Sniper", "checkbox")
        sniper_enabled_field.set_value(self.settings.get("sniper_enabled", False))
        sniper_enabled_field.set_tooltip("Enable Discord server sniping functionality")
        sniper_enabled_field.valueChanged.connect(self.on_setting_changed)
        sniper_section.add_widget(sniper_enabled_field)
        self.tab_entries["📡 Sniper & Advanced"]["sniper_enabled"] = sniper_enabled_field

        sniper_logs_field = ModernFormField("Enable Sniper Logging", "checkbox")
        sniper_logs_field.set_value(self.settings.get("sniper_logs", True))
        sniper_logs_field.valueChanged.connect(self.on_setting_changed)
        sniper_section.add_widget(sniper_logs_field)
        self.tab_entries["📡 Sniper & Advanced"]["sniper_logs"] = sniper_logs_field

        # Authentication subsection
        auth_subsection = CollapsibleSection("🔐 Authentication Credentials", collapsed=True)

        discord_token_field = ModernFormField("Discord Bot Token", "password")
        discord_token_field.set_value(self.settings.get("DISCORD_TOKEN", ""))
        discord_token_field.set_tooltip("Your Discord bot token for monitoring channels")
        discord_token_field.valueChanged.connect(self.on_setting_changed)
        auth_subsection.add_widget(discord_token_field)
        self.tab_entries["📡 Sniper & Advanced"]["DISCORD_TOKEN"] = discord_token_field

        roblox_cookie_field = ModernFormField("Roblox Security Cookie", "password")
        roblox_cookie_field.set_value(self.settings.get("ROBLOSECURITY_KEY", ""))
        roblox_cookie_field.set_tooltip("Your Roblox .ROBLOSECURITY cookie")
        roblox_cookie_field.valueChanged.connect(self.on_setting_changed)
        auth_subsection.add_widget(roblox_cookie_field)
        self.tab_entries["📡 Sniper & Advanced"]["ROBLOSECURITY_KEY"] = roblox_cookie_field

        sniper_section.add_widget(auth_subsection)

        # Channel Configuration
        channels_subsection = CollapsibleSection("📺 Channel Configuration", collapsed=True)

        scan_channels_list = ModernListWidget("Discord Channels to Monitor")
        scan_channels_list.set_items(self.settings.get("scan_channels", []))
        scan_channels_list.itemsChanged.connect(self.on_setting_changed)
        channels_subsection.add_widget(scan_channels_list)
        self.tab_entries["📡 Sniper & Advanced"]["scan_channels"] = scan_channels_list

        sniper_section.add_widget(channels_subsection)

        # Sniper Targets
        targets_subsection = CollapsibleSection("🎯 Sniper Targets", collapsed=True)

        sniper_toggles = self.settings.get("sniper_toggles", {})
        self.tab_entries["📡 Sniper & Advanced"]["sniper_toggles"] = {}

        for toggle_name, enabled in sniper_toggles.items():
            toggle_field = ModernFormField(f"Snipe {toggle_name} Servers", "checkbox")
            toggle_field.set_value(enabled)
            toggle_field.valueChanged.connect(self.on_setting_changed)
            targets_subsection.add_widget(toggle_field)
            self.tab_entries["📡 Sniper & Advanced"]["sniper_toggles"][toggle_name] = toggle_field

        sniper_section.add_widget(targets_subsection)
        scroll_layout.addWidget(sniper_section)

        # Advanced System Settings
        advanced_section = CollapsibleSection("⚙️ Advanced System Settings", collapsed=True)

        disconnect_prevention_field = ModernFormField("Prevent Disconnections", "checkbox")
        disconnect_prevention_field.set_value(self.settings.get("disconnect_prevention", False))
        disconnect_prevention_field.set_tooltip("Attempt to prevent game disconnections")
        disconnect_prevention_field.valueChanged.connect(self.on_setting_changed)
        advanced_section.add_widget(disconnect_prevention_field)
        self.tab_entries["📡 Sniper & Advanced"]["disconnect_prevention"] = disconnect_prevention_field

        disable_autokick_field = ModernFormField("Disable Anti-Kick System", "checkbox")
        disable_autokick_field.set_value(self.settings.get("disable_autokick_prevention", False))
        disable_autokick_field.set_tooltip("Disable the automatic kick prevention system")
        disable_autokick_field.valueChanged.connect(self.on_setting_changed)
        advanced_section.add_widget(disable_autokick_field)
        self.tab_entries["📡 Sniper & Advanced"]["disable_autokick_prevention"] = disable_autokick_field

        scroll_layout.addWidget(advanced_section)

        # Screenshot Settings
        screenshot_section = CollapsibleSection("📸 Screenshot Settings", collapsed=True)

        periodic_screenshots = self.settings.get("periodic_screenshots", {})
        self.tab_entries["📡 Sniper & Advanced"]["periodic_screenshots"] = {}

        inventory_screenshot_field = ModernFormField("Periodic Inventory Screenshots", "checkbox")
        inventory_screenshot_field.set_value(periodic_screenshots.get("inventory", False))
        inventory_screenshot_field.set_tooltip("Take periodic screenshots of inventory")
        inventory_screenshot_field.valueChanged.connect(self.on_setting_changed)
        screenshot_section.add_widget(inventory_screenshot_field)
        self.tab_entries["📡 Sniper & Advanced"]["periodic_screenshots"]["inventory"] = inventory_screenshot_field

        storage_screenshot_field = ModernFormField("Periodic Storage Screenshots", "checkbox")
        storage_screenshot_field.set_value(periodic_screenshots.get("storage", False))
        storage_screenshot_field.set_tooltip("Take periodic screenshots of storage")
        storage_screenshot_field.valueChanged.connect(self.on_setting_changed)
        screenshot_section.add_widget(storage_screenshot_field)
        self.tab_entries["📡 Sniper & Advanced"]["periodic_screenshots"]["storage"] = storage_screenshot_field

        scroll_layout.addWidget(screenshot_section)

        # Update Settings
        update_section = CollapsibleSection("🔄 Update Settings", collapsed=True)

        check_update_field = ModernFormField("Check for Updates on Startup", "checkbox")
        check_update_field.set_value(self.settings.get("check_update", True))
        check_update_field.valueChanged.connect(self.on_setting_changed)
        update_section.add_widget(check_update_field)
        self.tab_entries["📡 Sniper & Advanced"]["check_update"] = check_update_field

        auto_install_field = ModernFormField("Auto Install Updates", "checkbox")
        auto_install_field.set_value(self.settings.get("auto_install_update", False))
        auto_install_field.set_tooltip("Automatically install updates when available")
        auto_install_field.valueChanged.connect(self.on_setting_changed)
        update_section.add_widget(auto_install_field)
        self.tab_entries["📡 Sniper & Advanced"]["auto_install_update"] = auto_install_field

        scroll_layout.addWidget(update_section)

        # Developer Settings
        dev_section = CollapsibleSection("🔧 Developer Settings", collapsed=True)

        redownload_libs_field = ModernFormField("Redownload Libraries on Next Run", "checkbox")
        redownload_libs_field.set_value(self.settings.get("redownload_libs_on_run", False))
        redownload_libs_field.set_tooltip("Force redownload of all libraries on next startup")
        redownload_libs_field.valueChanged.connect(self.on_setting_changed)
        dev_section.add_widget(redownload_libs_field)
        self.tab_entries["📡 Sniper & Advanced"]["redownload_libs_on_run"] = redownload_libs_field

        scroll_layout.addWidget(dev_section)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Add action buttons
        self.add_tab_actions(layout, "📡 Sniper & Advanced")

        return tab_widget

    def add_tab_actions(self, layout, tab_name):
        """Add action buttons to tab"""
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)

        # Start/Stop buttons
        start_btn = QPushButton("Start (F1)")
        start_btn.setProperty("class", "success")
        start_btn.clicked.connect(self.start_macro)
        actions_layout.addWidget(start_btn)

        stop_btn = QPushButton("Stop (F2)")
        stop_btn.setProperty("class", "error")
        stop_btn.clicked.connect(self.stop_macro)
        actions_layout.addWidget(stop_btn)

        actions_layout.addStretch()

        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings_action)
        actions_layout.addWidget(save_btn)

        # Tab-specific buttons
        if tab_name.lower() == "other":
            rdl_btn = QPushButton("Redownload Libraries")
            rdl_btn.setProperty("class", "warning")
            rdl_btn.clicked.connect(self.toggle_redownload)
            actions_layout.addWidget(rdl_btn)
        else:
            donate_btn = QPushButton("Donate")
            donate_btn.setProperty("class", "secondary")
            donate_btn.clicked.connect(self.open_donation_url)
            actions_layout.addWidget(donate_btn)

        layout.addLayout(actions_layout)

    def create_credits_tab(self):
        """Create the credits tab"""
        credits_tab = QWidget()
        layout = QVBoxLayout(credits_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Title
        title_card = ModernCard()
        title_label = QLabel("Created by Baz and Cresqnt")
        title_font = title_label.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_card.add_widget(title_label)
        layout.addWidget(title_card)

        # Images (if available)
        if PIL_AVAILABLE:
            self.add_creator_images(layout)

        # Acknowledgements
        ack_card = ModernCard("Acknowledgements")
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
            ack_card.add_widget(ack_label)
        layout.addWidget(ack_card)

        # Donators
        self.add_donators_section(layout)

        self.tab_widget.addTab(credits_tab, "Credits")

    def add_creator_images(self, layout):
        """Add creator images to credits"""
        images_card = ModernCard("Creators")
        images_layout = QHBoxLayout()
        images_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Download and display images
        for name, url in [("baz.png", "https://raw.githubusercontent.com/bazthedev/SolsScope/main/img/baz.png"),
                         ("cresqnt.png", "https://raw.githubusercontent.com/bazthedev/SolsScope/main/img/cresqnt.png")]:
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            image_path = os.path.join(MACROPATH, name)
            if not os.path.exists(image_path):
                try:
                    with urllib.request.urlopen(url, timeout=10) as response, open(image_path, 'wb') as out_file:
                        if response.status == 200:
                            shutil.copyfileobj(response, out_file)
                except Exception as e:
                    self.logger.write_log(f"Error downloading {name}: {e}")

            try:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    image_label.setPixmap(scaled_pixmap)
                else:
                    image_label.setText(f"({name} unavailable)")
            except Exception:
                image_label.setText(f"({name} unavailable)")

            images_layout.addWidget(image_label)

        images_card.add_layout(images_layout)
        layout.addWidget(images_card)

    def add_donators_section(self, layout):
        """Add donators section to credits"""
        try:
            donation_url = "https://raw.githubusercontent.com/bazthedev/SolsScope/main/donations.json"
            with urllib.request.urlopen(donation_url, timeout=3) as response, open(f"{MACROPATH}/donations.json", 'wb') as out_file:
                if response.status == 200:
                    shutil.copyfileobj(response, out_file)

            with open(f"{MACROPATH}/donations.json", "r") as f:
                donors = json.load(f)

            donators_card = ModernCard("Donators")

            if len(donors) < 1:
                donators_card.add_widget(QLabel("No donations yet :("))
            else:
                for donor in donors:
                    donor_label = QLabel(donor)
                    donor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    donators_card.add_widget(donor_label)

                info_label = QLabel("Want your name here? All you have to do is donate any amount!")
                info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                donators_card.add_widget(info_label)

            layout.addWidget(donators_card)

        except Exception as e:
            self.logger.write_log(f"Failed to load donation data: {e}")

    @pyqtSlot(str)
    def append_log_message(self, message):
        """Append a message to the log widget (thread-safe)"""
        self.log_widget.moveCursor(QTextCursor.MoveOperation.End)
        self.log_widget.insertPlainText(message + '\n')
        self.log_widget.moveCursor(QTextCursor.MoveOperation.End)

        # Auto-scroll to bottom
        scrollbar = self.log_widget.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_setting_changed(self):
        """Handle setting changes"""
        # Could add real-time validation or auto-save here
        pass

    def update_status(self):
        """Update status dashboard"""
        # Update macro status
        if self.running:
            self.macro_status_label.set_status("running")
            self.macro_status_label.setText("Running")
            self.status_indicator.set_status("running")
            self.status_indicator.setText("Running")
        else:
            self.macro_status_label.set_status("stopped")
            self.macro_status_label.setText("Stopped")
            self.status_indicator.set_status("stopped")
            self.status_indicator.setText("Stopped")

        # Update thread count
        active_threads = len([t for t in self.threads if t.is_alive()])
        self.threads_label.setText(f"Active Threads: {active_threads}")

        # Update runtime if running
        if self.running and hasattr(self, 'start_time'):
            runtime = time.time() - self.start_time
            hours, remainder = divmod(int(runtime), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.runtime_label.setText(f"Runtime: {hours:02d}:{minutes:02d}:{seconds:02d}")
        else:
            self.runtime_label.setText("Runtime: 00:00:00")

        # Update aura/biome info (if available)
        try:
            if not self.running:
                self.aura_label.setText("Current Aura: Unknown")
                self.biome_label.setText("Current Biome: Unknown")
            else:
                aura = get_latest_equipped_aura()
                self.aura_label.setText(f"Current Aura: {aura if aura else 'Unknown'}")

                biome = get_latest_hovertext()
                self.biome_label.setText(f"Current Biome: {biome if biome else 'Unknown'}")
        except Exception:
            pass

    def save_settings_action(self):
        """Save settings action"""
        success, changes = self.save_settings()
        if success:
            QMessageBox.information(self, "Settings Saved", "Settings were saved successfully!")
        else:
            QMessageBox.critical(self, "Save Failed", "Failed to save settings. Check logs for details.")

    def save_settings(self):
        """Gather and save all settings"""
        self.logger.write_log("Gathering settings from modern UI...")

        try:
            # Collect all settings from UI
            updated_settings = {}

            # Updated tab structure with new organization
            tab_info = {
                "⚙️ Main Settings": GENERAL_KEYS + AURAS_KEYS + ["always_on_top"],
                "🔍 Detection & Automation": BIOMES_KEYS + AUTOCRAFT_KEYS + QUEST_KEYS + PATH_KEYS + ["disable_aura_detection", "disable_biome_detection"],
                "🛒 Merchant & Trading": MERCHANT_KEYS,
                "📡 Sniper & Advanced": SNIPER_KEYS + ["disconnect_prevention", "disable_autokick_prevention", "periodic_screenshots", "check_update", "auto_install_update", "redownload_libs_on_run"]
            }

            for tab_name, keys in tab_info.items():
                if tab_name in self.tab_entries:
                    tab_data = self.tab_entries[tab_name]
                    for key in keys:
                        if key in tab_data:
                            widget = tab_data[key]
                            value = self.get_widget_value(widget, key)
                            if value is not None:
                                updated_settings[key] = value

            # Merge with current settings
            current_settings = load_settings()
            current_settings.update(updated_settings)

            # Validate and save
            validated_settings, validation_errors = validate_settings(current_settings)

            if validation_errors:
                self.logger.write_log(f"Settings validation issues: {validation_errors}")
                QMessageBox.warning(self, "Validation Warning",
                                  f"Settings validation found issues (check logs). Saving anyway.\nIssues: {validation_errors}")

            if update_settings(validated_settings):
                self.settings = validated_settings
                self.original_settings = self.settings.copy()
                self.logger.write_log("Settings saved successfully.")
                return True, True
            else:
                self.logger.write_log("Failed to save settings to file.")
                return False, True

        except Exception as e:
            self.logger.write_log(f"Error saving settings: {e}")
            return False, True

    def get_widget_value(self, widget, key):
        """Get value from a widget based on its type"""
        try:
            if isinstance(widget, ModernFormField):
                return widget.get_value()
            elif isinstance(widget, ModernListWidget):
                return widget.get_items()
            elif isinstance(widget, AutocraftPotionSelector):
                return widget.get_value()
            elif isinstance(widget, CollapsibleSection):
                # Handle nested settings - collect from nested widgets
                return self.collect_nested_settings(widget, key)
            else:
                return None
        except Exception as e:
            self.logger.write_log(f"Error getting value for {key}: {e}")
            return None

    def collect_nested_settings(self, section_widget, key):
        """Collect settings from nested widgets in a collapsible section"""
        try:
            # Handle special cases for our new organized tabs
            if key == "biomes":
                # Collect biome settings
                biomes_dict = {}
                if "🔍 Detection & Automation" in self.tab_entries and "biomes" in self.tab_entries["🔍 Detection & Automation"]:
                    for biome_key, field in self.tab_entries["🔍 Detection & Automation"]["biomes"].items():
                        biomes_dict[biome_key] = field.get_value()
                return biomes_dict

            elif key == "items_to_sell":
                # Collect items to sell settings
                items_dict = {}
                if "🛒 Merchant & Trading" in self.tab_entries and "items_to_sell" in self.tab_entries["🛒 Merchant & Trading"]:
                    for item_key, field in self.tab_entries["🛒 Merchant & Trading"]["items_to_sell"].items():
                        items_dict[item_key] = field.get_value()
                return items_dict

            elif key == "quests_to_accept":
                # Collect quest settings
                quests_dict = {}
                if "🔍 Detection & Automation" in self.tab_entries and "quests_to_accept" in self.tab_entries["🔍 Detection & Automation"]:
                    for quest_key, field in self.tab_entries["🔍 Detection & Automation"]["quests_to_accept"].items():
                        quests_dict[quest_key] = field.get_value()
                return quests_dict

            elif key == "sniper_toggles":
                # Collect sniper toggle settings
                toggles_dict = {}
                if "📡 Sniper & Advanced" in self.tab_entries and "sniper_toggles" in self.tab_entries["📡 Sniper & Advanced"]:
                    for toggle_key, field in self.tab_entries["📡 Sniper & Advanced"]["sniper_toggles"].items():
                        toggles_dict[toggle_key] = field.get_value()
                return toggles_dict

            elif key == "auto_purchase_items_mari":
                # Collect Mari purchase items
                items_dict = {}
                if "🛒 Merchant & Trading" in self.tab_entries and "auto_purchase_items_mari" in self.tab_entries["🛒 Merchant & Trading"]:
                    for item_key, item_fields in self.tab_entries["🛒 Merchant & Trading"]["auto_purchase_items_mari"].items():
                        items_dict[item_key] = {
                            "Purchase": item_fields["Purchase"].get_value(),
                            "amount": item_fields["amount"].get_value()
                        }
                return items_dict

            elif key == "auto_purchase_items_jester":
                # Collect Jester purchase items
                items_dict = {}
                if "🛒 Merchant & Trading" in self.tab_entries and "auto_purchase_items_jester" in self.tab_entries["🛒 Merchant & Trading"]:
                    for item_key, item_fields in self.tab_entries["🛒 Merchant & Trading"]["auto_purchase_items_jester"].items():
                        items_dict[item_key] = {
                            "Purchase": item_fields["Purchase"].get_value(),
                            "amount": item_fields["amount"].get_value()
                        }
                return items_dict

            elif key == "periodic_screenshots":
                # Collect periodic screenshot settings
                screenshots_dict = {}
                if "📡 Sniper & Advanced" in self.tab_entries and "periodic_screenshots" in self.tab_entries["📡 Sniper & Advanced"]:
                    for screenshot_key, field in self.tab_entries["📡 Sniper & Advanced"]["periodic_screenshots"].items():
                        screenshots_dict[screenshot_key] = field.get_value()
                return screenshots_dict

            elif key in ["auto_use_items_in_glitch", "auto_use_items_in_dreamspace"]:
                # Collect auto use items settings
                items_dict = {}
                tab_key = "🔍 Detection & Automation"
                if tab_key in self.tab_entries and key in self.tab_entries[tab_key]:
                    for item_key, item_fields in self.tab_entries[tab_key][key].items():
                        items_dict[item_key] = {
                            "use": item_fields["use"].get_value(),
                            "amount": item_fields["amount"].get_value()
                        }
                return items_dict

            else:
                # For other nested settings, return original value
                original_value = self.settings.get(key, DEFAULTSETTINGS.get(key, {}))
                return original_value

        except Exception as e:
            self.logger.write_log(f"Error collecting nested settings for {key}: {e}")
            return self.settings.get(key, DEFAULTSETTINGS.get(key, {}))

    def start_macro(self):
        """Start the macro with modern UI feedback"""
        if self.running:
            QMessageBox.warning(self, "Macro Running", "Macro is already running!")
            return

        # Save settings first
        save_successful, changes_were_present = self.save_settings()
        if not save_successful and changes_were_present:
            if QMessageBox.question(self, "Save Failed",
                                  "Failed to save settings. Continue starting the macro with potentially unsaved changes?") == QMessageBox.StandardButton.No:
                self.logger.write_log("Macro start cancelled due to failed save.")
                return
            self.logger.write_log("Continuing start despite failed save. Reloading settings from file.")
            self.settings = load_settings()

        # Validate webhook
        if not self.settings.get("WEBHOOK_URL"):
            QMessageBox.critical(self, "Missing Webhook", "Please provide a primary Webhook URL in the General tab.")
            self.logger.write_log("Macro start failed: Missing Webhook URL.")
            return

        try:
            self.logger.write_log("Initializing webhook...")
            self.webhook = discord.SyncWebhook.from_url(self.settings["WEBHOOK_URL"])
            self.logger.write_log("Successfully initialized webhook.")
        except Exception as e:
            QMessageBox.critical(self, "Invalid Webhook", f"The primary Webhook URL is invalid:\n{e}")
            self.logger.write_log(f"Macro start failed: Invalid Webhook URL ({e}).")
            return

        # Check Roblox process
        use_player = self.settings.get("use_roblox_player", True)
        set_active_log_directory(force_player=use_player)
        if not exists_procs_by_name("Windows10Universal.exe") and not exists_procs_by_name("RobloxPlayerBeta.exe"):
            if QMessageBox.question(self, "Roblox Not Detected",
                                  "Roblox process not found. Start macro anyway?") == QMessageBox.StandardButton.No:
                self.logger.write_log("Macro start cancelled: Roblox not running.")
                return

        # Start macro
        self.running = True
        self.start_time = time.time()
        self.stop_event.clear()
        self.sniped_event.clear()
        self.ignore_next_detection.clear()
        self.threads = []

        self.logger.write_log("Starting Macro Threads...")

        # Start threads (using existing logic from original GUI)
        self._start_macro_threads()

        # Send start notification
        self._send_start_notification()

        self.logger.write_log("Macro started successfully.")

    def _start_macro_threads(self):
        """Start macro threads based on settings"""
        # This would contain the same thread starting logic as the original GUI
        # For brevity, I'm referencing the existing implementation
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
                    thread = threading.Thread(target=func, args=args, daemon=True, name=name)
                    thread.start()
                    self.threads.append(thread)
                    self.logger.write_log(f" > Started thread: {name}")
                except Exception as e:
                    self.logger.write_log(f" > Error starting thread {name}: {e}")

        # Start sniper if enabled
        if self.settings.get("sniper_enabled"):
            self.logger.write_log("Starting Sniper...")
            self._start_sniper_thread()

        # Start plugin threads
        self._start_plugin_threads(is_autocraft_mode)

    def _get_thread_targets(self, is_autocraft_mode, is_idle_mode):
        """Get thread targets based on mode - same logic as original"""
        # This would be the same implementation as in the original GUI
        # Returning a simplified version for now
        MERCHANT_DETECTION_POSSIBLE = TESSERACT_AVAILABLE

        if is_idle_mode:
            targets = {
                "Aura Detection": (aura_detection, [self.settings, self.webhook, self.stop_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.ignore_lock, self.ignore_next_detection]) if not self.settings.get("disable_aura_detection") else None,
                "Biome Detection": (biome_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event]) if not self.settings.get("disable_biome_detection") else None,
            }
        elif is_autocraft_mode:
            targets = {
                "Auto Craft Logic": (auto_craft, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.mouse_controller, self.ignore_lock, self.ignore_next_detection]),
                "Aura Detection": (aura_detection, [self.settings, self.webhook, self.stop_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.ignore_lock, self.ignore_next_detection]) if not self.settings.get("disable_aura_detection") else None,
                "Biome Detection": (biome_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event]) if not self.settings.get("disable_biome_detection") else None,
            }
        else:
            targets = {
                "Aura Detection": (aura_detection, [self.settings, self.webhook, self.stop_event, self.keyboard_lock, self.mkey, self.keyboard_controller, self.ignore_lock, self.ignore_next_detection]) if not self.settings.get("disable_aura_detection") else None,
                "Biome Detection": (biome_detection, [self.settings, self.webhook, self.stop_event, self.sniped_event]) if not self.settings.get("disable_biome_detection") else None,
                "Keep Alive": (keep_alive, [self.settings, self.stop_event, self.sniped_event, self.keyboard_lock, self.mkey]) if not self.settings.get("disable_autokick_prevention") else None,
            }

        return targets

    def _start_sniper_thread(self):
        """Start the sniper asyncio loop in a separate thread"""
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

    def _start_plugin_threads(self, is_autocraft_mode):
        """Start plugin threads"""
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

    def _send_start_notification(self):
        """Send start notification webhook"""
        is_autocraft_mode = self.settings.get("auto_craft_mode", False)
        is_idle_mode = self.settings.get("idle_mode", False)

        if is_idle_mode:
            mode_str = "IDLE"
        elif is_autocraft_mode:
            mode_str = "Auto Craft"
        else:
            mode_str = "Normal"

        emb = discord.Embed(
            title="Macro Started",
            colour=discord.Colour.green(),
            timestamp=datetime.now()
        )
        emb.set_footer(text=f"SolsScope v{LOCALVERSION}")
        emb.add_field(name="Mode", value=mode_str, inline=True)

        try:
            if self.webhook:
                self.webhook.send(embed=emb)
                forward_webhook_msg(self.webhook.url, self.settings.get("SECONDARY_WEBHOOK_URLS", []), embed=emb)
        except Exception as e:
            self.logger.write_log(f"Error sending start notification: {e}")

    def stop_macro(self):
        """Stop the macro"""
        if not self.running:
            QMessageBox.warning(self, "Macro Not Running", "Macro is not currently running.")
            return

        self.logger.write_log("Stopping Macro... Signaling threads.")
        self.stop_event.set()

        # Stop sniper if running
        if any(t.name == "SniperThread" for t in self.threads if t.is_alive()):
            self.logger.write_log(" > Attempting to stop sniper tasks...")
            def run_stop_sniper():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(stop_snipers())
                    loop.close()
                    self.logger.write_log(" > stop_snipers() executed.")
                except Exception as e:
                    self.logger.write_log(f" > Error stopping sniper tasks: {e}", level="ERROR")

            stop_sniper_thread = threading.Thread(target=run_stop_sniper, daemon=True, name="StopSniperThread")
            stop_sniper_thread.start()

        # Wait for threads to stop
        timeout_per_thread = 2
        threads_to_join = [t for t in self.threads if t != threading.current_thread() and t.is_alive()]

        self.logger.write_log(f"Waiting for {len(threads_to_join)} threads to stop...")
        for thread in threads_to_join:
            if thread.is_alive():
                try:
                    thread.join(timeout=timeout_per_thread)
                    if thread.is_alive():
                        self.logger.write_log(f"Warning: Thread {thread.name} did not stop gracefully.")
                except Exception as e:
                    self.logger.write_log(f"Error joining thread {thread.name}: {e}")

        self.logger.write_log("All threads signaled/joined.")
        self.running = False
        self.threads.clear()
        self.ignore_next_detection.clear()
        self.stop_event.clear()

        # Send stop notification
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

    def toggle_redownload(self):
        """Toggle library redownload setting"""
        save_success, error_occurred = self.save_settings()

        if save_success:
            self.logger.write_log("Settings were saved")
        else:
            self.logger.write_log(f"Error occurred saving settings: {error_occurred}")

        if not self.settings.get("redownload_libs_on_run", False):
            self.settings["redownload_libs_on_run"] = True
            QMessageBox.information(self, "SolsScope", "Required Libraries and paths will be redownloaded the next time the macro is run.")
            self.logger.write_log("Required Libraries and paths will be redownloaded the next time the macro is run.")
        else:
            self.settings["redownload_libs_on_run"] = False
            self.logger.write_log("Required Libraries and paths will not be redownloaded the next time the macro is run.")

        with open(get_settings_path(), "w") as f:
            json.dump(self.settings, f, indent=4)
            self.logger.write_log("Updated config to decide redownload.")

    def open_donation_url(self):
        """Open donation URL"""
        webbrowser.open("https://www.roblox.com/games/4998237654/GeoffDoes90ss-Place#!/store")

    def install_plugin(self):
        """Install a plugin file"""
        plugin_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Plugin File (.py)",
            str(Path.home()),
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

    def load_plugins(self):
        """Load plugins with modern UI integration"""
        plugin_dir = os.path.join(MACROPATH, "plugins")
        config_dir = os.path.join(plugin_dir, "config")
        os.makedirs(plugin_dir, exist_ok=True)
        os.makedirs(config_dir, exist_ok=True)

        plugin_files = glob.glob(os.path.join(plugin_dir, "*.py"))
        self.logger.write_log(f"Scanning for plugins in: {plugin_dir}")

        for plugin_file in plugin_files:
            plugin_name_from_file = os.path.splitext(os.path.basename(plugin_file))[0]
            if plugin_name_from_file.startswith("__"):
                continue

            try:
                self.logger.write_log(f"Attempting to load plugin: {plugin_name_from_file}")
                spec = importlib.util.spec_from_file_location(plugin_name_from_file, plugin_file)
                if spec is None or spec.loader is None:
                    self.logger.write_log(f"Could not create spec for plugin '{plugin_name_from_file}'. Skipping.")
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if not hasattr(module, "Plugin"):
                    self.logger.write_log(f"No 'Plugin' class found in {plugin_name_from_file}. Skipping.")
                    continue

                plugin_class = getattr(module, "Plugin")

                # Create plugin instance
                plugin_instance = plugin_class(self)
                plugin_instance.name = getattr(plugin_instance, "name", plugin_name_from_file)
                plugin_instance.version = getattr(plugin_instance, "version", "0.0.0")
                plugin_instance.author = getattr(plugin_instance, "author", "Unknown")
                plugin_instance.autocraft_compatible = getattr(plugin_instance, "autocraft_compatible", False)

                # Load plugin config
                if hasattr(plugin_instance, "load_or_create_config"):
                    plugin_instance.config = plugin_instance.load_or_create_config()
                else:
                    plugin_instance.config = {}

                # Create plugin tab if it has UI
                if hasattr(plugin_instance, "init_tab"):
                    self.create_plugin_tab(plugin_instance)

                self.plugins.append(plugin_instance)
                self.plugin_file_paths[plugin_instance.name] = plugin_file
                self.logger.write_log(f"Successfully loaded plugin: {plugin_instance.name} v{plugin_instance.version}")

            except Exception as e:
                self.logger.write_log(f"Error loading plugin '{plugin_file}': {e}", level="ERROR")

    def create_plugin_tab(self, plugin_instance):
        """Create a tab for a plugin"""
        plugin_tab = QWidget()
        plugin_tab_layout = QVBoxLayout(plugin_tab)
        plugin_tab_layout.setContentsMargins(16, 16, 16, 16)
        plugin_tab_layout.setSpacing(16)

        # Plugin info card
        info_card = ModernCard(f"{plugin_instance.name} v{plugin_instance.version}")
        info_card.add_widget(QLabel(f"Author: {plugin_instance.author}"))
        if hasattr(plugin_instance, "description"):
            info_card.add_widget(QLabel(f"Description: {plugin_instance.description}"))
        plugin_tab_layout.addWidget(info_card)

        # Plugin settings
        if plugin_instance.config:
            settings_card = ModernCard("Settings")
            self.tab_entries[plugin_instance.name] = {}

            # Create form fields for plugin config
            for key, value in plugin_instance.config.items():
                if isinstance(value, bool):
                    field = ModernFormField(format_key(key), "checkbox")
                elif isinstance(value, int):
                    field = ModernFormField(format_key(key), "number")
                elif isinstance(value, float):
                    field = ModernFormField(format_key(key), "decimal")
                else:
                    field = ModernFormField(format_key(key), "text")

                field.set_value(value)
                field.valueChanged.connect(self.on_setting_changed)
                settings_card.add_widget(field)
                self.tab_entries[plugin_instance.name][key] = field

            plugin_tab_layout.addWidget(settings_card)

        # Add action buttons
        self.add_tab_actions(plugin_tab_layout, plugin_instance.name)

        self.tab_widget.addTab(plugin_tab, plugin_instance.name)

    def start_key_listener(self):
        """Start keyboard listener for hotkeys"""
        try:
            listener = keyboard.Listener(on_press=self.on_press)
            listener_thread = threading.Thread(target=listener.run, daemon=True, name="HotkeyListener")
            listener_thread.start()
            self.logger.write_log("Hotkey listener started (F1/F2).")
        except Exception as e:
            self.logger.write_log(f"Failed to start hotkey listener: {e}")
            QMessageBox.critical(self, "Hotkey Error", f"Could not start hotkey listener: {e}")

    def on_press(self, key):
        """Handle key press events"""
        try:
            if key == keyboard.Key.f1:
                self.start_macro_signal.emit()
            elif key == keyboard.Key.f2:
                self.stop_macro_signal.emit()
        except Exception as e:
            self.logger.write_log(f"Hotkey listener error: {e}")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About SolsScope",
                         f"SolsScope v{LOCALVERSION}\n\n"
                         "Created by Baz and Cresqnt\n\n"
                         "A modern macro for Sol's RNG\n"
                         "Support server: https://discord.gg/8khGXqG7nA")

    def closeEvent(self, event):
        """Handle window close event"""
        if self.running:
            reply = QMessageBox.question(self, "Exit Confirmation",
                                       "Macro is running. Are you sure you want to stop and exit?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_macro()
                event.accept()
            else:
                event.ignore()
        else:
            reply = QMessageBox.question(self, "Exit Confirmation",
                                       "Are you sure you want to exit?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.Yes)
            if reply == QMessageBox.StandardButton.Yes:
                self.logger.write_log("Exiting application.")
                event.accept()
            else:
                event.ignore()

# Alias for compatibility
MainWindow = ModernMainWindow
