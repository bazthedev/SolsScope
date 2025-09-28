"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v2.0.0
Support server: https://discord.gg/8khGXqG7nA
"""

import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))

import json
from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QDialog,
    QLineEdit, QFormLayout, QDialogButtonBox, QWidget, QScrollArea,
    QGroupBox, QRubberBand, QCheckBox
)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QPen, QColor
import requests
import screeninfo
import psutil
import win32gui
import win32con
import win32process
import win32api
import ctypes

from constants import MACROPATH

UPTIME_API = "https://cresqnt.com/api/solsscopeup"

try:
    riu = requests.get(UPTIME_API, timeout=10)
    riu.raise_for_status()
    IS_UP = riu.json().get("status", "DOWN") == "OK"
except Exception as e:
    IS_UP = False

DEFAULT_CALIBRATION = {
    "width" : 2560,
    "height" : 1440,
    "scale" : 100,
    "windowed" : False,
    "clicks" : {
        "open_inventory" : [],
        "items_btn" : [],
        "search_bar" : [],
        "first_inv_item" : [],
        "item_amount" : [],
        "use_item" : [],
        "close_menu" : [],
        "open_storage" : [],
        "first_aura_position" : [],
        "equip_aura" : [],
        "collection" : [],
        "exit_collection" : [],
        "questboard_right" : [],
        "questboard_left" : [],
        "questboard_exit" : [],
        "questboard_dismiss" : [],
        "questboard_accept" : [],
        "menu" : [],
        "settings" : [],
        "rolling" : [],
        "cutscene_skip" : [],
        "close_settings_menu" : [],
        "autocraft_craft" : [],
        "autocraft_auto" : [],
        "autocraft_search" : [],
        "autocraft_first_potion" : [],
        "autocraft_first_add" : [],
        "autocraft_first_amt" : [],
        "autocraft_second_add" : [],
        "autocraft_second_amt" : [],
        "autocraft_third_add" : [],
        "autocraft_third_amt" : [],
        "autocraft_first_scrolled_add" : [],
        "autocraft_first_scrolled_amt" : [],
        "autocraft_second_scrolled_add" : [],
        "autocraft_second_scrolled_amt" : [],
        "autocraft_third_scrolled_add" : [],
        "autocraft_third_scrolled_amt" : [],
        "autocraft_scroll" : [],
        "jester_open" : [],
        "jester_exchange" : [],
        "merchant_amount" : [],
        "merchant_purchase" : [],
        "merchant_slot_1" : [],
        "merchant_slot_2" : [],
        "merchant_slot_3" : [],
        "merchant_slot_4" : [],
        "merchant_slot_5" : [],
        "merchant_close" : [],
        "jester_auto_ex_first" : [],
        "jester_auto_ex_second" : [],
        "jester_exchange_confirm" : [],
        "merchant_skip_dialog" : []
    },
    "ocr_regions" : {
        "merchant_name" : [],
        "merchant_boxes" : {
            "Box 1" : [],
            "Box 2" : [],
            "Box 3" : [],
            "Box 4" : [],
            "Box 5" : []
        },
        "jester_auto_ex_first" : [],
        "jester_auto_ex_second" : [],
        "questboard_quest_region" : [],
        "first_item_text_region" : [],
        "autocraft_top_add" : [],
        "autocraft_scrolled_bottom_add" : []
    }
}

gdi32 = ctypes.windll.gdi32
user32 = ctypes.windll.user32

def get_screen_scale():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

    hDC = user32.GetDC(0)
    LOGPIXELSX = 88
    dpi = gdi32.GetDeviceCaps(hDC, LOGPIXELSX)
    user32.ReleaseDC(0, hDC)

    return int(dpi * 100 / 96)

def is_window_fullscreen(hwnd):
    """Check if a given window handle is fullscreen"""
    if not win32gui.IsWindowVisible(hwnd):
        return False

    rect = win32gui.GetWindowRect(hwnd)
    left, top, right, bottom = rect
    width, height = right - left, bottom - top

    monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    monitor_info = win32api.GetMonitorInfo(monitor)
    m_left, m_top, m_right, m_bottom = monitor_info["Monitor"]
    m_width, m_height = m_right - m_left, m_bottom - m_top

    return (width, height) == (m_width, m_height)

def is_process_fullscreen(process_name):
    """Check if a process with the given exe name is running fullscreen"""
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        if proc.info["name"] and proc.info["name"].lower() == process_name.lower():
            hwnds = []

            def callback(hwnd, hwnds):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid == proc.info["pid"]:
                    hwnds.append(hwnd)
                return True

            win32gui.EnumWindows(callback, hwnds)

            for hwnd in hwnds:
                if is_window_fullscreen(hwnd):
                    return True
    return False

def download_all_calibrations():
    def download_folder(url, local_dir, overwrite=True):
        os.makedirs(local_dir, exist_ok=True)
        try:
            response = requests.get(url)
            response.raise_for_status()
            items = response.json()
            
            for item in items:
                if item['type'] == 'file':
                    file_url = item['download_url']
                    file_path = os.path.join(local_dir, item['name'])
                    if (overwrite or not os.path.exists(file_path)) and item["name"] != "template.json":
                        print(f"Downloading {file_path} from {item['download_url']}...")
                        r = requests.get(file_url)
                        r.raise_for_status()
                        with open(file_path, 'wb') as f:
                            f.write(r.content)
                elif item['type'] == 'dir':
                    download_folder(item['url'], os.path.join(local_dir, item['name']))
        except Exception as e:
            print(f"Error downloading calibration: {e}")
    
    if IS_UP:
        download_folder("https://api.github.com/repos/bazthedev/SolsScope/contents/calibrations?ref=main", f"{MACROPATH}\\calibrations")
    else:
        print("SolsScope is DOWN.")


def get_available_calibrations() -> list[str]:

    if not os.path.exists(f"{MACROPATH}/calibrations"):
        os.makedirs(f"{MACROPATH}/calibrations")

    calibs = []

    for calib in os.listdir(f"{MACROPATH}/calibrations"):

        with open(f"{MACROPATH}/calibrations/{calib}", "r") as f:
            _ = json.load(f)
            if calib != "template.json":
                calibs.append(f"{_['width']}x{_['height']} {_['scale']}% ({'Windowed' if _['windowed'] else 'Fullscreen'})")

    return calibs

def get_corresponding_calibration(friendly_calibration):

    for calib in os.listdir(f"{MACROPATH}/calibrations"):

        with open(f"{MACROPATH}/calibrations/{calib}", "r") as f:
            _ = json.load(f)
            if f"{_['width']}x{_['height']} {_['scale']}% ({'Windowed' if _['windowed'] else 'Fullscreen'})" == friendly_calibration:
                return calib

    return

def get_best_calibration(width, height, scale, windowed):

    friendly_calibration = f"{width}x{height} {scale}% ({'Windowed' if windowed else 'Fullscreen'})"
    last_calib = None

    for calib in os.listdir(f"{MACROPATH}/calibrations"):

        with open(f"{MACROPATH}/calibrations/{calib}", "r") as f:
            last_calib = json.load(f)
            print(f"{last_calib['width']}x{last_calib['height']} {last_calib['scale']}% ({'Windowed' if last_calib['windowed'] else 'Fullscreen'})")
            print(friendly_calibration)
            if f"{last_calib['width']}x{last_calib['height']} {last_calib['scale']}% ({'Windowed' if last_calib['windowed'] else 'Fullscreen'})" == friendly_calibration:
                return friendly_calibration

    if last_calib is None:
        raise ValueError("No calibrations available in calibrations directory")
    
    return f"{last_calib['width']}x{last_calib['height']} {last_calib['scale']}% ({'Windowed' if last_calib['windowed'] else 'Fullscreen'})"

def load_full_calibration(friendly_calibration) -> dict:

    calib = get_corresponding_calibration(friendly_calibration)

    with open(f"{MACROPATH}/calibrations/{calib}", "r") as f:
        return json.load(f)

def get_calibrations(friendly_calibration) -> dict:

    calib = get_corresponding_calibration(friendly_calibration)

    with open(f"{MACROPATH}/calibrations/{calib}", "r") as f:
        return json.load(f)["clicks"]
    
def get_regions(friendly_calibration) -> dict:

    calib = get_corresponding_calibration(friendly_calibration)

    with open(f"{MACROPATH}/calibrations/{calib}", "r") as f:
        return json.load(f)["ocr_regions"]
    
def validate_calibrations(friendly_calibration : str, required_calibrations : list) -> bool:

    _calibrations = get_calibrations(friendly_calibration)

    for calib in required_calibrations:
        if len(_calibrations.get(calib, [])) == 0:
            return False
        
    return True

def validate_regions(friendly_calibration : str, required_regions : list) -> bool:

    _regions = get_regions(friendly_calibration)

    for reg in required_regions:
        if reg == "merchant_boxes":
            for _ in _regions.get("merchant_boxes", {}):
                if len(_regions.get("merchant_boxes", {})[_]) == 0:
                    return False
            continue
        if len(_regions.get(reg, []) ) == 0:
            return False
        
    return True

def get_screen_info() -> dict:
    info = {}
    monitors = screeninfo.get_monitors()
    primary_monitor = None
    for mon in monitors:
        if mon.is_primary:
            primary_monitor = mon
            break
    info["width"] = primary_monitor.width
    info["height"] = primary_monitor.height
    info["scale"] = get_screen_scale()
    is_rblx_windowed = is_process_fullscreen("RobloxPlayerBeta.exe")
    if is_rblx_windowed:
        info['windowed'] = not is_rblx_windowed
    else:
        is_rblx_windowed = is_process_fullscreen("Windows10Universal.exe")
        if is_rblx_windowed:
            info['windowed'] = not is_rblx_windowed
        else:
            info['windowed'] = False
        
    return info

def is_completed(value):
    if isinstance(value, list):
        return len(value) > 0
    elif isinstance(value, dict):
        return all(is_completed(v) for v in value.values())
    return bool(value)

class ColoredRubberBand(QRubberBand):
    def __init__(self, *args, color=QColor(0, 0, 255, 100), **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color
        self.setStyleSheet(f"border: 2px solid rgba({color.red()},{color.green()},{color.blue()},{color.alpha()}); background: rgba({color.red()},{color.green()},{color.blue()},{color.alpha()});")


class ClickOverlay(QWidget):
    def __init__(self, mode="point", callback=None, parent_window=None, rect_color=QColor(0, 0, 255, 100)):
        super().__init__()
        self.mode = mode
        self.callback = callback
        self.parent_window = parent_window
        self.start = None
        self.end = None
        self.rubber_band = None
        self.rect_color = rect_color

        screen = QApplication.primaryScreen()
        geom = screen.geometry()
        self.setGeometry(geom)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setWindowOpacity(0.01)

    def showEvent(self, event):
        if self.parent_window:
            self.parent_window.hide()
        super().showEvent(event)

    def closeEvent(self, event):
        if self.parent_window:
            self.parent_window.show()
        super().closeEvent(event)

    def mousePressEvent(self, event):
        pos = event.position().toPoint()
        if self.mode == "point":
            self.start = pos
            if self.callback:
                self.callback([pos.x(), pos.y()])
            self.close()
        elif self.mode == "region":
            self.start = pos
            self.end = pos

    def mouseMoveEvent(self, event):
        if self.mode == "region" and self.start:
            self.end = event.position().toPoint()
            if self.rubber_band is None:
                self.rubber_band = ColoredRubberBand(QRubberBand.Shape.Rectangle, color=self.rect_color)
                self.rubber_band.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
                self.rubber_band.show()
            rect = QRect(self.start, self.end).normalized()
            self.rubber_band.setGeometry(rect)

    def mouseReleaseEvent(self, event):
        if self.mode == "region" and self.start and self.end:
            rect = QRect(self.start, self.end).normalized()
            if self.callback:
                self.callback([rect.x(), rect.y(), rect.x() + rect.width(), rect.y() + rect.height()])
            if self.rubber_band:
                self.rubber_band.hide()
            self.close()

    def paintEvent(self, event):
        if self.mode == "region" and self.start and self.end:
            painter = QPainter(self)
            painter.setBrush(QColor(0, 0, 255, 100))
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            painter.drawRect(QRect(self.start, self.end).normalized())

class ScreenRegionDialog(QDialog):
    """Manual screen region input dialog"""
    def __init__(self, parent=None, default_width=2560, default_height=1440, default_scale=100, default_windowed=False, theme_style=None):
        super().__init__(parent)
        self.setWindowTitle("Screen Region Setup")
        self.setModal(True)
        if theme_style:
            self.setStyleSheet(theme_style)

        self.setObjectName("screenRegionDialog")
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Enter your screen region and scale values:"))
        form_layout = QFormLayout()
        form_layout.setObjectName("screemRegionDialogContent")
        self.width_edit = QLineEdit(str(default_width))
        self.height_edit = QLineEdit(str(default_height))
        self.scale_edit = QLineEdit(str(default_scale))
        self.windowed_edit = QLineEdit(str(default_windowed))
        form_layout.addRow("Width:", self.width_edit)
        form_layout.addRow("Height:", self.height_edit)
        form_layout.addRow("Scale (%):", self.scale_edit)

        self.windowed_checkbox = QCheckBox()
        self.windowed_checkbox.setChecked(default_windowed)
        form_layout.addRow("Windowed:", self.windowed_checkbox)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                           QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.width_edit.textChanged.connect(self.validate_inputs)
        self.height_edit.textChanged.connect(self.validate_inputs)
        self.scale_edit.textChanged.connect(self.validate_inputs)
        self.validate_inputs()

    def validate_inputs(self):
        try:
            w,h,s = int(self.width_edit.text()), int(self.height_edit.text()), int(self.scale_edit.text())
            valid = w>0 and h>0 and s>0
        except ValueError:
            valid = False
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(valid)

    def get_values(self):
        return int(self.width_edit.text()), int(self.height_edit.text()), int(self.scale_edit.text()), self.windowed_checkbox.isChecked()


class CalibrationEditor(QWidget):
    def __init__(self, calibration=None, calibration_name =None, theme_style=None, parent=None):
        super().__init__(parent)
        self.parent = parent
        if calibration_name:
            self.calibration = load_full_calibration(calibration_name)
        elif calibration:
            self.calibration = calibration
        else:
            self.calibration = json.loads(json.dumps(DEFAULT_CALIBRATION))
            
            monitors = screeninfo.get_monitors()
            primary_monitor = None
            for mon in monitors:
                if mon.is_primary:
                    primary_monitor = mon
                    break
            self.calibration['width'] = primary_monitor.width
            self.calibration['height'] = primary_monitor.height
            self.calibration['scale'] = get_screen_scale()
            is_rblx_windowed = is_process_fullscreen("RobloxPlayerBeta.exe")
            if is_rblx_windowed:
                self.calibration['windowed'] = not is_rblx_windowed
            else:
                is_rblx_windowed = is_process_fullscreen("Windows10Universal.exe")
                if is_rblx_windowed:
                    self.calibration['windowed'] = not is_rblx_windowed
                else:
                    self.calibration['windowed'] = False


        self.overlay = None

        if theme_style:
            self.setStyleSheet(theme_style)
        self.setObjectName("CalibrationEditor")
        
        self.setWindowTitle("SolsScope Calibration Tool")

        if not self.confirm_screen():
            dlg = ScreenRegionDialog(default_width=self.calibration["width"],
                                     default_height=self.calibration["height"],
                                     default_scale=self.calibration["scale"], default_windowed=self.calibration['windowed'], theme_style=theme_style)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                w, h, s, win = dlg.get_values()
                self.calibration["width"] = w
                self.calibration["height"] = h
                self.calibration["scale"] = s
                self.calibration["windowed"] = win

        self.main_layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("CalibrationEditorContent")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        self.btn_layout = QHBoxLayout()
        self.import_btn = QPushButton("Import Calibration")
        self.export_btn = QPushButton("Export Calibration")
        self.import_btn.clicked.connect(self.import_calibration)
        self.export_btn.clicked.connect(self.export_calibration)
        self.btn_layout.addWidget(self.import_btn)
        self.btn_layout.addWidget(self.export_btn)
        self.main_layout.addLayout(self.btn_layout)

        self.populate_buttons()

    def calibrate_item_nested(self, category, key, sub_key):
        mode = "point" if category == "clicks" else "region"

        def callback(coords):
            try:
                if category not in self.calibration:
                    self.calibration[category] = {}
                if key not in self.calibration[category]:
                    self.calibration[category][key] = {}
                self.calibration[category][key][sub_key] = coords
                self.populate_buttons()
            except Exception as e:
                QMessageBox.critical(self, "Calibration Error", f"Failed to set calibration:\n{e}")

        self.overlay = ClickOverlay(mode=mode, callback=callback, parent_window=self)
        self.overlay.show()
        
    def populate_buttons(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for category, entries in self.calibration.items():
            if not isinstance(entries, dict):
                continue
            group_box = QGroupBox(category)
            group_layout = QVBoxLayout()

            for key, value in entries.items():
                if isinstance(value, dict):
                    sub_group = QGroupBox(key)
                    sub_layout = QVBoxLayout()
                    for sub_key, sub_val in value.items():
                        h_layout = QHBoxLayout()
                        label = QLabel(sub_key)
                        label.setMinimumWidth(200)
                        btn = QPushButton("Calibrate" if not sub_val else "Recalibrate")
                        btn.clicked.connect(
                            lambda checked, c=category, k=key, sk=sub_key: self.calibrate_item_nested(c, k, sk)
                        )
                        if sub_val:
                            label.setText(f"{sub_key}: {sub_val}")
                        h_layout.addWidget(label)
                        h_layout.addWidget(btn)
                        sub_layout.addLayout(h_layout)
                    sub_group.setLayout(sub_layout)
                    group_layout.addWidget(sub_group)
                else:
                    h_layout = QHBoxLayout()
                    label = QLabel(key)
                    label.setMinimumWidth(200)
                    btn = QPushButton("Calibrate" if not value else "Recalibrate")
                    btn.clicked.connect(lambda checked, c=category, k=key: self.calibrate_item(c, k))
                    if value:
                        label.setText(f"{key}: {value}")
                    h_layout.addWidget(label)
                    h_layout.addWidget(btn)
                    group_layout.addLayout(h_layout)

            group_box.setLayout(group_layout)
            self.scroll_layout.addWidget(group_box)

    def calibrate_item(self, category, key):
        mode = "point" if category == "clicks" else "region"

        def callback(coords):
            self.calibration[category][key] = coords
            self.populate_buttons()

        self.overlay = ClickOverlay(mode=mode, callback=callback, parent_window=self)
        self.overlay.show()


    def confirm_screen(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Confirm Screen")
        dlg.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        dlg.setWindowModality(Qt.WindowModality.ApplicationModal)
        dlg.setText(f"Detected screen: {self.calibration['width']}x{self.calibration['height']} @ {self.calibration['scale']}% ({'Windowed' if self.calibration['windowed'] else 'Fullscreen'})")
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        return dlg.exec() == QMessageBox.StandardButton.Ok


    def edit_value(self, section, key, button):
        mode = "point" if section is self.calibration["clicks"] else "region"
        self.overlay = ClickOverlay(mode=mode, callback=lambda coords: self.set_value(section, key, coords, button), parent_window=self)
        self.overlay.show()

    def set_value(self, section, key, coords, button):
        section[key] = coords
        self.populate_buttons()

    def export_calibration(self):
        if not os.path.exists(f"{MACROPATH}/calibrations"):
            os.makedirs(f"{MACROPATH}/calibrations")
        width = self.calibration.get("width", 2560)
        height = self.calibration.get("height", 1440)
        scale = self.calibration.get("scale", 100)
        windowed = self.calibration.get("windowed", False)
        filename = f"{width}x{height}_{scale}{'W' if windowed else 'F'}.json"
        full_path = os.path.join(MACROPATH, "calibrations", filename)
        try:
            with open(full_path, 'w') as f:
                json.dump(self.calibration, f, indent=4)
            QMessageBox.information(self, "Exported", f"Calibration saved to {full_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export calibration: {e}")

    def import_calibration(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Calibration",
            filter="JSON Files (*.json)"
        )
        if not path:
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if "clicks" not in data or "ocr_regions" not in data or "width" not in data or "height" not in data or "scale" not in data or "windowed" not in data:
                QMessageBox.warning(self, "Invalid File", "Selected file is not a valid calibration.")
                return

            def merge_dict(target, source, template):
                """Merge source into target, only keeping keys in template."""
                for key, val in source.items():
                    if key not in template:
                        continue
                    if isinstance(val, dict) and isinstance(template[key], dict):
                        merge_dict(target.setdefault(key, {}), val, template[key])
                    else:
                        target[key] = val

            def cleanup_dict(d, template):
                """Remove keys not in template."""
                return {
                    k: cleanup_dict(v, template[k]) if isinstance(v, dict) and isinstance(template[k], dict) else v
                    for k, v in d.items()
                    if k in template
                }

            def ensure_template_keys(target, template):
                """Fill in any missing keys from template with defaults."""
                for key, val in template.items():
                    if key not in target:
                        target[key] = json.loads(json.dumps(val))
                    elif isinstance(val, dict):
                        if not isinstance(target[key], dict):
                            target[key] = {}
                        ensure_template_keys(target[key], val)

            has_existing = any(
                bool(v) for cat in ("clicks", "ocr_regions")
                for v in self.calibration.get(cat, {}).values()
            )

            if has_existing:
                reply = QMessageBox.question(
                    self,
                    "Merge Calibration",
                    "You already have an existing calibration.\n"
                    "Do you want to merge the new one (this may overwrite overlapping entries)?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return

                merge_dict(self.calibration, data, DEFAULT_CALIBRATION)

            else:
                def filter_dict(source, template):
                    filtered = {}
                    for key, val in source.items():
                        if key not in template:
                            continue
                        if isinstance(val, dict) and isinstance(template[key], dict):
                            filtered[key] = filter_dict(val, template[key])
                        else:
                            filtered[key] = val
                    return filtered

                self.calibration = filter_dict(data, DEFAULT_CALIBRATION)

            self.calibration = cleanup_dict(self.calibration, DEFAULT_CALIBRATION)
            ensure_template_keys(self.calibration, DEFAULT_CALIBRATION)

            self.populate_buttons()
            QMessageBox.information(self, "Imported", f"Calibration imported from {path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import calibration:\n{e}")



    def closeEvent(self, event):
        if self.parent:
            self.parent.refresh_calibrations_dropdown()
            self.parent.show()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = CalibrationEditor()
    editor.show()
    sys.exit(app.exec())