"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v2.0.0
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
    import qb_vip, eden_vip, obby_vip, stella_vip
    import obby, qb
    import stella_abyssal, obby_abyssal
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
    get_autocraft_path, _type
)
from roblox_utils import (
    get_latest_equipped_aura, get_latest_hovertext, detect_client_disconnect,
    detect_client_reconnect, join_private_server_link, leave_main_menu,
    activate_ms_store_roblox, click_ms_store_spawn_button, toggle_fullscreen_ms_store,
    reset_character, detect_ui_nav, get_roblox_window_bbox, check_for_eden_spawn,
    join_private_share_link, extract_server_code, PlayerLogger, get_active_log_directory,
    get_latest_merchant_info
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
    load_keybind, load_delay
)

import mousenav

from mmint import run_macro

from stats import increment_stat, load_stats

from calibrations import validate_calibrations, validate_regions, get_calibrations, get_regions

def use_item(item_name: str, amount: int, _close_menu: bool, mkey, kb, settings: dict, reader, ms):
    logger = get_logger()
    logger.write_log(f"Attempting to use item: {item_name} (Amount: {amount})")


    delay = load_delay()

    if not settings.get("calibration"):
        logger.write_log("A calibration has not been selected.")
        return
    
    CLICKS = get_calibrations(settings.get("calibration"))
    
    if not validate_calibrations(settings.get("calibration"), ["open_inventory", "items_btn", "search_bar", "first_inv_item", "item_amount", "use_item", "close_menu"]):
        logger.write_log("Could not verify all calibrations.")
        return

    
    try:
        mkey.left_click_xy_natural(CLICKS["open_inventory"][0], CLICKS["open_inventory"][1])
        time.sleep(delay)
        mkey.left_click_xy_natural(CLICKS["items_btn"][0], CLICKS["items_btn"][1])
        time.sleep(delay)
        mkey.left_click_xy_natural(CLICKS["search_bar"][0], CLICKS["search_bar"][1])
        time.sleep(delay)
        _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), item_name)
        time.sleep(delay)
        mkey.move_to_natural(CLICKS["first_inv_item"][0], CLICKS["first_inv_item"][1])
        time.sleep(delay)
        ms.scroll(0, 30); time.sleep(delay)
        ms.scroll(0, 30); time.sleep(delay)
        ms.scroll(0, 30); time.sleep(delay)
        mkey.left_click_xy_natural(CLICKS["first_inv_item"][0], CLICKS["first_inv_item"][1])
        time.sleep(delay)
        mkey.left_click_xy_natural(CLICKS["item_amount"][0], CLICKS["item_amount"][1])
        time.sleep(delay)
        kb.press(keyboard.Key.ctrl)
        kb.press("a")
        time.sleep(0.05)
        kb.release("a")
        kb.release(keyboard.Key.ctrl)
        time.sleep(0.05)
        _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), str(amount))
        time.sleep(1)
        kb.press(keyboard.Key.enter)
        time.sleep(0.05)
        kb.release(keyboard.Key.enter)
        time.sleep(1)
        mkey.left_click_xy_natural(CLICKS["use_item"][0], CLICKS["use_item"][1])
        time.sleep(delay)
        mkey.left_click_xy_natural(CLICKS["close_menu"][0], CLICKS["close_menu"][1])
        time.sleep(delay)
    except Exception as e:
        logger.write_log(f"Error whilst using item: {e}")
        try:
            time.sleep(delay)
            mkey.left_click_xy_natural(CLICKS["close_menu"][0], CLICKS["close_menu"][1])
            time.sleep(delay)
        except Exception as close_e:
            logger.write_log(f"Error trying to close menu after item use error: {close_e}")

def equip_aura(aura_name, unequip, mkey, kb, settings: dict, ignore_next_detection: set, ignore_lock: threading.Lock, reader, ms):
    logger = get_logger()

    success = False

    try:
        with open(get_auras_path(), "r", encoding="utf-8") as f:
            auras = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        logger.write_log(f"Error loading auras data for detection: {e}. Aura detection stopped.")
        return
    
    delay = load_delay()

    if not settings.get("calibration"):
        logger.write_log("A calibration has not been selected.")
        return
    
    CLICKS = get_calibrations(settings.get("calibration"))
    
    if not validate_calibrations(settings.get("calibration"), ["open_storage", "first_aura_position", "search_bar", "equip_aura", "close_menu"]):
        logger.write_log("Could not verify all calibrations.")
        return
    
    full_aura_name = resolve_full_aura_name(aura_name, auras)
    _ = None
    

    while _ is None:
        _ = get_latest_equipped_aura()
        try:
            if _.lower() == full_aura_name.lower():
                if not unequip:
                    logger.write_log(f"Aura {full_aura_name} is already equipped.")
                    return
            if _.lower() != full_aura_name.lower():
                if unequip:
                    logger.write_log(f"Aura {full_aura_name} is already unequipped.")
                    return
        except Exception as e:
            logger.write_log(f"Error checking current equipped aura: {e}.")

    logger.write_log(f"{'Unequipping' if unequip else 'Equipping'} Aura: {aura_name} (resolved as '{full_aura_name}')")

    with ignore_lock:
        try:
            mkey.left_click_xy_natural(CLICKS["open_storage"][0], CLICKS["open_storage"][1])
            time.sleep(delay)
            mkey.left_click_xy_natural(CLICKS["search_bar"][0], CLICKS["search_bar"][1])
            time.sleep(delay)
            kb.press(keyboard.Key.backspace)
            time.sleep(0.2)
            kb.release(keyboard.Key.backspace)
            time.sleep(delay)
            _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), aura_name)
            time.sleep(delay)
            mkey.move_to_natural(CLICKS["first_aura_position"][0], CLICKS["first_aura_position"][1])
            time.sleep(delay)
            ms.scroll(0, 30); time.sleep(delay)
            ms.scroll(0, 30); time.sleep(delay)
            ms.scroll(0, 30); time.sleep(delay)
            mkey.left_click_xy_natural(CLICKS["first_aura_position"][0], CLICKS["first_aura_position"][1])
            time.sleep(delay)
            mkey.left_click_xy_natural(CLICKS["equip_aura"][0], CLICKS["equip_aura"][1])
            time.sleep(delay)
            mkey.left_click_xy_natural(CLICKS["close_menu"][0], CLICKS["close_menu"][1])
        except Exception as e:
            logger.write_log(f"Unable to equip aura: {e}")
            try:
                time.sleep(delay)
                mkey.left_click_xy_natural(CLICKS["close_menu"][0], CLICKS["close_menu"][1])
                time.sleep(delay)
            except Exception as close_e:
                logger.write_log(f"Error whilst closing menu: {close_e}")
        
        time.sleep(0.5)
        new_aura = get_latest_equipped_aura()
        if new_aura and new_aura.lower() == full_aura_name.lower() and not unequip:
            ignore_next_detection.add(full_aura_name.lower())
            logger.write_log(f"Aura '{full_aura_name}' successfully equipped.")
            success = True
        elif new_aura and new_aura.lower() != full_aura_name.lower() and unequip:
            logger.write_log(f"Aura '{full_aura_name}' successfully unequipped.")
            success = True
        else:
            logger.write_log(f"Failed to equip aura '{full_aura_name}', continuing without ignoring.")

    return success


def aura_detection(settings: dict, webhook, stop_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, ignore_lock, ignore_next_detection, pause_event, reader, ms):
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
                             description += f"**Rarity:** 1 / {effective_rarity:,} (from {current_biome if not biomes[current_biome_key].get('display_name') else biomes[current_biome_key].get('display_name')})\n"
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
                if (
                    use_reset_aura
                    and current_aura != reset_aura_target
                    and settings.get("mode", "Normal") not in ["IDLE", "Fishing"]
                ):
                    logger.write_log(f"Resetting aura back to {reset_aura_target}...")
                    with keyboard_lock:
                        try:
                            success = equip_aura(reset_aura_target, False, mkey, kb, settings,
                                                ignore_next_detection, ignore_lock, reader, ms)
                            if success:
                                previous_aura = reset_aura_target
                            else:
                                logger.write_log("Reset aura equip failed — keeping previous aura unchanged.")
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
    
    
    pllogger = PlayerLogger(get_active_log_directory(), webhook, settings, logger)

    def run_logger(biome, end_event : threading.Event):
        end_event.clear()
        try:
            pllogger.start_logging(biome, end_event)
        except Exception as e:
            print(f"Player logger encountered an error: {e}")

    end_event = threading.Event()
    end_event.clear()
    
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

    rare_biomes = [biome for biome, data in biomes.items() if data.get("rare")]

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

                end_event.set()
                
                prev_biome_data = biomes[previous_biome_key]
                emb_color_hex = prev_biome_data.get("colour", "#808080")
                emb_rgb = hex2rgb(emb_color_hex)
                emb = discord.Embed(
                    title=f"Biome Ended: {previous_biome if not prev_biome_data.get('display_name') else prev_biome_data.get('display_name')}",
                    description=f"Biome **{previous_biome if not prev_biome_data.get('display_name') else prev_biome_data.get('display_name')}** has ended.\n**Time:** <t:{str(int(time.time()))}>",
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

                    description = f"Biome {current_biome if not new_biome_data.get('display_name') else new_biome_data.get('display_name')} has started!\nTime: <t:{str(int(time.time()))}>"
                    title = f"Event Biome Started: {current_biome if not new_biome_data.get('display_name') else new_biome_data.get('display_name')}" if is_event else f"Biome Started: {current_biome if not new_biome_data.get('display_name') else new_biome_data.get('display_name')}"

                    emb = discord.Embed(
                        title=title,
                        description=description,
                        colour=discord.Colour.from_rgb(*emb_rgb)
                    )
                    if ps_link_valid:
                        emb.add_field(name="Server Invite:", value=f"{settings.get('private_server_link')}")

                    if new_biome_data.get("rare", False):
                        pl_thread = threading.Thread(target=run_logger, args=(current_biome.upper(), end_event), daemon=True)
                        pl_thread.start()
                        ping_content = "@everyone"
                        emb.set_footer(text=f"SolsScope v{LOCALVERSION}")
                    else:
                        ping_content = ""
                        if settings.get("enable_player_logger", True):
                            pl_thread = threading.Thread(target=run_logger, args=(current_biome.upper(), end_event), daemon=True)
                            pl_thread.start()

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

def portable_crack(settings: dict, stop_event: threading.Event, sniped_event: threading.Event, mkey, kb, keyboard_lock, pause_event, reader, ms):

    logger = get_logger()
    
    if not settings.get("calibration"):
        logger.write_log("No calibration is selected.")
        return

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
                use_item("Portable Crack", 1, True, mkey, kb, settings, reader, ms)
                time.sleep(0.5)

            logger.write_log("Portable Crack: Waiting 10 minutes before using again.")

            if stop_event.wait(timeout=wait_interval):
                break
        logger.write_log("Portable Crack thread stopped.")

def keep_alive(settings: dict, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, kb, pause_event, mkey):
    logger = get_logger()
    if stop_event.wait(timeout=5):
        return
    logger.write_log("Keep Alive (Anti-AFK) thread started.")

    if not settings.get("calibration"):
        logger.write_log("No calibratoin is selected.")
        return

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
                if not validate_calibrations(settings.get("calibration"), ["close_menu"]):
                    mkey.left_click_xy_natural(get_calibrations(settings.get("calibration"))["close_menu"][0], get_calibrations(settings.get("calibration"))["close_menu"][1])
                else:
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



def merchant_detection(settings: dict, webhook, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, ignore_lock, ignore_next_detection, reader, pause_event, ms):
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
        "jester_open", "jester_exchange", "merchant_amount", "merchant_purchase",
        "merchant_slot_1", "merchant_slot_2", "merchant_slot_3", "merchant_slot_4",
        "merchant_slot_5", "merchant_close", "jester_auto_ex_first", "jester_auto_ex_second",
        "merchant_skip_dialog", "jester_exchange_confirm"
    ]

    required_regions = [
        "merchant_name", "merchant_boxes", "jester_auto_ex_first"
    ]

    if not settings.get("calibration"):
        logger.write_log("Cannot start Merchant Detection: No calibration selected.")
        return
    
    if not validate_calibrations(settings.get("calibration"), required_coords):
        logger.write_log("Cannot start Merchant Detection: Calibration is invalid.")
        return
    
    if not validate_regions(settings.get("calibration"), required_regions):
        logger.write_log("Could not start Merchant Detection: Calibration is invalid.")
        return
    
    CLICKS = get_calibrations(settings.get("calibration"))
    REGIONS = get_regions(settings.get("calibration"))

    delay = load_delay()

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

    md_type = settings.get("merchant_detection_type", "Legacy")

    if (is_autocraft or is_idle_mode) and md_type == "Legacy":
        logger.write_log("Merchant Detection cannot be started in this mode whilst it is using Legacy Detection.")
        return
    
    screenshot_path = os.path.join(MACROPATH, "scr", "screenshot_merchant.png")
    ex_screenshot_path = os.path.join(MACROPATH, "scr", "screenshot_exchange.png")
    
    if md_type == "Legacy":

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


                try:
                    logger.write_log("Merchant Detection: Using Merchant Teleport item...")
                    use_item("Merchant Teleport", 1, True, mkey, kb, settings, reader, ms) 
                    time.sleep(settings.get("global_wait_time", 0.2) + 0.5) 

                    logger.write_log("Merchant Detection: Attempting interaction (E key)...")
                    kb.press('e')
                    time.sleep(0.2)
                    kb.release('e')
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["merchant_skip_dialog"][0], CLICKS["merchant_skip_dialog"][1])
                    time.sleep(2)
                    mkey.left_click_xy_natural(CLICKS["merchant_skip_dialog"][0], CLICKS["merchant_skip_dialog"][1])
                    time.sleep(2)

                    logger.write_log("Merchant Detection: Taking screenshot...")
                    pag.screenshot(screenshot_path)
                    time.sleep(0.2)

                    logger.write_log("Merchant Detection: Processing screenshot with OCR...")
                    image = cv2.imread(screenshot_path)
                    if image is None:
                        logger.write_log("Merchant Detection Error: Failed to read screenshot file.")
                        continue

                    x1, y1, x2, y2 = REGIONS["merchant_name"]
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
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["jester_open"][0], CLICKS["jester_open"][1])
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
                        description=f"A **{merchant_short_name}** has been detected.\n**Time:** <t:{str(int(time.time()))}>\nDetection Method: **{md_type}**",
                        colour=emb_color
                    )
                    if thumbnail_url: emb.set_thumbnail(url=thumbnail_url)
                    if file_to_send: emb.set_image(url="attachment://merchant.png")
                    if ps_link_valid: emb.add_field(name="Server Invite", value=settings['private_server_link'], inline=False)

                    emb.set_footer(text=f"SolsScope v{LOCALVERSION}")

                    logger.write_log("Merchant Detection: Detecting items...")
                    item_list = MARI_ITEMS if merchant_short_name == "Mari" else JESTER_ITEMS
                    item_ocr_results = []
                    for box_name, (x1, y1, x2, y2) in REGIONS["merchant_boxes"].items():
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
                        for box_name, item_name in items_to_buy.items():
                            try:
                                coord_key = f"merchant_slot_{box_name[-1]}"
                                mkey.left_click_xy_natural(CLICKS[coord_key][0], CLICKS[coord_key][1])
                                time.sleep(delay)
                                mkey.left_click_xy_natural(CLICKS["merchant_amount"][0], CLICKS["merchant_amount"][1])
                                time.sleep(delay)
                                kb.type(str(purchase_settings.get(item_name).get("amount", 1)))
                                time.sleep(delay)
                                mkey.left_click_xy_natural(CLICKS["merchant_purchase"][0], CLICKS["merchant_purchase"][1])
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
                        mkey.left_click_xy_natural(CLICKS["merchant_close"][0], CLICKS["merchant_close"][1])
                        time.sleep(delay)
                        kb.press('e')
                        time.sleep(0.2)
                        kb.release('e')
                        mkey.left_click_xy_natural(CLICKS["merchant_skip_dialog"][0], CLICKS["merchant_skip_dialog"][1])
                        time.sleep(3)
                        mkey.left_click_xy_natural(CLICKS["merchant_skip_dialog"][0], CLICKS["merchant_skip_dialog"][1])
                        time.sleep(3)
                        mkey.left_click_xy_natural(CLICKS["jester_exchange"][0], CLICKS["jester_exchange"][1])
                        time.sleep(3)
                        while not stop_event.is_set():
                            pag.screenshot(ex_screenshot_path)
                            time.sleep(0.2)
                            logger.write_log("Merchant Detection: Processing screenshot with OCR...")
                            image = cv2.imread(ex_screenshot_path)
                            if image is None:
                                logger.write_log("Merchant Detection Error: Failed to read screenshot file.")
                                continue
                            x1, y1, x2, y2 = REGIONS["jester_auto_ex_first"]
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
                                    x1, y1, x2, y2 = REGIONS["jester_auto_ex_second"]
                                    exchange_crop = image[y1:y2, x1:x2]
                                    ocr_results = reader.readtext(exchange_crop, detail=0)
                                    ocr_ex_item_raw = " ".join(ocr_results).strip().replace('\n', ' ')
                                    ocr_ex_item_clean = re.sub(r"[^a-zA-Z']", "", ocr_ex_item_raw).lower()

                                    detected_item_name = fuzzy_match_auto_sell(ocr_ex_item_clean, JESTER_SELL_ITEMS)
                                    debug_path = os.path.join(f"{MACROPATH}/debug", f"dbg_{str(int(time.time()))}.png")
                                    cv2.imwrite(debug_path, exchange_crop)
                                    if detected_item_name == "Void Coin":
                                        _break_second = True
                                        logger.write_log("Auto-Sell: Void coin detected in second slot, stopping job.")
                                        break
                                    elif detected_item_name in JESTER_SELL_ITEMS and settings.get("items_to_sell", {}).get(detected_item_name, False):
                                        logger.write_log(f"Auto-Sell: {detected_item_name} was detected")
                                        time.sleep(delay)
                                        mkey.left_click_xy_natural(CLICKS["jester_auto_ex_second"][0], CLICKS["jester_auto_ex_second"][1])
                                        time.sleep(delay)
                                        mkey.left_click_xy_natural(CLICKS["merchant_amount"][0], CLICKS["merchant_amount"][1])
                                        time.sleep(delay)
                                        kb.type(str(settings.get("amount_of_item_to_sell", 1)))
                                        time.sleep(delay)
                                        mkey.left_click_xy_natural(CLICKS["merchant_purchase"][0], CLICKS["merchant_purchase"][1])
                                        time.sleep(delay)
                                        mkey.left_click_xy_natural(CLICKS["jester_exchange_confirm"][0], CLICKS["jester_exchange_confirm"][1])
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
                                        logger.write_log(f"Auto-Sell: No item was detected (OCR results: {ocr_results})")
                                        logger.write_log("Auto-Sell: No items were found in the second box or unsure if Void Coin was not detected, ending auto sell job.")
                                        _break_second = True
                                        break
                                    time.sleep(1)
                                if _break_second:
                                    break
                            elif detected_item_name in JESTER_SELL_ITEMS and settings.get("items_to_get", {}).get(detected_item_name, False):
                                logger.write_log(f"Auto-Sell: {detected_item_name} was detected")
                                time.sleep(delay)
                                mkey.left_click_xy_natural(CLICKS["jester_auto_ex_first"][0], CLICKS["jester_auto_ex_first"][1])
                                time.sleep(delay)
                                mkey.left_click_xy_natural(CLICKS["merchant_amount"][0], CLICKS["merchant_amount"][1])
                                time.sleep(delay)
                                kb.type(str(settings.get("amount_of_item_to_sell", 1)))
                                time.sleep(delay)
                                mkey.left_click_xy_natural(CLICKS["merchant_purchase"][0], CLICKS["merchant_purchase"][1])
                                time.sleep(delay)
                                mkey.left_click_xy_natural(CLICKS["jester_exchange_confirm"][0], CLICKS["jester_exchange_confirm"][1])
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
                                logger.write_log(f"Auto-Sell: No item was detected (OCR results: {ocr_results})")
                                logger.write_log("Auto-Sell: No item was found or unsure if Void Coin was not detected, ending auto sell job.")
                                break
                            time.sleep(1)

                        mkey.left_click_xy_natural(CLICKS["merchant_close"][0], CLICKS["merchant_close"][1])
                        time.sleep(0.5)
                        reset_character()
                        time.sleep(3)

                    if afk_in_limbo and not is_idle_mode:
                        logger.write_log("Teleporting back to limbo...")
                        use_item("Portable Crack", 1, True, mkey, kb, settings, reader, ms)
                        time.sleep(0.5)

                    if stop_event.wait(timeout=cooldown_interval):
                        break

                except Exception as e:
                    logger.write_log(f"Error in Merchant Detection loop: {e}")
                    import traceback
                    logger.write_log(traceback.format_exc()) 

                    try:
                        mkey.left_click_xy_natural(CLICKS["merchant_close"][0], CLICKS["merchant_close"][1])
                    except Exception:
                        pass

                    if afk_in_limbo and not is_idle_mode:
                        logger.write_log("Teleporting back to limbo...")
                        use_item("Portable Crack", 1, True, mkey, kb, settings, reader, ms)
                        time.sleep(0.5)

    elif md_type == "Logs":

        previous_merchant = (None, time.time())
        mari_items = [item for item, data in settings.get("auto_purchase_items_mari", {}).items() if data.get("Purchase")]
        jester_items = [item for item, data in settings.get("auto_purchase_items_jester", {}).items() if data.get("Purchase")]

        if is_idle_mode:
            logger.write_log("SolsScope will only detect merchants whilst in IDLE mode and will not purchase/sell to them.")

        while not stop_event.is_set():
            
            if pause_event.is_set():
                time.sleep(2)
                continue

            merchant_spawn = get_latest_merchant_info(previous_merchant[1])

            if merchant_spawn:

                    if merchant_spawn[1] > previous_merchant[1]:
                        previous_merchant = merchant_spawn

                        if (auto_sell or len(mari_items) > 0 or len(jester_items) > 0) and not is_idle_mode:

                            detected_merchant_name = None
                            detected_items = {}
                                
                            with keyboard_lock:

                                try:
                                    logger.write_log("Merchant Detection: Using Merchant Teleport item...")
                                    use_item("Merchant Teleport", 1, True, mkey, kb, settings, reader, ms) 
                                    time.sleep(settings.get("global_wait_time", 0.2) + 0.5) 

                                    logger.write_log("Merchant Detection: Attempting interaction (E key)...")
                                    kb.press('e')
                                    time.sleep(0.2)
                                    kb.release('e')
                                    time.sleep(0.2)
                                    mkey.left_click_xy_natural(CLICKS["merchant_skip_dialog"][0], CLICKS["merchant_skip_dialog"][1])
                                    time.sleep(2)
                                    mkey.left_click_xy_natural(CLICKS["merchant_skip_dialog"][0], CLICKS["merchant_skip_dialog"][1])
                                    time.sleep(2)

                                    logger.write_log("Merchant Detection: Taking screenshot...")
                                    pag.screenshot(screenshot_path)
                                    time.sleep(0.2)

                                    logger.write_log("Merchant Detection: Processing screenshot with OCR...")
                                    image = cv2.imread(screenshot_path)
                                    if image is None:
                                        logger.write_log("Merchant Detection Error: Failed to read screenshot file.")
                                        continue

                                    x1, y1, x2, y2 = REGIONS["merchant_name"]
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
                                    time.sleep(delay)
                                    mkey.left_click_xy_natural(CLICKS["jester_open"][0], CLICKS["jester_open"][1])
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
                                        description=f"A **{merchant_short_name}** has been detected.\n**Time:** <t:{str(int(time.time()))}>\nDetection Method: **{md_type}**",
                                        colour=emb_color
                                    )
                                    if thumbnail_url: emb.set_thumbnail(url=thumbnail_url)
                                    if file_to_send: emb.set_image(url="attachment://merchant.png")
                                    if ps_link_valid: emb.add_field(name="Server Invite", value=settings['private_server_link'], inline=False)

                                    emb.set_footer(text=f"SolsScope v{LOCALVERSION}")

                                    logger.write_log("Merchant Detection: Detecting items...")
                                    item_list = MARI_ITEMS if merchant_short_name == "Mari" else JESTER_ITEMS
                                    item_ocr_results = []
                                    for box_name, (x1, y1, x2, y2) in REGIONS["merchant_boxes"].items():
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
                                        for box_name, item_name in items_to_buy.items():
                                            try:
                                                coord_key = f"merchant_slot_{box_name[-1]}"
                                                mkey.left_click_xy_natural(CLICKS[coord_key][0], CLICKS[coord_key][1])
                                                time.sleep(delay)
                                                mkey.left_click_xy_natural(CLICKS["merchant_amount"][0], CLICKS["merchant_amount"][1])
                                                time.sleep(delay)
                                                kb.type(str(purchase_settings.get(item_name).get("amount", 1)))
                                                time.sleep(delay)
                                                mkey.left_click_xy_natural(CLICKS["merchant_purchase"][0], CLICKS["merchant_purchase"][1])
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
                                        mkey.left_click_xy_natural(CLICKS["merchant_close"][0], CLICKS["merchant_close"][1])
                                        time.sleep(0.2)
                                        kb.press('e')
                                        time.sleep(0.2)
                                        kb.release('e')
                                        mkey.left_click_xy_natural(CLICKS["merchant_skip_dialog"][0], CLICKS["merchant_skip_dialog"][1])
                                        time.sleep(3)
                                        mkey.left_click_xy_natural(CLICKS["merchant_skip_dialog"][0], CLICKS["merchant_skip_dialog"][1])
                                        time.sleep(3)
                                        mkey.left_click_xy_natural(CLICKS["jester_exchange"][0], CLICKS["jester_exchange"][1])
                                        time.sleep(3)
                                        while not stop_event.is_set():
                                            pag.screenshot(ex_screenshot_path)
                                            time.sleep(0.2)
                                            logger.write_log("Merchant Detection: Processing screenshot with OCR...")
                                            image = cv2.imread(ex_screenshot_path)
                                            if image is None:
                                                logger.write_log("Merchant Detection Error: Failed to read screenshot file.")
                                                continue

                                            x1, y1, x2, y2 = REGIONS["jester_auto_ex_first"]
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
                                                    x1, y1, x2, y2 = REGIONS["jester_auto_ex_second"]
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
                                                        time.sleep(delay)
                                                        mkey.left_click_xy_natural(CLICKS["jester_auto_ex_second"][0], CLICKS["jester_auto_ex_second"][1])
                                                        time.sleep(delay)
                                                        mkey.left_click_xy_natural(CLICKS["merchant_amount"][0], CLICKS["merchant_amount"][1])
                                                        time.sleep(delay)
                                                        kb.type(str(settings.get("amount_of_item_to_sell", 1)))
                                                        time.sleep(delay)
                                                        mkey.left_click_xy_natural(CLICKS["merchant_purchase"][0], CLICKS["merchant_purchase"][1])
                                                        time.sleep(delay)
                                                        mkey.left_click_xy_natural(CLICKS["jester_exchange_confirm"][0], CLICKS["jester_exchange_confirm"][1])
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
                                                time.sleep(delay)
                                                mkey.left_click_xy_natural(CLICKS["jester_auto_ex_first"][0], CLICKS["jester_auto_ex_first"][1])
                                                time.sleep(delay)
                                                mkey.left_click_xy_natural(CLICKS["merchant_amount"][0], CLICKS["merchant_amount"][1])
                                                time.sleep(delay)
                                                kb.type(str(settings.get("amount_of_item_to_sell", 1)))
                                                time.sleep(delay)
                                                mkey.left_click_xy_natural(CLICKS["merchant_purchase"][0], CLICKS["merchant_purchase"][1])
                                                time.sleep(delay)
                                                mkey.left_click_xy_natural(CLICKS["jester_exchange_confirm"][0], CLICKS["jester_exchange_confirm"][1])
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

                                        mkey.left_click_xy_natural(CLICKS["merchant_close"][0], CLICKS["merchant_close"][1])
                                        time.sleep(0.5)
                                        reset_character()
                                        time.sleep(3)

                                    if afk_in_limbo and not is_idle_mode:
                                        logger.write_log("Teleporting back to limbo...")
                                        use_item("Portable Crack", 1, True, mkey, kb, settings, reader, ms)
                                        time.sleep(0.5)

                                    if stop_event.wait(timeout=cooldown_interval):
                                        break

                                except Exception as e:
                                    logger.write_log(f"Error in Merchant Detection loop: {e}")
                                    import traceback
                                    logger.write_log(traceback.format_exc()) 

                                    try:
                                        mkey.left_click_xy_natural(CLICKS["merchant_close"][0], CLICKS["merchant_close"][1])
                                    except Exception:
                                        pass

                                    if afk_in_limbo and not is_idle_mode:
                                        logger.write_log("Teleporting back to limbo...")
                                        use_item("Portable Crack", 1, True, mkey, kb, settings, reader, ms)
                                        time.sleep(0.5)
                        
                        else:
                            ping_content = ""
                            if merchant_spawn[0] == "Mari":
                                emb_color = discord.Colour.from_rgb(255, 255, 255)
                                thumbnail_url = "https://static.wikia.nocookie.net/sol-rng/images/3/37/MARI_HIGH_QUALITYY.png/revision/latest"
                                if settings.get("ping_mari", False) and settings.get("mari_ping_id", 0) != 0:
                                    ping_content += f"<@&{settings['mari_ping_id']}>"
                            elif merchant_spawn[0] == "Jester":
                                emb_color = discord.Colour.from_rgb(176, 49, 255)
                                thumbnail_url = "https://static.wikia.nocookie.net/sol-rng/images/d/db/Headshot_of_Jester.png/revision/latest"
                                if settings.get("ping_jester", False) and settings.get("jester_ping_id", 0) != 0:
                                    ping_content += f"<@&{settings['jester_ping_id']}>"
                            else:
                                emb_color = discord.Colour.default()
                                thumbnail_url = None

                            emb = discord.Embed(
                                title=f"{merchant_spawn[0]} Spawned!",
                                description=f"A **{merchant_spawn[0]}** has been detected.\n**Time:** <t:{str(int(merchant_spawn[1]))}>\nDetection Method: **{md_type}**",
                                colour=emb_color
                            )
                            if thumbnail_url: emb.set_thumbnail(url=thumbnail_url)
                            if ps_link_valid: emb.add_field(name="Server Invite", value=settings['private_server_link'], inline=False)

                            emb.set_footer(text=f"SolsScope v{LOCALVERSION}")
                            webhook.send(content=ping_content, embed=emb)
                            forward_webhook_msg(
                                primary_webhook_url=webhook.url,
                                secondary_urls=settings.get("SECONDARY_WEBHOOK_URLS", []),
                                embed=emb,
                                content=ping_content
                            )

    else:
        logger.write_log(f"Unknown Merchant Detection Type: {md_type}")
            

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
    VIP_STATUS = settings.get("vip_status", "No VIP")

    if stop_event.wait(timeout=10):
        return
    
    if not settings.get("do_not_walk_to_stella", True) and IMPORTED_ALL_PATHS:
        logger.write_log("Auto Craft: Walking To Stella's")
        with keyboard_lock:
            if has_abyssal:
                if equip_aura("Abyssal", False, mkey, kb, settings, ignore_next_detection, ignore_lock, reader, ms):
                    logger.write_log("Using Abyssal Path for Stella")
                    stella_abyssal.run_macro(stella_abyssal.macro_actions)
                else:
                    if VIP_STATUS in ["VIP", "VIP+"]:
                        logger.write_log("Using VIP Path for Stella (Abyssal Equip Failed)")
                        stella_vip.run_macro(stella_vip.macro_actions)
                    
                    else:
                        logger.write_log("Walking back to Stella is not supported with No VIP")
            elif VIP_STATUS in ["VIP", "VIP+"]:
                logger.write_log("Using VIP Path for Stella")
                stella_vip.run_macro(stella_vip.macro_actions)
            
            else:
                logger.write_log("Walking back to Stella is not supported with No VIP")

    else:
        logger.write_log("Ensure you are standing near the cauldron with the 'F' prompt visible.")

    screenshot_path = os.path.join(MACROPATH, "scr", "screenshot_autocraft.png")

    send_item_crafted_notification = settings.get("send_item_crafted_notification", True)

    if not settings.get("calibration"):
        logger.write_log("Cannot start Auto Craft: No calibration selected.")
        return
    
    if not validate_calibrations(settings.get("calibration"), ["autocraft_craft", "autocraft_auto", "autocraft_search", "autocraft_first_potion", "autocraft_first_add", "autocraft_first_amt", "autocraft_second_add", "autocraft_second_amt", "autocraft_third_add", "autocraft_third_amt", "autocraft_first_scrolled_add", "autocraft_first_scrolled_amt", "autocraft_second_scrolled_add", "autocraft_second_scrolled_amt", "autocraft_third_scrolled_add", "autocraft_third_scrolled_amt", "autocraft_scroll"]):
        logger.write_log("Cannot start Auto Craft: Calibration is invalid.")
        return
    
    if not validate_regions(settings.get("calibration"), ["autocraft_top_add", "autocraft_scrolled_bottom_add"]):
        logger.write_log("Could not start Auto Craft: Calibration is invalid.")
        return

    
    CLICKS = get_calibrations(settings.get("calibration"))
    REGIONS = get_regions(settings.get("calibration"))

    delay = load_delay()

    def _search(potion_name : str):
        kb.press("f")
        time.sleep(0.2)
        kb.release("f")
        time.sleep(delay)
        kb.press("f")
        time.sleep(0.2)
        kb.release("f")
        time.sleep(delay)
        mkey.left_click_xy_natural(CLICKS["autocraft_search"][0], CLICKS["autocraft_search"][1])
        time.sleep(delay)
        mkey.left_click_xy_natural(CLICKS["autocraft_first_potion"][0], CLICKS["autocraft_first_potion"][1])
        time.sleep(delay)
        ms.scroll(0, 30); time.sleep(delay)
        ms.scroll(0, 30); time.sleep(delay)
        ms.scroll(0, 30); time.sleep(delay)
        mkey.left_click_xy_natural(CLICKS["autocraft_search"][0], CLICKS["autocraft_search"][1])
        time.sleep(delay)
        _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), potion_name)
        time.sleep(delay)
        mkey.left_click_xy_natural(CLICKS["autocraft_first_potion"][0], CLICKS["autocraft_first_potion"][1])
        time.sleep(delay)


    while not stop_event.is_set():

        if pause_event.is_set():
            time.sleep(2)
            continue

        with keyboard_lock:

            try:
                wait_time = settings.get("global_wait_time", 0.2)

                if settings["auto_craft_item"].get("Jewelry Potion", False):
                    
                    _search("Jewelry")

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "20")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_add"][0], CLICKS["autocraft_first_add"][1])

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
                            _prev_jewel = True
                        else:
                            _prev_jewel = False

                    mkey.left_click_xy_natural(CLICKS["autocraft_craft"][0], CLICKS["autocraft_craft"][1])

                    if send_item_crafted_notification:
                        _jewel_isfull = False

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
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
                        mkey.left_click_xy_natural(CLICKS["autocraft_auto"][0], CLICKS["autocraft_auto"][1])
                    time.sleep(1)

                if settings["auto_craft_item"].get("Zombie Potion", False):
                    _search("Zombie")

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "10")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_add"][0], CLICKS["autocraft_first_add"][1])
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_add"][0], CLICKS["autocraft_second_add"][1])

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
                            _prev_zomb = True
                        else:
                            _prev_zomb = False

                    mkey.left_click_xy_natural(CLICKS["autocraft_craft"][0], CLICKS["autocraft_craft"][1])

                    if send_item_crafted_notification:
                        _zomb_isfull = False

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
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
                        mkey.left_click_xy_natural(CLICKS["autocraft_auto"][0], CLICKS["autocraft_auto"][1])
                    time.sleep(1)

                if settings["auto_craft_item"].get("Rage Potion", False):
                    _search("Rage")

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "10")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_add"][0], CLICKS["autocraft_first_add"][1])

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
                            _prev_rage = True
                        else:
                            _prev_rage = False

                    mkey.left_click_xy_natural(CLICKS["autocraft_craft"][0], CLICKS["autocraft_craft"][1])

                    if send_item_crafted_notification:
                        _rage_isfull = False

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
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
                        mkey.left_click_xy_natural(CLICKS["autocraft_auto"][0], CLICKS["autocraft_auto"][1])
                    time.sleep(1)

                if settings["auto_craft_item"].get("Diver Potion", False):
                    _search("Diver")

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "20")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_add"][0], CLICKS["autocraft_first_add"][1])
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_add"][0], CLICKS["autocraft_second_add"][1])

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
                            _prev_dive = True
                        else:
                            _prev_dive = False

                    mkey.left_click_xy_natural(CLICKS["autocraft_craft"][0], CLICKS["autocraft_craft"][1])

                    if send_item_crafted_notification:
                        _diver_isfull = False

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
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
                        mkey.left_click_xy_natural(CLICKS["autocraft_auto"][0], CLICKS["autocraft_auto"][1])
                    time.sleep(1)

                if settings["auto_craft_item"].get("Potion of Bound", False):
                    _search("Bound")

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_add"][0], CLICKS["autocraft_first_add"][1])
                    time.sleep(delay)
                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_amt"][0], CLICKS["autocraft_second_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_amt"][0], CLICKS["autocraft_second_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "3")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_add"][0], CLICKS["autocraft_second_add"][1])
                    time.sleep(delay)
                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_amt"][0], CLICKS["autocraft_third_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_amt"][0], CLICKS["autocraft_third_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "10")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_add"][0], CLICKS["autocraft_third_add"][1])
                    time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_amt"][0], CLICKS["autocraft_third_scrolled_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_amt"][0], CLICKS["autocraft_third_scrolled_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "100")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_add"][0], CLICKS["autocraft_third_scrolled_add"][1])
                    


                    if send_item_crafted_notification:
                        time.sleep(0.2)
                        mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                        time.sleep(0.2)
                        ms.scroll(0, -30); time.sleep(0.2)
                        ms.scroll(0, -30); time.sleep(0.2)

                        _s = detect_add_potions(True, reader, REGIONS)

                        if _s:
                            _prev_bound = True
                        else:
                            _prev_bound = False

                    mkey.left_click_xy_natural(CLICKS["autocraft_craft"][0], CLICKS["autocraft_craft"][1])

                    if send_item_crafted_notification:
                        _bound_isfull = False

                        _s = detect_add_potions(True, reader, REGIONS)

                        if _s:
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
                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)

                    if job == "Potion of Bound":
                        mkey.left_click_xy_natural(CLICKS["autocraft_auto"][0], CLICKS["autocraft_auto"][1])
                    time.sleep(1)

                if settings["auto_craft_item"].get("Heavenly Potion", False):
                    _search("Heavenly")

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "250")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_add"][0], CLICKS["autocraft_first_add"][1])
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_add"][0], CLICKS["autocraft_second_add"][1])
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_add"][0], CLICKS["autocraft_second_add"][1])
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_add"][0], CLICKS["autocraft_third_add"][1])

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_scrolled_add"][0], CLICKS["autocraft_second_scrolled_add"][1])
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_scrolled_add"][0], CLICKS["autocraft_second_scrolled_add"][1])

                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_amt"][0], CLICKS["autocraft_third_scrolled_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_amt"][0], CLICKS["autocraft_third_scrolled_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "5")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_add"][0], CLICKS["autocraft_third_scrolled_add"][1])

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
                            _prev_heaven = True
                        else:
                            _prev_heaven = False

                    mkey.left_click_xy_natural(CLICKS["autocraft_craft"][0], CLICKS["autocraft_craft"][1])

                    if send_item_crafted_notification:
                        _heaven_isfull = False

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
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
                        mkey.left_click_xy_natural(CLICKS["autocraft_auto"][0], CLICKS["autocraft_auto"][1])
                    time.sleep(1)

                if settings["auto_craft_item"].get("Godly Potion (Zeus)", False):
                    _search("Zeus")

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "50")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_add"][0], CLICKS["autocraft_first_add"][1])
                    time.sleep(delay)

                    mkey.left_click_xy_natural(CLICKS["autocraft_second_amt"][0], CLICKS["autocraft_second_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_amt"][0], CLICKS["autocraft_second_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "25")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_add"][0], CLICKS["autocraft_second_add"][1])
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_add"][0], CLICKS["autocraft_third_add"][1])
                    time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_scrolled_add"][0], CLICKS["autocraft_second_scrolled_add"][1])
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_amt"][0], CLICKS["autocraft_third_scrolled_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_amt"][0], CLICKS["autocraft_third_scrolled_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "15")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_add"][0], CLICKS["autocraft_third_scrolled_add"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
                            _prev_zeus = True
                        else:
                            _prev_zeus = False

                    mkey.left_click_xy_natural(CLICKS["autocraft_craft"][0], CLICKS["autocraft_craft"][1])

                    if send_item_crafted_notification:
                        _zeus_isfull = False

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
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
                        mkey.left_click_xy_natural(CLICKS["autocraft_auto"][0], CLICKS["autocraft_auto"][1])
                    time.sleep(1)

                if settings["auto_craft_item"].get("Godly Potion (Poseidon)", False):
                    _search("Poseidon")

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "50")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_add"][0], CLICKS["autocraft_first_add"][1])
                    time.sleep(delay)
                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_add"][0], CLICKS["autocraft_second_add"][1])
                    time.sleep(delay)
                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_add"][0], CLICKS["autocraft_third_add"][1])
                    time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_add"][0], CLICKS["autocraft_third_scrolled_add"][1])

                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
                            _prev_poseidon = True
                        else:
                            _prev_poseidon = False

                    mkey.left_click_xy_natural(CLICKS["autocraft_craft"][0], CLICKS["autocraft_craft"][1])

                    if send_item_crafted_notification:
                        _poseidon_isfull = False

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
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
                        mkey.left_click_xy_natural(CLICKS["autocraft_auto"][0], CLICKS["autocraft_auto"][1])
                    time.sleep(1)

                if settings["auto_craft_item"].get("Godly Potion (Hades)", False):
                    _search("Hades")

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "50")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_add"][0], CLICKS["autocraft_first_add"][1])
                    time.sleep(delay)
                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_add"][0], CLICKS["autocraft_second_add"][1])

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
                            _prev_hades = True
                        else:
                            _prev_hades = False

                    mkey.left_click_xy_natural(CLICKS["autocraft_craft"][0], CLICKS["autocraft_craft"][1])

                    if send_item_crafted_notification:
                        _hades_isfull = False

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
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
                        mkey.left_click_xy_natural(CLICKS["autocraft_auto"][0], CLICKS["autocraft_auto"][1])
                    time.sleep(1)

                if settings["auto_craft_item"].get("Warp Potion", False):
                    _search("Warp")

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_add"][0], CLICKS["autocraft_first_add"][1])
                    time.sleep(delay)

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_amt"][0], CLICKS["autocraft_second_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_amt"][0], CLICKS["autocraft_second_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "5")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_add"][0], CLICKS["autocraft_second_add"][1])
                    time.sleep(delay)

                    mkey.left_click_xy_natural(CLICKS["autocraft_third_amt"][0], CLICKS["autocraft_third_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_amt"][0], CLICKS["autocraft_third_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "7")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_add"][0], CLICKS["autocraft_third_add"][1])
                    time.sleep(delay)

                    ms.scroll(0, -30); time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_scrolled_amt"][0], CLICKS["autocraft_first_scrolled_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_scrolled_amt"][0], CLICKS["autocraft_first_scrolled_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "100")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_scrolled_add"][0], CLICKS["autocraft_first_scrolled_add"][1])

                    ms.scroll(0, -30); time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_scrolled_amt"][0], CLICKS["autocraft_second_scrolled_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_scrolled_amt"][0], CLICKS["autocraft_second_scrolled_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "200")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_scrolled_add"][0], CLICKS["autocraft_second_scrolled_add"][1])

                    ms.scroll(0, -30); time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_amt"][0], CLICKS["autocraft_third_scrolled_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_amt"][0], CLICKS["autocraft_third_scrolled_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "1000")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_add"][0], CLICKS["autocraft_third_scrolled_add"][1])

                    if send_item_crafted_notification:                        
                        time.sleep(0.2)
                        mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                        time.sleep(0.2)
                        ms.scroll(0, -30); time.sleep(0.2)
                        ms.scroll(0, -30); time.sleep(0.2)

                        _s = detect_add_potions(True, reader, REGIONS)

                        if _s:
                            _prev_warp = True
                        else:
                            _prev_warp = False

                    mkey.left_click_xy_natural(CLICKS["autocraft_craft"][0], CLICKS["autocraft_craft"][1])

                    if send_item_crafted_notification:
                        _warp_isfull = False

                        _s = detect_add_potions(True, reader, REGIONS)

                        if _s:
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
                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)

                    if job == "Warp Potion":
                        mkey.left_click_xy_natural(CLICKS["autocraft_auto"][0], CLICKS["autocraft_auto"][1])
                    time.sleep(1)

                if settings["auto_craft_item"].get("Godlike Potion", False):
                    _search("Godlike")

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_add"][0], CLICKS["autocraft_first_add"][1])
                    time.sleep(delay)
                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_add"][0], CLICKS["autocraft_second_add"][1])
                    time.sleep(delay)
                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_add"][0], CLICKS["autocraft_third_add"][1])
                    time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_amt"][0], CLICKS["autocraft_third_scrolled_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_amt"][0], CLICKS["autocraft_third_scrolled_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "600")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_add"][0], CLICKS["autocraft_third_scrolled_add"][1])

                    if send_item_crafted_notification:                        
                        time.sleep(0.2)
                        mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                        time.sleep(0.2)
                        ms.scroll(0, -30); time.sleep(0.2)
                        ms.scroll(0, -30); time.sleep(0.2)

                        _s = detect_add_potions(True, reader, REGIONS)

                        if _s:
                            _prev_godlike = True
                        else:
                            _prev_godlike = False

                    mkey.left_click_xy_natural(CLICKS["autocraft_craft"][0], CLICKS["autocraft_craft"][1])

                    if send_item_crafted_notification:
                        _godlike_isfull = False

                        _s = detect_add_potions(True, reader, REGIONS)

                        if _s:
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
                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)
                    ms.scroll(0, 30); time.sleep(0.2)

                if settings["auto_craft_item"].get("Forbidden Potion I", False):
                    _search("Forbidden Potion I")

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_add"][0], CLICKS["autocraft_first_add"][1])
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_add"][0], CLICKS["autocraft_first_add"][1])
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_add"][0], CLICKS["autocraft_second_add"][1])
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_add"][0], CLICKS["autocraft_third_add"][1])

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
                            _prev_f1 = True
                        else:
                            _prev_f1 = False

                    mkey.left_click_xy_natural(CLICKS["autocraft_craft"][0], CLICKS["autocraft_craft"][1])

                    if send_item_crafted_notification:
                        _f1_isfull = False

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
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
                    _search("Forbidden Potion II")

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "20")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_add"][0], CLICKS["autocraft_first_add"][1])
                    time.sleep(delay)
                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_amt"][0], CLICKS["autocraft_second_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_amt"][0], CLICKS["autocraft_second_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "10")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_add"][0], CLICKS["autocraft_second_add"][1])
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_add"][0], CLICKS["autocraft_third_add"][1])

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
                            _prev_f2 = True
                        else:
                            _prev_f2 = False

                    mkey.left_click_xy_natural(CLICKS["autocraft_craft"][0], CLICKS["autocraft_craft"][1])

                    if send_item_crafted_notification:
                        _f2_isfull = False

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
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
                    _search("Forbidden Potion III")

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "100")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_add"][0], CLICKS["autocraft_first_add"][1])
                    time.sleep(delay)
                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_amt"][0], CLICKS["autocraft_second_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_amt"][0], CLICKS["autocraft_second_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "65")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_add"][0], CLICKS["autocraft_second_add"][1])
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_add"][0], CLICKS["autocraft_third_add"][1])
                    
                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
                            _prev_f3 = True
                        else:
                            _prev_f3 = False

                    mkey.left_click_xy_natural(CLICKS["autocraft_craft"][0], CLICKS["autocraft_craft"][1])

                    if send_item_crafted_notification:
                        _f3_isfull = False

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
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
                
                if settings["auto_craft_item"].get("Void Heart", False):
                    _search("Void")

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_amt"][0], CLICKS["autocraft_first_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "50")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_first_add"][0], CLICKS["autocraft_first_add"][1])
                    time.sleep(delay)
                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_amt"][0], CLICKS["autocraft_second_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_amt"][0], CLICKS["autocraft_second_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "5")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_add"][0], CLICKS["autocraft_second_add"][1])
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_add"][0], CLICKS["autocraft_third_add"][1])
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_add"][0], CLICKS["autocraft_third_add"][1])
                    time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_scrolled_amt"][0], CLICKS["autocraft_second_scrolled_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_scrolled_amt"][0], CLICKS["autocraft_second_scrolled_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "10")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_second_scrolled_add"][0], CLICKS["autocraft_second_scrolled_add"][1])

                    ms.scroll(0, -30); time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_amt"][0], CLICKS["autocraft_third_scrolled_amt"][1])
                    time.sleep(0.2)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_amt"][0], CLICKS["autocraft_third_scrolled_amt"][1])
                    time.sleep(delay)
                    _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "10")
                    time.sleep(delay)
                    mkey.left_click_xy_natural(CLICKS["autocraft_third_scrolled_add"][0], CLICKS["autocraft_third_scrolled_add"][1])

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)
                    ms.scroll(0, -30); time.sleep(delay)

                    if send_item_crafted_notification:

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
                            _prev_void = True
                        else:
                            _prev_void = False

                    mkey.left_click_xy_natural(CLICKS["autocraft_craft"][0], CLICKS["autocraft_craft"][1])

                    if send_item_crafted_notification:
                        _void_isfull = False

                        _ = detect_add_potions(False, reader, REGIONS)

                        if _:
                            _void_isfull = True
                        else:
                            _void_isfull = False

                        if _prev_void != _void_isfull:
                            potions_crafted += 1
                            emb = create_autocraft_embed("Void Heart")
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

                        _prev_void = _void_isfull

                    mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
                    time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)
                    ms.scroll(0, 30); time.sleep(delay)

                    if job == "Void Heart":
                        mkey.left_click_xy_natural(CLICKS["autocraft_auto"][0], CLICKS["autocraft_auto"][1])
                    time.sleep(1)

                time.sleep(1)
                kb.press('f')
                time.sleep(0.2)
                kb.release('f')
                time.sleep(1)
                
                mkey.left_click_xy_natural(CLICKS["close_menu"][0], CLICKS["close_menu"][1])

                time.sleep(1)
                mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
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
                
                mkey.left_click_xy_natural(CLICKS["close_menu"][0], CLICKS["close_menu"][1])

                time.sleep(1)
                mkey.move_to_natural(CLICKS["autocraft_scroll"][0], CLICKS["autocraft_scroll"][1])
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

def auto_br(settings: dict, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, pause_event, reader, ms):
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
            use_item("Biome Random", 1, True, mkey, kb, settings, reader, ms)

        wait_interval = 2160 
        logger.write_log(f"Auto BR: Waiting {wait_interval} seconds...")
        if stop_event.wait(timeout=wait_interval):
            break
        if sniped_event.is_set(): break
    logger.write_log("Auto Biome Randomizer thread stopped.")

def auto_sc(settings: dict, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, pause_event, reader, ms):
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
            use_item("Strange Control", 1, True, mkey, kb, settings, reader, ms)

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

    if not settings.get("calibration"):
        logger.write_log("A calibration has not been selected.")
        return
    
    if not validate_calibrations(settings.get("calibration"), ["open_inventory", "items_btn", "search_bar", "close_menu"]):
        logger.write_log("Could not verify all calibrations.")
        return
    
    CLICKS = get_calibrations(settings.get("calibration"))
    delay = load_delay()

    while not stop_event.is_set():

        if pause_event.is_set():
            time.sleep(2)
            continue

        logger.write_log("Taking inventory screenshot...")
        screenshot_path = os.path.join(MACROPATH, "scr", "screenshot_inventory.png")
        file_to_send = None
        with keyboard_lock:

            mkey.left_click_xy_natural(CLICKS["open_inventory"][0], CLICKS["open_inventory"][1])
            time.sleep(delay)
            mkey.left_click_xy_natural(CLICKS["items_btn"][0], CLICKS["items_btn"][1])
            time.sleep(delay)
            mkey.left_click_xy_natural(CLICKS["search_bar"][0], CLICKS["search_bar"][1])
            time.sleep(delay)
            pag.screenshot(screenshot_path)
            file_to_send = create_discord_file_from_path(screenshot_path, filename="inventory.png")
            time.sleep(delay)
            mkey.left_click_xy_natural(CLICKS["close_menu"][0], CLICKS["close_menu"][1])
            time.sleep(delay)

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

    if not settings.get("calibration"):
        logger.write_log("A calibration has not been selected.")
        return
    
    if not validate_calibrations(settings.get("calibration"), ["open_storage", "search_bar", "close_menu"]):
        logger.write_log("Could not verify all calibrations.")
        return
    
    CLICKS = get_calibrations(settings.get("calibration"))
    delay = load_delay()

    while not stop_event.is_set():

        if pause_event.is_set():
            time.sleep(2)
            continue

        logger.write_log("Taking aura storage screenshot...")
        screenshot_path = os.path.join(MACROPATH, "scr", "screenshot_storage.png")
        file_to_send = None
        with keyboard_lock:
            
            mkey.left_click_xy_natural(CLICKS["open_storage"][0], CLICKS["open_storage"][1])
            time.sleep(delay)
            mkey.left_click_xy_natural(CLICKS["search_bar"][0], CLICKS["search_bar"][1])
            time.sleep(delay)
            kb.press(keyboard.Key.backspace)
            time.sleep(0.2)
            kb.release(keyboard.Key.backspace)
            time.sleep(delay)
            pag.screenshot(screenshot_path)
            file_to_send = create_discord_file_from_path(screenshot_path, filename="storage.png")
            time.sleep(delay)
            mkey.left_click_xy_natural(CLICKS["close_menu"][0], CLICKS["close_menu"][1])
            time.sleep(delay)

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
    link_code_type = None
    try:
        link_code, link_code_type = extract_server_code(ps_link)
    except Exception as e:
        logger.write_log(f"Error extracting link code for disconnect prevention: {e}")

    if not link_code or not link_code_type:
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
                    if link_code_type == 1:
                        join_private_server_link(link_code)
                    elif link_code_type == 2:
                        join_private_share_link(link_code)
                    else:
                        logger.write_log("Unknown Link code type (stopping).")
                        return
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


def do_obby(settings: dict, webhook, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, ignore_lock, ignore_next_detection, pause_event, reader, ms):
    logger = get_logger()
    if stop_event.wait(timeout=5):
        return
    logger.write_log("Obby Blessing thread started.")
    nav_mode = settings.get("interaction_type", "Mouse")

    is_autocraft = settings.get("mode", "Normal") == "Auto Craft"
    has_abyssal = settings.get("has_abyssal_hunter", False)
    afk_in_limbo = settings.get("mode", "Normal") == "Limbo"
    is_idle_mode = settings.get("mode", "Normal") == "IDLE"

    if not IMPORTED_ALL_PATHS:
        logger.write_log("Obby thread not started due to missing paths.")
        return
    
    if not settings.get("calibration"):
        logger.write_log("A calibration has not been selected.")
        return
    
    if not validate_calibrations(settings.get("calibration"), ["questboard_right", "questboard_left", "questboard_exit", "questboard_dismiss", "questboard_accept", "close_menu"]):
        logger.write_log("Could not verify all calibrations.")
        return
    
    CLICKS = get_calibrations(settings.get("calibration"))
    delay = load_delay()
    VIP_STATUS = settings.get("vip_status", "No VIP")

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
                mkey.left_click_xy_natural(CLICKS["collection"][0], CLICKS["collection"][1])
                time.sleep(1)
                mkey.left_click_xy_natural(CLICKS["exit_collection"][0], CLICKS["exit_collection"][1])
                time.sleep(1)
            except Exception as e:
                logger.write_log(f"Error during obby alignment: {e}")
                continue

            if has_abyssal:
                if equip_aura("Abyssal", False, mkey, kb, settings, ignore_next_detection, ignore_lock, reader, ms):
                    logger.write_log("Using Abyssal Path for Obby")
                    obby_abyssal.run_macro(obby_abyssal.macro_actions)
                else:
                    if VIP_STATUS in ["VIP", "VIP+"]:
                        logger.write_log("Using VIP Path for Obby (Abyssal Equip Failed)")
                        obby_vip.run_macro(obby_vip.macro_actions)
                    
                    else:
                        logger.write_log("Using Non VIP Path for Obby (Abyssal Equip Failed)")
                        obby.run_macro(obby.macro_actions)
            elif VIP_STATUS in ["VIP", "VIP+"]:
                logger.write_log("Using VIP Path for Obby")
                obby_vip.run_macro(obby_vip.macro_actions)            
            else:
                logger.write_log("Using Non VIP Path for Obby")
                obby.run_macro(obby.macro_actions)
            
            time.sleep(1)

            logger.write_log("Completed obby, realigning incase of failure.")
            try:
                reset_character()
                time.sleep(1)
                reset_character()
                time.sleep(1)
                mkey.left_click_xy_natural(CLICKS["collection"][0], CLICKS["collection"][1])
                time.sleep(1)
                mkey.left_click_xy_natural(CLICKS["exit_collection"][0], CLICKS["exit_collection"][1])
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
            
            if is_autocraft and IMPORTED_ALL_PATHS:
                if has_abyssal:
                    if equip_aura("Abyssal", False, mkey, kb, settings, ignore_next_detection, ignore_lock, reader, ms):
                        logger.write_log("Using Abyssal Path for Stella")
                        stella_abyssal.run_macro(stella_abyssal.macro_actions)
                    else:
                        if VIP_STATUS in ["VIP", "VIP+"]:
                            logger.write_log("Using VIP path for Stella (Abyssal Equip failed)")
                            stella_vip.run_macro(stella_vip.macro_actions)                        
                        else:
                            logger.write_log("Walking back to Stella is not supported with No VIP")
                elif VIP_STATUS in ["VIP", "VIP+"]:
                    logger.write_log("Using VIP Path for Stella")
                    stella_vip.run_macro(stella_vip.macro_actions)
                
                else:
                    logger.write_log("Walking back to Stella is not supported with No VIP")
            
            elif afk_in_limbo and not is_idle_mode:
                logger.write_log("Teleporting back to limbo...")
                use_item("Portable Crack", 1, True, mkey, kb, settings, reader, ms)
                time.sleep(0.5)

            if has_abyssal:
                equip_aura("Abyssal", True, mkey, kb, settings, ignore_next_detection, ignore_lock, reader, ms)

        wait_interval = 600 
        logger.write_log(f"Obby: Waiting {wait_interval} seconds...")
        if stop_event.wait(timeout=wait_interval):
            break
        if sniped_event.is_set(): break

    logger.write_log("Obby/Blessing thread stopped.")

def auto_questboard(settings: dict, webhook, stop_event: threading.Event, sniped_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, ms, ignore_lock, ignore_next_detection, pause_event, reader):
    logger = get_logger()
    nav_mode = settings.get("interaction_type", "Mouse")
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
    
    if not settings.get("calibration"):
        logger.write_log("A calibration has not been selected.")
        return
    
    if not validate_calibrations(settings.get("calibration"), ["collection", "exit_collection", "close_menu"]):
        logger.write_log("Could not verify all calibrations.")
        return
    
    if not validate_regions(settings.get("calibration"), ["questboard_quest_region"]):
        logger.write_log("Could not start auto questboard: Calibration is invalid.")
        return
    
    CLICKS = get_calibrations(settings.get("calibration"))
    REGIONS = get_regions(settings.get("calibration"))
    delay = load_delay()

    VIP_STATUS = settings.get("vip_status", "No VIP")
    afk_in_limbo = settings.get("mode", "Normal") == "Limbo"
    is_idle_mode = settings.get("mode", "Normal") == "IDLE"
    
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
            mkey.left_click_xy_natural(CLICKS["collection"][0], CLICKS["collection"][1])
            time.sleep(1)
            mkey.left_click_xy_natural(CLICKS["exit_collection"][0], CLICKS["exit_collection"][1])
            time.sleep(1)
            equip_aura("Abyssal", True, mkey, kb, settings, ignore_next_detection, ignore_lock, reader, ms)
            time.sleep(1)

            if VIP_STATUS in ["VIP", "VIP+"]:
                logger.write_log("Using VIP Path for Questboard")
                qb_vip.run_macro(qb_vip.macro_actions)
            elif VIP_STATUS == "No VIP":
                logger.write_log("Using Non VIP Path for Questboard")
                qb.run_macro(qb.macro_actions)
                return
            else:
                logger.write_log(f"VIP Status ({VIP_STATUS}) is unrecognised.")
                return
            
            time.sleep(1)
            kb.press(keyboard.Key.left)
            time.sleep(1.5)
            kb.release(keyboard.Key.left)
            
            time.sleep(1)
            kb.press("e")
            time.sleep(0.2)
            kb.release("e")
            time.sleep(3)

            previous_quest = None

            detected_quests = []

            time.sleep(1)

            for i in range(5):
                pag.screenshot(screenshot_path)            

                image = cv2.imread(screenshot_path)
                if image is None:
                    logger.write_log("Auto Quest Board Error: Failed to read screenshot file.")
                    continue
                
                x1, y1, x2, y2 = REGIONS["questboard_quest_region"]

                quest_title_crop = image[y1:y2, x1:x2]
                ocr_results = reader.readtext(quest_title_crop, detail=0)
                ocr_quest_raw = " ".join(ocr_results).strip()

                ocr_quest_clean = re.sub(r"[^a-zA-Z']", "", ocr_quest_raw).lower()
                detected_quest = fuzzy_match_qb(ocr_quest_clean, ALL_QB)

                if not detected_quest:
                    logger.write_log(f"Auto Quest Board: Could not identify quest from OCR ('{ocr_quest_raw}'). Dismissing.") 
                    mkey.left_click_xy_natural(CLICKS["questboard_dismiss"][0], CLICKS["questboard_dismiss"][1])
                    time.sleep(1)
                else:
                    logger.write_log(f"Auto Quest Board: Detected Quest ('{detected_quest}')")

                    if detected_quest in ACCEPTED_QUESTBOARD:

                        quest_data = questboard_data.get(detected_quest, None)

                        if not quest_data:
                            logger.write_log(f"Auto Quest Board: Could not find data for quest ('{detected_quest}'). Skipping")
                            mkey.left_click_xy_natural(CLICKS["questboard_dismiss"][0], CLICKS["questboard_dismiss"][1])
                            time.sleep(1)
                        else:
                            if settings.get("quests_to_accept", {}).get(detected_quest, False) and detected_quest not in tracked_quests.get("quest_board", []) and len(tracked_quests.get("quest_board", [])) <= 3:
                                logger.write_log(f"Auto Quest Board: Accepted Quest ('{detected_quest}')")
                                mkey.left_click_xy_natural(CLICKS["questboard_accept"][0], CLICKS["questboard_accept"][1])
                                time.sleep(0.2)
                                tracked_quests["quest_board"].append(detected_quest)
                                previous_quest = detected_quest
                                with open(TRACKED_QUESTS_PATH, "w", encoding="utf-8") as f:
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
                                mkey.left_click_xy_natural(CLICKS["questboard_right"][0], CLICKS["questboard_right"][1])
                                time.sleep(0.2)
                            elif detected_quest in tracked_quests.get("quest_board", []):
                                if previous_quest == detected_quest:
                                    logger.write_log("Quest already accepted and same as previous quest, therefore no more quests.")
                                    break
                                logger.write_log("Quest already accepted, attempting to claim.")
                                mkey.left_click_xy_natural(CLICKS["questboard_accept"][0], CLICKS["questboard_accept"][1])
                                time.sleep(0.2)
                                previous_quest = detected_quest

                                time.sleep(2)

                                pag.screenshot(screenshot_path)            

                                image = cv2.imread(screenshot_path)
                                if image is None:
                                    logger.write_log("Auto Quest Board Error: Failed to read screenshot file.")
                                    continue
                                
                                x1, y1, x2, y2 = REGIONS["questboard_quest_region"]

                                quest_title_crop = image[y1:y2, x1:x2]
                                ocr_results = reader.readtext(quest_title_crop, detail=0)
                                ocr_quest_raw = " ".join(ocr_results).strip()

                                ocr_quest_clean = re.sub(r"[^a-zA-Z']", "", ocr_quest_raw).lower()
                                detected_quest = fuzzy_match_qb(ocr_quest_clean, ALL_QB)
                                
                                if previous_quest == detected_quest:
                                    logger.write_log("Quest is not yet completed, moving to next quest.")
                                    time.sleep(3)
                                    mkey.left_click_xy_natural(CLICKS["questboard_right"][0], CLICKS["questboard_right"][1])
                                    time.sleep(0.2)
                                else:
                                    logger.write_log("Quest was completed, removing from tracked quests.")
                                    tracked_quests["quest_board"].remove(previous_quest)
                                    with open(TRACKED_QUESTS_PATH, "w", encoding="utf-8") as f:
                                        json.dump(tracked_quests, f, indent=4)
                                    description = f"**Objective**: {quest_data.get('objective', 'Failed to fetch objective.')}\n**Difficulty**: "
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
                                mkey.left_click_xy_natural(CLICKS["questboard_dismiss"][0], CLICKS["questboard_dismiss"][1])
                                time.sleep(1)
                                previous_quest = detected_quest
                    else:
                        logger.write_log(f"Auto Quest Board: Quest ('{detected_quest}') is not supported yet, dismissing.")
                        mkey.left_click_xy_natural(CLICKS["questboard_dismiss"][0], CLICKS["questboard_dismiss"][1])
                        time.sleep(1)
                        previous_quest = detected_quest
                    time.sleep(3)

            mkey.left_click_xy_natural(CLICKS["questboard_exit"][0], CLICKS["questboard_exit"][1])
            time.sleep(1)
            time.sleep(3)
            reset_character()
            time.sleep(1)
            reset_character()
            time.sleep(3)
            
            if afk_in_limbo and not is_idle_mode:
                logger.write_log("Teleporting back to limbo...")
                use_item("Portable Crack", 1, True, mkey, kb, settings, reader, ms)
                time.sleep(0.5)
        logger.write_log(f"Auto Quest Board: Waiting {wait_interval} seconds...")
        if stop_event.wait(timeout=wait_interval):
            break
        if sniped_event.is_set(): break
    logger.write_log("Auto Quest Board thread stopped.")

def auto_pop(biome: str, settings: dict, stop_event: threading.Event, keyboard_lock: threading.Lock, mkey, kb, reader, ms):
    logger = get_logger()
    logger.write_log(f"Auto Pop sequence initiated for biome: {biome}")
    biome_lower = biome.lower()

    if not settings.get("calibration"):
        logger.write_log("A calibration has not been selected.")
        return
    
    if not validate_calibrations(settings.get("calibration"), ["collection", "exit_collection", "close_menu"]):
        logger.write_log("Could not verify all calibrations.")
        return
    
    CLICKS = get_calibrations(settings.get("calibration"))

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
                mkey.left_click_xy_natural(CLICKS["menu"][0], CLICKS["menu"][1])
                time.sleep(1)
                mkey.left_click_xy_natural(CLICKS["settings"][0], CLICKS["settings"][1])
                time.sleep(1)
                mkey.left_click_xy_natural(CLICKS["rolling"][0], CLICKS["rolling"][1])
                time.sleep(1)
                mkey.left_click_xy_natural(CLICKS["cutscene_skip"][0], CLICKS["cutscene_skip"][1])
                time.sleep(1)
                _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "9999999999")
                mkey.left_click_xy_natural(CLICKS["close_menu"][0], CLICKS["close_menu"][1])
                time.sleep(1)                
            except Exception as cs_e:
                logger.write_log(f"Error changing cutscene settings: {cs_e}")

                try: mkey.left_click_xy_natural(CLICKS["close_menu"][0], CLICKS["close_menu"][1])
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
                    use_item(item, use_amount, True, mkey, kb, settings, reader, ms)
                remaining_amount -= use_amount
                time.sleep(1.5) 

                current_biome_check = get_latest_hovertext()
                if current_biome_check is None or current_biome_check.lower() != biome_lower:
                     logger.write_log("Auto Pop: Biome ended during item use. Stopping sequence.")
                     return
        else:
             with keyboard_lock:
                use_item(item, amount_to_use, True, mkey, kb, settings, reader, ms)
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

    if not settings.get("calibration"):
        logger.write_log("A calibration has not been selected.")
        return
    
    if not validate_calibrations(settings.get("calibration"), ["collection", "exit_collection", "close_menu"]):
        logger.write_log("Could not verify all calibrations.")
        return
    
    CLICKS = get_calibrations(settings.get("calibration"))
    delay = load_delay()
    VIP_STATUS = settings.get("vip_status", "No VIP")
    
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
                    use_item("Portable Crack", 1, True, mkey, kb, settings, reader, ms)
                    time.sleep(1)
                    mkey.left_click_xy_natural(CLICKS["collection"][0], CLICKS["collection"][1])
                    time.sleep(1)
                    mkey.left_click_xy_natural(CLICKS["exit_collection"][0], CLICKS["exit_collection"][1])
                    time.sleep(1)

                    if VIP_STATUS in ["VIP", "VIP+"]:
                        logger.write_log("Using VIP Path for Eden")
                        eden_vip.run_macro(eden_vip.macro_actions)
                    else:
                        logger.write_log(f"VIP Status ({VIP_STATUS}) is not currently supported by Auto Eden.")

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

            _type(kb, settings.get("typing_jitter", 0.2), settings.get("typing_delay", 0.2), settings.get("typing_hold", 0.2), "vok taran")

            kb.press(keyboard.Key.enter)
            time.sleep(0.05)
            kb.release(keyboard.Key.enter)
            time.sleep(0.05)

        if stop_event.wait(timeout=1860):
            break