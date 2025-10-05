"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v2.0.0
Support server: https://discord.gg/8khGXqG7nA
"""

import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))

import subprocess
import json
import requests
import platform
import zipfile
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt6.QtGui import QIcon

from constants import MACROPATH, PYTHON_EXE


PYTHON_DIR = os.path.join(MACROPATH, "py")
PIP_PATH = os.path.join(PYTHON_DIR, "Scripts", "pip.exe")
os.makedirs(PYTHON_DIR, exist_ok=True)

LOCKFILE = os.path.join(MACROPATH, "packages.json")

arch = platform.architecture()[0]

def download_python():
    if os.path.exists(PYTHON_EXE):
        return True
    
    try:
        BASE_URL = "https://www.python.org/ftp/python/3.12.1/"
        arch = "amd64" if platform.architecture()[0] == "64bit" else "win32"
        python_zip_name = f"python-3.12.1-embed-{arch}.zip"
        python_zip_url = BASE_URL + python_zip_name
        zip_path = os.path.join(MACROPATH, "temp", python_zip_name)
        os.makedirs(os.path.join(MACROPATH, "temp"), exist_ok=True)

        download_file(python_zip_url, zip_path)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(PYTHON_DIR)
        os.remove(zip_path)

        pth_file = os.path.join(PYTHON_DIR, "python312._pth")
        with open(pth_file, "r") as f:
            lines = f.readlines()
        if any("#import site" in line for line in lines):
            lines.append("import site\n")
            with open(pth_file, "w") as f:
                f.writelines(lines)
        
        _ = get_pip()
        if _:
            ensure_package("setuptools")
            ensure_package("wheel")
            return True
    except Exception as e:
        print(f"Error downloading Python/pip: {e}")
        return False

def get_pip():
    try:
        get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
        get_pip_path = os.path.join(MACROPATH, "temp", "get-pip.py")
        download_file(get_pip_url, get_pip_path)
        subprocess.check_call([
                PYTHON_EXE,
                get_pip_path
            ],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        os.remove(get_pip_path)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False


def pip_install_target(package):
    try:
        subprocess.check_call([
                PYTHON_EXE, "-m", "pip",
                "install", "--upgrade", "--no-cache-dir",
                "--no-warn-script-location", package
            ],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        INSTALLED[package.lower()] = "installed"
        save_lockfile()
        return True
    except subprocess.CalledProcessError:
        return False

def save_lockfile():
    os.makedirs(os.path.dirname(LOCKFILE), exist_ok=True)
    with open(LOCKFILE, "w", encoding="utf-8") as f:
        json.dump(INSTALLED, f, indent=2)
    

def download_file(url, dest_path):
    response = requests.get(url)
    response.raise_for_status()

    with open(dest_path, "wb") as f:
        f.write(response.content)


def ensure_package(package, force=False):
    """
    Install a package + dependencies into packages.
    Uses installed.json to skip already installed packages.
    """

    if not force and package.lower() in INSTALLED:
        print(f"{package} already installed, skipping.")
        return

    print(f"Installing {package} ...")
    success = pip_install_target(package)
    if success:
        print(f"{package} installed successfully.")
    else:
        print(f"{package} could not be installed. Check for compatible wheels or source build requirements.")
    

if os.path.exists(LOCKFILE):
    with open(LOCKFILE, "r", encoding="utf-8") as f:
        INSTALLED = json.load(f)
else:
    INSTALLED = {}
    save_lockfile()

class PackageInstallerGUI(QDialog):
    def __init__(self, requirements, parent=None):
        super().__init__(parent)
        self.requirements = requirements
        self.setWindowTitle("SolsScope - Installing Packages")
        self.setMinimumWidth(400)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint
        )
        self.setObjectName("PackageInstallerGUI")
        if os.path.exists(os.path.join(MACROPATH, "icon.ico")):
            self.setWindowIcon(QIcon(os.path.join(MACROPATH, "icon.ico")))
        layout = QVBoxLayout()
        self.label = QLabel("Installing packages...")
        self.progress = QProgressBar()
        self.progress.setMaximum(len(requirements))
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        self.setLayout(layout)

        self.worker = PackageInstallerWorker(requirements)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.install_done)

    def start_install(self):
        self.worker.start()

    def update_progress(self, i, pkg):
        self.label.setText(f"Installing {pkg} ({i}/{len(self.requirements)})...")
        self.progress.setValue(i)

    def install_done(self):
        self.label.setText("Installation complete!")
        QTimer.singleShot(1000, self.accept)


class PackageInstallerWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal()

    def __init__(self, requirements):
        super().__init__()
        self.requirements = requirements

    def run(self):
        for i, pkg in enumerate(self.requirements, start=1):
            self.progress.emit(i, pkg)
            ensure_package(pkg)
        self.finished.emit()