"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v2.0.0
Support server: https://discord.gg/8khGXqG7nA
"""

import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))

import pyautogui as pag
import time
from pynput.keyboard import Key
import datetime
import json

from constants import MACROPATH

try:
    with open(f"{MACROPATH}\\settings.json", "r", encoding="utf-8") as f:
        _ = json.load(f)
        TGIFRIDAY = _["use_alternate_uinav"]
except Exception as e:
    print(f"Error loading alt paths option: {e}")
    TGIFRIDAY =  True


def load_keybind() -> str:
    try:
        with open(f"{MACROPATH}\\settings.json", "r", encoding="utf-8") as f:
            return json.load(f)["enable_ui_nav_key"]
    except Exception as e:
        return "#"
    
def load_delay() -> int:
    try:
        with open(f"{MACROPATH}\\settings.json", "r", encoding="utf-8") as f:
            return json.load(f)["delay"]
    except Exception as e:
        return 0.05

def open_inventory(kb, disable_ui_nav_after : bool):

    ui_nav_key = load_keybind()
    delay = load_delay()

    kb.press(ui_nav_key)
    time.sleep(delay)
    kb.release(ui_nav_key)
    time.sleep(delay)

    if TGIFRIDAY:
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    else:

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)
        
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)
        
        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)
        
        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def open_storage(kb, disable_ui_nav_after : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    kb.press(ui_nav_key)
    time.sleep(delay)
    kb.release(ui_nav_key)
    time.sleep(delay)

    if TGIFRIDAY:
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)
        
    else:
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)
        
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)
        
        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)
        
        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)
        
        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def close_menu(kb, disable_ui_nav_after : bool, enable_before = True, is_merchant = False):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:
        if not is_merchant:
            kb.press(Key.left)
            time.sleep(delay)
            kb.release(Key.left)
            time.sleep(delay)

            kb.press(Key.right)
            time.sleep(delay)
            kb.release(Key.right)
            time.sleep(delay)

            kb.press(Key.up)
            time.sleep(delay)
            kb.release(Key.up)
            time.sleep(delay)
        else:
            kb.press(Key.down)
            time.sleep(delay)
            kb.release(Key.down)
            time.sleep(delay)

    else:        

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def merchant_skip_dialogue(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:
        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def close_check(kb, disable_ui_nav_after : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    kb.press(ui_nav_key)
    time.sleep(delay)
    kb.release(ui_nav_key)
    time.sleep(delay)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)
    
    else:

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)
    
    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def collection_align(kb, disable_ui_nav_after : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    kb.press(ui_nav_key)
    time.sleep(delay)
    kb.release(ui_nav_key)
    time.sleep(delay)

    if TGIFRIDAY:
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(1)

        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(0.5)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    else:

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)
        
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)
        
        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)
        
        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)
        
        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(2)

        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(2)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(2)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def search_in_menu(kb, disable_ui_nav_after : bool, enable_before : bool, is_inventory : bool, clear_field : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:

        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(0.5)

        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.right)
        time.sleep(delay)
        kb.release(Key.right)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    else:    
        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        if is_inventory:
            kb.press(Key.up)
            time.sleep(delay)
            kb.release(Key.up)
            time.sleep(delay)

            kb.press(Key.up)
            time.sleep(delay)
            kb.release(Key.up)
            time.sleep(delay)

        kb.press(Key.right)
        time.sleep(delay)
        kb.release(Key.right)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    if clear_field:

        if not is_inventory:
            kb.press(Key.backspace)
            time.sleep(delay)
            kb.release(Key.backspace)
            time.sleep(delay)
            
        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def select_item(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)
        
    else:
        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def open_mari(kb, disable_ui_nav_after : bool, enable_before : bool): # also works for jester exchange
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)
        
    else:
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def open_jester_shop(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    
    if TGIFRIDAY:

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    else:

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def open_jester_ex(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    
    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    else:

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def buy_item(kb, disable_ui_nav_after : bool, enable_before : bool, amount : int, box_pos):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)
        
    else:
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

    kb.press(Key.down)
    time.sleep(delay)
    kb.release(Key.down)
    time.sleep(delay)

    match box_pos:

        case 1:
            kb.press(Key.left)
            time.sleep(delay)
            kb.release(Key.left)
            time.sleep(delay)

            kb.press(Key.left)
            time.sleep(delay)
            kb.release(Key.left)
            time.sleep(delay)

            kb.press(Key.left)
            time.sleep(delay)
            kb.release(Key.left)
            time.sleep(delay)

            kb.press(Key.left)
            time.sleep(delay)
            kb.release(Key.left)
            time.sleep(delay)

        case 2:
            kb.press(Key.left)
            time.sleep(delay)
            kb.release(Key.left)
            time.sleep(delay)
            
            kb.press(Key.left)
            time.sleep(delay)
            kb.release(Key.left)
            time.sleep(delay)

            kb.press(Key.left)
            time.sleep(delay)
            kb.release(Key.left)
            time.sleep(delay)
        
        case 3:
            kb.press(Key.left)
            time.sleep(delay)
            kb.release(Key.left)
            time.sleep(delay)

            kb.press(Key.left)
            time.sleep(delay)
            kb.release(Key.left)
            time.sleep(delay)

        case 4:

            kb.press(Key.left)
            time.sleep(delay)
            kb.release(Key.left)
            time.sleep(delay)

        case 5:
            pass
    
    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(0.5)

    kb.press(ui_nav_key)
    time.sleep(delay)
    kb.release(ui_nav_key)
    time.sleep(1)

    kb.press(ui_nav_key)
    time.sleep(delay)
    kb.release(ui_nav_key)
    time.sleep(delay)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)
    else:
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    kb.press(Key.ctrl)
    kb.press("a")
    time.sleep(delay)
    kb.release("a")
    kb.release(Key.ctrl)
    time.sleep(delay)
    pag.write(str(amount))
    time.sleep(0.5)
    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(0.5)

    kb.press(Key.down)
    time.sleep(delay)
    kb.release(Key.down)
    time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(0.5)


def jester_exchange_first(kb, disable_ui_nav_after : bool, enable_before : bool, amount : int):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)
    else:
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)
        
    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    kb.press(Key.up)
    time.sleep(delay)
    kb.release(Key.up)
    time.sleep(delay)

    kb.press(Key.up)
    time.sleep(delay)
    kb.release(Key.up)
    time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    kb.press(Key.ctrl)
    kb.press("a")
    time.sleep(delay)
    kb.release("a")
    kb.release(Key.ctrl)
    time.sleep(delay)
    pag.write(str(amount))
    time.sleep(delay)
    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    kb.press(Key.down)
    time.sleep(delay)
    kb.release(Key.down)
    time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def jester_exchange_second(kb, disable_ui_nav_after : bool, enable_before : bool, amount : int):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.right)
        time.sleep(delay)
        kb.release(Key.right)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)
    else:
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.right)
        time.sleep(delay)
        kb.release(Key.right)
        time.sleep(delay)

    kb.press(Key.up)
    time.sleep(delay)
    kb.release(Key.up)
    time.sleep(delay)

    kb.press(Key.up)
    time.sleep(delay)
    kb.release(Key.up)
    time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    kb.press(Key.ctrl)
    kb.press("a")
    time.sleep(delay)
    kb.release("a")
    kb.release(Key.ctrl)
    time.sleep(delay)
    pag.write(str(amount))
    time.sleep(delay)
    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    kb.press(Key.down)
    time.sleep(delay)
    kb.release(Key.down)
    time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def change_rolling_cutscene(kb, disable_ui_nav_after : bool, enable_before : bool, new_rarity : int):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    kb.press(Key.left)
    time.sleep(delay)
    kb.release(Key.left)
    time.sleep(delay)

    kb.press(Key.left)
    time.sleep(delay)
    kb.release(Key.left)
    time.sleep(delay)

    kb.press(Key.left)
    time.sleep(delay)
    kb.release(Key.left)
    time.sleep(delay)
    
    kb.press(Key.left)
    time.sleep(delay)
    kb.release(Key.left)
    time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    kb.press(Key.right)
    time.sleep(delay)
    kb.release(Key.right)
    time.sleep(delay)

    kb.press(Key.up)
    time.sleep(delay)
    kb.release(Key.up)
    time.sleep(delay)

    kb.press(Key.up)
    time.sleep(delay)
    kb.release(Key.up)
    time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    kb.press(ui_nav_key)
    time.sleep(delay)
    kb.release(ui_nav_key)
    time.sleep(1)

    kb.press(ui_nav_key)
    time.sleep(delay)
    kb.release(ui_nav_key)
    time.sleep(1)

    kb.press(Key.left)
    time.sleep(delay)
    kb.release(Key.left)
    time.sleep(delay)

    kb.press(Key.left)
    time.sleep(delay)
    kb.release(Key.left)
    time.sleep(delay)

    kb.press(Key.left)
    time.sleep(delay)
    kb.release(Key.left)
    time.sleep(delay)
    
    kb.press(Key.left)
    time.sleep(delay)
    kb.release(Key.left)
    time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    kb.press(Key.down)
    time.sleep(delay)
    kb.release(Key.down)
    time.sleep(delay)

    kb.press(Key.down)
    time.sleep(delay)
    kb.release(Key.down)
    time.sleep(delay)

    kb.press(Key.down)
    time.sleep(delay)
    kb.release(Key.down)
    time.sleep(delay)

    kb.press(Key.down)
    time.sleep(delay)
    kb.release(Key.down)
    time.sleep(delay)

    kb.press(Key.down)
    time.sleep(delay)
    kb.release(Key.down)
    time.sleep(delay)

    kb.press(Key.down)
    time.sleep(delay)
    kb.release(Key.down)
    time.sleep(delay)

    kb.press(Key.down)
    time.sleep(delay)
    kb.release(Key.down)
    time.sleep(delay)

    kb.press(Key.down)
    time.sleep(delay)
    kb.release(Key.down)
    time.sleep(delay)

    kb.press(Key.down)
    time.sleep(delay)
    kb.release(Key.down)
    time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    time.sleep(delay)
    pag.write(str(new_rarity))
    time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def search_for_potion_in_cauldron(kb, disable_ui_nav_after : bool, enable_before : bool, potion_name):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    time.sleep(1)
    kb.press('f')
    time.sleep(0.2)
    kb.release('f')
    time.sleep(1)

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)
    
    if TGIFRIDAY:

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

        time.sleep(0.2)
        pag.write(potion_name, delay)
        time.sleep(0.3)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(1)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    else:

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

        time.sleep(0.2)
        pag.write(potion_name, delay)
        time.sleep(0.3)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(1)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)
        
        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def press_craft_button(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)
    else:

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def press_auto_button(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)
        
    else:
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def accept_quest(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)
    else:

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def dismiss_quest(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)
    
    else:

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.right)
        time.sleep(delay)
        kb.release(Key.right)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def next_quest(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)
    else:
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def exit_quest(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)
    else:
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def search_for_aura(kb, disable_ui_nav_after : bool, enable_before : bool, aura : str):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

    else:    
    
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

    kb.press(Key.backspace)
    time.sleep(delay)
    kb.release(Key.backspace)
    time.sleep(delay)

    time.sleep(0.2)
    pag.write(aura, delay)
    time.sleep(0.3)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(1)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def equip_selected_aura(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()
    
    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(1)

        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(1)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.right)
        time.sleep(delay)
        kb.release(Key.right)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(1)

        close_menu(kb, True, True, True)
        
    else:
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

        kb.press(Key.up)
        time.sleep(delay)
        kb.release(Key.up)
        time.sleep(delay)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(delay)

        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(1)

        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(1)

        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        kb.press(Key.enter)
        time.sleep(delay)
        kb.release(Key.enter)
        time.sleep(1)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def leave_roblox_server(kb):
    
    delay = load_delay()

    kb.press(Key.esc)
    time.sleep(delay)
    kb.release(Key.esc)
    time.sleep(delay)

    kb.press("l")
    time.sleep(delay)
    kb.release("l")
    time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(delay)

def add_amount_to_potion(kb, disable_ui_nav_after : bool, enable_before : bool, amount : int, extra_clicks = 0, from_bottom = False):
    
    ui_nav_key = load_keybind()
    delay = load_delay()
    
    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)

        if not from_bottom:
            
            kb.press(Key.left)
            time.sleep(delay)
            kb.release(Key.left)
            time.sleep(delay)

            kb.press(Key.down)
            time.sleep(delay)
            kb.release(Key.down)
            time.sleep(delay)

            for _ in range(0, extra_clicks):
                kb.press(Key.down)
                time.sleep(delay)
                kb.release(Key.down)
                time.sleep(delay)

            kb.press(Key.enter)
            time.sleep(delay)
            kb.release(Key.enter)
            time.sleep(0.1)

            kb.press(Key.ctrl)
            kb.press("a")
            time.sleep(delay)
            kb.release("a")
            kb.release(Key.ctrl)
            time.sleep(delay)
            pag.write(str(amount))
            time.sleep(delay)
            kb.press(Key.enter)
            time.sleep(delay)
            kb.release(Key.enter)
            time.sleep(0.1)

            kb.press(Key.right)
            time.sleep(delay)
            kb.release(Key.right)
            time.sleep(delay)

            kb.press(Key.enter)
            time.sleep(delay)
            kb.release(Key.enter)
            time.sleep(0.1)

        else:

            for _ in range(0, extra_clicks):
                kb.press(Key.down)
                time.sleep(delay)
                kb.release(Key.down)
                time.sleep(delay)

            kb.press(Key.down)
            time.sleep(delay)
            kb.release(Key.down)
            time.sleep(delay)
    
    else:
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

        if not from_bottom:
            kb.press(Key.left)
            time.sleep(delay)
            kb.release(Key.left)
            time.sleep(delay)

            kb.press(Key.left)
            time.sleep(delay)
            kb.release(Key.left)
            time.sleep(delay)

            for _ in range(0, extra_clicks):
                kb.press(Key.down)
                time.sleep(delay)
                kb.release(Key.down)
                time.sleep(delay)

            kb.press(Key.left)
            time.sleep(delay)
            kb.release(Key.left)
            time.sleep(delay)

            kb.press(Key.enter)
            time.sleep(delay)
            kb.release(Key.enter)
            time.sleep(0.1)

            kb.press(Key.ctrl)
            kb.press("a")
            time.sleep(delay)
            kb.release("a")
            kb.release(Key.ctrl)
            time.sleep(delay)
            pag.write(str(amount))
            time.sleep(delay)
            kb.press(Key.enter)
            time.sleep(delay)
            kb.release(Key.enter)
            time.sleep(0.1)

            kb.press(Key.right)
            time.sleep(delay)
            kb.release(Key.right)
            time.sleep(delay)

            kb.press(Key.enter)
            time.sleep(delay)
            kb.release(Key.enter)
            time.sleep(0.1)
        
        else:
            kb.press(Key.down)
            time.sleep(delay)
            kb.release(Key.down)
            time.sleep(delay)

            kb.press(Key.down)
            time.sleep(delay)
            kb.release(Key.down)
            time.sleep(delay)

            kb.press(Key.down)
            time.sleep(delay)
            kb.release(Key.down)
            time.sleep(delay)

            kb.press(Key.down)
            time.sleep(delay)
            kb.release(Key.down)
            time.sleep(delay)

            kb.press(Key.up)
            time.sleep(delay)
            kb.release(Key.up)
            time.sleep(delay)

            kb.press(Key.up)
            time.sleep(delay)
            kb.release(Key.up)
            time.sleep(delay)

            kb.press(Key.right)
            time.sleep(delay)
            kb.release(Key.right)
            time.sleep(delay)

            for _ in range(0, extra_clicks):
                kb.press(Key.up)
                time.sleep(delay)
                kb.release(Key.up)
                time.sleep(delay)

            kb.press(Key.left)
            time.sleep(delay)
            kb.release(Key.left)
            time.sleep(delay)

            kb.press(Key.enter)
            time.sleep(delay)
            kb.release(Key.enter)
            time.sleep(0.1)

            kb.press(Key.ctrl)
            kb.press("a")
            time.sleep(delay)
            kb.release("a")
            kb.release(Key.ctrl)
            time.sleep(delay)
            pag.write(str(amount))
            time.sleep(delay)
            kb.press(Key.enter)
            time.sleep(delay)
            kb.release(Key.enter)
            time.sleep(0.1)

            kb.press(Key.right)
            time.sleep(delay)
            kb.release(Key.right)
            time.sleep(delay)

            kb.press(Key.enter)
            time.sleep(delay)
            kb.release(Key.enter)
            time.sleep(0.1)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)


def press_fish_button(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    kb.press(Key.left)
    time.sleep(delay)
    kb.release(Key.left)
    time.sleep(delay)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

def accept_contract(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    kb.press(Key.left)
    time.sleep(delay)
    kb.release(Key.left)
    time.sleep(delay)
    
    kb.press(Key.left)
    time.sleep(delay)
    kb.release(Key.left)
    time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(0.1)


    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)


def close_cauldron(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()
    delay = load_delay()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(delay)
        kb.release(Key.down)
        time.sleep(delay)
        
    else:
        kb.press(Key.left)
        time.sleep(delay)
        kb.release(Key.left)
        time.sleep(delay)

    kb.press(Key.enter)
    time.sleep(delay)
    kb.release(Key.enter)
    time.sleep(0.1)


    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(delay)
        kb.release(ui_nav_key)
        time.sleep(delay)


def run_uinav_path(kb, text : str, path : str):

    ui_nav_key = load_keybind()
    delay = load_delay()

    for char in path:

        match char:

            case "#":
                kb.press(ui_nav_key)
                time.sleep(delay)
                kb.release(ui_nav_key)
                time.sleep(delay)

            case "u":
                kb.press(Key.up)
                time.sleep(delay)
                kb.release(Key.up)
                time.sleep(delay)

            case "d":
                kb.press(Key.down)
                time.sleep(delay)
                kb.release(Key.down)
                time.sleep(delay)

            case "l":
                kb.press(Key.left)
                time.sleep(delay)
                kb.release(Key.left)
                time.sleep(delay)

            case "r":
                kb.press(Key.right)
                time.sleep(delay)
                kb.release(Key.right)
                time.sleep(delay)

            case "e":
                kb.press(Key.enter)
                time.sleep(delay)
                kb.release(Key.enter)
                time.sleep(delay)

            case "t":
                kb.press(Key.ctrl)
                kb.press("a")
                time.sleep(delay)
                kb.release("a")
                kb.release(Key.ctrl)
                time.sleep(delay)
                pag.write(str(text))
                time.sleep(delay)
                kb.press(Key.enter)
                time.sleep(delay)
                kb.release(Key.enter)
                time.sleep(0.1)