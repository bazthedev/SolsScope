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
import mousekey as mk
from pynput import keyboard
import cv2
from PIL import Image
import numpy as np
from collections import namedtuple
import json

from constants import ASSETDIR, COORDS, CALIBDIR

Box = namedtuple("Box", ["left", "top", "width", "height"])


def load_calibrations() -> dict:
    with open(CALIBDIR, "r") as f:
        return json.load(f)
    
def load_calibration(calibration):
    return load_calibrations().get(calibration)

def scale_w_by_scr(x):

    return int((x/2560) * COORDS["scr_wid"])

def scale_h_by_scr(y):

    return int((y/1440) * COORDS["scr_hei"])

def locate_on_screen_scaled(img_path, confidence=0.7, scales=None):
    if scales is None:
        scales = [1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5]

    screenshot = pag.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    template = cv2.imread(img_path)
    if template is None:
        raise FileNotFoundError(f"Could not load template image: {img_path}")
    h, w = template.shape[:2]

    best_match = None
    best_val = 0

    for scale in scales:
        resized = cv2.resize(template, (int(w * scale), int(h * scale)))
        res = cv2.matchTemplate(screenshot, resized, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val > best_val:
            best_val = max_val
            best_match = (max_loc, resized.shape[:2])

    if best_match and best_val >= confidence:
        top_left, (h_scaled, w_scaled) = best_match
        return Box(left=top_left[0], top=top_left[1], width=w_scaled, height=h_scaled)

    return None

def wait_for(img_path, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        if locate_on_screen_scaled(img_path, confidence=0.8):
            return True
        time.sleep(0.2)
    return False

def handle_chat(mkey : mk.MouseKey, kb : keyboard.Controller):
    try:
        if not wait_for(f"{ASSETDIR}/chat.png", 10):
            raise pag.ImageNotFoundException
        
        chat_icon = locate_on_screen_scaled(f"{ASSETDIR}/chat.png", confidence=0.85)
        if chat_icon:
            x, y = pag.center(chat_icon)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

    except Exception:
        pass

def _use_item(mkey : mk.MouseKey, kb : keyboard.Controller, item : str, amt : int):
    
    try:
        if not wait_for(f"{ASSETDIR}/inv.png", 10):
            raise pag.ImageNotFoundException
        
        box_icon = locate_on_screen_scaled(f"{ASSETDIR}/inv.png", confidence=0.8)
        if box_icon:
            x, y = pag.center(box_icon)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        if not wait_for(f"{ASSETDIR}/items.png", 10):
            raise pag.ImageNotFoundException
        
        items_btn = locate_on_screen_scaled(f"{ASSETDIR}/items.png", confidence=0.8)
        if items_btn:
            x, y = pag.center(items_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
        
        if not wait_for(f"{ASSETDIR}/search.png", 10):
            raise pag.ImageNotFoundException
        
        search_icon = locate_on_screen_scaled(f"{ASSETDIR}/search.png", confidence=0.8)
        if search_icon:
            x, y = pag.center(search_icon)
            
            mkey.left_click_xy_natural(x + scale_w_by_scr(50), y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
        pag.write(item)
        time.sleep(1)

        kb.press(keyboard.Key.enter)
        time.sleep(0.2)
        kb.release(keyboard.Key.enter)

        time.sleep(0.2)
        mkey.left_click_xy_natural(x + scale_w_by_scr(50), y + scale_h_by_scr(100))
        time.sleep(0.2)

        if not wait_for(f"{ASSETDIR}/use.png", 10):
            raise pag.ImageNotFoundException

        amt_btn = locate_on_screen_scaled(f"{ASSETDIR}/use.png", confidence=0.8)
        if amt_btn:
            x, y =pag.center(amt_btn)
            
            mkey.left_click_xy_natural(x - scale_w_by_scr(150), y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        kb.press(keyboard.Key.ctrl)
        kb.press("a")
        time.sleep(0.2)
        kb.release("a")
        kb.release(keyboard.Key.ctrl)
        time.sleep(0.2)
        pag.write(str(amt))
        time.sleep(0.5)
        kb.press(keyboard.Key.enter)
        time.sleep(0.2)
        kb.release(keyboard.Key.enter)
        time.sleep(1)

        if not wait_for(f"{ASSETDIR}/use.png", 10):
            raise pag.ImageNotFoundException
        
        use_btn = locate_on_screen_scaled(f"{ASSETDIR}/use.png", confidence=0.8)
        if use_btn:
            x, y = pag.center(use_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        close_btn = locate_on_screen_scaled(f"{ASSETDIR}/close.png", confidence=0.8)
        if close_btn:
            x, y = pag.center(close_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
    
    except Exception:
        try:
            close_btn = locate_on_screen_scaled(f"{ASSETDIR}/close.png", confidence=0.8)
            if close_btn:
                x, y = pag.center(close_btn)
                
                mkey.left_click_xy_natural(x, y)
            else:
                return
            
            time.sleep(1)
        except Exception:
            pass

def use_merchant_tp(mkey : mk.MouseKey, kb : keyboard.Controller):
    
    try:
        if not wait_for(f"{ASSETDIR}/inv.png", 10):
            raise pag.ImageNotFoundException
        
        box_icon = locate_on_screen_scaled(f"{ASSETDIR}/inv.png", confidence=0.8)
        if box_icon:
            x, y = pag.center(box_icon)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        if not wait_for(f"{ASSETDIR}/items.png", 10):
            raise pag.ImageNotFoundException
        
        items_btn = locate_on_screen_scaled(f"{ASSETDIR}/items.png", confidence=0.8)
        if items_btn:
            x, y = pag.center(items_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
        
        if not wait_for(f"{ASSETDIR}/search.png", 10):
            raise pag.ImageNotFoundException
        
        search_icon = locate_on_screen_scaled(f"{ASSETDIR}/search.png", confidence=0.8)
        if search_icon:
            x, y = pag.center(search_icon)
            
            mkey.left_click_xy_natural(x + scale_w_by_scr(50), y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
        pag.write("Merchant Teleport")
        time.sleep(1)

        kb.press(keyboard.Key.enter)
        time.sleep(0.2)
        kb.release(keyboard.Key.enter)

        if not wait_for(f"{ASSETDIR}/mtp.png", 10):
            raise pag.ImageNotFoundException
        
        mtp = locate_on_screen_scaled(f"{ASSETDIR}/mtp.png", confidence=0.8)
        if mtp:
            x, y = pag.center(mtp)
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        amt_btn = locate_on_screen_scaled(f"{ASSETDIR}/use.png", confidence=0.8)
        if amt_btn:
            x, y =pag.center(amt_btn)
            
            mkey.left_click_xy_natural(x - scale_w_by_scr(150), y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        kb.press(keyboard.Key.ctrl)
        kb.press("a")
        time.sleep(0.2)
        kb.release("a")
        kb.release(keyboard.Key.ctrl)
        time.sleep(0.2)
        pag.write("1")
        time.sleep(0.5)
        kb.press(keyboard.Key.enter)
        time.sleep(0.2)
        kb.release(keyboard.Key.enter)
        time.sleep(1)

        if not wait_for(f"{ASSETDIR}/use.png", 10):
            raise pag.ImageNotFoundException
        
        use_btn = locate_on_screen_scaled(f"{ASSETDIR}/use.png", confidence=0.8)
        if use_btn:
            x, y = pag.center(use_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        close_btn = locate_on_screen_scaled(f"{ASSETDIR}/close.png", confidence=0.8)
        if close_btn:
            x, y = pag.center(close_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
    
    except Exception:
        try:
            close_btn = locate_on_screen_scaled(f"{ASSETDIR}/close.png", confidence=0.8)
            if close_btn:
                x, y = pag.center(close_btn)
                
                mkey.left_click_xy_natural(x, y)
            else:
                return
            
            time.sleep(1)
        except Exception:
            pass

def use_biome_random(mkey : mk.MouseKey, kb : keyboard.Controller):
    
    try:
        if not wait_for(f"{ASSETDIR}/inv.png", 10):
            raise pag.ImageNotFoundException
        
        box_icon = locate_on_screen_scaled(f"{ASSETDIR}/inv.png", confidence=0.8)
        if box_icon:
            x, y = pag.center(box_icon)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        if not wait_for(f"{ASSETDIR}/items.png", 10):
            raise pag.ImageNotFoundException
        
        items_btn = locate_on_screen_scaled(f"{ASSETDIR}/items.png", confidence=0.8)
        if items_btn:
            x, y = pag.center(items_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
        
        if not wait_for(f"{ASSETDIR}/search.png", 10):
            raise pag.ImageNotFoundException
        
        search_icon = locate_on_screen_scaled(f"{ASSETDIR}/search.png", confidence=0.8)
        if search_icon:
            x, y = pag.center(search_icon)
            
            mkey.left_click_xy_natural(x + scale_w_by_scr(50), y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
        pag.write("Biome Random")
        time.sleep(1)

        kb.press(keyboard.Key.enter)
        time.sleep(0.2)
        kb.release(keyboard.Key.enter)

        if not wait_for(f"{ASSETDIR}/br.png", 10):
            raise pag.ImageNotFoundException
        
        mtp = locate_on_screen_scaled(f"{ASSETDIR}/br.png", confidence=0.8)
        if mtp:
            x, y = pag.center(mtp)
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        amt_btn = locate_on_screen_scaled(f"{ASSETDIR}/use.png", confidence=0.8)
        if amt_btn:
            x, y =pag.center(amt_btn)
            
            mkey.left_click_xy_natural(x - scale_w_by_scr(150), y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        kb.press(keyboard.Key.ctrl)
        kb.press("a")
        time.sleep(0.2)
        kb.release("a")
        kb.release(keyboard.Key.ctrl)
        time.sleep(0.2)
        pag.write("1")
        time.sleep(0.5)
        kb.press(keyboard.Key.enter)
        time.sleep(0.2)
        kb.release(keyboard.Key.enter)
        time.sleep(1)

        if not wait_for(f"{ASSETDIR}/use.png", 10):
            raise pag.ImageNotFoundException
        
        use_btn = locate_on_screen_scaled(f"{ASSETDIR}/use.png", confidence=0.8)
        if use_btn:
            x, y = pag.center(use_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        close_btn = locate_on_screen_scaled(f"{ASSETDIR}/close.png", confidence=0.8)
        if close_btn:
            x, y = pag.center(close_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
    
    except Exception:
        try:
            close_btn = locate_on_screen_scaled(f"{ASSETDIR}/close.png", confidence=0.8)
            if close_btn:
                x, y = pag.center(close_btn)
                
                mkey.left_click_xy_natural(x, y)
            else:
                return
            
            time.sleep(1)
        except Exception:
            pass

def use_strange_control(mkey : mk.MouseKey, kb : keyboard.Controller):
    
    try:
        if not wait_for(f"{ASSETDIR}/inv.png", 10):
            raise pag.ImageNotFoundException
        
        box_icon = locate_on_screen_scaled(f"{ASSETDIR}/inv.png", confidence=0.8)
        if box_icon:
            x, y = pag.center(box_icon)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        if not wait_for(f"{ASSETDIR}/items.png", 10):
            raise pag.ImageNotFoundException
        
        items_btn = locate_on_screen_scaled(f"{ASSETDIR}/items.png", confidence=0.8)
        if items_btn:
            x, y = pag.center(items_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
        
        if not wait_for(f"{ASSETDIR}/search.png", 10):
            raise pag.ImageNotFoundException
        
        search_icon = locate_on_screen_scaled(f"{ASSETDIR}/search.png", confidence=0.8)
        if search_icon:
            x, y = pag.center(search_icon)
            
            mkey.left_click_xy_natural(x + scale_w_by_scr(50), y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
        pag.write("Strange Control")
        time.sleep(1)

        kb.press(keyboard.Key.enter)
        time.sleep(0.2)
        kb.release(keyboard.Key.enter)

        if not wait_for(f"{ASSETDIR}/sc.png", 10):
            raise pag.ImageNotFoundException
        
        mtp = locate_on_screen_scaled(f"{ASSETDIR}/sc.png", confidence=0.8)
        if mtp:
            x, y = pag.center(mtp)
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        amt_btn = locate_on_screen_scaled(f"{ASSETDIR}/use.png", confidence=0.8)
        if amt_btn:
            x, y =pag.center(amt_btn)
            
            mkey.left_click_xy_natural(x - scale_w_by_scr(150), y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        kb.press(keyboard.Key.ctrl)
        kb.press("a")
        time.sleep(0.2)
        kb.release("a")
        kb.release(keyboard.Key.ctrl)
        time.sleep(0.2)
        pag.write("1")
        time.sleep(0.5)
        kb.press(keyboard.Key.enter)
        time.sleep(0.2)
        kb.release(keyboard.Key.enter)
        time.sleep(1)

        if not wait_for(f"{ASSETDIR}/use.png", 10):
            raise pag.ImageNotFoundException
        
        use_btn = locate_on_screen_scaled(f"{ASSETDIR}/use.png", confidence=0.8)
        if use_btn:
            x, y = pag.center(use_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        close_btn = locate_on_screen_scaled(f"{ASSETDIR}/close.png", confidence=0.8)
        if close_btn:
            x, y = pag.center(close_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
    
    except Exception:
        try:
            close_btn = locate_on_screen_scaled(f"{ASSETDIR}/close.png", confidence=0.8)
            if close_btn:
                x, y = pag.center(close_btn)
                
                mkey.left_click_xy_natural(x, y)
            else:
                return
            
            time.sleep(1)
        except Exception:
            pass

def use_portable_crack(mkey : mk.MouseKey, kb : keyboard.Controller):
    
    try:
        if not wait_for(f"{ASSETDIR}/inv.png", 10):
            raise pag.ImageNotFoundException
        
        box_icon = locate_on_screen_scaled(f"{ASSETDIR}/inv.png", confidence=0.8)
        if box_icon:
            x, y = pag.center(box_icon)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        if not wait_for(f"{ASSETDIR}/items.png", 10):
            raise pag.ImageNotFoundException
        
        items_btn = locate_on_screen_scaled(f"{ASSETDIR}/items.png", confidence=0.8)
        if items_btn:
            x, y = pag.center(items_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
        
        if not wait_for(f"{ASSETDIR}/search.png", 10):
            raise pag.ImageNotFoundException
        
        search_icon = locate_on_screen_scaled(f"{ASSETDIR}/search.png", confidence=0.8)
        if search_icon:
            x, y = pag.center(search_icon)
            
            mkey.left_click_xy_natural(x + scale_w_by_scr(50), y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
        pag.write("Portable Crack")
        time.sleep(1)

        kb.press(keyboard.Key.enter)
        time.sleep(0.2)
        kb.release(keyboard.Key.enter)

        if not wait_for(f"{ASSETDIR}/pc.png", 10):
            raise pag.ImageNotFoundException
        
        mtp = locate_on_screen_scaled(f"{ASSETDIR}/pc.png", confidence=0.8)
        if mtp:
            x, y = pag.center(mtp)
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        amt_btn = locate_on_screen_scaled(f"{ASSETDIR}/use.png", confidence=0.8)
        if amt_btn:
            x, y =pag.center(amt_btn)
            
            mkey.left_click_xy_natural(x - scale_w_by_scr(150), y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        kb.press(keyboard.Key.ctrl)
        kb.press("a")
        time.sleep(0.2)
        kb.release("a")
        kb.release(keyboard.Key.ctrl)
        time.sleep(0.2)
        pag.write("1")
        time.sleep(0.5)
        kb.press(keyboard.Key.enter)
        time.sleep(0.2)
        kb.release(keyboard.Key.enter)
        time.sleep(1)

        if not wait_for(f"{ASSETDIR}/use.png", 10):
            raise pag.ImageNotFoundException
        
        use_btn = locate_on_screen_scaled(f"{ASSETDIR}/use.png", confidence=0.8)
        if use_btn:
            x, y = pag.center(use_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        close_btn = locate_on_screen_scaled(f"{ASSETDIR}/close.png", confidence=0.8)
        if close_btn:
            x, y = pag.center(close_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
    
    except Exception:
        try:
            close_btn = locate_on_screen_scaled(f"{ASSETDIR}/close.png", confidence=0.8)
            if close_btn:
                x, y = pag.center(close_btn)
                
                mkey.left_click_xy_natural(x, y)
            else:
                return
            
            time.sleep(1)
        except Exception:
            pass

def close(mkey : mk.MouseKey, kb : keyboard.Controller):
    try:
        close_btn = locate_on_screen_scaled(f"{ASSETDIR}/close.png", confidence=0.8)
        if close_btn:
            x, y = pag.center(close_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            close_btn = locate_on_screen_scaled(f"{ASSETDIR}/close2.png", confidence=0.8)
            if close_btn:
                x, y = pag.center(close_btn)
                
                mkey.left_click_xy_natural(x, y)
            else:
                raise pag.ImageNotFoundException
            
            time.sleep(1)
        
        time.sleep(1)
    except Exception:
        close_btn = locate_on_screen_scaled(f"{ASSETDIR}/qbexit.png", confidence=0.8)
        if close_btn:
            x, y = pag.center(close_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            return
        
        time.sleep(1)

def open_inventory(mkey : mk.MouseKey, kb : keyboard.Controller):
    
    try:
        if not wait_for(f"{ASSETDIR}/inv.png", 10):
            raise pag.ImageNotFoundException
        
        box_icon = locate_on_screen_scaled(f"{ASSETDIR}/inv.png", confidence=0.8)
        if box_icon:
            x, y = pag.center(box_icon)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        if not wait_for(f"{ASSETDIR}/items.png", 10):
            raise pag.ImageNotFoundException
        
        items_btn = locate_on_screen_scaled(f"{ASSETDIR}/items.png", confidence=0.8)
        if items_btn:
            x, y = pag.center(items_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
        
        if not wait_for(f"{ASSETDIR}/search.png", 10):
            raise pag.ImageNotFoundException
        
        search_icon = locate_on_screen_scaled(f"{ASSETDIR}/search.png", confidence=0.8)
        if search_icon:
            x, y = pag.center(search_icon)
            
            mkey.left_click_xy_natural(x + scale_w_by_scr(50), y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
    
    except Exception:
        try:
            close_btn = locate_on_screen_scaled(f"{ASSETDIR}/close.png", confidence=0.8)
            if close_btn:
                x, y = pag.center(close_btn)
                
                mkey.left_click_xy_natural(x, y)
            else:
                return
            
            time.sleep(1)
        except Exception:
            pass

def open_storage(mkey : mk.MouseKey, kb : keyboard.Controller):

    """try:
        handle_chat(mkey, kb)
    except Exception:
        pass"""
    
    try:
        if not wait_for(f"{ASSETDIR}/stor.png", 10):
            raise pag.ImageNotFoundException
        
        box_icon = locate_on_screen_scaled(f"{ASSETDIR}/stor.png", confidence=0.8)
        if box_icon:
            x, y = pag.center(box_icon)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
        
        if not wait_for(f"{ASSETDIR}/search.png", 10):
            raise pag.ImageNotFoundException
        
        search_icon = locate_on_screen_scaled(f"{ASSETDIR}/search.png", confidence=0.8)
        if search_icon:
            x, y = pag.center(search_icon)
            
            mkey.left_click_xy_natural(x + scale_w_by_scr(50), y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)
    
    except Exception:
        try:
            close_btn = locate_on_screen_scaled(f"{ASSETDIR}/close2.png", confidence=0.8)
            if close_btn:
                x, y = pag.center(close_btn)
                
                mkey.left_click_xy_natural(x, y)
            else:
                return
            
            time.sleep(1)
        except Exception:
            pass

def qb_left(mkey : mk.MouseKey, kb : keyboard.Controller):
    
    try:

        qbleft_btn = locate_on_screen_scaled(f"{ASSETDIR}/qbl.png", confidence=0.8)
        if qbleft_btn:
            x, y = pag.center(qbleft_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

    except Exception:
        try:
            close_btn = locate_on_screen_scaled(f"{ASSETDIR}/qbexit.png", confidence=0.8)
            if close_btn:
                x, y = pag.center(close_btn)
                
                mkey.left_click_xy_natural(x, y)
            else:
                return
            
            time.sleep(1)
        except Exception:
            pass

def qb_right(mkey : mk.MouseKey, kb : keyboard.Controller):
    
    try:

        qbright_btn = locate_on_screen_scaled(f"{ASSETDIR}/qbr.png", confidence=0.8)
        if qbright_btn:
            x, y = pag.center(qbright_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

    except Exception:
        try:
            close_btn = locate_on_screen_scaled(f"{ASSETDIR}/qbexit.png", confidence=0.8)
            if close_btn:
                x, y = pag.center(close_btn)
                
                mkey.left_click_xy_natural(x, y)
            else:
                return
            
            time.sleep(1)
        except Exception:
            pass

def qb_accept(mkey : mk.MouseKey, kb : keyboard.Controller):
    
    try:

        qbright_btn = locate_on_screen_scaled(f"{ASSETDIR}/qbacc.png", confidence=0.8)
        if qbright_btn:
            x, y = pag.center(qbright_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            qbright_btn = locate_on_screen_scaled(f"{ASSETDIR}/qbclaim.png", confidence=0.8)
            if qbright_btn:
                x, y = pag.center(qbright_btn)
                
                mkey.left_click_xy_natural(x, y)
            else:
                raise pag.ImageNotFoundException
        
        time.sleep(1)

    except Exception:
        try:
            close_btn = locate_on_screen_scaled(f"{ASSETDIR}/qbexit.png", confidence=0.8)
            if close_btn:
                x, y = pag.center(close_btn)
                
                mkey.left_click_xy_natural(x, y)
            else:
                return
            
            time.sleep(1)
        except Exception:
            pass

def qb_dismiss(mkey : mk.MouseKey, kb : keyboard.Controller):
    
    try:

        qbright_btn = locate_on_screen_scaled(f"{ASSETDIR}/qbdis.png", confidence=0.8)
        if qbright_btn:
            x, y = pag.center(qbright_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

    except Exception:
        try:
            close_btn = locate_on_screen_scaled(f"{ASSETDIR}/qbexit.png", confidence=0.8)
            if close_btn:
                x, y = pag.center(close_btn)
                
                mkey.left_click_xy_natural(x, y)
            else:
                return
            
            time.sleep(1)
        except Exception:
            pass

def collection_align(mkey : mk.MouseKey, kb : keyboard.Controller):

    #handle_chat(mkey, kb)

    try:

        qbright_btn = locate_on_screen_scaled(f"{ASSETDIR}/col.png", confidence=0.8)
        if qbright_btn:
            x, y = pag.center(qbright_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

        qbright_btn = locate_on_screen_scaled(f"{ASSETDIR}/colexit.png", confidence=0.8)
        if qbright_btn:
            x, y = pag.center(qbright_btn)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        time.sleep(1)

    except Exception:
        try:
            close_btn = locate_on_screen_scaled(f"{ASSETDIR}/colexit.png", confidence=0.8)
            if close_btn:
                x, y = pag.center(close_btn)
                
                mkey.left_click_xy_natural(x, y)
            else:
                return
            
            time.sleep(1)
        except Exception:
            pass

def _equip_aura(mkey : mk.MouseKey, kb : keyboard.Controller, aura_name : str):

    try:
        open_storage(mkey, kb)
        time.sleep(0.2)
        pag.write(aura_name)
        time.sleep(0.2)
        kb.press(keyboard.Key.enter)
        time.sleep(0.2)
        kb.release(keyboard.Key.enter)

        search_icon = locate_on_screen_scaled(f"{ASSETDIR}/search.png", confidence=0.8)
        if search_icon:
            x, y = pag.center(search_icon)
            
            time.sleep(0.2)
            mkey.left_click_xy_natural(x + scale_w_by_scr(50), y + scale_h_by_scr(100))
            time.sleep(0.2)
        else:
            raise pag.ImageNotFoundException

        search_icon = locate_on_screen_scaled(f"{ASSETDIR}/equip.png", confidence=0.8)
        if search_icon:
            x, y = pag.center(search_icon)
            
            mkey.left_click_xy_natural(x, y)
        else:
            raise pag.ImageNotFoundException
        
        close(mkey, kb)
        
    except Exception:
        try:
            close_btn = locate_on_screen_scaled(f"{ASSETDIR}/close2.png", confidence=0.8)
            if close_btn:
                x, y = pag.center(close_btn)
                
                mkey.left_click_xy_natural(x, y)
            else:
                return
            
            time.sleep(1)
        except Exception:
            pass