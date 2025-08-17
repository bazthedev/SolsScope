"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v1.2.8
Support server: https://discord.gg/8khGXqG7nA
"""

import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/path"))
import time
import random
import pyautogui as pag
import json 
import threading 
from datetime import datetime
import discord 
import re
from PIL import ImageGrab
from gc import collect
from itertools import cycle

try:
    import cv2
    from easyocr import Reader
    MERCHANT_DETECTION_POSSIBLE = True
except ImportError as e:
    MERCHANT_DETECTION_POSSIBLE = False
    print(f"Optional modules for Merchant Detection (cv2, easyocr) not found. Feature disabled.\n{e}")

try:
    #import eden_vip, fish_market, fish_market_abyssal, fishing_spot, obby, questboard, shrine_part1, shrine_part2, shrine_part3
    IMPORTED_ALL_PATHS = True
except ImportError:
    IMPORTED_ALL_PATHS = False
    print("Could not import all required Path Scripts.")

from pynput import keyboard
from pynput import mouse

from constants import (
    MACROPATH, WEBHOOK_ICON_URL, MARI_ITEMS, JESTER_ITEMS,
    POSSIBLE_MERCHANTS, COORDS, LOCALVERSION, JESTER_SELL_ITEMS,
    ACCEPTED_QUESTBOARD, QUESTBOARD_RARITY_COLOURS, PATH_DIR, ALL_QB, DONOTACCEPT_QB,
    COMPLETION_COLOURS, COORDS_PERCENT1610, COORDS_PERCENT43
)
from utils import (
    get_logger, create_discord_file_from_path, hex2rgb, fuzzy_match,
    fuzzy_match_merchant, exists_procs_by_name, validate_pslink, fuzzy_match_auto_sell,
    fuzzy_match_qb, rgb2hex, right_click_drag, left_click_drag, resolve_full_aura_name,
    get_coords_percent, convert_boxes, detect_add_potions, check_tab_menu_open,
    get_autocraft_path
)
from roblox_utils import (
    get_latest_equipped_aura, get_latest_hovertext, detect_client_disconnect,
    detect_client_reconnect, join_private_server_link, leave_main_menu,
    activate_ms_store_roblox, click_ms_store_spawn_button, toggle_fullscreen_ms_store,
    reset_character, detect_ui_nav, get_roblox_window_bbox, check_for_eden_spawn
)
from discord_utils import forward_webhook_msg, create_autocraft_embed
from settings_manager import get_auras_path, get_biomes_path, get_merchant_path, get_questboard_path, get_fish_path

from uinav import (
    open_inventory, open_storage, close_menu, collection_align,
    close_check, search_in_menu, select_item, open_mari, open_jester_shop,
    buy_item, jester_exchange_first, jester_exchange_second, change_rolling_cutscene,
    search_for_potion_in_cauldron, press_craft_button, press_auto_button,
    accept_quest, dismiss_quest, next_quest, exit_quest, search_for_aura, equip_selected_aura,
    add_amount_to_potion, close_cauldron, TGIFRIDAY, merchant_skip_dialogue, open_jester_ex,
    load_keybind
)

from mmint import run_macro

from stats import increment_stat, load_stats



def use_item(item_name: str, amount: int, _close_menu: bool, mkey, kb, settings: dict, reader):
    logger = get_logger()
    logger.write_log(f"Attempting to use item: {item_name} (Amount: {amount})")

    COORDS_PERCENT = get_coords_percent(COORDS)

    if not COORDS_PERCENT:
        logger.write_log("Could not determine screen ratio.")
        return

    try:

        if TGIFRIDAY and check_tab_menu_open(reader, COORDS_PERCENT, COORDS):
            kb.press(keyboard.Key.tab)
            time.sleep(0.05)
            kb.release(keyboard.Key.tab)
            time.sleep(0.05)

        open_inventory(kb, False)
        time.sleep(0.05)
        search_in_menu(kb, False, False, True, False)

        time.sleep(0.05)

        pag.write(item_name, 0.05)

        time.sleep(0.5)

        kb.press(keyboard.Key.enter)
        time.sleep(0.1)
        kb.release(keyboard.Key.enter)
        time.sleep(1)

        select_item(kb, False, False)
#
        time.sleep(0.05)

        kb.press(keyboard.Key.ctrl)
        kb.press("a")
        time.sleep(0.05)
        kb.release("a")
        kb.release(keyboard.Key.ctrl)
        time.sleep(0.05)
        pag.write(str(amount))
        time.sleep(1)
        kb.press(keyboard.Key.enter)
        time.sleep(0.05)
        kb.release(keyboard.Key.enter)
        time.sleep(1)
        kb.press(keyboard.Key.right)
        time.sleep(0.05)
        kb.release(keyboard.Key.right)
        time.sleep(0.05)

        kb.press(keyboard.Key.enter)
        time.sleep(0.05)
        kb.release(keyboard.Key.enter)
        time.sleep(1)

        kb.press(load_keybind())
        time.sleep(0.05)
        kb.release(load_keybind())
        time.sleep(1)

        if _close_menu:
            close_menu(kb, True, True)
        logger.write_log(f"Used item: {item_name}")
    except Exception as e:
        logger.write_log(f"Error during use_item execution: {e}")

        try:
            close_menu(kb, True)
        except Exception as close_e:
            logger.write_log(f"Error trying to close menu after item use error: {close_e}")

def equip_aura(aura_name, unequip, mkey, kb, settings: dict, ignore_next_detection: set, ignore_lock: threading.Lock, reader):
    logger = get_logger()
    try:
        with open(get_auras_path(), "r", encoding="utf-8") as f:
            auras = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        logger.write_log(f"Error loading auras data for detection: {e}. Aura detection stopped.")
        return
    
    COORDS_PERCENT = get_coords_percent(COORDS)

    if not COORDS_PERCENT:
        logger.write_log("Could not determine screen ratio.")
        return
    
    full_aura_name = resolve_full_aura_name(aura_name, auras)
    _ = None
    
    if TGIFRIDAY and not check_tab_menu_open(reader, COORDS_PERCENT, COORDS):
        kb.press(keyboard.Key.tab)
        time.sleep(0.05)
        kb.release(keyboard.Key.tab)
        time.sleep(0.05)

    while _ is None:
        _ = get_latest_equipped_aura()
        try:
            if _.lower() == full_aura_name.lower():
                if not unequip:
                    logger.write_log(f"Aura {full_aura_name} is already equipped.")
                    return
        except Exception as e:
            logger.write_log(f"Error checking current equipped aura: {e}.")

    if unequip:
        logger.write_log(f"Unequipping Aura: {aura_name} (resolved as '{full_aura_name}')")
    else:
        logger.write_log(f"Equipping Aura: {aura_name} (resolved as '{full_aura_name}')")
        with ignore_lock:
            ignore_next_detection.add(full_aura_name.lower())
    try:
        open_storage(kb, True)
        time.sleep(0.2)
        search_for_aura(kb, True, True, aura_name)
        time.sleep(0.2)
        equip_selected_aura(kb, True, True)
    except Exception as e:
        logger.write_log(f"Unable to equip aura: {e}")


def aura_detection(settings: dict, webhook, stop_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, ignore_lock, ignore_next_detection, pause_event, reader):
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

    COORDS_PERCENT = get_coords_percent(COORDS)

    if not COORDS_PERCENT:
        logger.write_log("Could not determine screen ratio.")
        return

    while not stop_event.is_set():
        
        if pause_event.is_set():
            time.sleep(2)
            continue

        try:
            current_aura = get_latest_equipped_aura()

            if current_aura is None:
                time.sleep(2) 
                continue
            
            with ignore_lock:
                if current_aura.lower() in ignore_next_detection:
                    ignore_next_detection.remove(current_aura.lower())
                    logger.write_log(f"Ignoring detection for aura '{current_aura}' due to recent equip.")
                    previous_aura = current_aura
                    time.sleep(settings.get("global_wait_time", 0.2) + 0.5)
                    continue

            if previous_aura is None or current_aura == previous_aura:
                previous_aura = current_aura
                time.sleep(settings.get("global_wait_time", 0.2) + 0.5) 
                continue

            if current_aura == "In Main Menu":
                previous_aura = current_aura
                time.sleep(1)
                continue
            
            aura_key = current_aura.lower()
            if aura_key in auras:
                aura_data = auras[aura_key]
                logger.write_log(f"New aura detected: {current_aura}")
                previous_aura = current_aura 
                rnow = datetime.now()
                current_biome = get_latest_hovertext() or "Unknown (not the aura)"
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
                use_reset_aura = settings.get("use_reset_aura", False)
                if use_reset_aura and current_aura != reset_aura_target and not settings.get("mode", "Normal") == "IDLE" and not settings.get("mode", "Normal") == "Fishing":
                    logger.write_log(f"Resetting aura back to {reset_aura_target}...")
                    with keyboard_lock:
                        try:
                            equip_aura(reset_aura_target, False, mkey, kb, settings, ignore_next_detection, ignore_lock, reader)
                            previous_aura = reset_aura_target
                            time.sleep(2)
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

def biome_detection(settings: dict, webhook, stop_event: threading.Event, sniped_event: threading.Event, mkey, kb, keyboard_lock, pause_event : threading.Event, gui):
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

    while not stop_event.is_set():

        if pause_event.is_set():
            time.sleep(2)
            continue

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
                    is_event = new_biome_data.get("event", False)
                    emb_color_hex = new_biome_data.get("colour", "#808080")
                    emb_rgb = hex2rgb(emb_color_hex)

                    description = f"Biome {current_biome} has started!\nTime: <t:{str(int(time.time()))}>"
                    title = f"Event Biome Started: {current_biome}" if is_event else f"Biome Started: {current_biome}"

                    emb = discord.Embed(
                        title=title,
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
                    increment_stat(current_biome.lower())
                    gui.biomeStatChanged.emit(current_biome.lower())
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

        if not stop_event.is_set():
            time.sleep(settings.get("global_wait_time", 0.2) + 1.0)

    logger.write_log("Biome Detection thread stopped.")

def portable_crack(settings: dict, stop_event: threading.Event, sniped_event: threading.Event, mkey, kb, keyboard_lock, pause_event, reader):

    logger = get_logger()

    afk_in_limbo = settings.get("mode", "Normal") == "Limbo"
    is_idle_mode = settings.get("mode", "Normal") == "IDLE"

    if afk_in_limbo and not is_idle_mode:
        logger.write_log("Portable Crack thread started (Limbo mode is ENABLED).")
        while not stop_event.is_set():

            if pause_event.is_set():
                time.sleep(2)
                continue

            wait_interval = 600
            with keyboard_lock:
                time.sleep(5)
                logger.write_log("Teleporting to limbo...")
                use_item("Portable Crack", 1, True, mkey, kb, settings, reader)
                time.sleep(0.5)

            logger.write_log("Portable Crack: Waiting 10 minutes before using again.")

            if stop_event.wait(timeout=wait_interval):
                break
        logger.write_log("Portable Crack thread stopped.")

def keep_alive(settings: dict, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, kb, pause_event):
    logger = get_logger()
    if stop_event.wait(timeout=5):
        return
    logger.write_log("Keep Alive (Anti-AFK) thread started.")

    while not stop_event.is_set():

        if pause_event.is_set():
            time.sleep(2)
            continue

        wait_interval = random.randint(550, 650)
        logger.write_log(f"Keep Alive: Waiting for {wait_interval} seconds before next action.")

        if stop_event.wait(timeout=wait_interval):
            break

        if sniped_event.is_set():
            break

        with keyboard_lock:
            try:
                logger.write_log("Keep Alive: Performing anti-AFK action (close check).")
                kb.press(keyboard.Key.space)
                time.sleep(0.02)
                kb.release(keyboard.Key.space)
                time.sleep(0.02)
                kb.press(keyboard.Key.space)
                time.sleep(0.02)
                kb.release(keyboard.Key.space)
                time.sleep(0.02)
            except Exception as e:
                logger.write_log(f"Error during Keep Alive action: {e}")

    logger.write_log("Keep Alive (Anti-AFK) thread stopped.")

def merchant_detection(settings: dict, webhook, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, ignore_lock, ignore_next_detection, reader, pause_event):
    logger = get_logger()

    if not MERCHANT_DETECTION_POSSIBLE:
        logger.write_log("Merchant Detection cannot start: Missing dependencies (cv2/easyocr).")
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
        "merchant_box", "manual_boxes"
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

    is_autocraft = settings.get("mode", "Normal") == "Auto Craft"
    has_abyssal = settings.get("has_abyssal_hunter", False)
    afk_in_limbo = settings.get("mode", "Normal") == "Limbo"
    is_idle_mode = settings.get("mode", "Normal") == "IDLE"

    COORDS_PERCENT = get_coords_percent(COORDS)

    if not COORDS_PERCENT:
        logger.write_log("Could not determine screen ratio.")
        return
    
    manual_boxes = convert_boxes(COORDS_PERCENT["manual_boxes"], COORDS["scr_wid"], COORDS["scr_hei"])
    screenshot_path = os.path.join(MACROPATH, "scr", "screenshot_merchant.png")
    ex_screenshot_path = os.path.join(MACROPATH, "scr", "screenshot_exchange.png")
    
    while not stop_event.is_set():

        if pause_event.is_set():
            time.sleep(2)
            continue

        wait_interval = before_check_interval
        logger.write_log(f"Merchant Detection: Waiting for {wait_interval} seconds...")
        if stop_event.wait(timeout=wait_interval):
            break

        logger.write_log("Merchant Detection: Merchant Check Scheduled")
        detected_merchant_name = None
        detected_items = {}
        
        with keyboard_lock:

            if TGIFRIDAY and not check_tab_menu_open(reader, COORDS_PERCENT, COORDS):
                kb.press(keyboard.Key.tab)
                time.sleep(0.05)
                kb.release(keyboard.Key.tab)
                time.sleep(0.05)

            try:
                logger.write_log("Merchant Detection: Using Merchant Teleport item...")
                use_item("Merchant Teleport", 1, True, mkey, kb, settings, reader) 
                time.sleep(settings.get("global_wait_time", 0.2) + 0.5) 

                logger.write_log("Merchant Detection: Attempting interaction (E key)...")
                kb.press('e')
                time.sleep(0.2)
                kb.release('e')
                time.sleep(0.2)
                merchant_skip_dialogue(kb, True, True)
                time.sleep(2)
                merchant_skip_dialogue(kb, True, True)
                time.sleep(2)

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
                
                ocr_results = reader.readtext(merchant_crop, detail=0)
                ocr_merchant_raw = " ".join(ocr_results).strip()

                ocr_merchant_clean = re.sub(r"[^a-zA-Z']", "", ocr_merchant_raw).lower()
                detected_merchant_name = fuzzy_match_merchant(ocr_merchant_clean, POSSIBLE_MERCHANTS)

                if not detected_merchant_name:
                    logger.write_log(f"Merchant Detection: Could not identify merchant from OCR ('{ocr_merchant_raw}'). Skipping.")
                    continue

                merchant_short_name = detected_merchant_name.split("'")[0] 
                logger.write_log(f"Merchant Detected: {merchant_short_name} (Raw OCR: '{ocr_merchant_raw}')")
                rnow = datetime.now()

                logger.write_log("Merchant Detection: Opening Shop...")
                if merchant_short_name == "Mari":
                    open_mari(kb, True, True)
                elif merchant_short_name == "Jester":
                    if TGIFRIDAY:
                        open_mari(kb, True, True)
                    else:
                        open_jester_shop(kb, True, True)
                    open_mari(kb, True, True)
                time.sleep(3)

                del image

                pag.screenshot(screenshot_path)

                image = cv2.imread(screenshot_path)
                if image is None:
                    logger.write_log("Merchant Detection Error: Failed to read screenshot file.")
                    continue

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
                item_ocr_results = []
                for box_name, (x1, y1, x2, y2) in manual_boxes.items():
                    if x1 >= image.shape[1] or y1 >= image.shape[0] or x2 <= x1 or y2 <= y1:
                        logger.write_log(f"Warning: Invalid coordinates for {box_name}. Skipping OCR.")
                        continue

                    cropped = image[y1:y2, x1:x2]

                    ocr_results = reader.readtext(cropped, detail=0)
                    ocr_raw = " ".join(ocr_results).strip().replace('\n', ' ')

                    matched = fuzzy_match(ocr_raw, item_list, threshold=0.5)
                    logger.write_log(f" > {box_name}: OCR='{ocr_raw}', Match='{matched}'")

                    detected_items[box_name] = matched
                    item_ocr_results.append(f"**{box_name}:** `{matched}` (Raw: `{ocr_raw}`)")
                emb.add_field(name="Detected Items", value="\n".join(item_ocr_results) if item_ocr_results else "None", inline=False)

                if not (settings.get("mention", False) and settings.get("mention_id", 0) != 0) and settings.get(f"{merchant_short_name.lower()}_ping_id", 0) != 0:
                    ping_content = f"<@{settings['mention_id']}>{ping_content}"

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
                    if TGIFRIDAY and not check_tab_menu_open(reader, COORDS_PERCENT, COORDS):
                        kb.press(keyboard.Key.tab)
                        time.sleep(0.05)
                        kb.release(keyboard.Key.tab)
                        time.sleep(0.05)
                    for box_name, item_name in items_to_buy.items():
                        try:
                            buy_item(kb, True, True, str(purchase_settings.get(item_name).get("amount", 1)), box_name[-1])
                            logger.write_log(f"Auto-purchased: {item_name}")
                            time.sleep(3)

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
                        except Exception as buy_e:
                            logger.write_log(f"Error auto-purchasing {item_name}: {buy_e}")

                if auto_sell and merchant_short_name == "Jester":
                    time.sleep(0.2)
                    kb.press('e')
                    time.sleep(0.2)
                    kb.release('e')
                    merchant_skip_dialogue(kb, True, True)
                    time.sleep(3)
                    merchant_skip_dialogue(kb, True, True)
                    time.sleep(3)
                    if TGIFRIDAY:
                        open_jester_shop(kb, True, True)
                    else:
                        open_jester_ex(kb, True, True)
                    time.sleep(3)
                    while not stop_event.is_set():
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
                        ocr_results = reader.readtext(exchange_crop, detail=0)
                        ocr_ex_item_raw = " ".join(ocr_results).strip().replace('\n', ' ')
                        ocr_ex_item_clean = re.sub(r"[^a-zA-Z']", "", ocr_ex_item_raw).lower()

                        detected_item_name = fuzzy_match_auto_sell(ocr_ex_item_clean, JESTER_SELL_ITEMS)
                        logger.write_log(f"Item: {detected_item_name} || OCR: {ocr_ex_item_raw}")
                        if detected_item_name == "Void Coin":
                            logger.write_log("Void Coin detected in first slot, skipping to second slot.")
                            _break_second = False
                            while detected_item_name in JESTER_ITEMS and not stop_event.is_set():
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
                                ocr_results = reader.readtext(exchange_crop, detail=0)
                                ocr_ex_item_raw = " ".join(ocr_results).strip().replace('\n', ' ')
                                ocr_ex_item_clean = re.sub(r"[^a-zA-Z']", "", ocr_ex_item_raw).lower()

                                detected_item_name = fuzzy_match_auto_sell(ocr_ex_item_clean, JESTER_SELL_ITEMS)
                                if detected_item_name == "Void Coin":
                                    _break_second = True
                                    logger.write_log("Auto-Sell: Void coin detected in second slot, stopping job.")
                                    break
                                elif detected_item_name in JESTER_SELL_ITEMS and settings.get("items_to_sell", {}).get(detected_item_name, False):
                                    logger.write_log(f"Auto-Sell: {detected_item_name} was detected")
                                    time.sleep(0.2)
                                    jester_exchange_first(kb, True, True, settings.get("amount_of_item_to_sell", 1))
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
                            jester_exchange_second(kb, True, True, settings.get("amount_of_item_to_sell", 1))
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

                    close_menu(kb, True, is_merchant=True)
                    time.sleep(0.5)
                    reset_character()
                    time.sleep(3)

                if afk_in_limbo and not is_idle_mode:
                    logger.write_log("Teleporting back to limbo...")
                    use_item("Portable Crack", 1, True, mkey, kb, settings, reader)
                    time.sleep(0.5)

                if stop_event.wait(timeout=cooldown_interval):
                    break

            except Exception as e:
                logger.write_log(f"Error in Merchant Detection loop: {e}")
                import traceback
                logger.write_log(traceback.format_exc()) 

                try:
                    close_menu(kb, True)
                except Exception:
                    pass

            


    logger.write_log("Merchant Detection thread stopped.")

def auto_craft(webhook, settings: dict, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, ms, ignore_lock, ignore_next_detection, reader, pause_event, potions_crafted):
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

    wait_between = []

    for item in items_to_craft:
        wait_between.append(item)
        for _ in range(0, 4):
            wait_between.append(None)

    auto_craft_loop = cycle(wait_between)
    job = next(auto_craft_loop)

    has_abyssal = settings.get("has_abyssal_hunter", False)

    if stop_event.wait(timeout=10):
        return
    
    if not settings.get("do_not_walk_to_stella", True):
        logger.write_log("Auto Craft: Walking To Stella's")
        with keyboard_lock:
            logger.write_log("Walking back to Stella's")
            try:
                reset_character()
                time.sleep(1)
                reset_character()
                time.sleep(1)
                collection_align(kb, True)
                time.sleep(1)
            except Exception as e:
                logger.write_log(f"Error during camera alignment: {e}")

            logger.write_log("Begin position alignment.")

            if not has_abyssal:
                try:
                    close_check(kb, True)
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

            else:
                saved_aura = None
                while saved_aura is None:
                    try:
                        saved_aura = get_latest_equipped_aura().lower()
                    except Exception as e:
                        logger.write_log(f"Error checking current equipped aura: {e}.")
                logger.write_log("Walking to Stella with Abyssal Hunter")
                time.sleep(2)
                equip_aura("Abyssal", False, mkey, kb, settings, ignore_next_detection, ignore_lock, reader)
                time.sleep(2)
                try:
                    close_check(kb, True)
                    time.sleep(0.4)
                    right_click_drag(1000, 0)
                    time.sleep(0.4)
                    kb.press("d")
                    time.sleep(1.8)
                    kb.release("d")
                    time.sleep(0.4)
                    kb.press("w")
                    time.sleep(6)
                    kb.release("w")
                    time.sleep(0.4)
                    kb.press("a")
                    time.sleep(1.3)
                    kb.release("a")
                    time.sleep(0.4)
                    kb.press("w")
                    time.sleep(0.5)
                    kb.release("w")
                    time.sleep(0.4)
                    kb.press("d")
                    time.sleep(0.4)
                    kb.release("d")
                    time.sleep(0.4)
                    kb.press("w")
                    time.sleep(0.5)
                    kb.release("w")
                except Exception as e:
                    logger.write_log(f"Error during position alignment: {e}")

            logger.write_log("Finished position alignment, walking to Stella.")

            time.sleep(1)

            if not has_abyssal:
                try:
                    right_click_drag(0, 600)
                    time.sleep(1)
                    run_macro(f"{PATH_DIR}/stella.mms")
                    time.sleep(1)
                except Exception as e:
                    logger.write_log(f"Error during walk to Stella's: {e}")
            else:
                try:
                    right_click_drag(0, 600)
                    time.sleep(1)
                    run_macro(f"{PATH_DIR}/stella_abyssal.mms")
                    time.sleep(1)
                except Exception as e:
                    logger.write_log(f"Error during walk to Stella's: {e}")
                if saved_aura:
                    equip_aura(saved_aura, False, mkey, kb, settings, ignore_next_detection, ignore_lock, reader)
                else:
                    equip_aura("Abyssal", True, mkey, kb, settings, ignore_next_detection, ignore_lock, reader)

    else:
        logger.write_log("Ensure you are standing near the cauldron with the 'F' prompt visible.")

    COORDS_PERCENT = get_coords_percent(COORDS)

    if not COORDS_PERCENT:
        logger.write_log("Could not determine screen ratio.")
        return
    
    screenshot_path = os.path.join(MACROPATH, "scr", "screenshot_autocraft.png")

    send_item_crafted_notification = settings.get("send_item_crafted_notification", True)

    while not stop_event.is_set():

        if pause_event.is_set():
            time.sleep(2)
            continue

        with keyboard_lock:

            try:
                wait_time = settings.get("global_wait_time", 0.2)

                if TGIFRIDAY and not check_tab_menu_open(reader, COORDS_PERCENT, COORDS):
                    kb.press(keyboard.Key.tab)
                    time.sleep(0.05)
                    kb.release(keyboard.Key.tab)
                    time.sleep(0.05)

                if settings["auto_craft_item"].get("Jewelry Potion", False):
                    search_for_potion_in_cauldron(kb, True, True, "Jewelry")

                    time.sleep(0.2)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    if not _[0]:
                        add_amount_to_potion(kb, True, True, 20)

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _prev_jewel = True
                        else:
                            _prev_jewel = False

                    press_craft_button(kb, True, True)

                    if send_item_crafted_notification:
                        _jewel_isfull = False

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _jewel_isfull = True
                        else:
                            _jewel_isfull = False

                        if _prev_jewel != _jewel_isfull:
                            potions_crafted += 1
                            emb = create_autocraft_embed("Jewelry Potion")
                            if emb:
                                try:
                                    webhook.send(embed=emb)
                                    forward_webhook_msg(
                                        primary_webhook_url=webhook.url,
                                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                        embed=emb
                                    )
                                except Exception as wh_e:
                                    logger.write_log(f"Error sending potion crafted webhook: {wh_e}")

                        _prev_jewel = _jewel_isfull

                    if job == "Jewelry Potion":
                        press_auto_button(kb, True, True)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Zombie Potion", False):
                    search_for_potion_in_cauldron(kb, True, True, "Zombie")

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    if not _[0]:
                        add_amount_to_potion(kb, True, True, 10)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 1)
                    elif not _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 1, 1)

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _prev_zomb = True
                        else:
                            _prev_zomb = False

                    press_craft_button(kb, True, True)

                    if send_item_crafted_notification:
                        _zomb_isfull = False

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _zomb_isfull = True
                        else:
                            _zomb_isfull = False

                        if _prev_zomb != _zomb_isfull:
                            potions_crafted += 1
                            emb = create_autocraft_embed("Zombie Potion")
                            if emb:
                                try:
                                    webhook.send(embed=emb)
                                    forward_webhook_msg(
                                        primary_webhook_url=webhook.url,
                                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                        embed=emb
                                    )
                                except Exception as wh_e:
                                    logger.write_log(f"Error sending potion crafted webhook: {wh_e}")

                        _prev_zomb = _zomb_isfull

                    if job == "Zombie Potion":
                        press_auto_button(kb, True, True)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Rage Potion", False):
                    search_for_potion_in_cauldron(kb, True, True, "Rage")

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    if not _[0]:
                        add_amount_to_potion(kb, True, True, 10)

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _prev_rage = True
                        else:
                            _prev_rage = False

                    press_craft_button(kb, True, True)

                    if send_item_crafted_notification:
                        _rage_isfull = False

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _rage_isfull = True
                        else:
                            _rage_isfull = False

                        if _prev_rage != _rage_isfull:
                            potions_crafted += 1
                            emb = create_autocraft_embed("Rage Potion")
                            if emb:
                                try:
                                    webhook.send(embed=emb)
                                    forward_webhook_msg(
                                        primary_webhook_url=webhook.url,
                                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                        embed=emb
                                    )
                                except Exception as wh_e:
                                    logger.write_log(f"Error sending potion crafted webhook: {wh_e}")

                        _prev_rage = _rage_isfull

                    if job == "Rage Potion":
                        press_auto_button(kb, True, True)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Diver Potion", False):
                    search_for_potion_in_cauldron(kb, True, True, "Diver")

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    if not _[0]:
                        add_amount_to_potion(kb, True, True, 10)
                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                        if _[0] and not _[1]:
                            add_amount_to_potion(kb, True, True, 1)
                        elif not _[0] and not _[1]:
                            add_amount_to_potion(kb, True, True, 1, 1)
                    elif _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 1)

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _prev_dive = True
                        else:
                            _prev_dive = False

                    press_craft_button(kb, True, True)

                    if send_item_crafted_notification:
                        _diver_isfull = False

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _diver_isfull = True
                        else:
                            _diver_isfull = False

                        if _prev_dive != _diver_isfull:
                            potions_crafted += 1
                            emb = create_autocraft_embed("Diver Potion")
                            if emb:
                                try:
                                    webhook.send(embed=emb)
                                    forward_webhook_msg(
                                        primary_webhook_url=webhook.url,
                                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                        embed=emb
                                    )
                                except Exception as wh_e:
                                    logger.write_log(f"Error sending potion crafted webhook: {wh_e}")

                        _prev_dive = _diver_isfull

                    if job == "Diver Potion":
                        press_auto_button(kb, True, True)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Potion of Bound", False):
                    search_for_potion_in_cauldron(kb, True, True, "Bound")

                    time.sleep(0.2)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    if not _[0]:
                        add_amount_to_potion(kb, True, True, 1)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 3)
                    elif not _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 3, 1)
                    
                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0]:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 10)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 10, 1)
                    else:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 10, 1)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 10, 2)

                    if TGIFRIDAY:
                        mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, -30); time.sleep(0.2)
                    ms.scroll(0, -30); time.sleep(0.2)
                    _s = detect_add_potions(True, reader, COORDS_PERCENT, COORDS)

                    if TGIFRIDAY:
                        time.sleep(0.2)
                        mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        moves = get_autocraft_path(_, _s, 4)
                        if moves != -1:
                            add_amount_to_potion(kb, True, True, 100, moves)
                    else:
                        if not _s[2]:
                            add_amount_to_potion(kb, True, True, 100, 0, True)

                    if send_item_crafted_notification:
                        time.sleep(0.2)
                        mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                        ms.scroll(0, -30); time.sleep(0.2)
                        ms.scroll(0, -30); time.sleep(0.2)

                        _s = detect_add_potions(True, reader, COORDS_PERCENT, COORDS)

                        if _s[2]:
                            _prev_bound = True
                        else:
                            _prev_bound = False

                    press_craft_button(kb, True, True)

                    if send_item_crafted_notification:
                        _bound_isfull = False

                        _s = detect_add_potions(True, reader, COORDS_PERCENT, COORDS)

                        if _s[2]:
                            _bound_isfull = True
                        else:
                            _bound_isfull = False

                        if _prev_bound != _bound_isfull:
                            potions_crafted += 1
                            emb = create_autocraft_embed("Potion of Bound")
                            if emb:
                                try:
                                    webhook.send(embed=emb)
                                    forward_webhook_msg(
                                        primary_webhook_url=webhook.url,
                                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                        embed=emb
                                    )
                                except Exception as wh_e:
                                    logger.write_log(f"Error sending potion crafted webhook: {wh_e}")

                        _prev_bound = _bound_isfull
                    
                    time.sleep(0.2)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)

                    if job == "Potion of Bound":
                        press_auto_button(kb, True, True)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Heavenly Potion", False):
                    search_for_potion_in_cauldron(kb, True, True, "Heavenly")

                    time.sleep(0.2)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    if not _[0]:
                        add_amount_to_potion(kb, True, True, 250)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 2)
                    elif not _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 2, 1)
                    
                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0]:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 1)
                    else:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 1)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 2)

                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, -30); time.sleep(0.2)
                    ms.scroll(0, -30); time.sleep(0.2)

                    _s = detect_add_potions(True, reader, COORDS_PERCENT, COORDS)

                    if TGIFRIDAY:
                        time.sleep(0.2)
                        mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                        moves = get_autocraft_path(_, _s, 5)
                        if moves != -1:
                            add_amount_to_potion(kb, True, True, 5, moves)
                    else:                    
                        if not _s[2]:
                            add_amount_to_potion(kb, True, True, 5, 0, True)

                    if TGIFRIDAY:
                        time.sleep(0.2)
                        mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    time.sleep(0.2)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, -30); time.sleep(0.2)
                    ms.scroll(0, -30); time.sleep(0.2)

                    _s = detect_add_potions(True, reader, COORDS_PERCENT, COORDS)

                    if TGIFRIDAY:
                        time.sleep(0.2)
                        mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        moves = get_autocraft_path(_, _s, 4)
                        if moves != -1:
                            add_amount_to_potion(kb, True, True, 2, moves)
                    else:
                    
                        if not _s[2] and not _s[1]:
                            add_amount_to_potion(kb, True, True, 2, 1, True)
                        elif _s[2] and not _s[1]:
                            add_amount_to_potion(kb, True, True, 2, 0, True)
                    
                    time.sleep(0.2)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _prev_heaven = True
                        else:
                            _prev_heaven = False

                    press_craft_button(kb, True, True)

                    if send_item_crafted_notification:
                        _heaven_isfull = False

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _heaven_isfull = True
                        else:
                            _heaven_isfull = False

                        if _prev_heaven != _heaven_isfull:
                            potions_crafted += 1
                            emb = create_autocraft_embed("Heavenly Potion")
                            if emb:
                                try:
                                    webhook.send(embed=emb)
                                    forward_webhook_msg(
                                        primary_webhook_url=webhook.url,
                                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                        embed=emb
                                    )
                                except Exception as wh_e:
                                    logger.write_log(f"Error sending potion crafted webhook: {wh_e}")

                        _prev_heaven = _heaven_isfull

                    if job == "Heavenly Potion":
                        press_auto_button(kb, True, True)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Godly Potion (Zeus)", False):
                    search_for_potion_in_cauldron(kb, True, True, "Zeus")

                    time.sleep(0.2)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    if not _[0]:
                        add_amount_to_potion(kb, True, True, 25)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 25)
                    elif not _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 25, 1)
                    
                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0]:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 1)
                    else:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 1)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 2)


                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, -30); time.sleep(0.2)
                    ms.scroll(0, -30); time.sleep(0.2)

                    _s = detect_add_potions(True, reader, COORDS_PERCENT, COORDS)

                    if TGIFRIDAY:
                        time.sleep(0.2)
                        mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                        moves = get_autocraft_path(_, _s, 5)
                        if moves != -1:
                            add_amount_to_potion(kb, True, True, 15, moves)
                    else:
                        if not _s[2]:
                            add_amount_to_potion(kb, True, True, 15, 0, True)

                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, -30); time.sleep(0.2)
                    ms.scroll(0, -30); time.sleep(0.2)

                    _s = detect_add_potions(True, reader, COORDS_PERCENT, COORDS)

                    
                    if TGIFRIDAY:
                        time.sleep(0.2)
                        mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                        moves = get_autocraft_path(_, _s, 4)
                        if moves != -1:
                            add_amount_to_potion(kb, True, True, 1, moves)
                    else:
                        if not _s[2] and not _s[1]:
                            add_amount_to_potion(kb, True, True, 1, 1, True)
                        elif _s[2] and not _s[1]:
                            add_amount_to_potion(kb, True, True, 1, 0, True)
                    
                    time.sleep(0.2)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _prev_zeus = True
                        else:
                            _prev_zeus = False

                    press_craft_button(kb, True, True)

                    if send_item_crafted_notification:
                        _zeus_isfull = False

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _zeus_isfull = True
                        else:
                            _zeus_isfull = False

                        if _prev_zeus != _zeus_isfull:
                            potions_crafted += 1
                            emb = create_autocraft_embed("Godly Potion (Zeus)")
                            if emb:
                                try:
                                    webhook.send(embed=emb)
                                    forward_webhook_msg(
                                        primary_webhook_url=webhook.url,
                                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                        embed=emb
                                    )
                                except Exception as wh_e:
                                    logger.write_log(f"Error sending potion crafted webhook: {wh_e}")

                        _prev_zeus = _zeus_isfull

                    if job == "Godly Potion (Zeus)":
                        press_auto_button(kb, True, True)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Godly Potion (Poseidon)", False):
                    search_for_potion_in_cauldron(kb, True, True, "Poseidon")

                    time.sleep(0.2)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    if not _[0]:
                        add_amount_to_potion(kb, True, True, 50)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 1)
                    elif not _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 1, 1)
                    
                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0]:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 1)
                    else:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 1)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 2)

                    if TGIFRIDAY:
                        mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, -30); time.sleep(0.2)
                    ms.scroll(0, -30); time.sleep(0.2)
                    _s = detect_add_potions(True, reader, COORDS_PERCENT, COORDS)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    
                    if TGIFRIDAY:
                        moves = get_autocraft_path(_, _s, 4)
                        if moves != -1:
                            add_amount_to_potion(kb, True, True, 1, moves)
                    else:
                        if not _s[2]:
                            add_amount_to_potion(kb, True, True, 1, 0, True)
                    
                    time.sleep(0.2)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _prev_poseidon = True
                        else:
                            _prev_poseidon = False

                    press_craft_button(kb, True, True)

                    if send_item_crafted_notification:
                        _poseidon_isfull = False

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _poseidon_isfull = True
                        else:
                            _poseidon_isfull = False

                        if _prev_poseidon != _poseidon_isfull:
                            potions_crafted += 1
                            emb = create_autocraft_embed("Godly Potion (Poseidon)")
                            if emb:
                                try:
                                    webhook.send(embed=emb)
                                    forward_webhook_msg(
                                        primary_webhook_url=webhook.url,
                                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                        embed=emb
                                    )
                                except Exception as wh_e:
                                    logger.write_log(f"Error sending potion crafted webhook: {wh_e}")

                        _prev_poseidon = _poseidon_isfull

                    if job == "Godly Potion (Poseidon)":
                        press_auto_button(kb, True, True)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Godly Potion (Hades)", False):
                    search_for_potion_in_cauldron(kb, True, True, "Hades")

                    time.sleep(0.2)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    if not _[0]:
                        add_amount_to_potion(kb, True, True, 50)
                        
                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 1)
                    elif not _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 1, 1)

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _prev_hades = True
                        else:
                            _prev_hades = False

                    press_craft_button(kb, True, True)

                    if send_item_crafted_notification:
                        _hades_isfull = False

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _hades_isfull = True
                        else:
                            _hades_isfull = False

                        if _prev_hades != _hades_isfull:
                            potions_crafted += 1
                            emb = create_autocraft_embed("Godly Potion (Hades)")
                            if emb:
                                try:
                                    webhook.send(embed=emb)
                                    forward_webhook_msg(
                                        primary_webhook_url=webhook.url,
                                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                        embed=emb
                                    )
                                except Exception as wh_e:
                                    logger.write_log(f"Error sending potion crafted webhook: {wh_e}")

                        _prev_hades = _hades_isfull

                    if job == "Godly Potion (Hades)":
                        press_auto_button(kb, True, True)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Warp Potion", False):
                    search_for_potion_in_cauldron(kb, True, True, "Warp")

                    time.sleep(0.2)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    if not _[0]:
                        add_amount_to_potion(kb, True, True, 1)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 5)
                    elif not _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 5, 1)
                    
                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0]:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 7)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 7, 1)
                    else:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 7, 1)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 7, 2)

                    if TGIFRIDAY:
                        mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, -30); time.sleep(0.2)
                    ms.scroll(0, -30); time.sleep(0.2)
                    _s = detect_add_potions(True, reader, COORDS_PERCENT, COORDS)

                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    
                    if TGIFRIDAY:
                        moves = get_autocraft_path(_, _s, 6)
                        if moves != -1:
                            add_amount_to_potion(kb, True, True, 1000, moves)
                    else:
                        if not _s[0]:
                            add_amount_to_potion(kb, True, True, 1000, 0, True)

                    if send_item_crafted_notification:                        
                        time.sleep(0.2)
                        mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                        ms.scroll(0, -30); time.sleep(0.2)
                        ms.scroll(0, -30); time.sleep(0.2)

                        _s = detect_add_potions(True, reader, COORDS_PERCENT, COORDS)

                        if _s[2]:
                            _prev_warp = True
                        else:
                            _prev_warp = False

                    press_craft_button(kb, True, True)

                    if send_item_crafted_notification:
                        _warp_isfull = False

                        _s = detect_add_potions(True, reader, COORDS_PERCENT, COORDS)

                        if _s[2]:
                            _warp_isfull = True
                        else:
                            _warp_isfull = False

                        if _prev_warp != _warp_isfull:
                            potions_crafted += 1
                            emb = create_autocraft_embed("Warp Potion")
                            if emb:
                                try:
                                    webhook.send(embed=emb)
                                    forward_webhook_msg(
                                        primary_webhook_url=webhook.url,
                                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                        embed=emb
                                    )
                                except Exception as wh_e:
                                    logger.write_log(f"Error sending potion crafted webhook: {wh_e}")

                        _prev_warp = _warp_isfull
                    
                    time.sleep(0.2)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)

                    if job == "Warp Potion":
                        press_auto_button(kb, True, True)
                    time.sleep(1)

                if settings["auto_craft_item"].get("Godlike Potion", False):
                    search_for_potion_in_cauldron(kb, True, True, "Godlike")

                    time.sleep(0.2)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    if not _[0]:
                        add_amount_to_potion(kb, True, True, 1)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 1)
                    elif not _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 1, 1)
                    
                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0]:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 1)
                    else:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 1)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 2)

                    if TGIFRIDAY:
                        mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        ms.scroll(0, 30); time.sleep(0.2)
                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, -30); time.sleep(0.2)
                    ms.scroll(0, -30); time.sleep(0.2)
                    _s = detect_add_potions(True, reader, COORDS_PERCENT, COORDS)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    
                    if TGIFRIDAY:
                        moves = get_autocraft_path(_, _s, 4)
                        if moves != -1:
                            add_amount_to_potion(kb, True, True, 600, moves)
                    else:
                        if not _s[2]:
                            add_amount_to_potion(kb, True, True, 600, 0, True)

                    if send_item_crafted_notification:                        
                        time.sleep(0.2)
                        mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                        time.sleep(0.2)
                        ms.scroll(0, -30); time.sleep(0.2)
                        ms.scroll(0, -30); time.sleep(0.2)

                        _s = detect_add_potions(True, reader, COORDS_PERCENT, COORDS)

                        if _s[2]:
                            _prev_godlike = True
                        else:
                            _prev_godlike = False

                    press_craft_button(kb, True, True)

                    if send_item_crafted_notification:
                        _godlike_isfull = False

                        _s = detect_add_potions(True, reader, COORDS_PERCENT, COORDS)

                        if _s[2]:
                            _godlike_isfull = True
                        else:
                            _godlike_isfull = False

                        if _prev_godlike != _godlike_isfull:
                            potions_crafted += 1
                            emb = create_autocraft_embed("Godlike Potion")
                            if emb:
                                try:
                                    webhook.send(embed=emb)
                                    forward_webhook_msg(
                                        primary_webhook_url=webhook.url,
                                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                        embed=emb
                                    )
                                except Exception as wh_e:
                                    logger.write_log(f"Error sending potion crafted webhook: {wh_e}")

                        _prev_godlike = _godlike_isfull
                    
                    time.sleep(0.2)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)

                if settings["auto_craft_item"].get("Forbidden Potion I", False):
                    search_for_potion_in_cauldron(kb, True, True, "Forbidden Potion I")

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    if not _[0]:
                        add_amount_to_potion(kb, True, True, 2)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 1)
                    elif not _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 1, 1)
                    
                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0]:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 1)
                    else:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 1)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 2)

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _prev_f1 = True
                        else:
                            _prev_f1 = False

                    press_craft_button(kb, True, True)

                    if send_item_crafted_notification:
                        _f1_isfull = False

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _f1_isfull = True
                        else:
                            _f1_isfull = False

                        if _prev_f1 != _f1_isfull:
                            potions_crafted += 1
                            emb = create_autocraft_embed("Forbidden Potion I")
                            if emb:
                                try:
                                    webhook.send(embed=emb)
                                    forward_webhook_msg(
                                        primary_webhook_url=webhook.url,
                                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                        embed=emb
                                    )
                                except Exception as wh_e:
                                    logger.write_log(f"Error sending potion crafted webhook: {wh_e}")

                        _prev_f1 = _f1_isfull
                
                if settings["auto_craft_item"].get("Forbidden Potion II", False):
                    search_for_potion_in_cauldron(kb, True, True, "Forbidden Potion II")
                    press_craft_button(kb, True, True)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    if not _[0]:
                        add_amount_to_potion(kb, True, True, 20)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 10)
                    elif not _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 10, 1)
                    
                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0]:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 1)
                    else:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 1)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 2)

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _prev_f2 = True
                        else:
                            _prev_f2 = False

                    press_craft_button(kb, True, True)

                    if send_item_crafted_notification:
                        _f2_isfull = False

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _f2_isfull = True
                        else:
                            _f2_isfull = False

                        if _prev_f2 != _f2_isfull:
                            potions_crafted += 1
                            emb = create_autocraft_embed("Forbidden Potion II")
                            if emb:
                                try:
                                    webhook.send(embed=emb)
                                    forward_webhook_msg(
                                        primary_webhook_url=webhook.url,
                                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                        embed=emb
                                    )
                                except Exception as wh_e:
                                    logger.write_log(f"Error sending potion crafted webhook: {wh_e}")

                        _prev_f2 = _f2_isfull

                if settings["auto_craft_item"].get("Forbidden Potion III", False):
                    search_for_potion_in_cauldron(kb, True, True, "Forbidden Potion III")
                    press_craft_button(kb, True, True)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                    if not _[0]:
                        add_amount_to_potion(kb, True, True, 100)

                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 65)
                    elif not _[0] and not _[1]:
                        add_amount_to_potion(kb, True, True, 65, 1)
                    
                    _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)
                    if _[0]:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 1)
                    else:
                        if _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 1)
                        elif not _[1] and not _[2]:
                            add_amount_to_potion(kb, True, True, 1, 2)
                    
                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _prev_f3 = True
                        else:
                            _prev_f3 = False

                    press_craft_button(kb, True, True)

                    if send_item_crafted_notification:
                        _f3_isfull = False

                        _ = detect_add_potions(False, reader, COORDS_PERCENT, COORDS)

                        if _[0]:
                            _f3_isfull = True
                        else:
                            _f3_isfull = False

                        if _prev_f3 != _f3_isfull:
                            potions_crafted += 1
                            emb = create_autocraft_embed("Forbidden Potion III")
                            if emb:
                                try:
                                    webhook.send(embed=emb)
                                    forward_webhook_msg(
                                        primary_webhook_url=webhook.url,
                                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                        embed=emb
                                    )
                                except Exception as wh_e:
                                    logger.write_log(f"Error sending potion crafted webhook: {wh_e}")

                        _prev_f3 = _f3_isfull

                time.sleep(1)
                kb.press('f')
                time.sleep(0.2)
                kb.release('f')
                time.sleep(1)
                
                close_cauldron(kb, True, True)

                time.sleep(1)
                mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                time.sleep(0.2)
                ms.scroll(0, -30); time.sleep(0.2)
                ms.scroll(0, -30); time.sleep(0.2)

                time.sleep(1)


            except Exception as craft_e:
                logger.write_log(f"Error during auto craft: {craft_e}")
                
                time.sleep(1)
                kb.press('f')
                time.sleep(0.2)
                kb.release('f')
                time.sleep(1)
                
                close_cauldron(kb, True, True)

                time.sleep(1)
                mkey.move_to_natural(round(float(COORDS_PERCENT["scroll_mouse_position"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["scroll_mouse_position"][1] * COORDS["scr_hei"])))
                time.sleep(0.2)
                ms.scroll(0, -30); time.sleep(0.2)
                ms.scroll(0, -30); time.sleep(0.2)

                time.sleep(1)
                

        job = next(auto_craft_loop)

        wait_interval = 60
        logger.write_log(f"Auto Craft: Waiting {wait_interval} seconds...")
        if stop_event.wait(timeout=wait_interval):
            break
        if sniped_event.is_set(): break

    logger.write_log("Auto Craft thread stopped.")

def auto_br(settings: dict, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, pause_event, reader):
    logger = get_logger()
    if stop_event.wait(timeout=5):
        return
    logger.write_log("Auto Biome Randomizer thread started.")
    while not stop_event.is_set():

        if pause_event.is_set():
            time.sleep(2)
            continue

        logger.write_log("Auto BR: Using Biome Randomizer...")
        with keyboard_lock:
            use_item("Biome Random", 1, True, mkey, kb, settings, reader)

        wait_interval = 2160 
        logger.write_log(f"Auto BR: Waiting {wait_interval} seconds...")
        if stop_event.wait(timeout=wait_interval):
            break
        if sniped_event.is_set(): break
    logger.write_log("Auto Biome Randomizer thread stopped.")

def auto_sc(settings: dict, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, pause_event, reader):
    logger = get_logger()
    if stop_event.wait(timeout=5):
        return
    logger.write_log("Auto Strange Controller thread started.")
    while not stop_event.is_set():

        if pause_event.is_set():
            time.sleep(2)
            continue

        logger.write_log("Auto SC: Using Strange Controller...")
        with keyboard_lock:
            use_item("Strange Control", 1, True, mkey, kb, settings, reader)

        wait_interval = 1260 
        logger.write_log(f"Auto SC: Waiting {wait_interval} seconds...")
        if stop_event.wait(timeout=wait_interval):
            break
        if sniped_event.is_set(): break
    logger.write_log("Auto Strange Controller thread stopped.")

def inventory_screenshot(settings: dict, webhook, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, pause_event, reader):
    logger = get_logger()
    if stop_event.wait(timeout=5):
        return
    logger.write_log("Periodic Inventory Screenshot thread started.")

    COORDS_PERCENT = get_coords_percent(COORDS)

    if not COORDS_PERCENT:
        logger.write_log("Could not determine screen ratio.")
        return

    while not stop_event.is_set():

        if pause_event.is_set():
            time.sleep(2)
            continue

        logger.write_log("Taking inventory screenshot...")
        screenshot_path = os.path.join(MACROPATH, "scr", "screenshot_inventory.png")
        file_to_send = None
        with keyboard_lock:
            try:
                open_inventory(kb, False)
                time.sleep(0.05)
                search_in_menu(kb, True, False, True, True)
                time.sleep(0.05)
                pag.screenshot(screenshot_path)
                file_to_send = create_discord_file_from_path(screenshot_path, filename="inventory.png")
                if TGIFRIDAY and check_tab_menu_open(reader, COORDS_PERCENT, COORDS):
                    kb.press(keyboard.Key.tab)
                    time.sleep(0.05)
                    kb.release(keyboard.Key.tab)
                    time.sleep(0.05)
                close_menu(kb, True)
            except Exception as e:
                logger.write_log(f"Error taking inventory screenshot: {e}")

                try: close_menu(kb, True)
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

def storage_screenshot(settings: dict, webhook, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, pause_event, reader):
    logger = get_logger()
    if stop_event.wait(timeout=5):
        return
    logger.write_log("Periodic Aura Storage Screenshot thread started.")

    COORDS_PERCENT = get_coords_percent(COORDS)

    if not COORDS_PERCENT:
        logger.write_log("Could not determine screen ratio.")
        return

    while not stop_event.is_set():

        if pause_event.is_set():
            time.sleep(2)
            continue

        logger.write_log("Taking aura storage screenshot...")
        screenshot_path = os.path.join(MACROPATH, "scr", "screenshot_storage.png")
        file_to_send = None
        with keyboard_lock:
            try:
                open_storage(kb, True)
                time.sleep(0.05)
                pag.screenshot(screenshot_path)
                file_to_send = create_discord_file_from_path(screenshot_path, filename="storage.png")
                if TGIFRIDAY and check_tab_menu_open(reader, COORDS_PERCENT, COORDS):
                    kb.press(keyboard.Key.tab)
                    time.sleep(0.05)
                    kb.release(keyboard.Key.tab)
                    time.sleep(0.05)
                close_menu(kb, True)
            except Exception as e:
                logger.write_log(f"Error taking storage screenshot: {e}")
                try: close_menu(kb, True)
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

def disconnect_prevention(settings: dict, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, pause_event):
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

    while not stop_event.is_set():

        if pause_event.is_set():
            time.sleep(2)
            continue

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
        if not stop_event.is_set():
             stop_event.wait(timeout=wait_interval)

    logger.write_log("Disconnect Prevention thread stopped.")

def storage_full_detection(settings: dict, webhook, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey):

    logger = get_logger()
    logger.write_log("Started Storage Full Detection")

    if stop_event.wait(timeout=5):
        return

    while not stop_event.is_set():

        with keyboard_lock:
            time.sleep(0.1)


def do_obby(settings: dict, webhook, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, ignore_lock, ignore_next_detection, pause_event, reader):
    logger = get_logger()
    if stop_event.wait(timeout=5):
        return
    logger.write_log("Obby Blessing thread started.")

    is_autocraft = settings.get("mode", "Normal") == "Auto Craft"
    has_abyssal = settings.get("has_abyssal_hunter", False)
    afk_in_limbo = settings.get("mode", "Normal") == "Limbo"
    is_idle_mode = settings.get("mode", "Normal") == "IDLE"

    if not IMPORTED_ALL_PATHS:
        logger.write_log("Obby thread not started due to missing paths.")
        return
    
    COORDS_PERCENT = get_coords_percent(COORDS)

    while not stop_event.is_set():

        if pause_event.is_set():
            time.sleep(2)
            continue

        with keyboard_lock:

            try:
                reset_character()
                time.sleep(1)
                reset_character()
                time.sleep(1)
                collection_align(kb, True)
            except Exception as e:
                logger.write_log(f"Error during obby alignment: {e}")
                continue

            if not has_abyssal:
                logger.write_log("Begin Phase 1 of Obby")
                #obby.run_macro()
                """try:
                    close_check(kb, True)
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
                    time.sleep(0.4)
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
                    #run_macro(f"{PATH_DIR}/obby1.mms")
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
                    continue"""
            else:
                saved_aura = None
                while saved_aura is None:
                    try:
                        saved_aura = get_latest_equipped_aura().lower()
                    except Exception as e:
                        logger.write_log(f"Error checking current equipped aura: {e}.")
                logger.write_log("Completing Obby with Abyssal Hunter")
                equip_aura("Abyssal", False, mkey, kb, settings, ignore_next_detection, ignore_lock, reader)
                time.sleep(2)
                logger.write_log("Begin Phase 1 of Obby")
                try:
                    time.sleep(1)
                    mkey.move_to_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
                    time.sleep(0.4)
                    right_click_drag(500, 0)
                    time.sleep(0.4)
                    kb.press("w")
                    time.sleep(5)
                    kb.release("w")
                    time.sleep(0.4)
                    right_click_drag(-500, 0)
                    time.sleep(0.4)
                    kb.press("w")
                    time.sleep(1.2)
                    kb.release("w")
                    time.sleep(0.4)
                    right_click_drag(500, 0)
                    time.sleep(0.4)
                    kb.press("w")
                    time.sleep(1)
                    kb.release("w")
                    time.sleep(0.4)
                    kb.press("d")
                    time.sleep(1)
                    kb.release("d")
                    time.sleep(0.4)
                    kb.press("w")
                    time.sleep(0.2)
                    kb.release("w")
                    time.sleep(0.4)
                    kb.press("a")
                    time.sleep(0.4)
                    kb.release("a")
                    time.sleep(0.4)
                    kb.press("w")
                    time.sleep(0.5)
                    kb.release("w")
                    time.sleep(1)
                except Exception as e:
                    logger.write_log(f"Error during obby phase 1: {e}")
                    continue

                logger.write_log("Phase 1 complete, begin phase 2.")

                try:
                    right_click_drag(0, 600)
                    time.sleep(1)
                except Exception as e:
                    logger.write_log(f"Error during obby phase 2: {e}")
                    continue

                logger.write_log("Phase 2 complete, begin phase 3.")

                try:
                    run_macro(f"{PATH_DIR}/obby1_abyssal.mms")
                    time.sleep(1)
                except Exception as e:
                    logger.write_log(f"Error during obby phase 3: {e}")
                    continue

                logger.write_log("Phase 3 complete, begin phase 4.")

                try:
                    run_macro(f"{PATH_DIR}/obby2_abyssal.mms")
                    time.sleep(1)
                except Exception as e:
                    logger.write_log(f"Error during obby phase 4: {e}")
                    continue

                logger.write_log("Phase 4 complete")

                if saved_aura:
                    equip_aura(saved_aura, False, mkey, kb, settings, ignore_next_detection, ignore_lock, reader)
                else:
                    equip_aura("Abyssal", True, mkey, kb, settings, ignore_next_detection, ignore_lock, reader)

            logger.write_log("Completed obby, realigning incase of failure.")
            try:
                reset_character()
                time.sleep(1)
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
                    description="Enjoy a 30% luck boost!",
                    colour=discord.Colour.from_rgb(158, 255, 172)
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

                if not has_abyssal:
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

                else:
                    saved_aura = None
                    while saved_aura is None:
                        try:
                            saved_aura = get_latest_equipped_aura().lower()
                        except Exception as e:
                            logger.write_log(f"Error checking current equipped aura: {e}.")
                    logger.write_log("Walking to Stella with Abyssal Hunter")
                    time.sleep(2)
                    equip_aura("Abyssal", False, mkey, kb, settings, ignore_next_detection, ignore_lock, reader)
                    time.sleep(2)
                    try:
                        mkey.move_to_natural(round(float(COORDS_PERCENT["close_pos"][0] * COORDS["scr_wid"])), round(float(COORDS_PERCENT["close_pos"][1] * COORDS["scr_hei"])))
                        time.sleep(0.4)
                        right_click_drag(1000, 0)
                        time.sleep(0.4)
                        kb.press("d")
                        time.sleep(1.8)
                        kb.release("d")
                        time.sleep(0.4)
                        kb.press("w")
                        time.sleep(6)
                        kb.release("w")
                        time.sleep(0.4)
                        kb.press("a")
                        time.sleep(1.3)
                        kb.release("a")
                        time.sleep(0.4)
                        kb.press("w")
                        time.sleep(0.5)
                        kb.release("w")
                        time.sleep(0.4)
                        kb.press("d")
                        time.sleep(0.4)
                        kb.release("d")
                        time.sleep(0.4)
                        kb.press("w")
                        time.sleep(0.5)
                        kb.release("w")
                    except Exception as e:
                        logger.write_log(f"Error during position alignment: {e}")
                        continue

                logger.write_log("Finished position alignment, walking to Stella.")

                time.sleep(1)

                if not has_abyssal:
                    try:
                        right_click_drag(0, 600)
                        time.sleep(1)
                        run_macro(f"{PATH_DIR}/stella.mms")
                        time.sleep(1)
                    except Exception as e:
                        logger.write_log(f"Error during walk to Stella's: {e}")
                        continue
                else:
                    try:
                        right_click_drag(0, 600)
                        time.sleep(1)
                        run_macro(f"{PATH_DIR}/stella_abyssal.mms")
                        time.sleep(1)
                    except Exception as e:
                        logger.write_log(f"Error during walk to Stella's: {e}")
                        continue
                    if saved_aura:
                        equip_aura(saved_aura, False, mkey, kb, settings, ignore_next_detection, ignore_lock, reader)
                    else:
                        equip_aura("Abyssal", True, mkey, kb, settings, ignore_next_detection, ignore_lock, reader)
            
            elif afk_in_limbo and not is_idle_mode:
                logger.write_log("Teleporting back to limbo...")
                use_item("Portable Crack", 1, True, mkey, kb, settings, reader)
                time.sleep(0.5)

        wait_interval = 600 
        logger.write_log(f"Obby: Waiting {wait_interval} seconds...")
        if stop_event.wait(timeout=wait_interval):
            break
        if sniped_event.is_set(): break

    logger.write_log("Obby/Blessing thread stopped.")

def auto_questboard(settings: dict, webhook, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, ms, reader, pause_event):
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
    
    if not IMPORTED_ALL_PATHS:
        logger.write_log("Could not start auto quest due to missing paths.")
        return
    
    COORDS_PERCENT = get_coords_percent(COORDS)
    
    while not stop_event.is_set():

        if pause_event.is_set():
            time.sleep(2)
            continue


        wait_interval = 3600
        time.sleep(2)
        with keyboard_lock:
            reset_character()
            time.sleep(1)
            reset_character()
            time.sleep(1)
            collection_align(kb, True)
            time.sleep(1)
            run_macro(f"{PATH_DIR}/questboard.mms")
            time.sleep(1)
            kb.press("e")
            time.sleep(0.2)
            kb.release("e")
            time.sleep(3)

            previous_quest = None

            detected_quests = []

            next_quest(kb, True, True)
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
                ocr_results = reader.readtext(quest_title_crop, detail=0)
                ocr_quest_raw = " ".join(ocr_results).strip()

                ocr_quest_clean = re.sub(r"[^a-zA-Z']", "", ocr_quest_raw).lower()
                detected_quest = fuzzy_match_qb(ocr_quest_clean, ALL_QB)

                if TGIFRIDAY and check_tab_menu_open(reader, COORDS_PERCENT, COORDS):
                    kb.press(keyboard.Key.tab)
                    time.sleep(0.05)
                    kb.release(keyboard.Key.tab)
                    time.sleep(0.05)

                if not detected_quest:
                    logger.write_log(f"Auto Quest Board: Could not identify quest from OCR ('{ocr_quest_raw}'). Dismissing.")
                    dismiss_quest(kb, True, True)
                else:
                    logger.write_log(f"Auto Quest Board: Detected Quest ('{detected_quest})")

                    if detected_quest in ACCEPTED_QUESTBOARD:

                        quest_data = questboard_data.get(detected_quest, None)

                        if not quest_data:
                            logger.write_log(f"Auto Quest Board: Could not find data for quest ('{detected_quest}'). Skipping")
                            dismiss_quest(kb, True, True)
                        else:
                            if settings.get("quests_to_accept", {}).get(detected_quest, False) and detected_quest not in tracked_quests.get("quest_board", []) and len(tracked_quests.get("quest_board", [])) <= 3:
                                logger.write_log(f"Auto Quest Board: Accepted Quest ('{detected_quest}')")
                                accept_quest(kb, True, True)
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
                                next_quest(kb, True, True)
                            elif detected_quest in tracked_quests.get("quest_board", []):
                                if previous_quest == detected_quest:
                                    logger.write_log("Quest already accepted and same as previous quest, therefore no more quests.")
                                    break
                                logger.write_log("Quest already accepted, attempting to claim.")
                                accept_quest(kb, True, True)
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
                                ocr_results = reader.readtext(quest_title_crop, detail=0)
                                ocr_quest_raw = " ".join(ocr_results).strip()

                                ocr_quest_clean = re.sub(r"[^a-zA-Z']", "", ocr_quest_raw).lower()
                                detected_quest = fuzzy_match_qb(ocr_quest_clean, ALL_QB)
                                
                                if previous_quest == detected_quest:
                                    logger.write_log("Quest is not yet completed, moving to next quest.")
                                    time.sleep(3)
                                    next_quest(kb, True, True)
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
                                dismiss_quest(kb, True, True)
                                previous_quest = detected_quest
                    else:
                        logger.write_log(f"Auto Quest Board: Quest ('{detected_quest}') is not supported yet, dismissing.")
                        dismiss_quest(kb, True, True)
                        previous_quest = detected_quest
                    time.sleep(3)

                    print(detected_quest, "\n", previous_quest)

            exit_quest(kb, True, True)
            time.sleep(3)
            reset_character()
            time.sleep(1)
            reset_character()
            time.sleep(3)
        logger.write_log(f"Auto Quest Board: Waiting {wait_interval} seconds...")
        if stop_event.wait(timeout=wait_interval):
            break
        if sniped_event.is_set(): break
    logger.write_log("Auto Quest Board thread stopped.")

def auto_pop(biome: str, settings: dict, stop_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, reader):
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
        with keyboard_lock:
            try:
                change_rolling_cutscene(kb, True, True, 9999999999)
                close_menu(kb, True, True)
            except Exception as cs_e:
                logger.write_log(f"Error changing cutscene settings: {cs_e}")

                try: close_check(kb, True)
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
                    use_item(item, use_amount, True, mkey, kb, settings, reader)
                remaining_amount -= use_amount
                time.sleep(1.5) 

                current_biome_check = get_latest_hovertext()
                if current_biome_check is None or current_biome_check.lower() != biome_lower:
                     logger.write_log("Auto Pop: Biome ended during item use. Stopping sequence.")
                     return
        else:
             with keyboard_lock:
                use_item(item, amount_to_use, True, mkey, kb, settings, reader)
             time.sleep(1.0) 

             current_biome_check = get_latest_hovertext()
             if current_biome_check is None or current_biome_check.lower() != biome_lower:
                  logger.write_log("Auto Pop: Biome ended after item use. Stopping sequence.")
                  return

    logger.write_log("Auto Pop sequence finished.")


def eden_detection(settings: dict, webhook, stop_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, ms, pause_event, reader):
    
    logger = get_logger()

    logger.write_log("Starting Eden Detection...")

    previous_spawn = 0
    
    while not stop_event.is_set():
        
        if pause_event.is_set():
            time.sleep(2)
            continue

        try:

            eden_spawned, time_of_spawn = check_for_eden_spawn()

            if eden_spawned and time_of_spawn > previous_spawn:

                logger.write_log("Eden has spawned in the server!")

                emb = discord.Embed(
                    title="The Void Cracks...",
                    description=f"**Eden** has spawned in your server!\n**Time:** <t:{str(int(time.time()))}>",
                    colour=discord.Colour.from_rgb(0, 0, 0)
                )
                emb.set_thumbnail(url="https://static.wikia.nocookie.net/sol-rng/images/9/9d/Eden%28NPC%29.png/revision/latest")
                emb.set_footer(text=f"SolsScope v{LOCALVERSION}")
                try:
                    webhook.send(embed=emb)
                    forward_webhook_msg(
                        primary_webhook_url=webhook.url,
                        secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                        embed=emb
                    )
                except Exception as wh_e:
                    logger.write_log(f"Error sending biome ended webhook: {wh_e}")
                
                with keyboard_lock:

                    time.sleep(5)
                    logger.write_log("Teleporting to limbo...")
                    use_item("Portable Crack", 1, True, mkey, kb, settings, reader)
                    time.sleep(1)
                    collection_align(kb, True)
                    time.sleep(1)

                    #eden_vip.run_macro()

                previous_spawn = time_of_spawn
    
        except Exception as e:
            logger.write_log(f"Error in Eden Detection Loop: {e}")
            time.sleep(5)

    logger.write_log("Eden Detection thread stopped.")


def vok_taran(settings: dict, webhook, stop_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, pause_event):

    logger = get_logger()

    time.sleep(5)

    while not stop_event.is_set():

        if pause_event.is_set():
            time.sleep(2)
            continue

        with keyboard_lock:

            logger.write_log("Spawning Sand Storm (vok taran)")

            kb.press("/")
            time.sleep(0.05)
            kb.release("/")
            time.sleep(0.05)

            pag.write("vok taran")

            kb.press(keyboard.Key.enter)
            time.sleep(0.05)
            kb.release(keyboard.Key.enter)
            time.sleep(0.05)

        if stop_event.wait(timeout=1860):
            break