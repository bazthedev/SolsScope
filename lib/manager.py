"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v2.0.0
Support server: https://discord.gg/8khGXqG7nA
"""

import sys, os, json, requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QListWidget, QVBoxLayout, QLabel, QPushButton,
    QTextEdit, QMessageBox, QStackedWidget, QComboBox, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

try:
    from constants import MACROPATH
except ImportError:
    MACROPATH = os.path.join(os.path.expandvars(r"%localappdata%"), "SolsScope")

LOCKFILE = os.path.join(MACROPATH, "manager.json")

def load_lockfile():
    if os.path.exists(LOCKFILE):
        try:
            with open(LOCKFILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"plugins": {}, "themes": {}}
    return {"plugins": {}, "themes": {}}

def save_lockfile(data):
    os.makedirs(os.path.dirname(LOCKFILE), exist_ok=True)
    with open(LOCKFILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

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

class ManagerGUI(QDialog):
    def __init__(self, gui, plugin_index, theme_index):
        super().__init__()
        self.gui = gui
        self.plugin_index = plugin_index
        self.theme_index = theme_index
        self.lock = load_lockfile()

        self.setWindowTitle("SolsScope Extras")
        self.setMinimumSize(400, 300)
        self.resize(500, 500)
        self.setObjectName("ManagerGUI")

        icon_path = os.path.join(MACROPATH, "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        if self.gui:
            self.setStyleSheet(self.gui.styleSheet())

        layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        self.selector = QComboBox()
        self.selector.addItems(["Plugins", "Themes"])
        self.selector.currentTextChanged.connect(self.change_mode)
        top_layout.addWidget(self.selector)

        self.manual_button = QPushButton("Manual Install")
        self.manual_button.clicked.connect(self.manual_install)
        top_layout.addWidget(self.manual_button)

        layout.addLayout(top_layout)

        self.main_area = QStackedWidget()
        layout.addWidget(self.main_area)

        self.plugin_widget = ItemManager(self.gui, plugin_index, mode="Plugin", lock=self.lock)
        self.theme_widget = ItemManager(self.gui, theme_index, mode="Theme", lock=self.lock)

        self.main_area.addWidget(self.plugin_widget)
        self.main_area.addWidget(self.theme_widget)

        self.change_mode("Plugins")

    def change_mode(self, mode):
        if mode == "Plugins":
            self.main_area.setCurrentWidget(self.plugin_widget)
        else:
            self.main_area.setCurrentWidget(self.theme_widget)

    def closeEvent(self, event):
        save_lockfile(self.lock)
        event.accept()

    def manual_install(self):

        if self.selector.currentText().lower() == "plugins":
            self.gui.install_plugin()
        else:
            self.gui.apply_theme_button()

class ItemManager(QWidget):
    def __init__(self, gui, index_data, mode="Plugin", lock=None):
        super().__init__()
        self.gui = gui
        self.index_data = index_data
        self.mode = mode
        self.lock = lock or {"plugins": {}, "themes": {}}
        self.section = "plugins" if self.mode == "Plugin" else "themes"
        self.installed = self.lock.get(self.section, {})

        layout = QHBoxLayout(self)
        self.sidebar = QListWidget()
        self.sidebar.addItems(index_data.keys())
        self.sidebar.currentTextChanged.connect(self.show_info)
        layout.addWidget(self.sidebar, 1)

        self.info_panel = QWidget()
        info_layout = QVBoxLayout(self.info_panel)

        self.name_label = QLabel()
        self.desc_text = QTextEdit()
        self.desc_text.setReadOnly(True)
        self.authors_label = QLabel()
        self.version_label = QLabel()
        self.installed_label = QLabel()
        self.requires_label = QLabel()
        self.requirements_label = QLabel()

        self.install_button = QPushButton("Install")
        self.uninstall_button = QPushButton("Uninstall")

        self.install_button.clicked.connect(self.install_item)
        self.uninstall_button.clicked.connect(self.uninstall_item)

        for widget in [
            self.name_label, self.desc_text, self.authors_label,
            self.version_label, self.installed_label, self.requires_label,
            self.requirements_label, self.install_button, self.uninstall_button
        ]:
            info_layout.addWidget(widget)

        layout.addWidget(self.info_panel, 3)

    def show_info(self, key):
        if not key:
            return
        item = self.index_data[key]
        self.name_label.setText(f"<b>{item['name']}</b>")
        self.desc_text.setText(item.get('description', 'No description.'))
        self.authors_label.setText(f"Authors: {', '.join(item.get('authors', []))}")
        self.version_label.setText(f"Latest Version: {item.get('version', 'N/A') if self.mode=='Plugin' else 'N/A'}")
        self.installed_label.setText(f"Installed Version: {self.installed.get(item['name'], 'Not Installed')}")

        if self.mode == "Plugin":
            self.requires_label.setText(f"Requires SolsScope v{item.get('requires_version', 'N/A')}")
            self.requirements_label.setText(f"Plugin Requirements: {', '.join(item.get('plugin_requirements', [])) or 'None'}")

            if item['name'] in self.installed and self.installed[item['name']] == item.get('version'):
                self.install_button.setEnabled(False)
                self.install_button.setText("Up to date")
            else:
                self.install_button.setEnabled(True)
                self.install_button.setText("Upgrade" if item['name'] in self.installed else "Install")
        else:
            if item['name'] in self.installed and self.installed[item['name']] == item.get('version'):
                self.install_button.setEnabled(False)
                self.install_button.setText("Up to date")
            else:
                if item['name'] in self.installed:
                    self.install_button.setEnabled(False)
                    self.install_button.setText("Installed")
                else:
                    self.install_button.setEnabled(True)
                    self.install_button.setText("Install")

    def install_item(self):
        if self.sidebar.currentItem():
            key = self.sidebar.currentItem().text()
        else:
            QMessageBox.information(self, "Error", "No plugin/theme was selected.")
            return
        item = self.index_data[key]
        if IS_SS_UP["primary"]:
            url = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}" + item.get("download_url")
        else:
            url = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('mirror')}" + item.get("download_url")
        try:
            r = requests.get(url)
            r.raise_for_status()
            folder = os.path.join(MACROPATH, "temp")
            os.makedirs(folder, exist_ok=True)
            path = os.path.join(folder, os.path.basename(url))
            with open(path, "wb") as f:
                f.write(r.content)
            if self.mode.lower() == "plugin":
                self.gui.install_plugin(path)
            else:
                self.gui.apply_theme_button(path)
            self.installed[item['name']] = item.get('version', '1.0.0')
            self.lock[self.section] = self.installed
            save_lockfile(self.lock)
            self.show_info(key)
            QMessageBox.information(self, f"{self.mode} Installed", f"{item['name']} installed successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def uninstall_item(self):
        if self.sidebar.currentItem():
            key = self.sidebar.currentItem().text()
        else:
            QMessageBox.information(self, "Error", "No plugin/theme was selected.")
            return
        item = self.index_data[key]
        if self.mode.lower() == "plugin":
            folder = os.path.join(MACROPATH, "plugins")
        else:
            folder = os.path.join(MACROPATH, "theme")
        path = os.path.join(folder, os.path.basename(item.get('download_url')))
        try:
            if os.path.exists(path):
                os.remove(path)
            if self.mode.lower() == "plugin":
                self.gui._unload_plugin(key)
            self.installed.pop(item['name'], None)
            self.lock[self.section] = self.installed
            save_lockfile(self.lock)
            self.show_info(key)
            QMessageBox.information(self, f"{self.mode} Removed", f"{item['name']} uninstalled.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))