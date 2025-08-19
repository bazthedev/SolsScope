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
    with open(f"{MACROPATH}\\settings.json", "r") as f:
        _ = json.load(f)
        TGIFRIDAY = _["use_alternate_uinav"]
except Exception as e:
    print(f"Error loading alt paths option: {e}")
    TGIFRIDAY =  True


def load_keybind() -> str:
    try:
        with open(f"{MACROPATH}\\settings.json", "r") as f:
            return json.load(f)["enable_ui_nav_key"]
    except Exception as e:
        return "#"

def open_inventory(kb, disable_ui_nav_after : bool):

    ui_nav_key = load_keybind()

    kb.press(ui_nav_key)
    time.sleep(0.05)
    kb.release(ui_nav_key)
    time.sleep(0.05)

    if TGIFRIDAY:
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    else:

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)
        
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)
        
        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)
        
        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def open_storage(kb, disable_ui_nav_after : bool):
    
    ui_nav_key = load_keybind()

    kb.press(ui_nav_key)
    time.sleep(0.05)
    kb.release(ui_nav_key)
    time.sleep(0.05)

    if TGIFRIDAY:
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)
        
    else:
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)
        
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)
        
        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)
        
        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)
        
        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def close_menu(kb, disable_ui_nav_after : bool, enable_before = True, is_merchant = False):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:
        if not is_merchant:
            kb.press(Key.left)
            time.sleep(0.05)
            kb.release(Key.left)
            time.sleep(0.05)

            kb.press(Key.right)
            time.sleep(0.05)
            kb.release(Key.right)
            time.sleep(0.05)

            kb.press(Key.up)
            time.sleep(0.05)
            kb.release(Key.up)
            time.sleep(0.05)
        else:
            kb.press(Key.down)
            time.sleep(0.05)
            kb.release(Key.down)
            time.sleep(0.05)

    else:        

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def merchant_skip_dialogue(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:
        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def close_check(kb, disable_ui_nav_after : bool):
    
    ui_nav_key = load_keybind()

    kb.press(ui_nav_key)
    time.sleep(0.05)
    kb.release(ui_nav_key)
    time.sleep(0.05)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)
    
    else:

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)
    
    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def collection_align(kb, disable_ui_nav_after : bool):
    
    ui_nav_key = load_keybind()

    kb.press(ui_nav_key)
    time.sleep(0.05)
    kb.release(ui_nav_key)
    time.sleep(0.05)

    if TGIFRIDAY:
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(1)

        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.5)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    else:

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)
        
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)
        
        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)
        
        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)
        
        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(2)

        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(2)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(2)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def search_in_menu(kb, disable_ui_nav_after : bool, enable_before : bool, is_inventory : bool, clear_field : bool):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:

        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.5)

        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.right)
        time.sleep(0.05)
        kb.release(Key.right)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    else:    
        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        if is_inventory:
            kb.press(Key.up)
            time.sleep(0.05)
            kb.release(Key.up)
            time.sleep(0.05)

            kb.press(Key.up)
            time.sleep(0.05)
            kb.release(Key.up)
            time.sleep(0.05)

        kb.press(Key.right)
        time.sleep(0.05)
        kb.release(Key.right)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    if clear_field:

        if not is_inventory:
            kb.press(Key.backspace)
            time.sleep(0.05)
            kb.release(Key.backspace)
            time.sleep(0.05)
            
        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def select_item(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)
        
    else:
        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def open_mari(kb, disable_ui_nav_after : bool, enable_before : bool): # also works for jester exchange
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)
        
    else:
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def open_jester_shop(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    
    if TGIFRIDAY:

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    else:

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def open_jester_ex(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    
    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    else:

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def buy_item(kb, disable_ui_nav_after : bool, enable_before : bool, amount : int, box_pos):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)
        
    else:
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

    kb.press(Key.down)
    time.sleep(0.05)
    kb.release(Key.down)
    time.sleep(0.05)

    match box_pos:

        case 1:
            kb.press(Key.left)
            time.sleep(0.05)
            kb.release(Key.left)
            time.sleep(0.05)

            kb.press(Key.left)
            time.sleep(0.05)
            kb.release(Key.left)
            time.sleep(0.05)

            kb.press(Key.left)
            time.sleep(0.05)
            kb.release(Key.left)
            time.sleep(0.05)

            kb.press(Key.left)
            time.sleep(0.05)
            kb.release(Key.left)
            time.sleep(0.05)

        case 2:
            kb.press(Key.left)
            time.sleep(0.05)
            kb.release(Key.left)
            time.sleep(0.05)
            
            kb.press(Key.left)
            time.sleep(0.05)
            kb.release(Key.left)
            time.sleep(0.05)

            kb.press(Key.left)
            time.sleep(0.05)
            kb.release(Key.left)
            time.sleep(0.05)
        
        case 3:
            kb.press(Key.left)
            time.sleep(0.05)
            kb.release(Key.left)
            time.sleep(0.05)

            kb.press(Key.left)
            time.sleep(0.05)
            kb.release(Key.left)
            time.sleep(0.05)

        case 4:

            kb.press(Key.left)
            time.sleep(0.05)
            kb.release(Key.left)
            time.sleep(0.05)

        case 5:
            pass
    
    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.5)

    kb.press(ui_nav_key)
    time.sleep(0.05)
    kb.release(ui_nav_key)
    time.sleep(1)

    kb.press(ui_nav_key)
    time.sleep(0.05)
    kb.release(ui_nav_key)
    time.sleep(0.05)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)
    else:
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    kb.press(Key.ctrl)
    kb.press("a")
    time.sleep(0.05)
    kb.release("a")
    kb.release(Key.ctrl)
    time.sleep(0.05)
    pag.write(str(amount))
    time.sleep(0.5)
    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.5)

    kb.press(Key.down)
    time.sleep(0.05)
    kb.release(Key.down)
    time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.5)


def jester_exchange_first(kb, disable_ui_nav_after : bool, enable_before : bool, amount : int):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)
    else:
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)
        
    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    kb.press(Key.up)
    time.sleep(0.05)
    kb.release(Key.up)
    time.sleep(0.05)

    kb.press(Key.up)
    time.sleep(0.05)
    kb.release(Key.up)
    time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    kb.press(Key.ctrl)
    kb.press("a")
    time.sleep(0.05)
    kb.release("a")
    kb.release(Key.ctrl)
    time.sleep(0.05)
    pag.write(str(amount))
    time.sleep(0.05)
    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    kb.press(Key.down)
    time.sleep(0.05)
    kb.release(Key.down)
    time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def jester_exchange_second(kb, disable_ui_nav_after : bool, enable_before : bool, amount : int):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.right)
        time.sleep(0.05)
        kb.release(Key.right)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)
    else:
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.right)
        time.sleep(0.05)
        kb.release(Key.right)
        time.sleep(0.05)

    kb.press(Key.up)
    time.sleep(0.05)
    kb.release(Key.up)
    time.sleep(0.05)

    kb.press(Key.up)
    time.sleep(0.05)
    kb.release(Key.up)
    time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    kb.press(Key.ctrl)
    kb.press("a")
    time.sleep(0.05)
    kb.release("a")
    kb.release(Key.ctrl)
    time.sleep(0.05)
    pag.write(str(amount))
    time.sleep(0.05)
    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    kb.press(Key.down)
    time.sleep(0.05)
    kb.release(Key.down)
    time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def change_rolling_cutscene(kb, disable_ui_nav_after : bool, enable_before : bool, new_rarity : int):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    kb.press(Key.left)
    time.sleep(0.05)
    kb.release(Key.left)
    time.sleep(0.05)

    kb.press(Key.left)
    time.sleep(0.05)
    kb.release(Key.left)
    time.sleep(0.05)

    kb.press(Key.left)
    time.sleep(0.05)
    kb.release(Key.left)
    time.sleep(0.05)
    
    kb.press(Key.left)
    time.sleep(0.05)
    kb.release(Key.left)
    time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    kb.press(Key.right)
    time.sleep(0.05)
    kb.release(Key.right)
    time.sleep(0.05)

    kb.press(Key.up)
    time.sleep(0.05)
    kb.release(Key.up)
    time.sleep(0.05)

    kb.press(Key.up)
    time.sleep(0.05)
    kb.release(Key.up)
    time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    kb.press(ui_nav_key)
    time.sleep(0.05)
    kb.release(ui_nav_key)
    time.sleep(1)

    kb.press(ui_nav_key)
    time.sleep(0.05)
    kb.release(ui_nav_key)
    time.sleep(1)

    kb.press(Key.left)
    time.sleep(0.05)
    kb.release(Key.left)
    time.sleep(0.05)

    kb.press(Key.left)
    time.sleep(0.05)
    kb.release(Key.left)
    time.sleep(0.05)

    kb.press(Key.left)
    time.sleep(0.05)
    kb.release(Key.left)
    time.sleep(0.05)
    
    kb.press(Key.left)
    time.sleep(0.05)
    kb.release(Key.left)
    time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    kb.press(Key.down)
    time.sleep(0.05)
    kb.release(Key.down)
    time.sleep(0.05)

    kb.press(Key.down)
    time.sleep(0.05)
    kb.release(Key.down)
    time.sleep(0.05)

    kb.press(Key.down)
    time.sleep(0.05)
    kb.release(Key.down)
    time.sleep(0.05)

    kb.press(Key.down)
    time.sleep(0.05)
    kb.release(Key.down)
    time.sleep(0.05)

    kb.press(Key.down)
    time.sleep(0.05)
    kb.release(Key.down)
    time.sleep(0.05)

    kb.press(Key.down)
    time.sleep(0.05)
    kb.release(Key.down)
    time.sleep(0.05)

    kb.press(Key.down)
    time.sleep(0.05)
    kb.release(Key.down)
    time.sleep(0.05)

    kb.press(Key.down)
    time.sleep(0.05)
    kb.release(Key.down)
    time.sleep(0.05)

    kb.press(Key.down)
    time.sleep(0.05)
    kb.release(Key.down)
    time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    time.sleep(0.05)
    pag.write(str(new_rarity))
    time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def search_for_potion_in_cauldron(kb, disable_ui_nav_after : bool, enable_before : bool, potion_name):
    
    ui_nav_key = load_keybind()

    time.sleep(1)
    kb.press('f')
    time.sleep(0.2)
    kb.release('f')
    time.sleep(1)

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)
    
    if TGIFRIDAY:

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

        time.sleep(0.2)
        pag.write(potion_name, 0.05)
        time.sleep(0.3)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(1)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    else:

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

        time.sleep(0.2)
        pag.write(potion_name, 0.05)
        time.sleep(0.3)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(1)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)
        
        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def press_craft_button(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)
    else:

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def press_auto_button(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)
        
    else:
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def accept_quest(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)
    else:

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def dismiss_quest(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)
    
    else:

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.right)
        time.sleep(0.05)
        kb.release(Key.right)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def next_quest(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)
    else:
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def exit_quest(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)
    else:
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def search_for_aura(kb, disable_ui_nav_after : bool, enable_before : bool, aura : str):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

    else:    
    
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

    kb.press(Key.backspace)
    time.sleep(0.05)
    kb.release(Key.backspace)
    time.sleep(0.05)

    time.sleep(0.2)
    pag.write(aura, 0.05)
    time.sleep(0.3)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(1)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def equip_selected_aura(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()
    
    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(1)

        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(1)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.right)
        time.sleep(0.05)
        kb.release(Key.right)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(1)

        close_menu(kb, True, True, True)
        
    else:
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

        kb.press(Key.up)
        time.sleep(0.05)
        kb.release(Key.up)
        time.sleep(0.05)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(0.05)

        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(1)

        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(1)

        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        kb.press(Key.enter)
        time.sleep(0.05)
        kb.release(Key.enter)
        time.sleep(1)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def leave_roblox_server(kb):

    kb.press(Key.esc)
    time.sleep(0.05)
    kb.release(Key.esc)
    time.sleep(0.05)

    kb.press("l")
    time.sleep(0.05)
    kb.release("l")
    time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.05)

def add_amount_to_potion(kb, disable_ui_nav_after : bool, enable_before : bool, amount : int, extra_clicks = 0, from_bottom = False):
    
    ui_nav_key = load_keybind()
    
    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)

        if not from_bottom:
            
            kb.press(Key.left)
            time.sleep(0.05)
            kb.release(Key.left)
            time.sleep(0.05)

            kb.press(Key.down)
            time.sleep(0.05)
            kb.release(Key.down)
            time.sleep(0.05)

            for _ in range(0, extra_clicks):
                kb.press(Key.down)
                time.sleep(0.05)
                kb.release(Key.down)
                time.sleep(0.05)

            kb.press(Key.enter)
            time.sleep(0.05)
            kb.release(Key.enter)
            time.sleep(0.1)

            kb.press(Key.ctrl)
            kb.press("a")
            time.sleep(0.05)
            kb.release("a")
            kb.release(Key.ctrl)
            time.sleep(0.05)
            pag.write(str(amount))
            time.sleep(0.05)
            kb.press(Key.enter)
            time.sleep(0.05)
            kb.release(Key.enter)
            time.sleep(0.1)

            kb.press(Key.right)
            time.sleep(0.05)
            kb.release(Key.right)
            time.sleep(0.05)

            kb.press(Key.enter)
            time.sleep(0.05)
            kb.release(Key.enter)
            time.sleep(0.1)

        else:

            for _ in range(0, extra_clicks):
                kb.press(Key.down)
                time.sleep(0.05)
                kb.release(Key.down)
                time.sleep(0.05)

            kb.press(Key.down)
            time.sleep(0.05)
            kb.release(Key.down)
            time.sleep(0.05)
    
    else:
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

        if not from_bottom:
            kb.press(Key.left)
            time.sleep(0.05)
            kb.release(Key.left)
            time.sleep(0.05)

            kb.press(Key.left)
            time.sleep(0.05)
            kb.release(Key.left)
            time.sleep(0.05)

            for _ in range(0, extra_clicks):
                kb.press(Key.down)
                time.sleep(0.05)
                kb.release(Key.down)
                time.sleep(0.05)

            kb.press(Key.left)
            time.sleep(0.05)
            kb.release(Key.left)
            time.sleep(0.05)

            kb.press(Key.enter)
            time.sleep(0.05)
            kb.release(Key.enter)
            time.sleep(0.1)

            kb.press(Key.ctrl)
            kb.press("a")
            time.sleep(0.05)
            kb.release("a")
            kb.release(Key.ctrl)
            time.sleep(0.05)
            pag.write(str(amount))
            time.sleep(0.05)
            kb.press(Key.enter)
            time.sleep(0.05)
            kb.release(Key.enter)
            time.sleep(0.1)

            kb.press(Key.right)
            time.sleep(0.05)
            kb.release(Key.right)
            time.sleep(0.05)

            kb.press(Key.enter)
            time.sleep(0.05)
            kb.release(Key.enter)
            time.sleep(0.1)
        
        else:
            kb.press(Key.down)
            time.sleep(0.05)
            kb.release(Key.down)
            time.sleep(0.05)

            kb.press(Key.down)
            time.sleep(0.05)
            kb.release(Key.down)
            time.sleep(0.05)

            kb.press(Key.down)
            time.sleep(0.05)
            kb.release(Key.down)
            time.sleep(0.05)

            kb.press(Key.down)
            time.sleep(0.05)
            kb.release(Key.down)
            time.sleep(0.05)

            kb.press(Key.up)
            time.sleep(0.05)
            kb.release(Key.up)
            time.sleep(0.05)

            kb.press(Key.up)
            time.sleep(0.05)
            kb.release(Key.up)
            time.sleep(0.05)

            kb.press(Key.right)
            time.sleep(0.05)
            kb.release(Key.right)
            time.sleep(0.05)

            for _ in range(0, extra_clicks):
                kb.press(Key.up)
                time.sleep(0.05)
                kb.release(Key.up)
                time.sleep(0.05)

            kb.press(Key.left)
            time.sleep(0.05)
            kb.release(Key.left)
            time.sleep(0.05)

            kb.press(Key.enter)
            time.sleep(0.05)
            kb.release(Key.enter)
            time.sleep(0.1)

            kb.press(Key.ctrl)
            kb.press("a")
            time.sleep(0.05)
            kb.release("a")
            kb.release(Key.ctrl)
            time.sleep(0.05)
            pag.write(str(amount))
            time.sleep(0.05)
            kb.press(Key.enter)
            time.sleep(0.05)
            kb.release(Key.enter)
            time.sleep(0.1)

            kb.press(Key.right)
            time.sleep(0.05)
            kb.release(Key.right)
            time.sleep(0.05)

            kb.press(Key.enter)
            time.sleep(0.05)
            kb.release(Key.enter)
            time.sleep(0.1)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)


def press_fish_button(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    kb.press(Key.left)
    time.sleep(0.05)
    kb.release(Key.left)
    time.sleep(0.05)

    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

def accept_contract(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    kb.press(Key.left)
    time.sleep(0.05)
    kb.release(Key.left)
    time.sleep(0.05)
    
    kb.press(Key.left)
    time.sleep(0.05)
    kb.release(Key.left)
    time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.1)


    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)


def close_cauldron(kb, disable_ui_nav_after : bool, enable_before : bool):
    
    ui_nav_key = load_keybind()

    if enable_before:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)

    if TGIFRIDAY:
        kb.press(Key.down)
        time.sleep(0.05)
        kb.release(Key.down)
        time.sleep(0.05)
        
    else:
        kb.press(Key.left)
        time.sleep(0.05)
        kb.release(Key.left)
        time.sleep(0.05)

    kb.press(Key.enter)
    time.sleep(0.05)
    kb.release(Key.enter)
    time.sleep(0.1)


    if disable_ui_nav_after:
        kb.press(ui_nav_key)
        time.sleep(0.05)
        kb.release(ui_nav_key)
        time.sleep(0.05)


def run_uinav_path(kb, text : str, path : str):

    ui_nav_key = load_keybind()

    for char in path:

        match char:

            case "#":
                kb.press(ui_nav_key)
                time.sleep(0.05)
                kb.release(ui_nav_key)
                time.sleep(0.05)

            case "u":
                kb.press(Key.up)
                time.sleep(0.05)
                kb.release(Key.up)
                time.sleep(0.05)

            case "d":
                kb.press(Key.down)
                time.sleep(0.05)
                kb.release(Key.down)
                time.sleep(0.05)

            case "l":
                kb.press(Key.left)
                time.sleep(0.05)
                kb.release(Key.left)
                time.sleep(0.05)

            case "r":
                kb.press(Key.right)
                time.sleep(0.05)
                kb.release(Key.right)
                time.sleep(0.05)

            case "e":
                kb.press(Key.enter)
                time.sleep(0.05)
                kb.release(Key.enter)
                time.sleep(0.05)

            case "t":
                kb.press(Key.ctrl)
                kb.press("a")
                time.sleep(0.05)
                kb.release("a")
                kb.release(Key.ctrl)
                time.sleep(0.05)
                pag.write(str(text))
                time.sleep(0.05)
                kb.press(Key.enter)
                time.sleep(0.05)
                kb.release(Key.enter)
                time.sleep(0.1)