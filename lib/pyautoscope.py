"""
SolsScope/Baz's Macro
Created by Meklows
v2.0.0
Support server: https://discord.gg/8khGXqG7nA
"""
from numpy import double
import numpy as np
import pygetwindow as gw
import win32gui
import mousekey
import time
import json
from easyocr import Reader
from pynput.keyboard import Key, Controller
import pyocrscope
import psutil
import win32process

from constants import MACROPATH


def load_ratios():
    try:
        with open(f"{MACROPATH}/ratios.json", "r") as f:
            return json.load(f)
    except Exception as e:
        return {}


# =======================
# ClientData class
# =======================
class ClientData:
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.screen_width = (win32gui.GetClientRect(self.hwnd))[2] - (win32gui.GetClientRect(self.hwnd))[0]
        self.screen_height = (win32gui.GetClientRect(self.hwnd))[3] - (win32gui.GetClientRect(self.hwnd))[1]
        self.top_left_pos = win32gui.ClientToScreen(self.hwnd, (0, 0))
        self.rect = win32gui.GetClientRect(self.hwnd)
        self.button_positions = {}
        _, self.pid = win32process.GetWindowThreadProcessId(self.hwnd)
        self._process = None
        self.file_handles = []
        
        try:
            self._process = psutil.Process(self.pid)
            self.file_handles = self._process.open_files()
        except psutil.AccessDenied:
            print(f"Access denied for PID {self.pid}")
        except psutil.NoSuchProcess:
            print(f"Process {self.pid} no longer exists")

    def focus(self):
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.SetFocus(self.hwnd)

    def change_button_positions(self, dictionary):
        self.button_positions.clear()
        self.button_positions = dictionary

    def update_pos(self) -> bool:
        changed = False
        new_width = (win32gui.GetClientRect(self.hwnd))[2] - (win32gui.GetClientRect(self.hwnd))[0]
        new_height = (win32gui.GetClientRect(self.hwnd))[3] - (win32gui.GetClientRect(self.hwnd))[1]
        new_top_left = win32gui.ClientToScreen(self.hwnd, (0, 0))
        new_rect = win32gui.GetClientRect(self.hwnd)

        if self.screen_width != new_width:
            self.screen_width = new_width
            changed = True
        if self.screen_height != new_height:
            self.screen_height = new_height
            changed = True
        if self.top_left_pos != new_top_left:
            self.top_left_pos = new_top_left
            changed = True
        if self.rect != new_rect:
            self.rect = new_rect
            changed = True

        if changed:
            # re-run calibration so button_positions is fresh
            calibrate_buttons(self.hwnd)
            return changed
        else:
            return False


# =======================
# Dictionary to hold clients
# =======================
roblox_clients = {}


# =======================
# Return list of client keys
# =======================
def return_clients():
    return list(roblox_clients.keys())


# ===============================================================
# Button Call Reference (for move_to_button)
# ===============================================================
"""
Usage:
    move_to_button("<button_name>", return_clients()[0])

Notes:
- Names are case-insensitive.
- Dot notation is supported for nested groups (e.g., "merchant.purchase").
- If a button key is empty ( [] ), click will fail with [ERR].

Inventory / Aura / Menu (top-level):
    "open_inventory"
    "items_btn"
    "search_bar"
    "first_inv_item"
    "item_amount"
    "use_item"
    "close_menu"
    "open_storage"
    "first_aura_position"
    "equip_aura"
    "settings"
    "close_settings_menu"

Jester flat aliases:
    "jester_open"
    "jester_exchange"          # Exchange button on exchange menu
    "jester_auto_ex_first"
    "jester_auto_ex_second"
    "jester_exchange_confirm"

Merchant (Mari) flat aliases:
    "merchant_open"
    "merchant_skip_dialog"
    "merchant_slot_1"
    "merchant_slot_2"
    "merchant_slot_3"
    "merchant_slot_4"
    "merchant_slot_5"
    "merchant_purchase"
    "merchant_amount"
    "merchant_close"

Namespaced versions also work:
    "jester.open", "jester.exchange", "jester.auto_ex_first", "jester.auto_ex_second", "jester.exchange_confirm"
    "merchant.open", "merchant.skip_dialog", "merchant.slot_1"... "merchant.purchase", "merchant.amount", "merchant.close"

Example:
    client = return_clients()[0]
    move_to_button("use_item", client)
    move_to_button("jester_exchange", client)
    move_to_button("merchant.purchase", client)
"""
# ===============================================================


# =======================
# Calibrate buttons with full clickpos
# =======================
def calibrate_buttons(client_key: str):
    roblox_client = roblox_clients[client_key]

    ratios = load_ratios()

    # =====================
    # AURA STORAGE: EQUIP, FIRST_AURA, SEARCH, EXIT
    # =====================
    if roblox_client.screen_width * ratios["AURA_STORAGE"]["SCALE_WIDTH"] / ratios["AURA_STORAGE"]["ASPECT_RATIO"] <= \
       roblox_client.screen_height * ratios["AURA_STORAGE"]["SCALE_HEIGHT"]:
        aura_equip_final_width  = roblox_client.screen_width * ratios["AURA_STORAGE"]["SCALE_WIDTH"]
        aura_equip_final_height = roblox_client.screen_width * ratios["AURA_STORAGE"]["SCALE_WIDTH"] / ratios["AURA_STORAGE"]["ASPECT_RATIO"]
    else:
        aura_equip_final_height = roblox_client.screen_height * ratios["AURA_STORAGE"]["SCALE_HEIGHT"]
        aura_equip_final_width  = roblox_client.screen_height * ratios["AURA_STORAGE"]["SCALE_HEIGHT"] * ratios["AURA_STORAGE"]["ASPECT_RATIO"]

    aura_equip_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - aura_equip_final_width) / 2) + \
                   (aura_equip_final_width * ratios["AURA_STORAGE"]["EQUIP_BUTTON"]["LEFT_OFFSET_RATIO"]) + \
                   ((aura_equip_final_width * ratios["AURA_STORAGE"]["EQUIP_BUTTON"]["WIDTH_RATIO"]) / 2)
    aura_equip_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - aura_equip_final_height) / 2) + \
                   (aura_equip_final_height * (ratios["AURA_STORAGE"]["EQUIP_BUTTON"]["TOP_OFFSET_RATIO"] + ratios["AURA_STORAGE"]["EQUIP_BUTTON"]["HEIGHT_RATIO"] / 2))

    if roblox_client.screen_width * ratios["AURA_STORAGE"]["SCALE_WIDTH"] / ratios["AURA_STORAGE"]["ASPECT_RATIO"] <= \
       roblox_client.screen_height * ratios["AURA_STORAGE"]["SCALE_HEIGHT"]:
        aura_pos_final_width  = roblox_client.screen_width * ratios["AURA_STORAGE"]["SCALE_WIDTH"]
        aura_pos_final_height = roblox_client.screen_width * ratios["AURA_STORAGE"]["SCALE_WIDTH"] / ratios["AURA_STORAGE"]["ASPECT_RATIO"]
    else:
        aura_pos_final_height = roblox_client.screen_height * ratios["AURA_STORAGE"]["SCALE_HEIGHT"]
        aura_pos_final_width  = roblox_client.screen_height * ratios["AURA_STORAGE"]["SCALE_HEIGHT"] * ratios["AURA_STORAGE"]["ASPECT_RATIO"]

    aura_pos_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - aura_pos_final_width) / 2) + \
                 (aura_pos_final_width * ratios["AURA_STORAGE"]["FIRST_AURA"]["LEFT_OFFSET_RATIO"]) + \
                 ((aura_pos_final_width * ratios["AURA_STORAGE"]["FIRST_AURA"]["WIDTH_RATIO"]) / 2)
    aura_pos_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - aura_pos_final_height) / 2) + \
                 (aura_pos_final_height * (ratios["AURA_STORAGE"]["FIRST_AURA"]["TOP_OFFSET_RATIO"] + ratios["AURA_STORAGE"]["FIRST_AURA"]["HEIGHT_RATIO"] / 2))

    # ---- SEARCH BAR (fixed name: search_bar_*) ----
    if roblox_client.screen_width * ratios["AURA_STORAGE"]["SCALE_WIDTH"] / ratios["AURA_STORAGE"]["ASPECT_RATIO"] <= \
       roblox_client.screen_height * ratios["AURA_STORAGE"]["SCALE_HEIGHT"]:
        search_bar_final_width  = roblox_client.screen_width * ratios["AURA_STORAGE"]["SCALE_WIDTH"]
        search_bar_final_height = roblox_client.screen_width * ratios["AURA_STORAGE"]["SCALE_WIDTH"] / ratios["AURA_STORAGE"]["ASPECT_RATIO"]
    else:
        search_bar_final_height = roblox_client.screen_height * ratios["AURA_STORAGE"]["SCALE_HEIGHT"]
        search_bar_final_width  = roblox_client.screen_height * ratios["AURA_STORAGE"]["SCALE_HEIGHT"] * ratios["AURA_STORAGE"]["ASPECT_RATIO"]

    search_bar_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - search_bar_final_width) / 2) + \
                   (search_bar_final_width * ratios["AURA_STORAGE"]["SEARCH_BAR"]["LEFT_OFFSET_RATIO"]) + \
                   ((search_bar_final_width * ratios["AURA_STORAGE"]["SEARCH_BAR"]["WIDTH_RATIO"]) / 2)
    search_bar_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - search_bar_final_height) / 2) + \
                   (search_bar_final_height * (ratios["AURA_STORAGE"]["SEARCH_BAR"]["TOP_OFFSET_RATIO"] + ratios["AURA_STORAGE"]["SEARCH_BAR"]["HEIGHT_RATIO"] / 2))

    if roblox_client.screen_width * ratios["AURA_STORAGE"]["SCALE_WIDTH"] / ratios["AURA_STORAGE"]["ASPECT_RATIO"] <= \
       roblox_client.screen_height * ratios["AURA_STORAGE"]["SCALE_HEIGHT"]:
        exit_storage_final_width  = roblox_client.screen_width * ratios["AURA_STORAGE"]["SCALE_WIDTH"]
        exit_storage_final_height = roblox_client.screen_width * ratios["AURA_STORAGE"]["SCALE_WIDTH"] / ratios["AURA_STORAGE"]["ASPECT_RATIO"]
    else:
        exit_storage_final_height = roblox_client.screen_height * ratios["AURA_STORAGE"]["SCALE_HEIGHT"]
        exit_storage_final_width  = roblox_client.screen_height * ratios["AURA_STORAGE"]["SCALE_HEIGHT"] * ratios["AURA_STORAGE"]["ASPECT_RATIO"]

    exit_storage_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - exit_storage_final_width) / 2) + \
                     (exit_storage_final_width * ratios["AURA_STORAGE"]["EXIT_BUTTON"]["LEFT_OFFSET_RATIO"]) + \
                     ((exit_storage_final_width * ratios["AURA_STORAGE"]["EXIT_BUTTON"]["WIDTH_RATIO"]) / 2)
    exit_storage_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - exit_storage_final_height) / 2) + \
                     (exit_storage_final_height * (ratios["AURA_STORAGE"]["EXIT_BUTTON"]["TOP_OFFSET_RATIO"] + ratios["AURA_STORAGE"]["EXIT_BUTTON"]["HEIGHT_RATIO"] / 2))

    # =====================
    # INVENTORY: USE_ITEM / ITEM_AMOUNT / ITEMS_BUTTON / FIRST_INV_ITEM
    # =====================
    if roblox_client.screen_width * ratios["INVENTORY"]["SCALE_WIDTH"] / ratios["INVENTORY"]["ASPECT_RATIO"] <= \
       roblox_client.screen_height * ratios["INVENTORY"]["SCALE_HEIGHT"]:
        inv_final_w = roblox_client.screen_width * ratios["INVENTORY"]["SCALE_WIDTH"]
        inv_final_h = roblox_client.screen_width * ratios["INVENTORY"]["SCALE_WIDTH"] / ratios["INVENTORY"]["ASPECT_RATIO"]
    else:
        inv_final_h = roblox_client.screen_height * ratios["INVENTORY"]["SCALE_HEIGHT"]
        inv_final_w = roblox_client.screen_height * ratios["INVENTORY"]["SCALE_HEIGHT"] * ratios["INVENTORY"]["ASPECT_RATIO"]

    use_item_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - inv_final_w) / 2) + \
                 (inv_final_w * ratios["INVENTORY"]["USE_ITEM"]["LEFT_OFFSET_RATIO"]) + \
                 ((inv_final_w * ratios["INVENTORY"]["USE_ITEM"]["WIDTH_RATIO"]) / 2)
    use_item_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - inv_final_h) / 2) + \
                 (inv_final_h * (ratios["INVENTORY"]["USE_ITEM"]["TOP_OFFSET_RATIO"] + ratios["INVENTORY"]["USE_ITEM"]["HEIGHT_RATIO"] / 2))

    item_amount_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - inv_final_w) / 2) + \
                    (inv_final_w * ratios["INVENTORY"]["ITEM_AMOUNT"]["LEFT_OFFSET_RATIO"]) + \
                    ((inv_final_w * ratios["INVENTORY"]["ITEM_AMOUNT"]["WIDTH_RATIO"]) / 2)
    item_amount_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - inv_final_h) / 2) + \
                    (inv_final_h * (ratios["INVENTORY"]["ITEM_AMOUNT"]["TOP_OFFSET_RATIO"] + ratios["INVENTORY"]["ITEM_AMOUNT"]["HEIGHT_RATIO"] / 2))

    items_button_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - inv_final_w) / 2) + \
                     (inv_final_w * ratios["INVENTORY"]["ITEMS_BUTTON"]["LEFT_OFFSET_RATIO"]) + \
                     ((inv_final_w * ratios["INVENTORY"]["ITEMS_BUTTON"]["WIDTH_RATIO"]) / 2)
    items_button_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - inv_final_h) / 2) + \
                     (inv_final_h * (ratios["INVENTORY"]["ITEMS_BUTTON"]["TOP_OFFSET_RATIO"] + ratios["INVENTORY"]["ITEMS_BUTTON"]["HEIGHT_RATIO"] / 2))

    first_inv_item_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - inv_final_w) / 2) + \
                       (inv_final_w * ratios["INVENTORY"]["FIRST_INV_ITEM"]["LEFT_OFFSET_RATIO"]) + \
                       ((inv_final_w * ratios["INVENTORY"]["FIRST_INV_ITEM"]["WIDTH_RATIO"]) / 2)
    first_inv_item_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - inv_final_h) / 2) + \
                       (inv_final_h * (ratios["INVENTORY"]["FIRST_INV_ITEM"]["TOP_OFFSET_RATIO"] + ratios["INVENTORY"]["FIRST_INV_ITEM"]["HEIGHT_RATIO"] / 2))

    # =====================
    # MENU: OPEN_INVENTORY (centered, fixed AR)
    # =====================
    if roblox_client.screen_width * ratios["MENU"]["SCALE_WIDTH"] / ratios["MENU"]["ASPECT_RATIO"] <= \
       roblox_client.screen_height * ratios["MENU"]["SCALE_HEIGHT"]:
        menu_final_width  = roblox_client.screen_width * ratios["MENU"]["SCALE_WIDTH"]
        menu_final_height = roblox_client.screen_width * ratios["MENU"]["SCALE_WIDTH"] / ratios["MENU"]["ASPECT_RATIO"]
    else:
        menu_final_height = roblox_client.screen_height * ratios["MENU"]["SCALE_HEIGHT"]
        menu_final_width  = roblox_client.screen_height * ratios["MENU"]["SCALE_HEIGHT"] * ratios["MENU"]["ASPECT_RATIO"]

    open_settings_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - menu_final_width) / 2) + \
                      (menu_final_width * ratios["MENU"]["OPEN_INVENTORY"]["LEFT_OFFSET_RATIO"]) + \
                      ((menu_final_width * ratios["MENU"]["OPEN_INVENTORY"]["WIDTH_RATIO"]) / 2)
    open_settings_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - menu_final_height) / 2) + \
                      (menu_final_height * (ratios["MENU"]["OPEN_INVENTORY"]["TOP_OFFSET_RATIO"] + (ratios["MENU"]["OPEN_INVENTORY"]["HEIGHT_RATIO"] / 2)))

    # =====================
    # JESTER EXCHANGE
    # =====================
    if roblox_client.screen_width * ratios["JESTER_EXCHANGE"]["SCALE_WIDTH"] / ratios["JESTER_EXCHANGE"]["ASPECT_RATIO"] <= \
       roblox_client.screen_height * ratios["JESTER_EXCHANGE"]["SCALE_HEIGHT"]:
        jex_final_w = roblox_client.screen_width * ratios["JESTER_EXCHANGE"]["SCALE_WIDTH"]
        jex_final_h = roblox_client.screen_width * ratios["JESTER_EXCHANGE"]["SCALE_WIDTH"] / ratios["JESTER_EXCHANGE"]["ASPECT_RATIO"]
    else:
        jex_final_h = roblox_client.screen_height * ratios["JESTER_EXCHANGE"]["SCALE_HEIGHT"]
        jex_final_w = roblox_client.screen_height * ratios["JESTER_EXCHANGE"]["SCALE_HEIGHT"] * ratios["JESTER_EXCHANGE"]["ASPECT_RATIO"]

    jex_first_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - jex_final_w) / 2) + \
                  (jex_final_w * ratios["JESTER_EXCHANGE"]["SELL_ITEM_1"]["LEFT_OFFSET_RATIO"]) + \
                  ((jex_final_w * ratios["JESTER_EXCHANGE"]["SELL_ITEM_1"]["WIDTH_RATIO"]) / 2)
    jex_first_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - jex_final_h) / 2) + \
                  (jex_final_h * (ratios["JESTER_EXCHANGE"]["SELL_ITEM_1"]["TOP_OFFSET_RATIO"] + ratios["JESTER_EXCHANGE"]["SELL_ITEM_1"]["HEIGHT_RATIO"] / 2))

    jex_second_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - jex_final_w) / 2) + \
                   (jex_final_w * ratios["JESTER_EXCHANGE"]["SELL_ITEM_2"]["LEFT_OFFSET_RATIO"]) + \
                   ((jex_final_w * ratios["JESTER_EXCHANGE"]["SELL_ITEM_2"]["WIDTH_RATIO"]) / 2)
    jex_second_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - jex_final_h) / 2) + \
                   (jex_final_h * (ratios["JESTER_EXCHANGE"]["SELL_ITEM_2"]["TOP_OFFSET_RATIO"] + ratios["JESTER_EXCHANGE"]["SELL_ITEM_2"]["HEIGHT_RATIO"] / 2))

    jex_button_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - jex_final_w) / 2) + \
                   (jex_final_w * ratios["JESTER_EXCHANGE"]["EXCHANGE_BUTTON"]["LEFT_OFFSET_RATIO"]) + \
                   ((jex_final_w * ratios["JESTER_EXCHANGE"]["EXCHANGE_BUTTON"]["WIDTH_RATIO"]) / 2)
    jex_button_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - jex_final_h) / 2) + \
                   (jex_final_h * (ratios["JESTER_EXCHANGE"]["EXCHANGE_BUTTON"]["TOP_OFFSET_RATIO"] + ratios["JESTER_EXCHANGE"]["EXCHANGE_BUTTON"]["HEIGHT_RATIO"] / 2))

    # =====================
    # JESTER CONFIRM
    # =====================
    if roblox_client.screen_width * ratios["JESTER_CONFIRM"]["SCALE_WIDTH"] / ratios["JESTER_CONFIRM"]["ASPECT_RATIO"] <= \
       roblox_client.screen_height * ratios["JESTER_CONFIRM"]["SCALE_HEIGHT"]:
        jcf_final_w = roblox_client.screen_width * ratios["JESTER_CONFIRM"]["SCALE_WIDTH"]
        jcf_final_h = roblox_client.screen_width * ratios["JESTER_CONFIRM"]["SCALE_WIDTH"] / ratios["JESTER_CONFIRM"]["ASPECT_RATIO"]
    else:
        jcf_final_h = roblox_client.screen_height * ratios["JESTER_CONFIRM"]["SCALE_HEIGHT"]
        jcf_final_w = roblox_client.screen_height * ratios["JESTER_CONFIRM"]["SCALE_HEIGHT"] * ratios["JESTER_CONFIRM"]["ASPECT_RATIO"]

    jcf_confirm_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - jcf_final_w) / 2) + \
                    (jcf_final_w * ratios["JESTER_CONFIRM"]["EXCHANGE_CONFIRM"]["LEFT_OFFSET_RATIO"]) + \
                    ((jcf_final_w * ratios["JESTER_CONFIRM"]["EXCHANGE_CONFIRM"]["WIDTH_RATIO"]) / 2)
    jcf_confirm_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - jcf_final_h) / 2) + \
                    (jcf_final_h * (ratios["JESTER_CONFIRM"]["EXCHANGE_CONFIRM"]["TOP_OFFSET_RATIO"] + ratios["JESTER_CONFIRM"]["EXCHANGE_CONFIRM"]["HEIGHT_RATIO"] / 2))

    # =====================
    # JESTER DIALOG — container + row buttons (OPEN/EXCHANGE/WHO/LEAVE)
    # =====================
    jester_scale_w = ratios["JESTER_DIALOG"]["SCALE_WIDTH"]
    jester_scale_h = ratios["JESTER_DIALOG"]["SCALE_HEIGHT"]
    jester_aspect  = ratios["JESTER_DIALOG"]["ASPECT_RATIO"]

    jester_raw_w        = roblox_client.screen_width * jester_scale_w
    jester_raw_h_from_w = jester_raw_w / jester_aspect
    jester_raw_h        = roblox_client.screen_height * jester_scale_h
    jester_raw_w_from_h = jester_raw_h * jester_aspect

    if jester_raw_h_from_w <= jester_raw_h:
        jester_final_w = jester_raw_w
        jester_final_h = jester_raw_h_from_w
    else:
        jester_final_w = jester_raw_w_from_h
        jester_final_h = jester_raw_h

    jdlg_left = (roblox_client.screen_width - jester_final_w) / 2.0
    jdlg_top  = roblox_client.screen_height * ratios["JESTER_DIALOG"]["SCREEN_TOP_RATIO"]

    def _btn_xy_from(block):
        return (
            roblox_client.top_left_pos[0] + jdlg_left + jester_final_w * (block["LEFT_OFFSET_RATIO"] + block["WIDTH_RATIO"]/2.0),
            roblox_client.top_left_pos[1] + jdlg_top  + jester_final_h * (block["TOP_OFFSET_RATIO"]  + block["HEIGHT_RATIO"]/2.0),
        )

    jester_open_x,     jester_open_y     = _btn_xy_from(ratios["JESTER_DIALOG"]["OPEN"])
    jester_exchange_x, jester_exchange_y = _btn_xy_from(ratios["JESTER_DIALOG"]["EXCHANGE"])
    jester_who_x,      jester_who_y      = _btn_xy_from(ratios["JESTER_DIALOG"]["WHO"])
    jester_leave_x,    jester_leave_y    = _btn_xy_from(ratios["JESTER_DIALOG"]["LEAVE"])

    # =====================
    # MERCHANT (Mari) DIALOG — container + row buttons (OPEN/WHO/LEAVE)
    # =====================
    merch_scale_w = ratios["MERCHANT_DIALOG"]["SCALE_WIDTH"]
    merch_scale_h = ratios["MERCHANT_DIALOG"]["SCALE_HEIGHT"]
    merch_aspect  = ratios["MERCHANT_DIALOG"]["ASPECT_RATIO"]
    merch_top_ratio = ratios["MERCHANT_DIALOG"].get("SCREEN_TOP_RATIO",
                        ratios.get("MARI_DIALOG", {}).get("SCREEN_TOP_RATIO", 0.624))

    merch_raw_w        = roblox_client.screen_width * merch_scale_w
    merch_raw_h_from_w = merch_raw_w / merch_aspect
    merch_raw_h        = roblox_client.screen_height * merch_scale_h
    merch_raw_w_from_h = merch_raw_h * merch_aspect

    if merch_raw_h_from_w <= merch_raw_h:
        merch_final_w = merch_raw_w
        merch_final_h = merch_raw_h_from_w
    else:
        merch_final_w = merch_raw_w_from_h
        merch_final_h = merch_raw_h

    mdlg_left = (roblox_client.screen_width - merch_final_w) / 2.0
    mdlg_top  = roblox_client.screen_height * merch_top_ratio

    def _m_btn_xy_from(block):
        return (
            roblox_client.top_left_pos[0] + mdlg_left + merch_final_w * (block["LEFT_OFFSET_RATIO"] + block["WIDTH_RATIO"]/2.0),
            roblox_client.top_left_pos[1] + mdlg_top  + merch_final_h * (block["TOP_OFFSET_RATIO"]  + block["HEIGHT_RATIO"]/2.0),
        )

    merchant_open_x,  merchant_open_y  = _m_btn_xy_from(ratios["MERCHANT_DIALOG"]["OPEN"])
    merchant_who_x,   merchant_who_y   = _m_btn_xy_from(ratios["MERCHANT_DIALOG"]["WHO"])
    merchant_leave_x, merchant_leave_y = _m_btn_xy_from(ratios["MERCHANT_DIALOG"]["LEAVE"])

    # =====================
    # MARI PURCHASE (shop grid + purchase UI)
    # =====================
    if roblox_client.screen_width * ratios["MARI_PURCHASE"]["SCALE_WIDTH"] / ratios["MARI_PURCHASE"]["ASPECT_RATIO"] <= \
       roblox_client.screen_height * ratios["MARI_PURCHASE"]["SCALE_HEIGHT"]:
        mp_final_w = roblox_client.screen_width * ratios["MARI_PURCHASE"]["SCALE_WIDTH"]
        mp_final_h = roblox_client.screen_width * ratios["MARI_PURCHASE"]["SCALE_WIDTH"] / ratios["MARI_PURCHASE"]["ASPECT_RATIO"]
    else:
        mp_final_h = roblox_client.screen_height * ratios["MARI_PURCHASE"]["SCALE_HEIGHT"]
        mp_final_w = roblox_client.screen_height * ratios["MARI_PURCHASE"]["SCALE_HEIGHT"] * ratios["MARI_PURCHASE"]["ASPECT_RATIO"]

    ms1_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - mp_final_w) / 2) + \
            (mp_final_w * ratios["MARI_PURCHASE"]["ITEM_1"]["LEFT_OFFSET_RATIO"]) + \
            ((mp_final_w * ratios["MARI_PURCHASE"]["ITEM_1"]["WIDTH_RATIO"]) / 2)
    ms1_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - mp_final_h) / 2) + \
            (mp_final_h * (ratios["MARI_PURCHASE"]["ITEM_1"]["TOP_OFFSET_RATIO"] + ratios["MARI_PURCHASE"]["ITEM_1"]["HEIGHT_RATIO"] / 2))

    ms2_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - mp_final_w) / 2) + \
            (mp_final_w * ratios["MARI_PURCHASE"]["ITEM_2"]["LEFT_OFFSET_RATIO"]) + \
            ((mp_final_w * ratios["MARI_PURCHASE"]["ITEM_2"]["WIDTH_RATIO"]) / 2)
    ms2_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - mp_final_h) / 2) + \
            (mp_final_h * (ratios["MARI_PURCHASE"]["ITEM_2"]["TOP_OFFSET_RATIO"] + ratios["MARI_PURCHASE"]["ITEM_2"]["HEIGHT_RATIO"] / 2))

    ms3_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - mp_final_w) / 2) + \
            (mp_final_w * ratios["MARI_PURCHASE"]["ITEM_3"]["LEFT_OFFSET_RATIO"]) + \
            ((mp_final_w * ratios["MARI_PURCHASE"]["ITEM_3"]["WIDTH_RATIO"]) / 2)
    ms3_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - mp_final_h) / 2) + \
            (mp_final_h * (ratios["MARI_PURCHASE"]["ITEM_3"]["TOP_OFFSET_RATIO"] + ratios["MARI_PURCHASE"]["ITEM_3"]["HEIGHT_RATIO"] / 2))

    ms4_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - mp_final_w) / 2) + \
            (mp_final_w * ratios["MARI_PURCHASE"]["ITEM_4"]["LEFT_OFFSET_RATIO"]) + \
            ((mp_final_w * ratios["MARI_PURCHASE"]["ITEM_4"]["WIDTH_RATIO"]) / 2)
    ms4_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - mp_final_h) / 2) + \
            (mp_final_h * (ratios["MARI_PURCHASE"]["ITEM_4"]["TOP_OFFSET_RATIO"] + ratios["MARI_PURCHASE"]["ITEM_4"]["HEIGHT_RATIO"] / 2))

    ms5_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - mp_final_w) / 2) + \
            (mp_final_w * ratios["MARI_PURCHASE"]["ITEM_5"]["LEFT_OFFSET_RATIO"]) + \
            ((mp_final_w * ratios["MARI_PURCHASE"]["ITEM_5"]["WIDTH_RATIO"]) / 2)
    ms5_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - mp_final_h) / 2) + \
            (mp_final_h * (ratios["MARI_PURCHASE"]["ITEM_5"]["TOP_OFFSET_RATIO"] + ratios["MARI_PURCHASE"]["ITEM_5"]["HEIGHT_RATIO"] / 2))

    mp_buy_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - mp_final_w) / 2) + \
               (mp_final_w * ratios["MARI_PURCHASE"]["PURCHASE_BUTTON"]["LEFT_OFFSET_RATIO"]) + \
               ((mp_final_w * ratios["MARI_PURCHASE"]["PURCHASE_BUTTON"]["WIDTH_RATIO"]) / 2)
    mp_buy_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - mp_final_h) / 2) + \
               (mp_final_h * (ratios["MARI_PURCHASE"]["PURCHASE_BUTTON"]["TOP_OFFSET_RATIO"] + ratios["MARI_PURCHASE"]["PURCHASE_BUTTON"]["HEIGHT_RATIO"] / 2))

    mp_amt_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - mp_final_w) / 2) + \
               (mp_final_w * ratios["MARI_PURCHASE"]["AMOUNT_INPUT"]["LEFT_OFFSET_RATIO"]) + \
               ((mp_final_w * ratios["MARI_PURCHASE"]["AMOUNT_INPUT"]["WIDTH_RATIO"]) / 2)
    mp_amt_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - mp_final_h) / 2) + \
               (mp_final_h * (ratios["MARI_PURCHASE"]["AMOUNT_INPUT"]["TOP_OFFSET_RATIO"] + ratios["MARI_PURCHASE"]["AMOUNT_INPUT"]["HEIGHT_RATIO"] / 2))

    mp_close_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - mp_final_w) / 2) + \
                 (mp_final_w * ratios["MARI_PURCHASE"]["EXIT_BUTTON"]["LEFT_OFFSET_RATIO"]) + \
                 ((mp_final_w * ratios["MARI_PURCHASE"]["EXIT_BUTTON"]["WIDTH_RATIO"]) / 2)
    mp_close_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - mp_final_h) / 2) + \
                 (mp_final_h * (ratios["MARI_PURCHASE"]["EXIT_BUTTON"]["TOP_OFFSET_RATIO"] + ratios["MARI_PURCHASE"]["EXIT_BUTTON"]["HEIGHT_RATIO"] / 2))

    # =====================
    # MENU: extra buttons
    # =====================
    rolling_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - menu_final_width) / 2) + \
                (menu_final_width * ratios["MENU"]["ROLLING"]["LEFT_OFFSET_RATIO"]) + \
                ((menu_final_width * ratios["MENU"]["ROLLING"]["WIDTH_RATIO"]) / 2)
    rolling_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - menu_final_height) / 2) + \
                (menu_final_height * (ratios["MENU"]["ROLLING"]["TOP_OFFSET_RATIO"] + (ratios["MENU"]["ROLLING"]["HEIGHT_RATIO"] / 2)))

    cutscene_skip_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - menu_final_width) / 2) + \
                      (menu_final_width * ratios["MENU"]["CUTSCENE_SKIP"]["LEFT_OFFSET_RATIO"]) + \
                      ((menu_final_width * ratios["MENU"]["CUTSCENE_SKIP"]["WIDTH_RATIO"]) / 2)
    cutscene_skip_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - menu_final_height) / 2) + \
                      (menu_final_height * (ratios["MENU"]["CUTSCENE_SKIP"]["TOP_OFFSET_RATIO"] + (ratios["MENU"]["CUTSCENE_SKIP"]["HEIGHT_RATIO"] / 2)))

    close_settings_menu_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - menu_final_width) / 2) + \
                            (menu_final_width * ratios["MENU"]["CLOSE_SETTINGS_MENU"]["LEFT_OFFSET_RATIO"]) + \
                            ((menu_final_width * ratios["MENU"]["CLOSE_SETTINGS_MENU"]["WIDTH_RATIO"]) / 2)
    close_settings_menu_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - menu_final_height) / 2) + \
                            (menu_final_height * (ratios["MENU"]["CLOSE_SETTINGS_MENU"]["TOP_OFFSET_RATIO"] + (ratios["MENU"]["CLOSE_SETTINGS_MENU"]["HEIGHT_RATIO"] / 2)))

    # =====================
    # AUTOCRAFT (centered, fixed AR)
    # =====================
    if roblox_client.screen_width * ratios["AUTOCRAFT"]["SCALE_WIDTH"] / ratios["AUTOCRAFT"]["ASPECT_RATIO"] <= \
       roblox_client.screen_height * ratios["AUTOCRAFT"]["SCALE_HEIGHT"]:
        autoc_final_w = roblox_client.screen_width * ratios["AUTOCRAFT"]["SCALE_WIDTH"]
        autoc_final_h = roblox_client.screen_width * ratios["AUTOCRAFT"]["SCALE_WIDTH"] / ratios["AUTOCRAFT"]["ASPECT_RATIO"]
    else:
        autoc_final_h = roblox_client.screen_height * ratios["AUTOCRAFT"]["SCALE_HEIGHT"]
        autoc_final_w = roblox_client.screen_height * ratios["AUTOCRAFT"]["SCALE_HEIGHT"] * ratios["AUTOCRAFT"]["ASPECT_RATIO"]

    # craft
    autocraft_craft_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - autoc_final_w) / 2) + \
                        (autoc_final_w * ratios["AUTOCRAFT"]["CRAFT"]["LEFT_OFFSET_RATIO"]) + \
                        ((autoc_final_w * ratios["AUTOCRAFT"]["CRAFT"]["WIDTH_RATIO"]) / 2)
    autocraft_craft_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - autoc_final_h) / 2) + \
                        (autoc_final_h * (ratios["AUTOCRAFT"]["CRAFT"]["TOP_OFFSET_RATIO"] + (ratios["AUTOCRAFT"]["CRAFT"]["HEIGHT_RATIO"] / 2)))

    # auto
    autocraft_auto_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - autoc_final_w) / 2) + \
                       (autoc_final_w * ratios["AUTOCRAFT"]["AUTO"]["LEFT_OFFSET_RATIO"]) + \
                       ((autoc_final_w * ratios["AUTOCRAFT"]["AUTO"]["WIDTH_RATIO"]) / 2)
    autocraft_auto_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - autoc_final_h) / 2) + \
                       (autoc_final_h * (ratios["AUTOCRAFT"]["AUTO"]["TOP_OFFSET_RATIO"] + (ratios["AUTOCRAFT"]["AUTO"]["HEIGHT_RATIO"] / 2)))

    # search
    autocraft_search_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - autoc_final_w) / 2) + \
                         (autoc_final_w * ratios["AUTOCRAFT"]["SEARCH"]["LEFT_OFFSET_RATIO"]) + \
                         ((autoc_final_w * ratios["AUTOCRAFT"]["SEARCH"]["WIDTH_RATIO"]) / 2)
    autocraft_search_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - autoc_final_h) / 2) + \
                         (autoc_final_h * (ratios["AUTOCRAFT"]["SEARCH"]["TOP_OFFSET_RATIO"] + (ratios["AUTOCRAFT"]["SEARCH"]["HEIGHT_RATIO"] / 2)))

    # first potion
    autocraft_first_potion_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - autoc_final_w) / 2) + \
                               (autoc_final_w * ratios["AUTOCRAFT"]["FIRST_POTION"]["LEFT_OFFSET_RATIO"]) + \
                               ((autoc_final_w * ratios["AUTOCRAFT"]["FIRST_POTION"]["WIDTH_RATIO"]) / 2)
    autocraft_first_potion_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - autoc_final_h) / 2) + \
                               (autoc_final_h * (ratios["AUTOCRAFT"]["FIRST_POTION"]["TOP_OFFSET_RATIO"] + (ratios["AUTOCRAFT"]["FIRST_POTION"]["HEIGHT_RATIO"] / 2)))

    # row 1
    autocraft_first_amt_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - autoc_final_w) / 2) + \
                            (autoc_final_w * ratios["AUTOCRAFT"]["FIRST_AMT"]["LEFT_OFFSET_RATIO"]) + \
                            ((autoc_final_w * ratios["AUTOCRAFT"]["FIRST_AMT"]["WIDTH_RATIO"]) / 2)
    autocraft_first_amt_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - autoc_final_h) / 2) + \
                            (autoc_final_h * (ratios["AUTOCRAFT"]["FIRST_AMT"]["TOP_OFFSET_RATIO"] + (ratios["AUTOCRAFT"]["FIRST_AMT"]["HEIGHT_RATIO"] / 2)))

    autocraft_first_add_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - autoc_final_w) / 2) + \
                            (autoc_final_w * ratios["AUTOCRAFT"]["FIRST_ADD"]["LEFT_OFFSET_RATIO"]) + \
                            ((autoc_final_w * ratios["AUTOCRAFT"]["FIRST_ADD"]["WIDTH_RATIO"]) / 2)
    autocraft_first_add_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - autoc_final_h) / 2) + \
                            (autoc_final_h * (ratios["AUTOCRAFT"]["FIRST_ADD"]["TOP_OFFSET_RATIO"] + (ratios["AUTOCRAFT"]["FIRST_ADD"]["HEIGHT_RATIO"] / 2)))

    # row 2
    autocraft_second_amt_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - autoc_final_w) / 2) + \
                             (autoc_final_w * ratios["AUTOCRAFT"]["SECOND_AMT"]["LEFT_OFFSET_RATIO"]) + \
                             ((autoc_final_w * ratios["AUTOCRAFT"]["SECOND_AMT"]["WIDTH_RATIO"]) / 2)
    autocraft_second_amt_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - autoc_final_h) / 2) + \
                             (autoc_final_h * (ratios["AUTOCRAFT"]["SECOND_AMT"]["TOP_OFFSET_RATIO"] + (ratios["AUTOCRAFT"]["SECOND_AMT"]["HEIGHT_RATIO"] / 2)))

    autocraft_second_add_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - autoc_final_w) / 2) + \
                             (autoc_final_w * ratios["AUTOCRAFT"]["SECOND_ADD"]["LEFT_OFFSET_RATIO"]) + \
                             ((autoc_final_w * ratios["AUTOCRAFT"]["SECOND_ADD"]["WIDTH_RATIO"]) / 2)
    autocraft_second_add_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - autoc_final_h) / 2) + \
                             (autoc_final_h * (ratios["AUTOCRAFT"]["SECOND_ADD"]["TOP_OFFSET_RATIO"] + (ratios["AUTOCRAFT"]["SECOND_ADD"]["HEIGHT_RATIO"] / 2)))

    # row 3
    autocraft_third_amt_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - autoc_final_w) / 2) + \
                            (autoc_final_w * ratios["AUTOCRAFT"]["THIRD_AMT"]["LEFT_OFFSET_RATIO"]) + \
                            ((autoc_final_w * ratios["AUTOCRAFT"]["THIRD_AMT"]["WIDTH_RATIO"]) / 2)
    autocraft_third_amt_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - autoc_final_h) / 2) + \
                            (autoc_final_h * (ratios["AUTOCRAFT"]["THIRD_AMT"]["TOP_OFFSET_RATIO"] + (ratios["AUTOCRAFT"]["THIRD_AMT"]["HEIGHT_RATIO"] / 2)))

    autocraft_third_add_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - autoc_final_w) / 2) + \
                            (autoc_final_w * ratios["AUTOCRAFT"]["THIRD_ADD"]["LEFT_OFFSET_RATIO"]) + \
                            ((autoc_final_w * ratios["AUTOCRAFT"]["THIRD_ADD"]["WIDTH_RATIO"]) / 2)
    autocraft_third_add_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - autoc_final_h) / 2) + \
                            (autoc_final_h * (ratios["AUTOCRAFT"]["THIRD_ADD"]["TOP_OFFSET_RATIO"] + (ratios["AUTOCRAFT"]["THIRD_ADD"]["HEIGHT_RATIO"] / 2)))

    # scrolled rows
    autocraft_first_scrolled_amt_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - autoc_final_w) / 2) + \
                                     (autoc_final_w * ratios["AUTOCRAFT"]["FIRST_SCROLLED_AMT"]["LEFT_OFFSET_RATIO"]) + \
                                     ((autoc_final_w * ratios["AUTOCRAFT"]["FIRST_SCROLLED_AMT"]["WIDTH_RATIO"]) / 2)
    autocraft_first_scrolled_amt_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - autoc_final_h) / 2) + \
                                     (autoc_final_h * (ratios["AUTOCRAFT"]["FIRST_SCROLLED_AMT"]["TOP_OFFSET_RATIO"] + (ratios["AUTOCRAFT"]["FIRST_SCROLLED_AMT"]["HEIGHT_RATIO"] / 2)))

    autocraft_first_scrolled_add_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - autoc_final_w) / 2) + \
                                     (autoc_final_w * ratios["AUTOCRAFT"]["FIRST_SCROLLED_ADD"]["LEFT_OFFSET_RATIO"]) + \
                                     ((autoc_final_w * ratios["AUTOCRAFT"]["FIRST_SCROLLED_ADD"]["WIDTH_RATIO"]) / 2)
    autocraft_first_scrolled_add_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - autoc_final_h) / 2) + \
                                     (autoc_final_h * (ratios["AUTOCRAFT"]["FIRST_SCROLLED_ADD"]["TOP_OFFSET_RATIO"] + (ratios["AUTOCRAFT"]["FIRST_SCROLLED_ADD"]["HEIGHT_RATIO"] / 2)))

    autocraft_second_scrolled_amt_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - autoc_final_w) / 2) + \
                                      (autoc_final_w * ratios["AUTOCRAFT"]["SECOND_SCROLLED_AMT"]["LEFT_OFFSET_RATIO"]) + \
                                      ((autoc_final_w * ratios["AUTOCRAFT"]["SECOND_SCROLLED_AMT"]["WIDTH_RATIO"]) / 2)
    autocraft_second_scrolled_amt_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - autoc_final_h) / 2) + \
                                      (autoc_final_h * (ratios["AUTOCRAFT"]["SECOND_SCROLLED_AMT"]["TOP_OFFSET_RATIO"] + (ratios["AUTOCRAFT"]["SECOND_SCROLLED_AMT"]["HEIGHT_RATIO"] / 2)))

    autocraft_second_scrolled_add_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - autoc_final_w) / 2) + \
                                      (autoc_final_w * ratios["AUTOCRAFT"]["SECOND_SCROLLED_ADD"]["LEFT_OFFSET_RATIO"]) + \
                                      ((autoc_final_w * ratios["AUTOCRAFT"]["SECOND_SCROLLED_ADD"]["WIDTH_RATIO"]) / 2)
    autocraft_second_scrolled_add_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - autoc_final_h) / 2) + \
                                      (autoc_final_h * (ratios["AUTOCRAFT"]["SECOND_SCROLLED_ADD"]["TOP_OFFSET_RATIO"] + (ratios["AUTOCRAFT"]["SECOND_SCROLLED_ADD"]["HEIGHT_RATIO"] / 2)))

    autocraft_third_scrolled_amt_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - autoc_final_w) / 2) + \
                                     (autoc_final_w * ratios["AUTOCRAFT"]["THIRD_SCROLLED_AMT"]["LEFT_OFFSET_RATIO"]) + \
                                     ((autoc_final_w * ratios["AUTOCRAFT"]["THIRD_SCROLLED_AMT"]["WIDTH_RATIO"]) / 2)
    autocraft_third_scrolled_amt_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - autoc_final_h) / 2) + \
                                     (autoc_final_h * (ratios["AUTOCRAFT"]["THIRD_SCROLLED_AMT"]["TOP_OFFSET_RATIO"] + (ratios["AUTOCRAFT"]["THIRD_SCROLLED_AMT"]["HEIGHT_RATIO"] / 2)))

    autocraft_third_scrolled_add_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - autoc_final_w) / 2) + \
                                     (autoc_final_w * ratios["AUTOCRAFT"]["THIRD_SCROLLED_ADD"]["LEFT_OFFSET_RATIO"]) + \
                                     ((autoc_final_w * ratios["AUTOCRAFT"]["THIRD_SCROLLED_ADD"]["WIDTH_RATIO"]) / 2)
    autocraft_third_scrolled_add_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - autoc_final_h) / 2) + \
                                     (autoc_final_h * (ratios["AUTOCRAFT"]["THIRD_SCROLLED_ADD"]["TOP_OFFSET_RATIO"] + (ratios["AUTOCRAFT"]["THIRD_SCROLLED_ADD"]["HEIGHT_RATIO"] / 2)))

    # scroll bar
    autocraft_scroll_x = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - autoc_final_w) / 2) + \
                         (autoc_final_w * ratios["AUTOCRAFT"]["SCROLL"]["LEFT_OFFSET_RATIO"]) + \
                         ((autoc_final_w * ratios["AUTOCRAFT"]["SCROLL"]["WIDTH_RATIO"]) / 2)
    autocraft_scroll_y = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - autoc_final_h) / 2) + \
                         (autoc_final_h * (ratios["AUTOCRAFT"]["SCROLL"]["TOP_OFFSET_RATIO"] + (ratios["AUTOCRAFT"]["SCROLL"]["HEIGHT_RATIO"] / 2)))

    # =====================
    # QUESTBOARD
    # =====================
    qb_right_x = roblox_client.top_left_pos[0] + roblox_client.screen_width  * ratios["QUESTBOARD"]["WINDOW_ANCHORS"]["RIGHT"]["CENTER_X_RATIO"]
    qb_right_y = roblox_client.top_left_pos[1] + roblox_client.screen_height * ratios["QUESTBOARD"]["WINDOW_ANCHORS"]["RIGHT"]["CENTER_Y_RATIO"]

    qb_left_x  = roblox_client.top_left_pos[0] + roblox_client.screen_width  * ratios["QUESTBOARD"]["WINDOW_ANCHORS"]["LEFT"]["CENTER_X_RATIO"]
    qb_left_y  = roblox_client.top_left_pos[1] + roblox_client.screen_height * ratios["QUESTBOARD"]["WINDOW_ANCHORS"]["LEFT"]["CENTER_Y_RATIO"]

    qb_exit_x  = roblox_client.top_left_pos[0] + roblox_client.screen_width  * ratios["QUESTBOARD"]["WINDOW_ANCHORS"]["EXIT"]["CENTER_X_RATIO"]
    qb_exit_y  = roblox_client.top_left_pos[1] + roblox_client.screen_height * ratios["QUESTBOARD"]["WINDOW_ANCHORS"]["EXIT"]["CENTER_Y_RATIO"]

    qb_info_w = roblox_client.screen_width  * ratios["QUESTBOARD"]["INFO_BOX"]["WIDTH_RATIO"]
    qb_info_h = roblox_client.screen_height * ratios["QUESTBOARD"]["INFO_BOX"]["HEIGHT_RATIO"]

    qb_info_left = roblox_client.top_left_pos[0] + roblox_client.screen_width  * ratios["QUESTBOARD"]["INFO_BOX"]["LEFT_OFFSET_RATIO"]
    qb_info_top  = roblox_client.top_left_pos[1] + roblox_client.screen_height * ratios["QUESTBOARD"]["INFO_BOX"]["TOP_OFFSET_RATIO"]

    qb_accept_x = qb_info_left + (qb_info_w * ratios["QUESTBOARD"]["ACCEPT"]["LEFT_OFFSET_RATIO"]) + ((qb_info_w * ratios["QUESTBOARD"]["ACCEPT"]["WIDTH_RATIO"]) / 2)
    qb_accept_y = qb_info_top  + (qb_info_h * ratios["QUESTBOARD"]["ACCEPT"]["TOP_OFFSET_RATIO"]) + ((qb_info_h * ratios["QUESTBOARD"]["ACCEPT"]["HEIGHT_RATIO"]) / 2)

    qb_dismiss_x = qb_info_left + (qb_info_w * ratios["QUESTBOARD"]["DISMISS"]["LEFT_OFFSET_RATIO"]) + ((qb_info_w * ratios["QUESTBOARD"]["DISMISS"]["WIDTH_RATIO"]) / 2)
    qb_dismiss_y = qb_info_top  + (qb_info_h * ratios["QUESTBOARD"]["DISMISS"]["TOP_OFFSET_RATIO"]) + ((qb_info_h * ratios["QUESTBOARD"]["DISMISS"]["HEIGHT_RATIO"]) / 2)

    # =====================
    # SIDEBAR (derived from SidebarButton.lua)
    # =====================
    SB_LEFT_PX = 10
    SB_SIZE_W_RATIO = 0.025
    SB_SIZE_H_RATIO = 0.527
    SB_PAD_RATIO = 0.01
    SB_MIN_BTN_PX = 35
    SB_NUM = 6  # 1:Aura Storage, 2:Collection, 3:Storage, 4:Quests, 5:Daily Quests, 6:Menu

    # Container geometry (absolute)
    sb_cont_w  = roblox_client.screen_width  * SB_SIZE_W_RATIO
    sb_cont_h  = roblox_client.screen_height * SB_SIZE_H_RATIO
    sb_cont_l  = roblox_client.top_left_pos[0] + SB_LEFT_PX
    sb_cont_t  = roblox_client.top_left_pos[1] + (roblox_client.screen_height * 0.5) - (sb_cont_h / 2.0)

    # Button size & padding (absolute)
    sb_btn_size = sb_cont_w
    if sb_btn_size < SB_MIN_BTN_PX:
        sb_btn_size = SB_MIN_BTN_PX

    sb_pad = sb_cont_h * SB_PAD_RATIO  # vertical gap between items

    # Total vertical stack height
    sb_stack_h = (SB_NUM * sb_btn_size) + ((SB_NUM - 1) * sb_pad)

    # Center X for all buttons (middle of the container width)
    sb_center_x = sb_cont_l + (sb_cont_w / 2.0)

    # First button center Y: top + centered stack offset + half a button
    sb_first_center_y = sb_cont_t + ((sb_cont_h - sb_stack_h) / 2.0) + (sb_btn_size / 2.0)

    # Compute centers for the 6 buttons
    sidebar_xy = []
    for i in range(SB_NUM):
        cy = sb_first_center_y + i * (sb_btn_size + sb_pad)
        sidebar_xy.append([int(round(sb_center_x)), int(round(cy))])

    # Map (1..6) → explicit flat vars used in clickpos
    aura_storage_x, aura_storage_y = sidebar_xy[0]
    collection_x,   collection_y   = sidebar_xy[1]
    storage_x,      storage_y      = sidebar_xy[2]
    quests_x,       quests_y       = sidebar_xy[3]
    daily_quests_x, daily_quests_y = sidebar_xy[4]
    menu_x,         menu_y         = sidebar_xy[5]

    # =====================
    # COLLECTION: Exit
    # =====================
    # Compute Collection size
    if roblox_client.screen_width * ratios["COLLECTION"]["SCALE_WIDTH"] / ratios["COLLECTION"]["ASPECT_RATIO"] <= \
    roblox_client.screen_height * ratios["COLLECTION"]["SCALE_HEIGHT"]:
        coll_final_w = roblox_client.screen_width * ratios["COLLECTION"]["SCALE_WIDTH"]
        coll_final_h = roblox_client.screen_width * ratios["COLLECTION"]["SCALE_WIDTH"] / ratios["COLLECTION"]["ASPECT_RATIO"]
    else:
        coll_final_h = roblox_client.screen_height * ratios["COLLECTION"]["SCALE_HEIGHT"]
        coll_final_w = roblox_client.screen_height * ratios["COLLECTION"]["SCALE_HEIGHT"] * ratios["COLLECTION"]["ASPECT_RATIO"]

    # Anchor: fixed offsets instead of centering
    coll_x = roblox_client.top_left_pos[0] + ratios["COLLECTION"]["LEFT_OFFSET_PX"]
    coll_y = roblox_client.top_left_pos[1] + ratios["COLLECTION"]["TOP_OFFSET_PX"]

    # Exit button inside Collection frame
    exit_collection_x = coll_x + (coll_final_w * ratios["COLLECTION"]["EXIT_BUTTON"]["LEFT_OFFSET_RATIO"]) + \
                        ((coll_final_w * ratios["COLLECTION"]["EXIT_BUTTON"]["WIDTH_RATIO"]) / 2)

    exit_collection_y = coll_y + (coll_final_h * ratios["COLLECTION"]["EXIT_BUTTON"]["TOP_OFFSET_RATIO"]) + \
                        ((coll_final_h * ratios["COLLECTION"]["EXIT_BUTTON"]["HEIGHT_RATIO"]) / 2)

    # Store positions
    roblox_client.button_positions["exit_collection"] = [exit_collection_x, exit_collection_y]
    roblox_client.button_positions.setdefault("CollectionUI", {})
    roblox_client.button_positions["CollectionUI"]["ExitCollection"] = [exit_collection_x, exit_collection_y]

    # =====================
    # Build clickpos and assign (flat aliases + namespaced)
    # =====================
    clickpos = {
        # --- Inventory / Aura / Menu ---
        "items_btn": [items_button_x, items_button_y],
        "search_bar": [search_bar_x, search_bar_y],
        "first_inv_item": [first_inv_item_x, first_inv_item_y],
        "item_amount": [item_amount_x, item_amount_y],
        "use_item": [use_item_x, use_item_y],
        "close_menu": [exit_storage_x, exit_storage_y],
        "first_aura_position": [aura_pos_x, aura_pos_y],
        "equip_aura": [aura_equip_x, aura_equip_y],
        "questboard_right": [qb_right_x, qb_right_y],
        "questboard_left": [qb_left_x, qb_left_y],
        "questboard_exit": [qb_exit_x, qb_exit_y],
        "questboard_dismiss": [qb_dismiss_x, qb_dismiss_y],
        "questboard_accept": [qb_accept_x, qb_accept_y],
        "settings": [open_settings_x, open_settings_y],
        "rolling": [rolling_x, rolling_y],
        "cutscene_skip": [cutscene_skip_x, cutscene_skip_y],
        "close_settings_menu": [close_settings_menu_x, close_settings_menu_y],

        # --- Sidebar (flat aliases) ---
        "aura_storage": [aura_storage_x, aura_storage_y],
        "collection":   [collection_x,   collection_y],
        "open_inventory":      [storage_x,      storage_y],
        "quests":       [quests_x,       quests_y],
        "daily_quests": [daily_quests_x, daily_quests_y],
        "menu_button":  [menu_x,         menu_y],   # avoid "menu" collision

        # --- Sidebar (namespaced group) ---
        "Sidebar": {
            "AuraStorage":  [aura_storage_x,  aura_storage_y],
            "Collection":   [collection_x,    collection_y],
            "Storage":      [storage_x,       storage_y],
            "Quests":       [quests_x,        quests_y],
            "DailyQuests":  [daily_quests_x,  daily_quests_y],
            "Menu":         [menu_x,          menu_y],
        },

        # --- Collection ---
        "exit_collection": [exit_collection_x, exit_collection_y],

        # --- Auto Crafting ---
        "autocraft_craft": [autocraft_craft_x, autocraft_craft_y],
        "autocraft_auto": [autocraft_auto_x, autocraft_auto_y],
        "autocraft_search": [autocraft_search_x, autocraft_search_y],
        "autocraft_first_potion": [autocraft_first_potion_x, autocraft_first_potion_y],
        "autocraft_first_add": [autocraft_first_add_x, autocraft_first_add_y],
        "autocraft_first_amt": [autocraft_first_amt_x, autocraft_first_amt_y],
        "autocraft_second_add": [autocraft_second_add_x, autocraft_second_add_y],
        "autocraft_second_amt": [autocraft_second_amt_x, autocraft_second_amt_y],
        "autocraft_third_add": [autocraft_third_add_x, autocraft_third_add_y],
        "autocraft_third_add": [autocraft_third_amt_x, autocraft_third_amt_y],

        "autocraft_first_scrolled_add": [autocraft_first_scrolled_add_x, autocraft_first_scrolled_add_y],
        "autocraft_first_scrolled_amt": [autocraft_first_scrolled_amt_x, autocraft_first_scrolled_amt_y],
        "autocraft_second_scrolled_add": [autocraft_second_scrolled_add_x, autocraft_second_scrolled_add_y],
        "autocraft_second_scrolled_amt": [autocraft_second_scrolled_amt_x, autocraft_second_scrolled_amt_y],
        "autocraft_third_scrolled_add": [autocraft_third_scrolled_add_x, autocraft_third_scrolled_add_y],
        "autocraft_third_scrolled_amt": [autocraft_third_scrolled_amt_x, autocraft_third_scrolled_amt_y],

        "autocraft_scroll": [autocraft_scroll_x, autocraft_scroll_y],

        # --- Flat aliases (Jester dialog row) ---
        "jester_open": [jester_open_x, jester_open_y],
        "jester_exchange": [jester_exchange_x, jester_exchange_y],   # dialog row
        "jester_exchange_ui": [jex_button_x, jex_button_y],          # exchange screen action button
        "jester_who": [jester_who_x, jester_who_y],
        "jester_leave": [jester_leave_x, jester_leave_y],
        "jester_auto_ex_first": [jex_first_x, jex_first_y],
        "jester_auto_ex_second": [jex_second_x, jex_second_y],
        "jester_exchange_confirm": [jcf_confirm_x, jcf_confirm_y],

        # --- Flat aliases (Merchant / Mari dialog row + shop) ---
        "merchant_open":  [merchant_open_x,  merchant_open_y],
        "merchant_who":   [merchant_who_x,   merchant_who_y],
        "merchant_leave": [merchant_leave_x, merchant_leave_y],
        "merchant_slot_1": [ms1_x, ms1_y],
        "merchant_slot_2": [ms2_x, ms2_y],
        "merchant_slot_3": [ms3_x, ms3_y],
        "merchant_slot_4": [ms4_x, ms4_y],
        "merchant_slot_5": [ms5_x, ms5_y],
        "merchant_purchase": [mp_buy_x, mp_buy_y],
        "merchant_amount": [mp_amt_x, mp_amt_y],
        "merchant_close": [mp_close_x, mp_close_y],

        # --- Namespaced groups (dot-lookups) ---
        "jester": {
            "open": [jester_open_x, jester_open_y],
            "exchange": [jester_exchange_x, jester_exchange_y],   # dialog row
            "exchange_ui": [jex_button_x, jex_button_y],          # exchange screen action button
            "auto_ex_first": [jex_first_x, jex_first_y],
            "auto_ex_second": [jex_second_x, jex_second_y],
            "exchange_confirm": [jcf_confirm_x, jcf_confirm_y],
        },
        "merchant": {
             "open": [merchant_open_x, merchant_open_y],
             "who": [merchant_who_x, merchant_who_y],
             "leave": [merchant_leave_x, merchant_leave_y],
             "slot_1": [ms1_x, ms1_y],
             "slot_2": [ms2_x, ms2_y],
             "slot_3": [ms3_x, ms3_y],
             "slot_4": [ms4_x, ms4_y],
             "slot_5": [ms5_x, ms5_y],
             "purchase": [mp_buy_x, mp_buy_y],
             "amount": [mp_amt_x, mp_amt_y],
             "close": [mp_close_x, mp_close_y],
         }
    }
    roblox_client.button_positions = clickpos


# =======================
# Refresh clients
# =======================
def refresh_clients():
    windows = gw.getWindowsWithTitle("Roblox")
    for win in windows:
        hwnd_key = f"client{win._hWnd}"
        roblox_clients[hwnd_key] = ClientData(win._hWnd)
        calibrate_buttons(hwnd_key)


# =======================
# Move to button
# =======================
def click_button(mkey, button_name: str, client_key: str, delay: float = 0.1):
    """
    Click a button by name (case-insensitive).
    - button_name: e.g. "use_item", "items_btn", "merchant.purchase", "jester_exchange", etc.
    - client_key: which client from return_clients()
    """
    roblox_client = roblox_clients[client_key]

    # refresh geometry + button positions if needed
    roblox_client.update_pos()
    calibrate_buttons(client_key)

    # normalize input (lowercase alphanumeric + "_" + ".")
    def _norm(s: str) -> str:
        return "".join(ch for ch in s.lower() if ch.isalnum() or ch in ("_", "."))

    target = _norm(button_name)

    # depth-first search through button_positions
    def _find_button_xy(data):
        if isinstance(data, (list, tuple)) and len(data) == 2:
            return [int(data[0]), int(data[1])]
        if isinstance(data, dict):
            for k, v in data.items():
                nk = _norm(k)
                if nk == target or target in nk:
                    got = _find_button_xy(v)
                    if got:
                        return got
                if isinstance(v, dict):
                    got = _find_button_xy(v)
                    if got:
                        return got
        return None

    xy = _find_button_xy(roblox_client.button_positions)
    if xy is None:
        print(f"[ERR] Button '{button_name}' not found in {client_key}. "
              f"Available keys: {list(roblox_client.button_positions.keys())}")
        return False

    # bring client to front best effort
    try:
        win32gui.SetForegroundWindow(roblox_client.hwnd)
        win32gui.SetFocus(roblox_client.hwnd)
    except Exception:
        pass

    time.sleep(delay)
    mkey.left_click_xy_natural(xy[0], xy[1])

    return True

def move_to_button(mkey, button_name: str, client_key: str, delay: float = 0.1):
    """
    Click a button by name (case-insensitive).
    - button_name: e.g. "use_item", "items_btn", "merchant.purchase", "jester_exchange", etc.
    - client_key: which client from return_clients()
    """
    roblox_client = roblox_clients[client_key]

    # refresh geometry + button positions if needed
    roblox_client.update_pos()
    calibrate_buttons(client_key)

    # normalize input (lowercase alphanumeric + "_" + ".")
    def _norm(s: str) -> str:
        return "".join(ch for ch in s.lower() if ch.isalnum() or ch in ("_", "."))

    target = _norm(button_name)

    # depth-first search through button_positions
    def _find_button_xy(data):
        if isinstance(data, (list, tuple)) and len(data) == 2:
            return [int(data[0]), int(data[1])]
        if isinstance(data, dict):
            for k, v in data.items():
                nk = _norm(k)
                if nk == target or target in nk:
                    got = _find_button_xy(v)
                    if got:
                        return got
                if isinstance(v, dict):
                    got = _find_button_xy(v)
                    if got:
                        return got
        return None

    xy = _find_button_xy(roblox_client.button_positions)
    if xy is None:
        print(f"[ERR] Button '{button_name}' not found in {client_key}. "
              f"Available keys: {list(roblox_client.button_positions.keys())}")
        return False

    # bring client to front best effort
    try:
        win32gui.SetForegroundWindow(roblox_client.hwnd)
        win32gui.SetFocus(roblox_client.hwnd)
    except Exception:
        pass

    time.sleep(delay)
    mkey.move_to_natural(xy[0], xy[1])

    return True

def get_merchant_shop(client_key: str, reader) -> dict:

    ratios = load_ratios()

    roblox_client = roblox_clients[client_key]

    if roblox_client.screen_width * ratios["MARI_PURCHASE"]["SCALE_WIDTH"] / ratios["MARI_PURCHASE"]["ASPECT_RATIO"] <= \
       roblox_client.screen_height * ratios["MARI_PURCHASE"]["SCALE_HEIGHT"]:
        mp_final_w = roblox_client.screen_width * ratios["MARI_PURCHASE"]["SCALE_WIDTH"]
        mp_final_h = roblox_client.screen_width * ratios["MARI_PURCHASE"]["SCALE_WIDTH"] / ratios["MARI_PURCHASE"]["ASPECT_RATIO"]
    else:
        mp_final_h = roblox_client.screen_height * ratios["MARI_PURCHASE"]["SCALE_HEIGHT"]
        mp_final_w = roblox_client.screen_height * ratios["MARI_PURCHASE"]["SCALE_HEIGHT"] * ratios["MARI_PURCHASE"]["ASPECT_RATIO"]

    # ITEM 1
    item1_left   = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - mp_final_w) / 2) + \
               (mp_final_w * ratios["MARI_PURCHASE"]["ITEM_1"]["LEFT_OFFSET_RATIO"])
    item1_top    = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - mp_final_h) / 2) + \
               (mp_final_h * ratios["MARI_PURCHASE"]["ITEM_1"]["TOP_OFFSET_RATIO"])
    item1_width  = mp_final_w * ratios["MARI_PURCHASE"]["ITEM_1"]["WIDTH_RATIO"]
    item1_height = mp_final_h * ratios["MARI_PURCHASE"]["ITEM_1"]["HEIGHT_RATIO"]

    # ITEM 2
    item2_left   = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - mp_final_w) / 2) + \
               (mp_final_w * ratios["MARI_PURCHASE"]["ITEM_2"]["LEFT_OFFSET_RATIO"])
    item2_top    = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - mp_final_h) / 2) + \
               (mp_final_h * ratios["MARI_PURCHASE"]["ITEM_2"]["TOP_OFFSET_RATIO"])
    item2_width  = mp_final_w * ratios["MARI_PURCHASE"]["ITEM_2"]["WIDTH_RATIO"]
    item2_height = mp_final_h * ratios["MARI_PURCHASE"]["ITEM_2"]["HEIGHT_RATIO"]

    # ITEM 3
    item3_left   = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - mp_final_w) / 2) + \
               (mp_final_w * ratios["MARI_PURCHASE"]["ITEM_3"]["LEFT_OFFSET_RATIO"])
    item3_top    = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - mp_final_h) / 2) + \
               (mp_final_h * ratios["MARI_PURCHASE"]["ITEM_3"]["TOP_OFFSET_RATIO"])
    item3_width  = mp_final_w * ratios["MARI_PURCHASE"]["ITEM_3"]["WIDTH_RATIO"]
    item3_height = mp_final_h * ratios["MARI_PURCHASE"]["ITEM_3"]["HEIGHT_RATIO"]

    # ITEM 4
    item4_left   = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - mp_final_w) / 2) + \
               (mp_final_w * ratios["MARI_PURCHASE"]["ITEM_4"]["LEFT_OFFSET_RATIO"])
    item4_top    = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - mp_final_h) / 2) + \
               (mp_final_h * ratios["MARI_PURCHASE"]["ITEM_4"]["TOP_OFFSET_RATIO"])
    item4_width  = mp_final_w * ratios["MARI_PURCHASE"]["ITEM_4"]["WIDTH_RATIO"]
    item4_height = mp_final_h * ratios["MARI_PURCHASE"]["ITEM_4"]["HEIGHT_RATIO"]

    # ITEM 5
    item5_left   = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - mp_final_w) / 2) + \
               (mp_final_w * ratios["MARI_PURCHASE"]["ITEM_5"]["LEFT_OFFSET_RATIO"])
    item5_top    = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - mp_final_h) / 2) + \
               (mp_final_h * ratios["MARI_PURCHASE"]["ITEM_5"]["TOP_OFFSET_RATIO"])
    item5_width  = mp_final_w * ratios["MARI_PURCHASE"]["ITEM_5"]["WIDTH_RATIO"]
    item5_height = mp_final_h * ratios["MARI_PURCHASE"]["ITEM_5"]["HEIGHT_RATIO"]

    locations = {
    "item1": [item1_left, item1_top, item1_width, item1_height, "merchantItems"],
    "item2": [item2_left, item2_top, item2_width, item2_height, "merchantItems"],
    "item3": [item3_left, item3_top, item3_width, item3_height, "merchantItems"],
    "item4": [item4_left, item4_top, item4_width, item4_height, "merchantItems"],
    "item5": [item5_left, item5_top, item5_width, item5_height, "merchantItems"],
    }
    return pyocrscope.read_ocr(reader, locations)

def get_first_inventory_item(client_key: str, reader) -> dict:
    
    ratios = load_ratios()

    roblox_client = roblox_clients[client_key]

    # Scale inventory container
    if roblox_client.screen_width * ratios["INVENTORY"]["SCALE_WIDTH"] / ratios["INVENTORY"]["ASPECT_RATIO"] <= \
       roblox_client.screen_height * ratios["INVENTORY"]["SCALE_HEIGHT"]:
        inv_final_w = roblox_client.screen_width * ratios["INVENTORY"]["SCALE_WIDTH"]
        inv_final_h = roblox_client.screen_width * ratios["INVENTORY"]["SCALE_WIDTH"] / ratios["INVENTORY"]["ASPECT_RATIO"]
    else:
        inv_final_h = roblox_client.screen_height * ratios["INVENTORY"]["SCALE_HEIGHT"]
        inv_final_w = roblox_client.screen_height * ratios["INVENTORY"]["SCALE_HEIGHT"] * ratios["INVENTORY"]["ASPECT_RATIO"]

    # First inventory item rect (for OCR)
    first_inv_item_left = roblox_client.top_left_pos[0] + ((roblox_client.screen_width - inv_final_w) / 2) + \
                          (inv_final_w * ratios["INVENTORY"]["FIRST_INV_ITEM"]["LEFT_OFFSET_RATIO"])
    first_inv_item_top  = roblox_client.top_left_pos[1] + ((roblox_client.screen_height - inv_final_h) / 2) + \
                          (inv_final_h * ratios["INVENTORY"]["FIRST_INV_ITEM"]["TOP_OFFSET_RATIO"])
    first_inv_item_w    = inv_final_w * ratios["INVENTORY"]["FIRST_INV_ITEM"]["WIDTH_RATIO"]
    first_inv_item_h    = inv_final_h * ratios["INVENTORY"]["FIRST_INV_ITEM"]["HEIGHT_RATIO"]

    locations = {
        "first_inv_item": [first_inv_item_left, first_inv_item_top, first_inv_item_w, first_inv_item_h, "validInventoryItems"]
    }

    return pyocrscope.read_ocr(reader, locations)

def get_jester_exchange(client_key: str, reader) -> dict:

    ratios = load_ratios()

    roblox_client = roblox_clients[client_key]

    # Container scaling
    if roblox_client.screen_width * ratios["JESTER_EXCHANGE"]["SCALE_WIDTH"] / ratios["JESTER_EXCHANGE"]["ASPECT_RATIO"] <= \
       roblox_client.screen_height * ratios["JESTER_EXCHANGE"]["SCALE_HEIGHT"]:
        jex_final_w = roblox_client.screen_width * ratios["JESTER_EXCHANGE"]["SCALE_WIDTH"]
        jex_final_h = roblox_client.screen_width * ratios["JESTER_EXCHANGE"]["SCALE_WIDTH"] / ratios["JESTER_EXCHANGE"]["ASPECT_RATIO"]
    else:
        jex_final_h = roblox_client.screen_height * ratios["JESTER_EXCHANGE"]["SCALE_HEIGHT"]
        jex_final_w = roblox_client.screen_height * ratios["JESTER_EXCHANGE"]["SCALE_HEIGHT"] * ratios["JESTER_EXCHANGE"]["ASPECT_RATIO"]

    # Top-left corner of the container
    base_x = roblox_client.top_left_pos[0] + (roblox_client.screen_width - jex_final_w) / 2
    base_y = roblox_client.top_left_pos[1] + (roblox_client.screen_height - jex_final_h) / 2

    # Rects (TLWH)
    jex_first   = [
        base_x + jex_final_w * ratios["JESTER_EXCHANGE"]["SELL_ITEM_1"]["LEFT_OFFSET_RATIO"],
        base_y + jex_final_h * ratios["JESTER_EXCHANGE"]["SELL_ITEM_1"]["TOP_OFFSET_RATIO"],
        jex_final_w * ratios["JESTER_EXCHANGE"]["SELL_ITEM_1"]["WIDTH_RATIO"],
        jex_final_h * ratios["JESTER_EXCHANGE"]["SELL_ITEM_1"]["HEIGHT_RATIO"],
        "validInventoryItems"
    ]
    jex_second  = [
        base_x + jex_final_w * ratios["JESTER_EXCHANGE"]["SELL_ITEM_2"]["LEFT_OFFSET_RATIO"],
        base_y + jex_final_h * ratios["JESTER_EXCHANGE"]["SELL_ITEM_2"]["TOP_OFFSET_RATIO"],
        jex_final_w * ratios["JESTER_EXCHANGE"]["SELL_ITEM_2"]["WIDTH_RATIO"],
        jex_final_h * ratios["JESTER_EXCHANGE"]["SELL_ITEM_2"]["HEIGHT_RATIO"],
        "validInventoryItems"
    ]

    locations = {
        "sell_item_1": jex_first,
        "sell_item_2": jex_second
    }
    return pyocrscope.read_ocr(reader, locations)

def get_first_crafting_potion(client_key: str, reader) -> dict:

    ratios = load_ratios()

    roblox_client = roblox_clients[client_key]

    # Container scaling
    if roblox_client.screen_width * ratios["AUTOCRAFT"]["SCALE_WIDTH"] / ratios["AUTOCRAFT"]["ASPECT_RATIO"] <= \
       roblox_client.screen_height * ratios["AUTOCRAFT"]["SCALE_HEIGHT"]:
        autoc_final_w = roblox_client.screen_width * ratios["AUTOCRAFT"]["SCALE_WIDTH"]
        autoc_final_h = roblox_client.screen_width * ratios["AUTOCRAFT"]["SCALE_WIDTH"] / ratios["AUTOCRAFT"]["ASPECT_RATIO"]
    else:
        autoc_final_h = roblox_client.screen_height * ratios["AUTOCRAFT"]["SCALE_HEIGHT"]
        autoc_final_w = roblox_client.screen_height * ratios["AUTOCRAFT"]["SCALE_HEIGHT"] * ratios["AUTOCRAFT"]["ASPECT_RATIO"]

    # Top-left of container
    base_x = roblox_client.top_left_pos[0] + (roblox_client.screen_width - autoc_final_w) / 2
    base_y = roblox_client.top_left_pos[1] + (roblox_client.screen_height - autoc_final_h) / 2

    # First crafting potion rect (TLWH) — only top 30% of the full potion box
    full_left   = base_x + autoc_final_w * ratios["AUTOCRAFT"]["FIRST_POTION"]["LEFT_OFFSET_RATIO"]
    full_top    = base_y + autoc_final_h * ratios["AUTOCRAFT"]["FIRST_POTION"]["TOP_OFFSET_RATIO"]
    full_width  = autoc_final_w * ratios["AUTOCRAFT"]["FIRST_POTION"]["WIDTH_RATIO"]
    full_height = autoc_final_h * ratios["AUTOCRAFT"]["FIRST_POTION"]["HEIGHT_RATIO"]

    first_left   = full_left
    first_top    = full_top
    first_width  = full_width
    first_height = full_height * 0.8 #HOW MUCH OF THE BOX

    locations = {
        "first_crafting_potion": [first_left, first_top, first_width, first_height, "craftingPotions"]
    }
    return pyocrscope.read_ocr(reader, locations)

def get_potion_add_check(client_key: str, reader, scrolled: bool = False) -> dict:

    ratios = load_ratios()

    roblox_client = roblox_clients[client_key]

    # ===== container scale (unchanged) =====
    if roblox_client.screen_width * ratios["AUTOCRAFT"]["SCALE_WIDTH"] / ratios["AUTOCRAFT"]["ASPECT_RATIO"] <= \
       roblox_client.screen_height * ratios["AUTOCRAFT"]["SCALE_HEIGHT"]:
        autoc_final_w = roblox_client.screen_width * ratios["AUTOCRAFT"]["SCALE_WIDTH"]
        autoc_final_h = roblox_client.screen_width * ratios["AUTOCRAFT"]["SCALE_WIDTH"] / ratios["AUTOCRAFT"]["ASPECT_RATIO"]
    else:
        autoc_final_h = roblox_client.screen_height * ratios["AUTOCRAFT"]["SCALE_HEIGHT"]
        autoc_final_w = roblox_client.screen_height * ratios["AUTOCRAFT"]["SCALE_HEIGHT"] * ratios["AUTOCRAFT"]["ASPECT_RATIO"]

    base_x = roblox_client.top_left_pos[0] + (roblox_client.screen_width - autoc_final_w) / 2.0
    base_y = roblox_client.top_left_pos[1] + (roblox_client.screen_height - autoc_final_h) / 2.0

    # ===== ADD button (new dimension) =====
    # Use FIRST_SCROLLED_ADD if the list is scrolled
    key = "THIRD_SCROLLED_ADD" if scrolled and "THIRD_SCROLLED_ADD" in ratios["AUTOCRAFT"] else "FIRST_ADD"
    r = ratios["AUTOCRAFT"][key]

    left   = base_x + autoc_final_w * r["LEFT_OFFSET_RATIO"]
    top    = base_y + autoc_final_h * r["TOP_OFFSET_RATIO"]
    width  = autoc_final_w * r["WIDTH_RATIO"]
    height = autoc_final_h * r["HEIGHT_RATIO"]

    # Icon button → use raw OCR (or just for screenshot logging)
    locations = {
        "first_add_button": [left, top, width, height, "validAdd"]
    }
    return pyocrscope.read_ocr(reader, locations, scale_up=2.0)


def get_questboard_header(client_key: str, reader) -> dict:

    ratios = load_ratios()


    roblox_client = roblox_clients[client_key]
    QB = ratios["QUESTBOARD"]
    INFO = QB["INFO_BOX"]

    # Client absolute top-left
    tlx, tly = roblox_client.top_left_pos
    sw, sh = roblox_client.screen_width, roblox_client.screen_height

    # INFO_BOX absolute TLWH (ratios are relative to the client window)
    info_left   = tlx + sw * INFO["LEFT_OFFSET_RATIO"]
    info_top    = tly + sh * INFO["TOP_OFFSET_RATIO"]
    info_width  = sw  * INFO["WIDTH_RATIO"]
    info_height = sh  * INFO["HEIGHT_RATIO"]

    # Slice: top 20% of INFO_BOX
    header_left   = info_left * 0.98
    header_top    = info_top
    header_width  = info_width * 1.02
    header_height = info_height * 0.20

    locations = {
        "questboard_header": [header_left, header_top, header_width, header_height, "validQuests"]
    }
    # Upscale a bit; thin UI text benefits from padding too
    return pyocrscope.read_ocr(reader, locations, 2)

# ===============================================
# MERCHANT (Mari): Read upper 35% of dialog text
# ===============================================
def get_merchant_name(client_key: str, reader) -> dict:

    ratios = load_ratios()
    
    roblox_client = roblox_clients[client_key]
    MD = ratios["MARI_DIALOG"]

    # Client geometry
    tlx, tly = roblox_client.top_left_pos
    sw, sh   = roblox_client.screen_width, roblox_client.screen_height

    # =====================
    # CONTAINER SIZE
    # =====================
    if sw * MD["SCALE_WIDTH"] / MD["ASPECT_RATIO"] <= sh * MD["SCALE_HEIGHT"]:
        mdlg_final_w = sw * MD["SCALE_WIDTH"]
        mdlg_final_h = sw * MD["SCALE_WIDTH"] / MD["ASPECT_RATIO"]
    else:
        mdlg_final_h = sh * MD["SCALE_HEIGHT"]
        mdlg_final_w = sh * MD["SCALE_HEIGHT"] * MD["ASPECT_RATIO"]

    # =====================
    # POSITIONING (CENTER X, SCREEN_TOP_RATIO Y)
    # =====================
    mdlg_base_x = tlx + (sw - mdlg_final_w) / 2
    mdlg_base_y = tly + (sh * MD["SCREEN_TOP_RATIO"])

    # =====================
    # ABSOLUTE TLWH (ENTIRE DIALOG)
    # =====================
    dlg_left   = mdlg_base_x
    dlg_top    = mdlg_base_y
    dlg_width  = mdlg_final_w
    dlg_height = mdlg_final_h

    # =====================
    # TOP-THIRD SLICE (EXPANDED ×2)
    # =====================
    top_part_left   = dlg_left * 0.98
    top_part_top    = dlg_top
    top_part_width  = dlg_width * 0.8
    top_part_height = (dlg_height / 3.0)

    locations = {
        "merchant_name": [top_part_left, top_part_top, top_part_width, top_part_height, "validMerchants"]
    }

    # =====================
    # OCR CALL (UPSCALE + PAD)
    # =====================
    return pyocrscope.read_ocr(reader, locations, scale_up=3.0, pad=5)