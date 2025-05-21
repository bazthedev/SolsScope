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
import random
import pyautogui as pag
import json 
import threading 
from datetime import datetime
import discord 
import re
from PIL import ImageGrab

try:
    import cv2
    import pytesseract
    MERCHANT_DETECTION_POSSIBLE = True
except ImportError:
    MERCHANT_DETECTION_POSSIBLE = False
    print("Optional modules for Merchant Detection (cv2, pytesseract) not found. Feature disabled.")

from pynput import keyboard
from pynput import mouse

from constants import (
    MACROPATH, WEBHOOK_ICON_URL, MARI_ITEMS, JESTER_ITEMS,
    POSSIBLE_MERCHANTS, COORDS, LOCALVERSION, JESTER_SELL_ITEMS, COORDS_PERCENT,
    ACCEPTED_QUESTBOARD, QUESTBOARD_RARITY_COLOURS, PATH_DIR, ALL_QB, DONOTACCEPT_QB,
    COMPLETION_COLOURS
)
from utils import (
    get_logger, create_discord_file_from_path, hex2rgb, fuzzy_match,
    fuzzy_match_merchant, exists_procs_by_name, validate_pslink, fuzzy_match_auto_sell,
    fuzzy_match_qb, rgb2hex, right_click_drag, left_click_drag
)
from roblox_utils import (
    get_latest_equipped_aura, get_latest_hovertext, detect_client_disconnect,
    detect_client_reconnect, join_private_server_link, leave_main_menu,
    activate_ms_store_roblox, click_ms_store_spawn_button, toggle_fullscreen_ms_store,
    align_camera, reset_character
)
from discord_utils import forward_webhook_msg
from settings_manager import get_auras_path, get_biomes_path, get_merchant_path, get_questboard_path

from mmint import run_macro

def use_item(item_name: str, amount: int, close_menu: bool, mkey, kb, settings: dict):
    logger = get_logger()
    logger.write_log(f"Attempting to use item: {item_name} (Amount: {amount})")

    required_coords = [
        "inv_button_pos", "items_pos", "search_pos", "query_pos",
        "item_amt_pos", "use_pos", "close_pos"
    ]
    if not all(coord in COORDS for coord in required_coords):
        logger.write_log("Error using item: Required coordinates missing.")
        return

    try:
        wait_time = settings.get("global_wait_time", 0.2)
        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["inv_button_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["inv_button_pos"][1] * COORDS["scr_hei"])))
        time.sleep(wait_time)
        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["items_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["items_pos"][1] * COORDS["scr_hei"])))
        time.sleep(wait_time)
        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["search_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["search_pos"][1] * COORDS["scr_hei"])))
        time.sleep(wait_time)
        kb.type(item_name)
        time.sleep(wait_time + 0.2) 
        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["query_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["query_pos"][1] * COORDS["scr_hei"])))
        time.sleep(wait_time)
        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["item_amt_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["item_amt_pos"][1] * COORDS["scr_hei"])))
        time.sleep(wait_time)

        kb.press(keyboard.Key.ctrl)
        kb.press("a")
        time.sleep(0.05)
        kb.release("a")
        kb.release(keyboard.Key.ctrl)
        time.sleep(wait_time)
        kb.type(str(amount))
        time.sleep(wait_time)
        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["use_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["use_pos"][1] * COORDS["scr_hei"])))
        time.sleep(wait_time + 0.2) 

        if close_menu:
            mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
            time.sleep(wait_time)

            mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
            time.sleep(wait_time)
        logger.write_log(f"Used item: {item_name}")
    except Exception as e:
        logger.write_log(f"Error during use_item execution: {e}")

        try:
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
                time.sleep(wait_time)
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
        except Exception as close_e:
                logger.write_log(f"Error trying to close menu after item use error: {close_e}")

def aura_detection(settings: dict, webhook, stop_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb):
    logger = get_logger()
    logger.write_log("Aura Detection thread started.")

    try:
        with open(get_auras_path(), "r", encoding="utf-8") as f:
            auras = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        logger.write_log(f"Error loading auras data for detection: {e}. Aura detection stopped.")
        return

    try:
         with open(get_biomes_path(), "r", encoding="utf-8") as f:
             biomes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
         logger.write_log(f"Error loading biomes data for aura detection: {e}. Biome-specific rarity disabled.")
         biomes = {} 

    previous_aura = None

    try:
        previous_aura = get_latest_equipped_aura()
        logger.write_log(f"Initial aura state: {previous_aura}")
    except Exception as e:
         logger.write_log(f"Error getting initial aura state: {e}")

    while not stop_event.is_set():
        try:
            current_aura = get_latest_equipped_aura()
            if current_aura is None:
                time.sleep(2) 
                continue

            if previous_aura is None or current_aura == previous_aura:
                previous_aura = current_aura
                time.sleep(settings.get("global_wait_time", 0.2) + 0.5) 
                continue

            if current_aura == "In Main Menu":
                previous_aura = current_aura
                time.sleep(1)
                continue
            if settings.get("reset_aura", "") and current_aura == settings["reset_aura"]:
                 previous_aura = current_aura
                 time.sleep(1)
                 continue

            aura_key = current_aura.lower()
            if aura_key in auras:
                aura_data = auras[aura_key]
                logger.write_log(f"New aura detected: {current_aura}")
                previous_aura = current_aura 
                rnow = datetime.now()
                current_biome = get_latest_hovertext() or "Unknown"
                current_biome_key = current_biome.lower()
                base_rarity_str = aura_data.get("rarity", "0")

                description = f"**Rolled Aura:** {current_aura}\n"

                try:
                    base_rarity = int(base_rarity_str)
                    native_biome = aura_data.get("native_biome", "").lower()
                    biome_multiplier = 1.0
                    if current_biome_key == native_biome and current_biome_key in biomes:
                         biome_multiplier = biomes[current_biome_key].get("multiplier", 1.0)
                         if biome_multiplier > 0:
                             effective_rarity = int(base_rarity / biome_multiplier)
                             description += f"**Rarity:** 1 / {effective_rarity:,} (from {current_biome})\n"
                         else:
                             description += f"**Rarity:** 1 / {base_rarity:,} (Base)\n" 
                    else:
                         description += f"**Rarity:** 1 / {base_rarity:,} (Base)\n"

                    description += f"**Time:** <t:{str(int(time.time()))}>"
                    min_ping_val = int(settings.get("minimum_ping", "0"))
                    should_ping = settings.get("mention", False) and settings.get("mention_id", 0) != 0 and base_rarity >= min_ping_val

                except ValueError:
                    logger.write_log(f"Could not parse rarity '{base_rarity_str}' for {current_aura}.")
                    description += f"**Rarity:** {base_rarity_str} (Raw)\n"
                    description += f"**Time:** <t:{str(int(time.time()))}>"
                    should_ping = False
                
                emb_color_hex = aura_data.get("emb_colour", "#FFFFFF")
                emb_rgb = hex2rgb(emb_color_hex)
                emb = discord.Embed(
                    title=f"Aura Rolled: {current_aura}",
                    description=description,
                    colour=discord.Colour.from_rgb(*emb_rgb)
                )
                if img_url := aura_data.get("img_url", ""):
                    emb.set_thumbnail(url=img_url)
                if base_rarity > 99999998:
                    emb.set_footer(text=f"SolsScope v{LOCALVERSION}")

                file_to_send = None
                if settings.get("take_screenshot_on_detection", False):
                    screenshot_path = os.path.join(MACROPATH, "scr", "screenshot_aura.png")
                    try:
                        pag.screenshot(screenshot_path)
                        file_to_send = create_discord_file_from_path(screenshot_path, filename="aura.png")
                        if file_to_send:
                            emb.set_image(url="attachment://aura.png")
                        else:
                            logger.write_log("Failed to create discord file from screenshot.")
                    except Exception as scr_e:
                        logger.write_log(f"Failed to take or process screenshot: {scr_e}")

                ping_content = f"<@{settings['mention_id']}>" if should_ping else ""
                try:
                    if file_to_send:
                        webhook.send(
                            content=ping_content,
                            embed=emb,
                            file=file_to_send
                        )
                        forward_webhook_msg(
                            primary_webhook_url=webhook.url,
                            secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                            content=ping_content,
                            embed=emb,
                            file=file_to_send
                        )
                    else:
                        webhook.send(
                            content=ping_content,
                            embed=emb
                        )
                        forward_webhook_msg(
                            primary_webhook_url=webhook.url,
                            secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                            content=ping_content,
                            embed=emb
                        )
                except Exception as wh_e:
                    logger.write_log(f"Error sending aura webhook: {wh_e}")

                reset_aura_target = settings.get("reset_aura", "")
                if reset_aura_target and current_aura != reset_aura_target:
                    logger.write_log(f"Resetting aura back to {reset_aura_target}...")

                    if not all(c in COORDS for c in ["aura_button_pos", "search_pos", "query_pos", "equip_pos", "close_pos"]):
                        logger.write_log("Cannot reset aura: Coordinates missing.")
                    else:
                        with keyboard_lock:
                            try:
                                wait_time = settings.get("global_wait_time", 0.2)
                                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["aura_button_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["aura_button_pos"][1] * COORDS["scr_hei"])))
                                time.sleep(wait_time)
                                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["search_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["search_pos"][1] * COORDS["scr_hei"])))
                                time.sleep(wait_time)
                                kb.type(reset_aura_target)
                                time.sleep(wait_time + 0.2)
                                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["equip_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["equip_pos"][1] * COORDS["scr_hei"])))
                                time.sleep(wait_time)

                                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["equip_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["equip_pos"][1] * COORDS["scr_hei"])))
                                time.sleep(wait_time)
                                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["equip_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["equip_pos"][1] * COORDS["scr_hei"])))
                                time.sleep(wait_time)
                                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
                                time.sleep(wait_time)
                                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
                                logger.write_log("Aura reset initiated.")
                                previous_aura = reset_aura_target 
                            except Exception as reset_e:
                                logger.write_log(f"Error during aura reset: {reset_e}")

            else: 
                logger.write_log(f"Detected unknown aura: {current_aura}")
                previous_aura = current_aura 

        except Exception as e:
            logger.write_log(f"Error in Aura Detection loop: {e}")

            time.sleep(5)

        if not stop_event.is_set():
             time.sleep(settings.get("global_wait_time", 0.2) + 0.3) 

    logger.write_log("Aura Detection thread stopped.")

def biome_detection(settings: dict, webhook, stop_event: threading.Event, sniped_event: threading.Event):
    logger = get_logger()
    logger.write_log("Biome Detection thread started.")

    try:
        with open(get_biomes_path(), "r", encoding="utf-8") as f:
            biomes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        logger.write_log(f"Error loading biomes data: {e}. Biome detection stopped.")
        return

    previous_biome = None
    try:
        previous_biome = get_latest_hovertext()
        logger.write_log(f"Initial biome state: {previous_biome}")
    except Exception as e:
        logger.write_log(f"Error getting initial biome state: {e}")

    ps_link_valid = validate_pslink(settings.get("private_server_link", ""))

    while not stop_event.is_set() and not sniped_event.is_set():
        try:
            current_biome = get_latest_hovertext()
            if current_biome is None:
                time.sleep(2)
                continue

            current_biome_key = current_biome.lower()
            previous_biome_key = previous_biome.lower() if previous_biome else None

            if previous_biome_key is None or current_biome_key == previous_biome_key:
                previous_biome = current_biome
                continue

            logger.write_log(f"Biome change detected: {previous_biome} -> {current_biome}")
            rnow = datetime.now()

            if previous_biome_key and previous_biome_key != "normal" and previous_biome_key in biomes and settings.get("biomes", {}).get(previous_biome_key, False):
                prev_biome_data = biomes[previous_biome_key]
                emb_color_hex = prev_biome_data.get("colour", "#808080")
                emb_rgb = hex2rgb(emb_color_hex)
                emb = discord.Embed(
                    title=f"Biome Ended: {previous_biome}",
                    description=f"Biome **{previous_biome}** has ended.\n**Time:** <t:{str(int(time.time()))}>",
                    colour=discord.Colour.from_rgb(*emb_rgb)
                )
                emb.set_thumbnail(url=biomes.get(previous_biome.lower()).get("img_url"))
                try:
                    webhook.send(embed=emb)
                    forward_webhook_msg(
                        primary_webhook_url=webhook.url,
                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                        embed=emb
                    )
                except Exception as wh_e:
                    logger.write_log(f"Error sending biome ended webhook: {wh_e}")

            previous_biome = current_biome

            if current_biome_key != "normal" and current_biome_key in biomes:
                if settings.get("biomes", {}).get(current_biome_key, False):

                    new_biome_data = biomes[current_biome_key]
                    emb_color_hex = new_biome_data.get("colour", "#808080")
                    emb_rgb = hex2rgb(emb_color_hex)

                    description = f"Biome {current_biome} has started!\nTime: <t:{str(int(time.time()))}>"

                    emb = discord.Embed(
                        title=f"Biome Started: {current_biome}",
                        description=description,
                        colour=discord.Colour.from_rgb(*emb_rgb)
                    )
                    if ps_link_valid:
                        emb.add_field(name="Server Invite:", value=f"{settings.get('private_server_link')}")

                    if new_biome_data.get("rare", False):
                        ping_content = "@everyone"
                        emb.set_footer(text=f"SolsScope v{LOCALVERSION}")
                    else:
                        ping_content = ""

                    emb.set_thumbnail(url=biomes.get(current_biome.lower()).get("img_url"))
                    try:
                        webhook.send(content=ping_content, embed=emb)
                        forward_webhook_msg(
                            primary_webhook_url=webhook.url,
                            secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                            content=ping_content,
                            embed=emb
                        )
                        logger.write_log(f"Sent notification for biome start: {current_biome}")
                    except Exception as wh_e:
                        logger.write_log(f"Error sending biome started webhook: {wh_e}")
                else:
                    logger.write_log(f"Biome {current_biome} started, but notifications are disabled for it in settings.")

        except Exception as e:
            logger.write_log(f"Error in Biome Detection loop: {e}")
            time.sleep(5)

        if not stop_event.is_set() and not sniped_event.is_set():
            time.sleep(settings.get("global_wait_time", 0.2) + 1.0)

    logger.write_log("Biome Detection thread stopped.")

def keep_alive(settings: dict, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey):
    logger = get_logger()
    if stop_event.wait(timeout=5):
        return
    logger.write_log("Keep Alive (Anti-AFK) thread started.")
    required_coords = ["close_pos"]
    if not all(coord in COORDS for coord in required_coords):
        logger.write_log("Cannot start Keep Alive: close_pos coordinate missing.")
        return

    while not stop_event.is_set() and not sniped_event.is_set():
        wait_interval = random.randint(550, 650)
        logger.write_log(f"Keep Alive: Waiting for {wait_interval} seconds before next action.")

        if stop_event.wait(timeout=wait_interval):
            break

        if sniped_event.is_set():
            break

        with keyboard_lock:
            try:
                logger.write_log("Keep Alive: Performing anti-AFK action (clicking close pos).")
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
                time.sleep(0.2)
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
            except Exception as e:
                logger.write_log(f"Error during Keep Alive action: {e}")

    logger.write_log("Keep Alive (Anti-AFK) thread stopped.")

def merchant_detection(settings: dict, webhook, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb):
    logger = get_logger()
    if not MERCHANT_DETECTION_POSSIBLE:
        logger.write_log("Merchant Detection cannot start: Missing dependencies (cv2/pytesseract).")
        return

    _check_config_items = False
    for item in settings.get("auto_purchase_items_mari").keys():
        if settings.get("auto_purchase_items_mari", {}).get(item, {}).get("Purchase", False):
            _check_config_items = True
    for item in settings.get("auto_purchase_items_jester").keys():
        if settings.get("auto_purchase_items_jester", {}).get(item, {}).get("Purchase", False):
            _check_config_items = True

    _check_sell_items = False
    for item in settings.get("items_to_sell").keys():
        if settings.get("items_to_sell").get(item, False):
            _check_sell_items = True

    
    
    if not _check_config_items or not _check_sell_items:
        logger.write_log("No items were selected to be auto purchased/sold, not starting.")
        return

    if stop_event.wait(timeout=5):
        return
    

    logger.write_log("Merchant Detection thread started.")

    try:
        with open(get_merchant_path(), "r", encoding="utf-8") as f:
            merchants = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        logger.write_log(f"Error loading merchant data: {e}. Merchant detection stopped.")
        return

    required_coords = [
        "close_pos", "open_merch_pos", "merchant_box", "manual_boxes",
        "merch_item_pos_1_purchase", "merch_item_pos_2_purchase",
        "merch_item_pos_3_purchase", "merch_item_pos_4_purchase",
        "merch_item_pos_5_purchase", "quantity_btn_pos", "purchase_btn_pos"
    ]
    if not all(coord in COORDS for coord in required_coords):
        logger.write_log("Cannot start Merchant Detection: Required coordinates missing.")
        return

    ps_link_valid = validate_pslink(settings.get("private_server_link", ""))

    if settings.get("auto_sell_to_jester", False):
        cooldown_interval = 120
        before_check_interval = 60
    else:
        cooldown_interval = 90
        before_check_interval = 90    

    auto_sell = settings.get("auto_sell_to_jester", False)
    if auto_sell:
        logger.write_log("Auto sell for Jester is enabled.")

    is_autocraft = settings.get("auto_craft_mode", False)

    while not stop_event.is_set() and not sniped_event.is_set():

        wait_interval = before_check_interval
        logger.write_log(f"Merchant Detection: Waiting for {wait_interval} seconds...")
        if stop_event.wait(timeout=wait_interval):
            break
        if sniped_event.is_set(): break

        logger.write_log("Merchant Detection: Merchant Check Scheduled")
        screenshot_path = os.path.join(MACROPATH, "scr", "screenshot_merchant.png")
        ex_screenshot_path = os.path.join(MACROPATH, "scr", "screenshot_exchange.png")
        detected_merchant_name = None
        detected_items = {}
        
        with keyboard_lock:

            try:
                logger.write_log("Merchant Detection: Using Merchant Teleport item...")
                use_item("Merchant Teleport", 1, False, mkey, kb, settings) 
                time.sleep(settings.get("global_wait_time", 0.2) + 0.5) 

                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
                time.sleep(1)

                logger.write_log("Merchant Detection: Attempting interaction (E key)...")
                kb.press('e')
                time.sleep(0.2)
                kb.release('e')
                time.sleep(7) 

                logger.write_log("Merchant Detection: Clicking open merchant position...")
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["open_merch_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["open_merch_pos"][1] * COORDS["scr_hei"])))
                time.sleep(3) 

                logger.write_log("Merchant Detection: Taking screenshot...")
                pag.screenshot(screenshot_path)
                time.sleep(0.2)

                logger.write_log("Merchant Detection: Processing screenshot with OCR...")
                image = cv2.imread(screenshot_path)
                if image is None:
                    logger.write_log("Merchant Detection Error: Failed to read screenshot file.")
                    continue

                x1p, y1p, x2p, y2p = COORDS_PERCENT["merchant_box"]
                x1 = round(x1p * COORDS["scr_wid"])
                y1 = round(y1p * COORDS["scr_hei"])
                x2 = round(x2p * COORDS["scr_wid"])
                y2 = round(y2p * COORDS["scr_hei"])
                merchant_crop = image[y1:y2, x1:x2]
                ocr_merchant_raw = pytesseract.image_to_string(merchant_crop).strip()

                ocr_merchant_clean = re.sub(r"[^a-zA-Z']", "", ocr_merchant_raw).lower()
                detected_merchant_name = fuzzy_match_merchant(ocr_merchant_clean, POSSIBLE_MERCHANTS)

                if not detected_merchant_name:
                    logger.write_log(f"Merchant Detection: Could not identify merchant from OCR ('{ocr_merchant_raw}'). Skipping.")
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
                    continue

                merchant_short_name = detected_merchant_name.split("'")[0] 
                logger.write_log(f"Merchant Detected: {merchant_short_name} (Raw OCR: '{ocr_merchant_raw}')")
                rnow = datetime.now()

                file_to_send = create_discord_file_from_path(screenshot_path, filename="merchant.png")
                ping_content = ""
                if merchant_short_name == "Mari":
                    emb_color = discord.Colour.from_rgb(255, 255, 255)
                    thumbnail_url = "https://static.wikia.nocookie.net/sol-rng/images/3/37/MARI_HIGH_QUALITYY.png/revision/latest"
                    if settings.get("ping_mari", False) and settings.get("mari_ping_id", 0) != 0:
                        ping_content += f"<@&{settings['mari_ping_id']}>"
                elif merchant_short_name == "Jester":
                    emb_color = discord.Colour.from_rgb(176, 49, 255)
                    thumbnail_url = "https://static.wikia.nocookie.net/sol-rng/images/d/db/Headshot_of_Jester.png/revision/latest"
                    if settings.get("ping_jester", False) and settings.get("jester_ping_id", 0) != 0:
                        ping_content += f"<@&{settings['jester_ping_id']}>"
                else:
                    emb_color = discord.Colour.default()
                    thumbnail_url = None

                emb = discord.Embed(
                    title=f"{merchant_short_name} Spawned!",
                    description=f"A **{merchant_short_name}** has been detected.\n**Time:** <t:{str(int(time.time()))}>",
                    colour=emb_color
                )
                if thumbnail_url: emb.set_thumbnail(url=thumbnail_url)
                if file_to_send: emb.set_image(url="attachment://merchant.png")
                if ps_link_valid: emb.add_field(name="Server Invite", value=settings['private_server_link'], inline=False)

                emb.set_footer(text=f"SolsScope v{LOCALVERSION}")

                logger.write_log("Merchant Detection: Detecting items...")
                item_list = MARI_ITEMS if merchant_short_name == "Mari" else JESTER_ITEMS
                manual_boxes = COORDS.get("manual_boxes", {})
                item_ocr_results = []
                for box_name, (x1, y1, x2, y2) in manual_boxes.items():
                    if x1 >= image.shape[1] or y1 >= image.shape[0] or x2 <= x1 or y2 <= y1:
                        logger.write_log(f"Warning: Invalid coordinates for {box_name}. Skipping OCR.")
                        continue
                    cropped = image[y1:y2, x1:x2]
                    ocr_raw = pytesseract.image_to_string(cropped).strip().replace('\n', ' ')
                    matched = fuzzy_match(ocr_raw, item_list, threshold=0.5)
                    logger.write_log(f" > {box_name}: OCR='{ocr_raw}', Match='{matched}'")
                    detected_items[box_name] = matched
                    item_ocr_results.append(f"**{box_name}:** `{matched}` (Raw: `{ocr_raw}`)")
                emb.add_field(name="Detected Items", value="\n".join(item_ocr_results) if item_ocr_results else "None", inline=False)

                if not (settings.get("mention", False) and settings.get("mention_id", 0) != 0) and settings.get(f"{merchant_short_name.lower()}_ping_id", 0) != 0:
                    ping_content = f"<@{settings['mention_id']}>{ping_content}"

                if not settings.get(f"ping_{merchant_short_name.lower()}", False):
                    ping_content = ""

                try:
                    webhook.send(content=ping_content.strip(), embed=emb, file=file_to_send)
                    forward_webhook_msg(
                        primary_webhook_url=webhook.url,
                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                        content=ping_content.strip(), embed=emb, file=file_to_send
                    )
                except Exception as wh_e:
                    logger.write_log(f"Error sending merchant detection webhook: {wh_e}")

                purchase_settings = settings.get("auto_purchase_items_mari" if merchant_short_name == "Mari" else "auto_purchase_items_jester", {})
                items_to_buy = {box_name: item_name for box_name, item_name in detected_items.items() if purchase_settings.get(item_name, {"Purchase" : False}).get("Purchase", False)}

                if items_to_buy:
                    logger.write_log(f"Merchant Detection: Attempting to auto-purchase items: {list(items_to_buy.values())}")
                    for box_name, item_name in items_to_buy.items():
                        try:

                            coord_key = f"merch_item_pos_{box_name[-1]}_purchase"
                            if coord_key in COORDS:
                                wait_time = settings.get("global_wait_time", 0.2)
                                mkey.left_click_xy_natural(round(float(COORDS_PERCENT[coord_key][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT[coord_key][1] * COORDS["scr_hei"])))
                                time.sleep(wait_time)
                                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["quantity_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["quantity_btn_pos"][1] * COORDS["scr_hei"])))
                                time.sleep(wait_time)
                                kb.type(str(purchase_settings.get(item_name).get("amount", 1)))
                                time.sleep(wait_time)
                                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["purchase_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["purchase_btn_pos"][1] * COORDS["scr_hei"])))
                                time.sleep(wait_time + 0.5) 
                                logger.write_log(f"Auto-purchased: {item_name}")

                                try:
                                    purch_emb = discord.Embed(
                                        title=f"Auto-Purchased from {merchant_short_name}",
                                        description=f"Item: **{item_name}**\nAmount: **{str(purchase_settings.get(item_name).get('amount', 1))}**",
                                        colour=emb_color
                                    )
                                    purch_emb.set_footer(text=f"SolsScope v{LOCALVERSION}")
                                    if merchants.get(merchant_short_name.lower()).get("items").get(item_name.lower()).get("item_image_url"): purch_emb.set_thumbnail(url=merchants.get(merchant_short_name.lower()).get("items").get(item_name.lower()).get("item_image_url"))
                                    webhook.send(embed=purch_emb)
                                    forward_webhook_msg(
                                        primary_webhook_url=webhook.url,
                                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                        embed=purch_emb
                                    )
                                except Exception as purch_wh_e:
                                    logger.write_log(f"Error sending purchase confirmation webhook: {purch_wh_e}")
                            else:
                                logger.write_log(f"Error purchasing {item_name}: Coordinate key {coord_key} not found.")
                        except Exception as buy_e:
                            logger.write_log(f"Error auto-purchasing {item_name}: {buy_e}")
                        time.sleep(1)

                if auto_sell and merchant_short_name == "Jester":
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_merchant_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_merchant_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    kb.press('e')
                    time.sleep(0.2)
                    kb.release('e')
                    time.sleep(7)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["exchange_menu_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["exchange_menu_btn_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(9)
                    while not stop_event.is_set() and not sniped_event.is_set():
                        pag.screenshot(ex_screenshot_path)
                        time.sleep(0.2)
                        logger.write_log("Merchant Detection: Processing screenshot with OCR...")
                        image = cv2.imread(ex_screenshot_path)
                        if image is None:
                            logger.write_log("Merchant Detection Error: Failed to read screenshot file.")
                            continue
                        x1p, y1p, x2p, y2p = COORDS_PERCENT["first_sell_item_box_pos"]
                        x1 = round(x1p * COORDS["scr_wid"])
                        y1 = round(y1p * COORDS["scr_hei"])
                        x2 = round(x2p * COORDS["scr_wid"]) 
                        y2 = round(y2p * COORDS["scr_hei"])
                        exchange_crop = image[y1:y2, x1:x2]
                        ocr_ex_item_raw = pytesseract.image_to_string(exchange_crop).strip().replace('\n', ' ')
                        ocr_ex_item_clean = re.sub(r"[^a-zA-Z']", "", ocr_ex_item_raw).lower()
                        detected_item_name = fuzzy_match_auto_sell(ocr_ex_item_clean, JESTER_SELL_ITEMS)
                        logger.write_log(f"Item: {detected_item_name} || OCR: {ocr_ex_item_raw}")
                        if detected_item_name == "Void Coin":
                            logger.write_log("Void Coin detected in first slot, skipping to second slot.")
                            _break_second = False
                            while detected_item_name in JESTER_ITEMS and not stop_event.is_set() and not sniped_event.is_set():
                                logger.write_log("Auto-Sell: Taking screenshot")
                                pag.screenshot(ex_screenshot_path)
                                time.sleep(0.2)
                                logger.write_log("Auto-Sell: Processing screenshot with OCR...")
                                image = cv2.imread(ex_screenshot_path)
                                if image is None:
                                    logger.write_log("Auto-Sell Error: Failed to read screenshot file.")
                                    continue
                                x1p, y1p, x2p, y2p = COORDS_PERCENT["second_sell_item_box_pos"]
                                x1 = round(x1p * COORDS["scr_wid"])
                                y1 = round(y1p * COORDS["scr_hei"])
                                x2 = round(x2p * COORDS["scr_wid"])
                                y2 = round(y2p * COORDS["scr_hei"])
                                exchange_crop = image[y1:y2, x1:x2]
                                ocr_ex_item_raw = pytesseract.image_to_string(exchange_crop).strip().replace('\n', ' ')
                                ocr_ex_item_clean = re.sub(r"[^a-zA-Z']", "", ocr_ex_item_raw).lower()
                                detected_item_name = fuzzy_match_auto_sell(ocr_ex_item_clean, JESTER_SELL_ITEMS)
                                if detected_item_name == "Void Coin":
                                    _break_second = True
                                    logger.write_log("Auto-Sell: Void coin detected in second slot, stopping job.")
                                    break
                                elif detected_item_name in JESTER_SELL_ITEMS and settings.get("items_to_sell", {}).get(detected_item_name, False):
                                    logger.write_log(f"Auto-Sell: {detected_item_name} was detected")
                                    time.sleep(0.2)
                                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["second_sell_item_click_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["second_sell_item_click_pos"][1] * COORDS["scr_hei"])))
                                    time.sleep(0.2)
                                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["quantity_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["quantity_btn_pos"][1] * COORDS["scr_hei"])))
                                    time.sleep(0.2)
                                    kb.type(str(settings.get("amount_of_item_to_sell", 1)))
                                    time.sleep(0.2)
                                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["purchase_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["purchase_btn_pos"][1] * COORDS["scr_hei"])))
                                    time.sleep(0.2)
                                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["exchange_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["exchange_btn_pos"][1] * COORDS["scr_hei"])))
                                    time.sleep(4.5)
                                    sell_emb = discord.Embed(
                                        title=f"Auto-Sold to {merchant_short_name}",
                                        description=f"Item: **{detected_item_name}**\nAmount: **{str(settings.get('amount_of_item_to_sell', 1))}**\nMaximum Profit: **{str(settings.get('amount_of_item_to_sell', 1) * merchants.get(merchant_short_name.lower()).get('exchange').get(detected_item_name.lower()).get('price'))}P",
                                        colour=emb_color
                                    )
                                    sell_emb.set_footer(text=f"SolsScope v{LOCALVERSION}")
                                    if merchants.get(merchant_short_name.lower()).get("exchange").get(detected_item_name.lower()).get("item_image_url"): sell_emb.set_thumbnail(url=merchants.get(merchant_short_name.lower()).get("exchange").get(detected_item_name.lower()).get("item_image_url"))
                                    webhook.send(embed=sell_emb)
                                    forward_webhook_msg(
                                        primary_webhook_url=webhook.url,
                                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                        embed=sell_emb
                                    )
                                else:
                                    logger.write_log("Auto-Sell: No items were found in the second box or unsure if Void Coin was not detected, ending auto sell job.")
                                    _break_second = True
                                    break
                                time.sleep(1)
                            if _break_second:
                                break
                        elif detected_item_name in JESTER_SELL_ITEMS and settings.get("items_to_get", {}).get(detected_item_name, False):
                            logger.write_log(f"Auto-Sell: {detected_item_name} was detected")
                            time.sleep(0.2)
                            mkey.left_click_xy_natural(round(float(COORDS_PERCENT["first_sell_item_click_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["first_sell_item_click_pos"][1] * COORDS["scr_hei"])))
                            time.sleep(0.2)
                            mkey.left_click_xy_natural(round(float(COORDS_PERCENT["quantity_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["quantity_btn_pos"][1] * COORDS["scr_hei"])))
                            time.sleep(0.2)
                            kb.type(str(settings.get("amount_of_item_to_sell", 0)))
                            time.sleep(0.2)
                            mkey.left_click_xy_natural(round(float(COORDS_PERCENT["purchase_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["purchase_btn_pos"][1] * COORDS["scr_hei"])))
                            time.sleep(0.2)
                            mkey.left_click_xy_natural(round(float(COORDS_PERCENT["exchange_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["exchange_btn_pos"][1] * COORDS["scr_hei"])))
                            time.sleep(4.5)
                            sell_emb = discord.Embed(
                                title=f"Auto-Sold to {merchant_short_name}",
                                description=f"Item: **{detected_item_name}**\nAmount: **{str(settings.get('amount_of_item_to_sell', 1))}**\nMaximum Profit: **{str(settings.get('amount_of_item_to_sell', 1) * merchants.get(merchant_short_name.lower()).get('exchange').get(detected_item_name.lower()).get('price'))}P**",
                                colour=emb_color
                            )
                            sell_emb.set_footer(text=f"SolsScope v{LOCALVERSION}")
                            if merchants.get(merchant_short_name.lower()).get("exchange").get(detected_item_name.lower()).get("item_image_url"): sell_emb.set_thumbnail(url=merchants.get(merchant_short_name.lower()).get("exchange").get(detected_item_name.lower()).get("item_image_url"))
                            webhook.send(embed=sell_emb)
                            forward_webhook_msg(
                                primary_webhook_url=webhook.url,
                                secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                embed=sell_emb
                            )
                        else:
                            logger.write_log("Auto-Sell: No item was found or unsure if Void Coin was not detected, ending auto sell job.")
                            break
                        time.sleep(1)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_merchant_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_merchant_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(1)
            
                if is_autocraft:
                    logger.write_log("Walking back to Stella's")
                    try:
                        reset_character()
                        time.sleep(1)
                        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["collection_open_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["collection_open_pos"][1] * COORDS["scr_hei"])))
                        time.sleep(0.5)
                        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["exit_collection_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["exit_collection_pos"][1] * COORDS["scr_hei"])))
                        time.sleep(1)
                    except Exception as e:
                        logger.write_log(f"Error during camera alignment: {e}")
                        continue

                    logger.write_log("Begin position alignment.")

                    try:
                        mkey.move_to_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
                        time.sleep(0.4)
                        right_click_drag(1000, 0)
                        time.sleep(0.4)
                        kb.press("d")
                        time.sleep(3)
                        kb.release("d")
                        time.sleep(0.4)
                        kb.press("w")
                        time.sleep(8)
                        kb.release("w")
                        time.sleep(0.4)
                        kb.press("a")
                        time.sleep(3)
                        kb.release("a")
                        time.sleep(0.4)
                        kb.press("w")
                        time.sleep(1)
                        kb.release("w")
                        time.sleep(0.4)
                        kb.press("d")
                        time.sleep(0.75)
                        kb.release("d")
                        time.sleep(0.4)
                        kb.press("w")
                        time.sleep(1)
                        kb.release("w")
                    except Exception as e:
                        logger.write_log(f"Error during position alignment: {e}")
                        continue

                    logger.write_log("Finished position alignment, walking to Stella.")

                    try:
                        right_click_drag(0, 600)
                        time.sleep(1)
                        run_macro(f"{PATH_DIR}/stella.mms")
                        time.sleep(1)
                    except Exception as e:
                        logger.write_log(f"Error during walk to Stella's: {e}")
                        continue

                else:
                    time.sleep(cooldown_interval)

            except Exception as e:
                logger.write_log(f"Error in Merchant Detection loop: {e}")
                import traceback
                logger.write_log(traceback.format_exc()) 

                try:
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_merchant_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_merchant_pos"][1] * COORDS["scr_hei"])))
                except Exception:
                    pass

    logger.write_log("Merchant Detection thread stopped.")

def auto_craft(settings: dict, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, ms):
    logger = get_logger()
    logger.write_log("Starting Auto Craft in 10 seconds")
    if stop_event.wait(timeout=10):
        return
    logger.write_log("Auto Craft thread started.")

    items_to_craft = [item for item, enabled in settings.get("auto_craft_item", {}).items() if enabled]
    if not items_to_craft:
        logger.write_log("Auto Craft stopped: No items selected for crafting.")
        return

    logger.write_log(f"Auto Crafting enabled for: {', '.join(items_to_craft)}")
    logger.write_log("Ensure you are standing near the cauldron with the 'F' prompt visible.")

    auto_craft_index = 0 
    auto_mode_swap = 0 

    required_coords = [
        "potion_search_pos", "first_potion_pos", "craft_btn_pos", "hp1_pos_potions",
        "hp2_pos_potions", "hp1_pos_celestial", 

    ]
    if not all(coord in COORDS for coord in required_coords):
         logger.write_log("Cannot start Auto Craft: Required coordinates missing.")
         return

    def search_for_potion_in_cauldron(potion_name):
        kb.press('f') 
        time.sleep(0.2)
        kb.release('f')
        time.sleep(0.5) 
        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["potion_search_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["potion_search_pos"][1] * COORDS["scr_hei"])))
        time.sleep(0.2)
        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["potion_search_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["potion_search_pos"][1] * COORDS["scr_hei"])))
        time.sleep(0.2)

        kb.press(keyboard.Key.ctrl); kb.press('a'); time.sleep(0.05); kb.release('a'); kb.release(keyboard.Key.ctrl); time.sleep(0.2)
        kb.press(keyboard.Key.backspace); time.sleep(0.05); kb.release(keyboard.Key.backspace)
        time.sleep(0.2)
        kb.type(potion_name)
        time.sleep(0.3)
        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["first_potion_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["first_potion_pos"][1] * COORDS["scr_hei"])))
        time.sleep(0.2)

        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["potion_search_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["potion_search_pos"][1] * COORDS["scr_hei"])))
        time.sleep(0.2)

    if stop_event.wait(timeout=10):
        return
    
    logger.write_log("Auto Craft: Walking To Stella's")
    with keyboard_lock:
        try:
            reset_character()
            time.sleep(1)
            mkey.left_click_xy_natural(round(float(COORDS_PERCENT["collection_open_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["collection_open_pos"][1] * COORDS["scr_hei"])))
            time.sleep(0.5)
            mkey.left_click_xy_natural(round(float(COORDS_PERCENT["exit_collection_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["exit_collection_pos"][1] * COORDS["scr_hei"])))
            time.sleep(1)
        except Exception as e:
            logger.write_log(f"Error during camera alignment: {e}")

        logger.write_log("Begin position alignment.")

        try:
            mkey.move_to_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
            time.sleep(0.4)
            right_click_drag(1000, 0)
            time.sleep(0.4)
            kb.press("d")
            time.sleep(3)
            kb.release("d")
            time.sleep(0.4)
            kb.press("w")
            time.sleep(8)
            kb.release("w")
            time.sleep(0.4)
            kb.press("a")
            time.sleep(3)
            kb.release("a")
            time.sleep(0.4)
            kb.press("w")
            time.sleep(1)
            kb.release("w")
            time.sleep(0.4)
            kb.press("d")
            time.sleep(0.75)
            kb.release("d")
            time.sleep(0.4)
            kb.press("w")
            time.sleep(1)
            kb.release("w")
        except Exception as e:
            logger.write_log(f"Error during position alignment: {e}")

        logger.write_log("Finished position alignment, walking to Stella.")

        try:
            right_click_drag(0, 600)
            time.sleep(1)
            run_macro(f"{PATH_DIR}/stella.mms")
            time.sleep(1)
        except Exception as e:
            logger.write_log(f"Error during walk to Stella's: {e}")

    while not stop_event.is_set() and not sniped_event.is_set():

        with keyboard_lock:
            try:
                wait_time = settings.get("global_wait_time", 0.2)

                if settings["auto_craft_item"].get("Jewelry Potion", False):
                    search_for_potion_in_cauldron("Jewelry")
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["craft_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["craft_btn_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])) - round(float(110 / 2560 * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])) - round(float(110 / 2560 * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    kb.type("20"); time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)

                    if auto_craft_index == 1 and len(items_to_craft) > 1 and auto_mode_swap == 5:
                        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["auto_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["auto_btn_pos"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Zombie Potion", False):
                    search_for_potion_in_cauldron("Zombie")
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["craft_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["craft_btn_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])) - round(float(110 / 2560 * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])) - round(float(110 / 2560 * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    kb.type("10"); time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp2_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp2_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)

                    if auto_craft_index == 2 and len(items_to_craft) > 1 and auto_mode_swap == 5:
                        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["auto_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["auto_btn_pos"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Rage Potion", False):
                    search_for_potion_in_cauldron("Rage")
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["craft_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["craft_btn_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])) - round(float(110 / 2560 * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])) - round(float(110 / 2560 * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    kb.type("10"); time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)

                    if auto_craft_index == 3 and len(items_to_craft) > 1 and auto_mode_swap == 5:
                        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["auto_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["auto_btn_pos"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Diver Potion", False):
                    search_for_potion_in_cauldron("Diver")
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["craft_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["craft_btn_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])) - round(float(110 / 2560 * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])) - round(float(110 / 2560 * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    kb.type("20"); time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp2_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp2_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)

                    if auto_craft_index == 4 and len(items_to_craft) > 1 and auto_mode_swap == 5:
                        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["auto_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["auto_btn_pos"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Potion of Bound", False):
                    search_for_potion_in_cauldron("Bound")
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["craft_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["craft_btn_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp2_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp2_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp2_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp2_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp2_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp2_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float((954 / 2560) * COORDS["scr_wid"])), round(float((1048 / 1440) * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(round(float((954 / 2560) * COORDS["scr_wid"])), round(float((1048 / 1440) * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    kb.type("100")
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(round(float((1064 / 2560) * COORDS["scr_wid"])), round(float((1048 / 1440) * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    if auto_craft_index == 5 and len(items_to_craft) > 1 and auto_mode_swap == 5:
                        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["auto_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["auto_btn_pos"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Heavenly Potion", False):
                    search_for_potion_in_cauldron("Heavenly")
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["craft_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["craft_btn_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])) - round(float(110 / 2560 * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])) - round(float(110 / 2560 * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    kb.type("250")
                    time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp2_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp2_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp2_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp2_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float((1064 / 2560) * COORDS["scr_wid"])), round(float((988 / 1440) * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    if auto_craft_index == 6 and len(items_to_craft) > 1 and auto_mode_swap == 5:
                        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["auto_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["auto_btn_pos"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Godly Potion (Zeus)", False):
                    search_for_potion_in_cauldron("Zeus")
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["craft_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["craft_btn_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])) - round(float(110 / 2560 * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])) - round(float(110 / 2560 * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    kb.type("25"); time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp2_pos_potions"][0] * COORDS["scr_wid"])) - round(float(110 / 2560 * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp2_pos_potions"][1] * COORDS["scr_hei"])) )
                    time.sleep(wait_time); mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp2_pos_potions"][0] * COORDS["scr_wid"])) - round(float(110 / 2560 * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp2_pos_potions"][1] * COORDS["scr_hei"])))
                    kb.type("25"); time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"]))); time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp2_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp2_pos_potions"][1] * COORDS["scr_hei"]))); time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float((1064 / 2560) * COORDS["scr_wid"])), round(float((988 / 1440) * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(round(float((1064 / 2560) * COORDS["scr_wid"])), round(float((1048 / 1440) * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    if auto_craft_index == 7 and len(items_to_craft) > 1 and auto_mode_swap == 5:
                        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["auto_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["auto_btn_pos"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Godly Potion (Poseidon)", False):
                    search_for_potion_in_cauldron("Poseidon")
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["craft_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["craft_btn_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)

                    mkey.left_click_xy_natural(COORDS["hp1_pos_potions"][0] - (110 * COORDS['scale_w']), COORDS["hp1_pos_potions"][1])
                    time.sleep(wait_time); mkey.left_click_xy_natural(COORDS["hp1_pos_potions"][0] - (110 * COORDS['scale_w']), COORDS["hp1_pos_potions"][1]); time.sleep(wait_time)
                    kb.type("50"); time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"]))); time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp2_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp2_pos_potions"][1] * COORDS["scr_hei"]))); time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float((1064 / 2560) * COORDS["scr_wid"])), round(float((988 / 1440) * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(round(float((1064 / 2560) * COORDS["scr_wid"])), round(float((1048 / 1440) * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    if auto_craft_index == 8 and len(items_to_craft) > 1 and auto_mode_swap == 5:
                        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["auto_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["auto_btn_pos"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Godly Potion (Hades)", False):
                    search_for_potion_in_cauldron("Hades")
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["craft_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["craft_btn_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)

                    mkey.left_click_xy_natural(COORDS["hp1_pos_potions"][0] - (110 * COORDS['scale_w']), COORDS["hp1_pos_potions"][1])
                    time.sleep(wait_time); mkey.left_click_xy_natural(COORDS["hp1_pos_potions"][0] - (110 * COORDS['scale_w']), COORDS["hp1_pos_potions"][1]); time.sleep(wait_time)
                    kb.type("50"); time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"])));time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp2_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp2_pos_potions"][1] * COORDS["scr_hei"]))); time.sleep(wait_time)
                    if auto_craft_index == 9 and len(items_to_craft) > 1 and auto_mode_swap == 5:
                        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["auto_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["auto_btn_pos"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Warp Potion", False):
                    search_for_potion_in_cauldron("Warp")
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["craft_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["craft_btn_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"]))); time.sleep(wait_time)

                    ms.scroll(0, -30); time.sleep(0.2)
                    ms.scroll(0, -30); time.sleep(0.2)

                    mkey.left_click_xy_natural((round(float(COORDS_PERCENT["hp1_pos_celestial"][0] * COORDS["scr_wid"])) - round(float(110 / 2560 * COORDS["scr_wid"]))) , round(float(COORDS_PERCENT["hp1_pos_celestial"][1] * COORDS["scr_hei"])) );time.sleep(wait_time)
                    mkey.left_click_xy_natural((round(float(COORDS_PERCENT["hp1_pos_celestial"][0] * COORDS["scr_wid"])) - round(float(110 / 2560 * COORDS["scr_wid"]))), round(float(COORDS_PERCENT["hp1_pos_celestial"][1] * COORDS["scr_hei"])) );time.sleep(wait_time)
                    kb.type("1000"); time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"]))); time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_celestial"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_celestial"][1] * COORDS["scr_hei"]))); time.sleep(wait_time)

                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    if auto_craft_index == 10 and len(items_to_craft) > 1 and auto_mode_swap == 5:
                        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["auto_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["auto_btn_pos"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Godlike Potion", False):
                    search_for_potion_in_cauldron("Godlike")
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["craft_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["craft_btn_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp1_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp1_pos_potions"][1] * COORDS["scr_hei"]))); time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["hp2_pos_potions"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["hp2_pos_potions"][1] * COORDS["scr_hei"]))); time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float((1064 / 2560) * COORDS["scr_wid"])), round(float((988 / 1440) * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(round(float((954 / 2560) * COORDS["scr_wid"])), round(float((1048 / 1440) * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(round(float((954 / 2560) * COORDS["scr_wid"])), round(float((1048 / 1440) * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    kb.type("600")
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(round(float((1064 / 2560) * COORDS["scr_wid"])), round(float((1048 / 1440) * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["potion_search_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["potion_search_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    time.sleep(1)

                time.sleep(1)

            except Exception as craft_e:
                logger.write_log(f"Error during auto craft: {craft_e}")

        if auto_craft_index >= len(items_to_craft):
            auto_craft_index = 1
        else:
            auto_craft_index += 1
        if auto_mode_swap == 5:
            auto_mode_swap = 0
        else:
            auto_mode_swap += 1

        wait_interval = 60
        logger.write_log(f"Auto Craft: Waiting {wait_interval} seconds...")
        if stop_event.wait(timeout=wait_interval):
            break
        if sniped_event.is_set(): break

    logger.write_log("Auto Craft thread stopped.")

def auto_br(settings: dict, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb):
    logger = get_logger()
    if stop_event.wait(timeout=5):
        return
    logger.write_log("Auto Biome Randomizer thread started.")
    while not stop_event.is_set() and not sniped_event.is_set():
        logger.write_log("Auto BR: Using Biome Randomizer...")
        with keyboard_lock:
            use_item("Biome Random", 1, True, mkey, kb, settings)

        wait_interval = 2160 
        logger.write_log(f"Auto BR: Waiting {wait_interval} seconds...")
        if stop_event.wait(timeout=wait_interval):
            break
        if sniped_event.is_set(): break
    logger.write_log("Auto Biome Randomizer thread stopped.")

def auto_sc(settings: dict, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb):
    logger = get_logger()
    if stop_event.wait(timeout=5):
        return
    logger.write_log("Auto Strange Controller thread started.")
    while not stop_event.is_set() and not sniped_event.is_set():
        logger.write_log("Auto SC: Using Strange Controller...")
        with keyboard_lock:
            use_item("Strange Control", 1, True, mkey, kb, settings)

        wait_interval = 1260 
        logger.write_log(f"Auto SC: Waiting {wait_interval} seconds...")
        if stop_event.wait(timeout=wait_interval):
            break
        if sniped_event.is_set(): break
    logger.write_log("Auto Strange Controller thread stopped.")

def inventory_screenshot(settings: dict, webhook, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey):
    logger = get_logger()
    if stop_event.wait(timeout=5):
        return
    logger.write_log("Periodic Inventory Screenshot thread started.")
    required_coords = ["inv_button_pos", "items_pos", "search_pos", "close_pos"]
    if not all(coord in COORDS for coord in required_coords):
         logger.write_log("Cannot start Inventory Screenshots: Required coordinates missing.")
         return

    while not stop_event.is_set() and not sniped_event.is_set():
        logger.write_log("Taking inventory screenshot...")
        screenshot_path = os.path.join(MACROPATH, "scr", "screenshot_inventory.png")
        file_to_send = None
        with keyboard_lock:
            try:
                wait_time = settings.get("global_wait_time", 0.2)
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["inv_button_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["inv_button_pos"][1] * COORDS["scr_hei"])))
                time.sleep(wait_time)
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["items_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["items_pos"][1] * COORDS["scr_hei"])))
                time.sleep(wait_time)
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["search_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["search_pos"][1] * COORDS["scr_hei"])))
                time.sleep(0.5) 
                pag.screenshot(screenshot_path)
                time.sleep(0.2)
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
                time.sleep(wait_time)
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
                file_to_send = create_discord_file_from_path(screenshot_path, filename="inventory.png")
            except Exception as e:
                logger.write_log(f"Error taking inventory screenshot: {e}")

                try: mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"]))); time.sleep(0.2); mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
                except: pass

        if file_to_send:
            try:
                emb = discord.Embed(title="Inventory Screenshot")
                emb.set_image(url="attachment://inventory.png")
                emb.timestamp = datetime.now()
                webhook.send(embed=emb, file=file_to_send)
                forward_webhook_msg(
                     primary_webhook_url=webhook.url,
                     secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                     embed=emb, file=file_to_send
                 )
            except Exception as wh_e:
                logger.write_log(f"Error sending inventory screenshot webhook: {wh_e}")
        wait_interval = 1140 
        logger.write_log(f"Inventory Screenshot: Waiting {wait_interval} seconds...")
        if stop_event.wait(timeout=wait_interval):
            break
        if sniped_event.is_set(): break

    logger.write_log("Periodic Inventory Screenshot thread stopped.")

def storage_screenshot(settings: dict, webhook, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey):
    logger = get_logger()
    if stop_event.wait(timeout=5):
        return
    logger.write_log("Periodic Aura Storage Screenshot thread started.")
    required_coords = ["aura_button_pos", "search_pos", "close_pos"]
    if not all(coord in COORDS for coord in required_coords):
         logger.write_log("Cannot start Storage Screenshots: Required coordinates missing.")
         return

    while not stop_event.is_set() and not sniped_event.is_set():
        logger.write_log("Taking aura storage screenshot...")
        screenshot_path = os.path.join(MACROPATH, "scr", "screenshot_storage.png")
        file_to_send = None
        with keyboard_lock:
            try:
                wait_time = settings.get("global_wait_time", 0.2)
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["aura_button_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["aura_button_pos"][1] * COORDS["scr_hei"])))
                time.sleep(wait_time)
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["search_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["search_pos"][1] * COORDS["scr_hei"])))
                time.sleep(0.5)
                pag.screenshot(screenshot_path)
                time.sleep(0.2)
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
                time.sleep(wait_time)
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
                file_to_send = create_discord_file_from_path(screenshot_path, filename="storage.png")
            except Exception as e:
                logger.write_log(f"Error taking storage screenshot: {e}")
                try: mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"]))); time.sleep(0.2); mkey.left_click_xy_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
                except: pass

        if file_to_send:
            try:
                emb = discord.Embed(title="Aura Storage Screenshot")
                emb.set_image(url="attachment://storage.png")
                emb.timestamp = datetime.now()
                webhook.send(embed=emb, file=file_to_send)
                forward_webhook_msg(
                     primary_webhook_url=webhook.url,
                     secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                     embed=emb, file=file_to_send
                 )
            except Exception as wh_e:
                logger.write_log(f"Error sending storage screenshot webhook: {wh_e}")
        wait_interval = 1260 
        logger.write_log(f"Storage Screenshot: Waiting {wait_interval} seconds...")
        if stop_event.wait(timeout=wait_interval):
            break
        if sniped_event.is_set(): break

    logger.write_log("Periodic Aura Storage Screenshot thread stopped.")

def disconnect_prevention(settings: dict, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb):
    logger = get_logger()
    logger.write_log("Disconnect Prevention thread started.")
    ps_link = settings.get("private_server_link", "")
    ps_link_valid = validate_pslink(ps_link)

    if not ps_link_valid:
        logger.write_log("Disconnect Prevention disabled: Invalid or missing private server link in settings.")
        return

    link_code = None
    try:
        if "privateServerLinkCode=" in ps_link:
            link_code = ps_link.split("privateServerLinkCode=")[-1]

    except Exception as e:
        logger.write_log(f"Error extracting link code for disconnect prevention: {e}")

    if not link_code:
        logger.write_log("Disconnect Prevention disabled: Could not extract link code from private server link.")
        return

    logger.write_log("Disconnect Prevention active.")

    while not stop_event.is_set() and not sniped_event.is_set():
        disconnected = False
        try:

            if detect_client_disconnect():
                logger.write_log("Disconnection detected via logs.")
                disconnected = True

            elif not exists_procs_by_name("Windows10Universal.exe") and not exists_procs_by_name("RobloxPlayerBeta.exe"):
                logger.write_log("Disconnection detected via missing Roblox process.")
                disconnected = True

            if disconnected:
                logger.write_log("Attempting to rejoin private server...")
                rejoin_attempts = 0
                max_rejoin_attempts = 5 
                reconnected = False

                try: os.system("taskkill /f /im RobloxPlayerBeta.exe /t > nul 2>&1")
                except: pass
                try: os.system("taskkill /f /im Windows10Universal.exe /t > nul 2>&1")
                except: pass
                time.sleep(5)

                while rejoin_attempts < max_rejoin_attempts and not stop_event.is_set() and not reconnected:
                    rejoin_attempts += 1
                    logger.write_log(f"Rejoin attempt #{rejoin_attempts}...")
                    join_private_server_link(link_code)
                    time.sleep(15) 

                    if exists_procs_by_name("Windows10Universal.exe"):
                        if activate_ms_store_roblox():
                            time.sleep(2)
                            click_ms_store_spawn_button()
                            time.sleep(2)
                            toggle_fullscreen_ms_store()
                            time.sleep(10) 
                        else:
                             logger.write_log("Failed to activate MS Store Roblox window during rejoin.")

                    reconnect_check_start = time.time()
                    while time.time() - reconnect_check_start < 45:
                         if detect_client_reconnect():
                             logger.write_log("Reconnection successful based on logs!")
                             reconnected = True

                             leave_main_menu()
                             break
                         if stop_event.is_set(): break
                         time.sleep(2)
                    if reconnected: break
                    logger.write_log(f"Rejoin attempt #{rejoin_attempts} failed. Waiting before retry...")
                    if not stop_event.is_set(): time.sleep(30)

                if not reconnected:
                    logger.write_log("Failed to reconnect after multiple attempts. Stopping disconnect prevention.")

                    break 

        except Exception as e:
            logger.write_log(f"Error in Disconnect Prevention loop: {e}")

            time.sleep(15)

        wait_interval = 30 
        if not stop_event.is_set() and not sniped_event.is_set():
             stop_event.wait(timeout=wait_interval)

    logger.write_log("Disconnect Prevention thread stopped.")

def storage_full_detection(settings: dict, webhook, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey):

    logger = get_logger()
    logger.write_log("Started Storage Full Detection")

    if stop_event.wait(timeout=5):
        return

    while not stop_event.is_set() and not sniped_event.is_set():

        with keyboard_lock:
            time.sleep(0.1)


def do_obby(settings: dict, webhook, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, ms):
    logger = get_logger()
    if stop_event.wait(timeout=5):
        return
    logger.write_log("Obby/Blessing thread started.")

    is_autocraft = settings.get("auto_craft_mode", False)

    while not stop_event.is_set() and not sniped_event.is_set():
        with keyboard_lock:
            try:
                reset_character()
                time.sleep(1)
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["collection_open_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["collection_open_pos"][1] * COORDS["scr_hei"])))
                time.sleep(0.5)
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["exit_collection_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["exit_collection_pos"][1] * COORDS["scr_hei"])))
                time.sleep(1)
            except Exception as e:
                logger.write_log(f"Error during obby alignment: {e}")
                continue

            logger.write_log("Begin Phase 1 of Obby")
            try:
                mkey.move_to_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
                time.sleep(0.4)
                right_click_drag(500, 0)
                time.sleep(0.4)
                kb.press("w")
                time.sleep(10)
                kb.release("w")
                time.sleep(0.4)
                right_click_drag(-500, 0)
                time.sleep(0.4)
                kb.press("w")
                time.sleep(2)
                kb.release("w")
                time.sleep(0.4)
                right_click_drag(500, 0)
                time.sleep(0.4)
                kb.press("w")
                time.sleep(3)
                kb.release("w")
                time.sleep(0.4)
                kb.press("d")
                time.sleep(4)
                kb.release("d")
                time.sleep(0.4)
                kb.press("w")
                time.sleep(1)
                kb.release("w")
                time.sleep(0.4)
                kb.press("a")
                time.sleep(0.6)
                kb.release("a")
                time.sleep(0.4)
                kb.press("w")
                time.sleep(1)
                kb.release("w")
                time.sleep(1)
            except Exception as e:
                logger.write_log(f"Error during obby phase 1: {e}")
                continue

            logger.write_log("Phase 1 complete, begin phase 2.")

            try:
                run_macro(f"{PATH_DIR}/obby1.mms")
                time.sleep(1)
            except Exception as e:
                logger.write_log(f"Error during obby phase 2: {e}")
                continue

            logger.write_log("Phase 2 complete, begin phase 3.")

            try:
                right_click_drag(0, 600)
                time.sleep(1)
            except Exception as e:
                logger.write_log(f"Error during obby phase 3: {e}")
                continue

            logger.write_log("Phase 3 complete, begin phase 4.")

            try:
                run_macro(f"{PATH_DIR}/obby2.mms")
                time.sleep(1)
            except Exception as e:
                logger.write_log(f"Error during obby phase 4: {e}")
                continue

            logger.write_log("Completed obby, realigning incase of failure.")
            try:
                reset_character()
                time.sleep(1)
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["collection_open_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["collection_open_pos"][1] * COORDS["scr_hei"])))
                time.sleep(0.5)
                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["exit_collection_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["exit_collection_pos"][1] * COORDS["scr_hei"])))
                time.sleep(1)
            except Exception as e:
                logger.write_log(f"Error during obby alignment: {e}")
                continue

            if settings.get("notify_obby_completion", False):
                emb = discord.Embed(
                    title="Completed Obby Blessing",
                    description="Enjoy a 30% luck boost!"
                )
                emb.set_footer(text=f"SolsScope v{LOCALVERSION}")
                emb.set_thumbnail(url="https://static.wikia.nocookie.net/sol-rng/images/a/a5/Basicblessingactualsize.png/revision/latest")
                webhook.send(
                    embed=emb
                )
                forward_webhook_msg(
                    primary_webhook_url=webhook.url,
                    secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                    embed=emb
                )
            
            if is_autocraft:
                logger.write_log("Walking back to Stella's")
                try:
                    reset_character()
                    time.sleep(1)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["collection_open_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["collection_open_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(0.5)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["exit_collection_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["exit_collection_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(1)
                except Exception as e:
                    logger.write_log(f"Error during camera alignment: {e}")
                    continue

                logger.write_log("Begin position alignment.")

                try:
                    mkey.move_to_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(0.4)
                    right_click_drag(1000, 0)
                    time.sleep(0.4)
                    kb.press("d")
                    time.sleep(3)
                    kb.release("d")
                    time.sleep(0.4)
                    kb.press("w")
                    time.sleep(8)
                    kb.release("w")
                    time.sleep(0.4)
                    kb.press("a")
                    time.sleep(3)
                    kb.release("a")
                    time.sleep(0.4)
                    kb.press("w")
                    time.sleep(1)
                    kb.release("w")
                    time.sleep(0.4)
                    kb.press("d")
                    time.sleep(0.75)
                    kb.release("d")
                    time.sleep(0.4)
                    kb.press("w")
                    time.sleep(1)
                    kb.release("w")
                except Exception as e:
                    logger.write_log(f"Error during position alignment: {e}")
                    continue

                logger.write_log("Finished position alignment, walking to Stella.")

                try:
                    right_click_drag(0, 600)
                    time.sleep(1)
                    run_macro(f"{PATH_DIR}/stella.mms")
                    time.sleep(1)
                except Exception as e:
                    logger.write_log(f"Error during walk to Stella's: {e}")
                    continue

        wait_interval = 600 
        logger.write_log(f"Obby: Waiting {wait_interval} seconds...")
        if stop_event.wait(timeout=wait_interval):
            break
        if sniped_event.is_set(): break

    logger.write_log("Obby/Blessing thread stopped.")

def auto_questboard(settings: dict, webhook, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, ms):
    logger = get_logger()
    if stop_event.wait(timeout=5):
        return
    logger.write_log("Auto Quest Board thread started.")

    screenshot_path = os.path.join(MACROPATH, "scr", "screenshot_questboard.png")
    try:
        with open(get_questboard_path(), "r", encoding="utf-8") as f:
            questboard_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        logger.write_log(f"Error loading questboard data: {e}. Auto Quest Board stopped.")
        return
    
    TRACKED_QUESTS_PATH = os.path.join(MACROPATH, "quest_tracker.json")
    
    if not os.path.exists(TRACKED_QUESTS_PATH):
        x = open(TRACKED_QUESTS_PATH, "w")
        x.write("{\"quest_board\" : []}")
        x.close()

    try:
        with open(TRACKED_QUESTS_PATH, "r", encoding="utf-8") as f:
            tracked_quests = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        logger.write_log(f"Error loading tracked quests: {e}. Auto Quest Board stopped.")
        return
    
    while not stop_event.is_set() and not sniped_event.is_set():
        wait_interval = 3600
        time.sleep(2)
        with keyboard_lock:
            reset_character()
            time.sleep(1)
            mkey.left_click_xy_natural(round(float(COORDS_PERCENT["collection_open_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["collection_open_pos"][1] * COORDS["scr_hei"])))
            time.sleep(0.5)
            mkey.left_click_xy_natural(round(float(COORDS_PERCENT["exit_collection_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["exit_collection_pos"][1] * COORDS["scr_hei"])))
            time.sleep(1)
            run_macro(f"{PATH_DIR}/questboard.mms")
            time.sleep(1)
            kb.press("e")
            time.sleep(0.2)
            kb.release("e")
            time.sleep(3)

            previous_quest = None

            detected_quests = []

            mkey.left_click_xy_natural(round(float(COORDS_PERCENT["right_arrow_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["right_arrow_pos"][1] * COORDS["scr_hei"])))
            time.sleep(1)

            for i in range(5):
                pag.screenshot(screenshot_path)            

                image = cv2.imread(screenshot_path)
                if image is None:
                    logger.write_log("Auto Quest Board Error: Failed to read screenshot file.")
                    continue
                
                x1p, y1p, x2p, y2p = COORDS_PERCENT["questboard_title_range"]
                x1 = round(x1p * COORDS["scr_wid"])
                y1 = round(y1p * COORDS["scr_hei"])
                x2 = round(x2p * COORDS["scr_wid"])
                y2 = round(y2p * COORDS["scr_hei"])

                quest_title_crop = image[y1:y2, x1:x2]
                ocr_quest_raw = pytesseract.image_to_string(quest_title_crop).strip()

                ocr_quest_clean = re.sub(r"[^a-zA-Z']", "", ocr_quest_raw).lower()
                detected_quest = fuzzy_match_qb(ocr_quest_clean, ALL_QB)

                if not detected_quest:
                    logger.write_log(f"Auto Quest Board: Could not identify quest from OCR ('{ocr_quest_raw}'). Dismissing.")
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["dismiss_quest_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["dismiss_quest_pos"][1] * COORDS["scr_hei"])))
                else:
                    logger.write_log(f"Auto Quest Board: Detected Quest ('{detected_quest})")

                    if detected_quest in ACCEPTED_QUESTBOARD:

                        quest_data = questboard_data.get(detected_quest, None)

                        if not quest_data:
                            logger.write_log(f"Auto Quest Board: Could not find data for quest ('{detected_quest}'). Skipping")
                            mkey.left_click_xy_natural(round(float(COORDS_PERCENT["exit_questboard_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["exit_questboard_pos"][1] * COORDS["scr_hei"])))
                        else:
                            if settings.get("quests_to_accept", {}).get(detected_quest, False) and detected_quest not in tracked_quests.get("quest_board", []) and len(tracked_quests.get("quest_board", [])) <= 3:
                                logger.write_log(f"Auto Quest Board: Accepted Quest ('{detected_quest}')")
                                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["accept_quest_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["accept_quest_pos"][1] * COORDS["scr_hei"])))
                                time.sleep(0.2)
                                tracked_quests["quest_board"].append(detected_quest)
                                previous_quest = detected_quest
                                with open(TRACKED_QUESTS_PATH, "w") as f:
                                    json.dump(tracked_quests, f, indent=4)
                                description = f"**Objective**: {quest_data.get('objective', "Failed to fetch objective.")}\n**Difficulty**: "
                                for i in range(quest_data.get("difficulty", 1)):
                                    description += ":star:"
                                description += "\n**Rewards**:\n"
                                for rew in quest_data.get("reward", []):
                                    rew_name = rew.get("name", "Error fetching name of reward")
                                    rew_amt = rew.get("amount", "Error fetching amount of reward to receive")
                                    rew_type = rew.get("type", "Error fetching reward type")
                                    rew_chance = rew.get("chance", "Error fetching reward chance")
                                    description += f"   Name: {rew_name}\n   Amount: {rew_amt}\n   Type: {rew_type.capitalize()}\n"
                                    if rew_chance != 1:
                                        description += f"   Chance: {str(int(rew_chance * 100))}%\n"
                                    description += "\n"
                                colour = hex2rgb(QUESTBOARD_RARITY_COLOURS[quest_data.get("difficulty", 1) - 1])
                                emb = discord.Embed(
                                    title=f"Accepted Quest: {detected_quest}",
                                    description=description,
                                    colour=discord.Colour.from_rgb(*colour)
                                )
                                emb.set_thumbnail(url=quest_data.get("img_url", ""))
                                emb.set_footer(text=f"SolsScope v{LOCALVERSION}")
                                webhook.send(
                                    embed=emb
                                )
                                forward_webhook_msg(
                                    primary_webhook_url=webhook.url,
                                    secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                    embed=emb
                                )
                                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["right_arrow_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["right_arrow_pos"][1] * COORDS["scr_hei"])))
                            elif detected_quest in tracked_quests.get("quest_board", []):
                                if previous_quest == detected_quest:
                                    logger.write_log("Quest already accepted and same as previous quest, therefore no more quests.")
                                    break
                                logger.write_log("Quest already accepted, attempting to claim.")
                                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["accept_quest_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["accept_quest_pos"][1] * COORDS["scr_hei"])))
                                previous_quest = detected_quest

                                time.sleep(2)

                                pag.screenshot(screenshot_path)            

                                image = cv2.imread(screenshot_path)
                                if image is None:
                                    logger.write_log("Auto Quest Board Error: Failed to read screenshot file.")
                                    continue
                                
                                x1p, y1p, x2p, y2p = COORDS_PERCENT["questboard_title_range"]
                                x1 = round(x1p * COORDS["scr_wid"])
                                y1 = round(y1p * COORDS["scr_hei"])
                                x2 = round(x2p * COORDS["scr_wid"])
                                y2 = round(y2p * COORDS["scr_hei"])

                                quest_title_crop = image[y1:y2, x1:x2]
                                ocr_quest_raw = pytesseract.image_to_string(quest_title_crop).strip()

                                ocr_quest_clean = re.sub(r"[^a-zA-Z']", "", ocr_quest_raw).lower()
                                detected_quest = fuzzy_match_qb(ocr_quest_clean, ALL_QB)
                                
                                if previous_quest == detected_quest:
                                    logger.write_log("Quest is not yet completed, moving to next quest.")
                                    time.sleep(3)
                                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["right_arrow_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["right_arrow_pos"][1] * COORDS["scr_hei"])))
                                else:
                                    logger.write_log("Quest was completed, removing from tracked quests.")
                                    tracked_quests["quest_board"].remove(previous_quest)
                                    with open(TRACKED_QUESTS_PATH, "w") as f:
                                        json.dump(tracked_quests, f, indent=4)
                                    description = f"**Objective**: {quest_data.get('objective', "Failed to fetch objective.")}\n**Difficulty**: "
                                    for i in range(quest_data.get("difficulty", 1)):
                                        description += ":star:"
                                    description += "\n**Rewards**:\n"
                                    for rew in quest_data.get("reward", []):
                                        rew_name = rew.get("name", "Error fetching name of reward")
                                        rew_amt = rew.get("amount", "Error fetching amount of reward to receive")
                                        rew_type = rew.get("type", "Error fetching reward type")
                                        rew_chance = rew.get("chance", "Error fetching reward chance")
                                        description += f"   Name: {rew_name}\n   Amount: {rew_amt}\n   Type: {rew_type.capitalize()}\n"
                                        if rew_chance != 1:
                                            description += f"   Chance: {str(int(rew_chance * 100))}%\n"
                                        description += "\n"
                                    colour = hex2rgb(QUESTBOARD_RARITY_COLOURS[quest_data.get("difficulty", 1) - 1])
                                    emb = discord.Embed(
                                        title=f"Completed Quest: {previous_quest}",
                                        description=description,
                                        colour=discord.Colour.from_rgb(*colour)
                                    )
                                    emb.set_thumbnail(url=quest_data.get("img_url", ""))
                                    emb.set_footer(text=f"SolsScope v{LOCALVERSION}")
                                    webhook.send(
                                        embed=emb
                                    )
                                    forward_webhook_msg(
                                        primary_webhook_url=webhook.url,
                                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                        embed=emb
                                    )
                            else:
                                logger.write_log(f"Auto Quest Board: Quest ('{detected_quest}') is set to be dismissed.")
                                mkey.left_click_xy_natural(round(float(COORDS_PERCENT["dismiss_quest_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["dismiss_quest_pos"][1] * COORDS["scr_hei"])))
                                previous_quest = detected_quest
                    else:
                        logger.write_log(f"Auto Quest Board: Quest ('{detected_quest}') is not supported yet, dismissing.")
                        mkey.left_click_xy_natural(round(float(COORDS_PERCENT["dismiss_quest_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["dismiss_quest_pos"][1] * COORDS["scr_hei"])))
                        previous_quest = detected_quest
                    time.sleep(3)

                    print(detected_quest, "\n", previous_quest)

            mkey.left_click_xy_natural(round(float(COORDS_PERCENT["exit_questboard_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["exit_questboard_pos"][1] * COORDS["scr_hei"])))
            time.sleep(3)
            reset_character()
            time.sleep(3)
        logger.write_log(f"Auto Quest Board: Waiting {wait_interval} seconds...")
        if stop_event.wait(timeout=wait_interval):
            break
        if sniped_event.is_set(): break
    logger.write_log("Auto Quest Board thread stopped.")



def auto_pop(biome: str, settings: dict, stop_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb):
    logger = get_logger()
    logger.write_log(f"Auto Pop sequence initiated for biome: {biome}")
    biome_lower = biome.lower()

    if biome_lower == "glitched" and settings.get("pop_in_glitch", False):
        pop_settings = settings.get("auto_use_items_in_glitch", {})
    elif biome_lower == "dreamspace" and settings.get("pop_in_dreamspace", False):
        pop_settings = settings.get("auto_use_items_in_dreamspace", {})
    else:
        logger.write_log(f"Auto Pop not configured or enabled for biome '{biome}'. Stopping sequence.")
        return

    if settings.get("change_cutscene_on_pop", True):
         logger.write_log("Auto Pop: Changing cutscene settings...")
         required_coords = ["menu_btn_pos", "settings_btn_pos", "rolling_conf_pos", "cutscene_conf_pos"]
         if not all(c in COORDS for c in required_coords):
             logger.write_log("Cannot change cutscene: Coordinates missing.")
         else:
             with keyboard_lock:
                try:
                    wait_time = settings.get("global_wait_time", 0.2)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["menu_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["menu_btn_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["settings_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["settings_btn_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time + 0.2) 
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["rolling_conf_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["rolling_conf_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["cutscene_conf_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["cutscene_conf_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)

                    kb.press(keyboard.Key.ctrl); kb.press('a'); time.sleep(0.05); kb.release('a'); kb.release(keyboard.Key.ctrl); time.sleep(wait_time)
                    kb.type("9999999999")
                    time.sleep(wait_time)
                    kb.press(keyboard.Key.enter); time.sleep(0.05); kb.release(keyboard.Key.enter)
                    time.sleep(wait_time)

                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["menu_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["menu_btn_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                    mkey.left_click_xy_natural(round(float(COORDS_PERCENT["menu_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["menu_btn_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(wait_time)
                except Exception as cs_e:
                    logger.write_log(f"Error changing cutscene settings: {cs_e}")

                    try: mkey.left_click_xy_natural(round(float(COORDS_PERCENT["menu_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["menu_btn_pos"][1] * COORDS["scr_hei"]))); time.sleep(0.2); mkey.left_click_xy_natural(round(float(COORDS_PERCENT["menu_btn_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["menu_btn_pos"][1] * COORDS["scr_hei"])))
                    except: pass

    item_keys = list(pop_settings.keys()) 
    logger.write_log(f"Auto Pop: Items configured: {item_keys}")

    for item in reversed(item_keys):
        if stop_event.is_set():
            logger.write_log("Auto Pop stopped by user.")
            break

        item_data = pop_settings.get(item, {})
        if not item_data.get("use", False):

            continue

        amount_to_use = item_data.get("amount", 1)
        logger.write_log(f"Auto Pop: Preparing to use {amount_to_use} of '{item}'")

        stackable_items = ["Heavenly Potion", "Potion of Bound", "Oblivion Potion"]
        if item in stackable_items:
            remaining_amount = amount_to_use
            while remaining_amount > 0 and not stop_event.is_set():
                use_amount = min(remaining_amount, 10) 
                logger.write_log(f" > Using {use_amount} of {item} (Remaining: {remaining_amount - use_amount})")
                with keyboard_lock:
                    use_item(item, use_amount, True, mkey, kb, settings)
                remaining_amount -= use_amount
                time.sleep(1.5) 

                current_biome_check = get_latest_hovertext()
                if current_biome_check is None or current_biome_check.lower() != biome_lower:
                     logger.write_log("Auto Pop: Biome ended during item use. Stopping sequence.")
                     return 
        else:
             with keyboard_lock:
                use_item(item, amount_to_use, True, mkey, kb, settings)
             time.sleep(1.0) 

             current_biome_check = get_latest_hovertext()
             if current_biome_check is None or current_biome_check.lower() != biome_lower:
                  logger.write_log("Auto Pop: Biome ended after item use. Stopping sequence.")
                  return

    logger.write_log("Auto Pop sequence finished.")

