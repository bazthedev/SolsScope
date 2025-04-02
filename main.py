#           Baz's Macro/SolsRNGBot
#   A discord bot for macroing Sol's RNG on Roblox
#   Version: 1.2.0 Hotfix 2
#   https://github.com/bazthedev/SolsRNGBot
#
import  sys
try:
    import os
    import discord
    from discord.ext import commands, tasks
    import pyautogui as pag
    from datetime import datetime
    import json
    from pynput import mouse, keyboard
    from pynput.keyboard import Key
    import asyncio
    from PIL import ImageGrab
    import requests
    import screeninfo as si
    import re
    import glob
    import shutil
    import tempfile
    import psutil
    import random
    import tkinter as tk
    from tkinter import ttk, messagebox
    import mousekey as mk
    from aiohttp import ClientSession
    import subprocess
    import typing
    from websockets import connect
    from pathlib import Path
    import zipfile
except ModuleNotFoundError:
    print("A module is missing, please reinstall the requirements to fix this.")
    sys.exit()

mkey = mk.MouseKey()
MACROPATH = os.path.expandvars(r"%localappdata%\Baz's Macro") # Windows Roaming Path
LOCALVERSION = "1.2.0"
PRERELEASE = False
SERVERMACRO_EDITION = False
if PRERELEASE:
    print(f"Warning! This is a prerelease version of SolsRNGBot, meaning you can expect bugs and some errors to occur!\nYou can find logs relating to events that occur during the prerelease in this folder: {MACROPATH}\n\nYou are currently running prerelease for version {LOCALVERSION}, are you sure you wish to continue?")
    input("Press ENTER to continue using the macro: ")
if SERVERMACRO_EDITION or LOCALVERSION.endswith("SE"):
    print("This is a stripped down version of SolsRNGBot designed for people who macro in Glitch Hunt Servers.")
DEFAULTSETTINGS = {"TOKEN": "", "__version__" :  LOCALVERSION, "log_channel_id": 0, "use_rblx_player" : True, "global_wait_time" : 0.1, "skip_aura_download": False, "mention" : True, "mention_id" : 0, "minimum_roll" : "99998", "minimum_ping" : "349999", "reset_aura" : "", "merchant_detection" : False, "send_mari" : True, "ping_mari" : False, "send_jester" : True, "ping_jester" : True, "auto_purchase_items" : {"Void Coin/Lucky Penny" : True, "Oblivion Potion" : True}, "clear_logs" : False, "pop_in_glitch" : False, "auto_use_items_in_glitch": {"Heavenly Potion" : {"use" : True, "amount" : 200}, "Fortune Potion III" : {"use" : True, "amount" : 1}, "Lucky Potion" : {"use" : True, "amount" : 10}, "Pumpkin" : {"use" : True, "amount" : 10}, "Haste Potion III" : {"use" : False, "amount" : 1}, "Warp Potion" : {"use" : True, "amount" : 1}, "Transcended Potion" : {"use" : False, "amount" : 1}, "Mixed Potion" : {"use" : True, "amount" : 10}, "Stella's Candle" : {"use" : True, "amount" : 1}, "Santa Claus Potion" : {"use" : True, "amount" : 5}, "Hwachae" : {"use" : True, "amount" : 1}}, "pop_in_dreamspace" : False, "auto_use_items_in_dreamspace" : {"Heavenly Potion" : {"use" : False, "amount" : 1}, "Fortune Potion III" : {"use" : True, "amount" : 1}, "Lucky Potion" : {"use" : True, "amount" : 10}, "Pumpkin" : {"use" : True, "amount" : 10}, "Haste Potion III" : {"use" : False, "amount" : 1}, "Warp Potion" : {"use" : True, "amount" : 1}, "Transcended Potion" : {"use" : False, "amount" : 1}, "Mixed Potion" : {"use" : True, "amount" : 10}, "Stella's Candle" : {"use" : True, "amount" : 1}, "Santa Claus Potion" : {"use" : True, "amount" : 5}, "Hwachae" : {"use" : True, "amount" : 1}}, "auto_craft_mode" : False, "skip_auto_mode_warning" : False, "auto_craft_item" : {"Potion of Bound" : False, "Heavenly Potion" : True, "Godly Potion (Zeus)" : True, "Godly Potion (Poseidon)" : True, "Godly Potion (Hades)" : True, "Warp Potion" : True, "Godlike Potion" : True}, "auto_biome_randomizer" : False, "auto_strange_controller" : False, "edit_settings_mode" : True, "failsafe_key" : "ctrl+e", "merchant_detec_wait" : 0, "private_server_link" : "", "take_screenshot_on_detection" : False, "ROBLOSECURITY_KEY" : "", "DISCORD_TOKEN" : "", "collect_items" : {"1" : False, "2" : False, "3" : False, "4" : False}, "sniper_enabled" : False, "sniper_toggles" : {"Glitched" : True, "Dreamspace" : False}, "sniper_channel_id" : 0, "sniper_logs" : True, "change_cutscene_on_pop" : True, "disable_autokick_prevention" : False, "periodic_screenshots" : {"inventory" : False, "storage" : False}, "disconnect_prevention" : False, "check_update" : True, "auto_install_update" : False, "biomes" : {"snowy" : False, "windy" : False, "rainy" : False, "sand storm" : False, "hell" : False, "starfall" : False, "corruption" : False, "null" : False, "glitched" : True, "dreamspace" : True}}
VALIDSETTINGSKEYS = ["TOKEN", "__version__", "log_channel_id", "use_rblx_player", "global_wait_time", "skip_aura_download", "mention", "mention_id", "minimum_roll", "minimum_ping", "reset_aura", "merchant_detection", "send_mari", "ping_mari", "send_jester", "ping_jester", "auto_purchase_items", "clear_logs", "pop_in_glitch", "auto_use_items_in_glitch", "pop_in_dreamspace", "auto_use_items_in_dreamspace", "auto_craft_mode", "skip_auto_mode_warning", "auto_craft_item", "auto_biome_randomizer", "auto_strange_controller", "edit_settings_mode", "failsafe_key", "merchant_detec_wait", "private_server_link", "take_screenshot_on_detection", "ROBLOSECURITY_KEY", "DISCORD_TOKEN", "sniper_enabled", "sniper_toggles", "collect_items", "sniper_channel_id", "sniper_logs", "change_cutscene_on_pop", "disable_autokick_prevention", "periodic_screenshots", "disconnect_prevention", "check_update", "auto_install_update", "biomes"]
STARTUP_MSGS = ["Let's go gambling!", "Nah, I'd Roll", "I give my life...", "Take a break", "Waste of time", "I can't stop playing this", "Touch the grass", "Eternal time...", "Break the Reality", "Finished work for today", "When is payday???", "-One who stands before God-", "-Flaws in the world-", "We do a little bit of rolling", "Exotic Destiny", "Always bet on yourself", "(Lime shivers quietly in the cold)", "There's no way to stop it!", "[Tip]: Get Lucky", "I'm addicted to Sol's RNG", "The Lost"]
ACCEPTEDPOTIONS = ["Potion of Bound", "Heavenly Potion", "Godly Potion (Zeus)", "Godly Potion (Poseidon)", "Godly Potion (Hades)", "Warp Potion", "Godlike Potion"]
detected_snipe = False

if not os.path.exists(f"{MACROPATH}"):
    os.mkdir(MACROPATH)

if not os.path.isfile(f"{MACROPATH}/settings.json"):
    with open(f"{MACROPATH}/settings.json", "w") as f:
        json.dump(DEFAULTSETTINGS, f, indent=4)

# THE FOLLOWING CODE IS A SLIGHTLY MODIFIED VERSION OF YAY JOINS SNIPER 1.2.10, WHICH IS OWNED BY Root1527. YOU CAN DOWNLOAD THE REGULAR VERSION OF YAY JOINS HERE: https://github.com/Root1527/yay-joins

PLACE_ID = 15532962292
BASE_ROBLOX_URL = f"https://www.roblox.com/games/{PLACE_ID}/Sols-RNG-Eon1-1"
DISCORD_WS_BASE = "wss://gateway.discord.gg/?v=10&encoding-json"
SHARELINKS_API = "https://apis.roblox.com/sharelinks/v1/resolve-link"


class Sniper:
    def __init__(self):
        self.config = self._load_config()
        self.roblox_session: typing.Optional[ClientSession] = None
        self._refresh_task = None
        self.output_list = []
        self.is_running = True

        self.words = ["Glitched", "Dreamspace"]

        self.link_pattern = re.compile(
            f"https://www.roblox.com/games/{PLACE_ID}/Sols-RNG-Eon1-1\\?privateServerLinkCode="
        )
        self.link_pattern_2 = re.compile(r"https://.*&type=Server")

        self.blacklists = [
            re.compile(pattern)
            for pattern in [
                "need|want|lf|look|stop|how|bait|ste|snip|fak|real|pl|hunt|sho|sea|wait|tho|gone|think|ago|prob|try|dev|adm|or|see|cap|tot|is|us|spa|giv|get|hav|and|str|sc|br|rai|wi|san|star|null|pm|gra|pump|moon|scr|mac|do|did|jk|no|rep|dm|farm|sum|who|if|imag|pro|bot|next|post|was|bae|fae",
                "need|want|lf|look|stop|how|bait|ste|snip|fak|real|pl|hunt|sho|sea|wait|tho|gone|think|ago|prob|try|dev|adm|or|see|cap|tot|is|us|giv|get|hav|and|str|br|rai|wi|san|star|null|pm|gra|pump|moon|scr|mac|do|did|jk|no|rep|dm|farm|sum|who|if|imag|pro|bot|next|post|was|bae|fae",
            ]
        ]
        self.word_patterns = [
            re.compile(pattern)
            for pattern in [r"g[liotc]+h", r"d[rea]+ms"]
        ]

    def _load_config(self):
        with open(f"{MACROPATH}/settings.json", "r") as f:
            config = json.load(f)
        return config

    async def setup(self):
        self.roblox_session = ClientSession()
        self.roblox_session.cookie_jar.update_cookies(
            {".ROBLOSECURITY": self.config["ROBLOSECURITY_KEY"]}
        )

    async def _identify(self, ws):
        try:
            identify_payload = {
                "op": 2,
                "d": {
                    "token": self.config["DISCORD_TOKEN"],
                    "properties": {"$os": "windows", "$browser": "chrome", "$device": "pc"}
                }
            }
            await ws.send(json.dumps(identify_payload))
        except Exception as e:
            if self.config["sniper_logs"]:
                print(f"[SNIPER] Error: {e}")
        
    async def _subscribe(self, ws):
        subscription_payload = {
            "op": 14,
            "d": {
                    "guild_id": "1186570213077041233",
                    "channels_ranges": {},
                    "typing": True,
                    "threads": False,
                    "activities": False,
                    "members": [],
                    "thread_member_lists": []
                }
            }
        await ws.send(json.dumps(subscription_payload))

    async def heartbeat(self, ws, interval):
        while True:
            try:
                heartbeat_json= {
                    'op':1,
                    'd': 'null'
                }
                await ws.send(json.dumps(heartbeat_json))
                await asyncio.sleep(interval)
            except Exception as e:
                if self.config["sniper_logs"]:
                    print(f"[SNIPER] Error: {e}")

    async def _on_message(self, ws):
        while True:
            event = json.loads(await ws.recv())
            try:
                if event["t"] == "MESSAGE_CREATE":
                    channel_id = event["d"]["channel_id"]
                    content = event["d"]["content"]
                    for choice_id in self.cycle_index:
                        if int(channel_id) == [1282542323590496277, 1282542323590496277][choice_id]:
                            await self.process_message(content, choice_id)
            except Exception as e:
                if self.config["sniper_logs"]:
                    print(f"[SNIPER] Error: {e}")

    def _should_process_message(self, message: str, choice_id: int) -> bool:          
        if not self.word_patterns[choice_id].search(message.lower()):
            return False

        if self.blacklists[choice_id].search(message.lower()):
            if self.config["sniper_logs"]:
                print(f"[SNIPER] Filtered message! content: {message}")
            return False

        return True

    async def _extract_server_code(self, message: str) -> typing.Optional[str]:
        if link_match := self.link_pattern.search(message):
            return link_match.group(0).split("LinkCode=")[-1]

        if link_match_2 := self.link_pattern_2.search(message):
            share_code = link_match_2.group(0).split("code=")[-1].split("&")[0]
            return await self._convert_link(share_code)
        
        if "locked" in message.lower():
            print("The #biomes channel has been locked!")
        return None

    async def _convert_link(self, link_id: str) -> typing.Optional[str]:
        payload = {"linkId": link_id, "linkType": "Server"}

        async with self.roblox_session.post(SHARELINKS_API, json=payload) as response:
            if response.status == 403 and "X-CSRF-TOKEN" in response.headers:
                self.roblox_session.headers["X-CSRF-TOKEN"] = response.headers[
                    "X-CSRF-TOKEN"
                ]
                async with self.roblox_session.post(
                    SHARELINKS_API, json=payload
                ) as retry_response:
                    data = await retry_response.json()
            else:
                data = await response.json()

        if data["privateServerInviteData"]["placeId"] != PLACE_ID:
            if self.config["sniper_logs"]:
                print("[SNIPER] Filtered non-sols link!")
            return None

        return data["privateServerInviteData"]["linkCode"]

    async def _handle_server_join(self, choice_id: int, server_code: str):
        global detected_snipe, rblx_log_dir
        if rblx_log_dir == rblx_player_log_dir:
            os.system("taskkill /f /im RobloxPlayerBeta.exe /t")
            rblx_log_dir = ms_rblx_log_dir
        detected_snipe = True
        await self._join_windows(server_code)
        print(f"[SNIPER] {self.words[choice_id]} link found\nyay joins (modified for bazthedev/SolsRNGBot v{LOCALVERSION})")
        aura_detection.cancel()
        merchant_detection.cancel()
        biome_randomizer.cancel()
        strange_controller.cancel()
        keep_alive.cancel()
        if settings["pop_in_glitch"] and self.words[choice_id] == "Glitched":
            await auto_pop("glitched")


    async def _join_windows(self, server_code: str):
        final_link = f"roblox://placeID={PLACE_ID}^&linkCode={server_code}"
        subprocess.Popen(["start", final_link], shell=True)

    async def _send_notification(self, choice_id: int, server_code: str):
        sniper_channel = client.get_channel(settings["sniper_channel_id"])
        if not sniper_channel:
            return

        colors = [11206400, 16744703]

        embed_link = f"{BASE_ROBLOX_URL}?privateServerLinkCode={server_code}"
        embed = discord.Embed(
            title = f'[{datetime.now().strftime("%H:%M:%S")}] {self.words[choice_id]} Link Sniped!',
            colour = colors[choice_id],
        )
        embed.add_field(name =  f"{self.words[choice_id]} Link:", value = embed_link, inline=True)
        embed.set_footer(text=f"yay joins (modified for bazthedev/SolsRNGBot v{LOCALVERSION})")

        await sniper_channel.send(f"<@{self.config['mention_id']}>", embed=embed)

    async def process_message(self, content: str, choice_id: int) -> None:
        try:
            if not self._should_process_message(content, choice_id):
                return

            server_code = await self._extract_server_code(content)
            if not server_code:
                return

            print(f"[SNIPER] Found message! content: {content}")

            await self._handle_server_join(choice_id, server_code)
            await self._send_notification(choice_id, server_code)

        except Exception as e:
            if self.config["sniper_logs"]:
                print(f"[SNIPER] Error processing message: {str(e)}")

    async def run(self):
        global ps_link_code
        await self.setup()

        glitch = self.config["sniper_toggles"]["Glitched"]
        dream = self.config["sniper_toggles"]["Dreamspace"]
        snipe_list = [glitch, dream]

        self.cycle_index = [i for i, x in enumerate(snipe_list) if x]

        if not (glitch or dream):
            print("[SNIPER] At least one option has to be True. Sniper has not been started.")
            return
            
        if not detect_client_disconnect(rblx_log_dir):
            print("Started yay joins (sniper)")
            ps_link_code = await self._extract_server_code(settings["private_server_link"])
            sniper_channel = client.get_channel(settings["sniper_channel_id"])
            emb = discord.Embed(
                title="Started Sniper!",
                description = f"Snipe Glitched: {str(glitch)}\nSnipe Dreamspace: {str(dream)}"
            )
            emb.set_footer(text=f"yay joins (modified for bazthedev/SolsRNGBot v{LOCALVERSION})")
            await sniper_channel.send(embed=emb)
        else:
            print("Attempting to reconnect sniper.")
        while True:
            try:
                async with connect(DISCORD_WS_BASE, max_size=None, ping_interval=None) as ws:
                    await self._identify(ws)
                    await self._subscribe(ws)
                                        
                    event = json.loads(await ws.recv())
                    interval = event["d"]["heartbeat_interval"] / 1000
                    async with asyncio.TaskGroup() as tg:
                        tg.create_task(self.heartbeat(ws, interval))
                        tg.create_task(self._on_message(ws))
            except Exception as e:
                if self.config["sniper_logs"]:
                    print(f"[SNIPER] Error: {e}")


sniper = Sniper()

# THE ABOVE CODE IS A SLIGHTLY MODIFIED VERSION OF YAY JOINS SNIPER 1.2.10, WHICH IS OWNED BY Root1527. YOU CAN DOWNLOAD THE REGULAR VERSION OF YAY JOINS HERE: https://github.com/Root1527/yay-joins


if not os.path.isfile(f"{MACROPATH}/icon.ico"):
    dl = requests.get("https://raw.githubusercontent.com/bazthedev/SolsRNGBot/main/icon.ico")
    f = open(f"{MACROPATH}/icon.ico", "wb")
    f.write(dl.content)
    f.close()

def get_auras():
    print("Downloading Aura List")
    dl = requests.get("https://raw.githubusercontent.com/bazthedev/SolsRNGBot/main/auras_new.json")
    f = open(f"{MACROPATH}/auras_new.json", "wb")
    f.write(dl.content)
    f.close()
    print("Downloaded Aura List")

def update_settings(settings):
    with open(f"{MACROPATH}/settings.json", "w") as f:
        json.dump(settings, f, indent=4)

def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def hex2rgb(_hex):
    _hex = _hex.lstrip("#")
    return tuple(int(_hex[i:i+2], 16) for i in (0, 2, 4))

def reload_settings():
    global settings
    with open(f"{MACROPATH}/settings.json", "r") as f:
        settings = json.load(f)

def validate_settings():
    found_keys = []
    todel = []
    for k in settings.keys():
        if k not in VALIDSETTINGSKEYS:
            todel.append(k)
            print(f"Invalid setting ({k}) detected")
        else:
            found_keys.append(k)
    for _ in todel:
        del settings[_]
        print(f"Invalid setting ({_}) deleted")
    for _ in VALIDSETTINGSKEYS:
        if _ not in found_keys:
            settings[_] = DEFAULTSETTINGS[_]
            print(f"Missing setting ({_}) added")
    update_settings(settings)
    reload_settings()

def validate_potions():
    found_keys = []
    todel = []
    for k in settings["auto_craft_item"].keys():
        if k not in ACCEPTEDPOTIONS:
            todel.append(k)
            print(f"Invalid potion ({k}) detected")
        else:
            found_keys.append(k)
    for _ in todel:
        del settings["auto_craft_item"][_]
        print(f"Invalid potion ({_}) deleted")
    for _ in ACCEPTEDPOTIONS:
        if _ not in found_keys:
            settings["auto_craft_item"][_] = False
            print(f"Missing potion ({_}) added")
    update_settings(settings)
    reload_settings()

def validate_pslink(ps_server_link : str):
    if "https://www.roblox.com/share?code=" not in ps_server_link:
        return False
    if "&type=Server" not in ps_server_link:
        return False
    return True

def format_roblosecurity():
    if "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_" in settings["ROBLOSECURITY_KEY"]:
        new_roblosec = settings["ROBLOSECURITY_KEY"].replace("_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_", "")
        settings["ROBLOSECURITY_KEY"] = new_roblosec
        update_settings(settings)
        reload_settings()


def migrate_settings():
    if os.path.exists("./settings.json") and not os.path.exists(f"{MACROPATH}/settings.json"):
        with open("./settings.json", "r") as f:
            _ = json.load(f)
        with open(f"{MACROPATH}/settings.json", "w+") as f:
            json.dump(_, f, indent=4)
    reload_settings()
    if not os.path.exists(f"{MACROPATH}"):
        print(f"Moving to new directory: {MACROPATH}")

async def use_item(item_name : str, amount : int, close_menu : bool):
    mkey.left_click_xy_natural(inv_button_pos[0], inv_button_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(items_pos[0], items_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(search_pos[0], search_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    _keyboard.type(item_name)
    await asyncio.sleep(settings["global_wait_time"]) 
    mkey.left_click_xy_natural(query_pos[0], query_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(item_amt_pos[0], item_amt_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    _keyboard.press(Key.ctrl)
    _keyboard.press("a")
    await asyncio.sleep(settings["global_wait_time"])
    _keyboard.release("a")
    _keyboard.release(Key.ctrl)
    await asyncio.sleep(settings["global_wait_time"])
    _keyboard.type(str(amount))
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(use_pos[0], use_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    if close_menu:
        mkey.left_click_xy_natural(close_pos[0], close_pos[1])
        await asyncio.sleep(settings["global_wait_time"])

async def leave_main_menu():
    if get_latest_equipped_aura(rblx_log_dir) == "In Main Menu":
        mkey.left_click_xy_natural(start_btn_pos[0], start_btn_pos[1])
        await asyncio.sleep(2)
        await leave_main_menu()

def get_latest_hovertext(logs_dir):
    log_files = glob.glob(os.path.join(logs_dir, "*.log"))
    if not log_files:
        return None

    latest_log_file = max(log_files, key=os.path.getctime)
    try:
        temp_file = os.path.join(tempfile.gettempdir(), "solsrngbot_biome_detection.log")
        shutil.copy2(latest_log_file, temp_file)
    except PermissionError:
        return None

    json_pattern = re.compile(r'\{.*\}')
    last_hover_text = None

    try:
        with open(temp_file, "r", encoding="utf-8") as file:
            for line in reversed(file.readlines()):
                match = json_pattern.search(line)
                if match:
                    try:
                        json_data = json.loads(match.group())
                        hover_text = json_data.get("data", {}).get("largeImage", {}).get("hoverText")
                        if hover_text:
                            return hover_text
                    except json.JSONDecodeError:
                        continue
    except Exception:
        return None
    
    return last_hover_text

def get_latest_equipped_aura(logs_dir):
    log_files = glob.glob(os.path.join(logs_dir, "*.log"))
    if not log_files:
        return None

    latest_log_file = max(log_files, key=os.path.getctime)
    try:
        temp_file = os.path.join(tempfile.gettempdir(), "solsrngbot_aura_detection.log")
        shutil.copy2(latest_log_file, temp_file)
    except PermissionError:
        return None

    json_pattern = re.compile(r'\{.*\}')
    
    try:
        with open(temp_file, "r", encoding="utf-8") as file:
            for line in reversed(file.readlines()):
                match = json_pattern.search(line)
                if match:
                    try:
                        json_data = json.loads(match.group())
                        if json_data.get("data", {}).get("state", "") == "In Main Menu":
                            return "In Main Menu"
                        aura = json_data.get("data", {}).get("state", "").replace("Equipped \"", "").replace("\"", "")
                        if aura:
                            aura = aura.replace("_", ": ")
                            return aura
                    except json.JSONDecodeError:
                        continue
    except Exception:
        return None
    
    return None

def detect_client_disconnect(logs_dir, lines_to_check=10):
    log_files = glob.glob(os.path.join(logs_dir, "*.log"))
    if not log_files:
        return False

    latest_log_file = max(log_files, key=os.path.getctime)
    try:
        temp_file = os.path.join(tempfile.gettempdir(), "solsrngbot_biome_detection.log")
        shutil.copy2(latest_log_file, temp_file)
    except PermissionError:
        return False

    disconnect_patterns = [
        r"Lost connection with reason : Lost connection to the game server, please reconnect",
    ]
    
    try:
        with open(temp_file, "r", encoding="utf-8") as file:
            last_lines = file.readlines()[-lines_to_check:]
            for line in reversed(last_lines):
                if any(re.search(pattern, line) for pattern in disconnect_patterns):
                    timestamp_match = re.search(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", line)
                    if timestamp_match:
                        timestamp = timestamp_match.group()
                        print(f"Disconnection detected at {timestamp}")
                    return True
    except Exception:
        return False
    
    return False

def detect_client_reconnect(logs_dir, lines_to_check=20):
    log_files = glob.glob(os.path.join(logs_dir, "*.log"))
    if not log_files:
        return False

    latest_log_file = max(log_files, key=os.path.getctime)
    try:
        temp_file = os.path.join(tempfile.gettempdir(), "solsrngbot_biome_detection.log")
        shutil.copy2(latest_log_file, temp_file)
    except PermissionError:
        return False

    disconnect_patterns = [
        r"NetworkClient:Create",
        r"Info: Stack End",
        r"Connection accepted from"
    ]
    
    try:
        with open(temp_file, "r", encoding="utf-8") as file:
            last_lines = file.readlines()[-lines_to_check:]
            for line in reversed(last_lines):
                if any(re.search(pattern, line) for pattern in disconnect_patterns):
                    timestamp_match = re.search(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", line)
                    if timestamp_match:
                        timestamp = timestamp_match.group()
                        print(f"Reconnection detected at {timestamp}")
                    return True
    except Exception:
        return False
    
    return False

def exists_procs_by_name(name):
    for p in psutil.process_iter(['name']):
        if p.info['name'].lower() == name.lower():
            return True
    return False

def get_process_by_name(name):
    for p in psutil.process_iter(['name']):
        if p.info['name'].lower() == name.lower():
            return p
    return False

def match_rblx_hwnd_to_pid(pid):
    for w in mkey.get_all_windows():
        if w.pid == pid:
            return w
    return False

async def auto_pop(biome : str):
    global ps_link_code, detected_snipe, rblx_log_dir
    _ended = False
    if detected_snipe and rblx_log_dir == ms_rblx_log_dir:
        rblx_log_dir = ms_rblx_log_dir
        while not exists_procs_by_name("Windows10Universal.exe"):
            pass # Wait for roblox to start
        ps_rblxms = get_process_by_name("Windows10Universal.exe")
        rblxms_window = match_rblx_hwnd_to_pid(ps_rblxms.pid)
        mkey.activate_window(rblxms_window.hwnd)
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(ms_rblx_spawn_pos[0], ms_rblx_spawn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(ms_rblx_spawn_pos[0], ms_rblx_spawn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        _keyboard.press(Key.f11)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.f11)
        await leave_main_menu()
    if biome.lower() != get_latest_hovertext(rblx_log_dir).lower():
        _ended = True
    if settings["change_cutscene_on_pop"]:
        mkey.left_click_xy_natural(menu_btn_pos[0], menu_btn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(settings_btn_pos[0], settings_btn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(rolling_conf_pos[0], rolling_conf_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(cutscene_conf_pos[0], cutscene_conf_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        _keyboard.press(Key.ctrl)
        _keyboard.press("a")
        await asyncio.sleep(settings["global_wait_time"])
        _keyboard.release("a")
        _keyboard.release(Key.ctrl)
        await asyncio.sleep(settings["global_wait_time"])
        _keyboard.type("9999999999")
        await asyncio.sleep(settings["global_wait_time"])
        _keyboard.press(Key.enter)
        await asyncio.sleep(settings["global_wait_time"])
        _keyboard.release(Key.enter)
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(menu_btn_pos[0], menu_btn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(menu_btn_pos[0], menu_btn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
    if biome.lower() == "glitched" and settings["pop_in_glitch"]:
        original_hp2_amt = settings["auto_use_items_in_glitch"]["Heavenly Potion II"]["amount"]
        for item in reversed(settings["auto_use_items_in_glitch"].keys()):
            if biome.lower() != get_latest_hovertext(rblx_log_dir).lower():
                _ended = True
            if _ended:
                break
            if not settings["auto_use_items_in_glitch"][item]["use"]:
                continue
            if item == "Heavenly Potion II" or item == "Oblivion Potion":
                while True:
                    if get_latest_hovertext(rblx_log_dir).lower() != biome:
                        print("Biome has ended")
                        _ended = True
                        break
                    else:
                        if original_hp2_amt > 10:
                            await use_item(item, 10, True)
                            original_hp2_amt -= 10
                        elif original_hp2_amt > 1:
                            await use_item(item, 1, True)
                            original_hp2_amt -= 1
                        else:
                            break
                    await asyncio.sleep(2)
            else:
                await use_item(item, settings["auto_use_items_in_glitch"][item]["amount"], True)

    if not aura_detection.is_running():
        aura_detection.start()    
    if valid_ps:
        print("Attempting to rejoin private server")
        await asyncio.sleep(5)
        await sniper._join_windows(ps_link_code)
        await asyncio.sleep(10)
        ps_rblxms = get_process_by_name("Windows10Universal.exe")
        rblxms_window = match_rblx_hwnd_to_pid(ps_rblxms.pid)
        mkey.activate_window(rblxms_window.hwnd)
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(ms_rblx_spawn_pos[0], ms_rblx_spawn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(ms_rblx_spawn_pos[0], ms_rblx_spawn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        _keyboard.press(Key.f11)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.f11)
        await leave_main_menu()
        print("Success!")
    else:
        sys.exit("No server to rejoin in settings")
    if not keep_alive.is_running():
        keep_alive.start()
    if not merchant_detection.is_running() and settings["merchant_detection"]:
        merchant_detection.start()
    if not biome_randomizer.is_running() and settings["auto_biome_randomizer"]:
        biome_randomizer.start()
    if not strange_controller.is_running() and settings["auto_strange_controller"]:
        strange_controller.start()

migrate_settings()

if not os.path.exists(f"{MACROPATH}/scr/"):
    os.mkdir(f"{MACROPATH}/scr/")

if not os.path.exists(f"{MACROPATH}/plugins/"):
    os.mkdir(f"{MACROPATH}/plugins/")
    os.mkdir(f"{MACROPATH}/plugins/config/")

if not os.path.exists(f"{MACROPATH}/logs/"):
    os.mkdir(f"{MACROPATH}/logs/")

now = datetime.now()
client = commands.Bot(commands.when_mentioned, case_insensitive=True, intents=None)
_mouse = mouse.Controller()
_keyboard = keyboard.Controller()
screens = si.get_monitors()
monitor = None
for mon in screens:
    if mon.is_primary:
        monitor = mon
scale_w = monitor.width / 2560
scale_h = monitor.height / 1440
aura_button_pos = ((53 * scale_w), (538 * scale_h))
inv_button_pos = ((67 * scale_w), (732 * scale_h))
default_pos = ((1280 * scale_w), (720 * scale_h))
close_pos = ((1887 * scale_w), (399 * scale_h))
search_pos = ((1164 * scale_w), (486 * scale_h))
secondary_pos = ((564 * scale_w), (401 * scale_h))
query_pos = ((1086 * scale_w), (572 * scale_h))
equip_pos = ((812 * scale_w), (844 * scale_h))
use_pos = ((910 * scale_w), (772 * scale_h))
item_amt_pos = ((756 * scale_w), (772 * scale_h))
items_pos = ((1692 * scale_w), (440 * scale_h)) 
purchase_btn_pos = ((990 * scale_w), (860 * scale_h))
quantity_btn_pos = ((910 * scale_w), (796 * scale_h))
open_merch_pos = ((876 * scale_w), (1256 * scale_h))
merch_item_pos_1 = (int(656 * scale_w), int(922 * scale_h))
merch_item_pos_1_end = (int(890 * scale_w), int(994 * scale_h))
merch_item_pos_1_purchase = ((766 * scale_w), (988 * scale_h))
merch_item_pos_2 = (int(908 * scale_w), int(922 * scale_h))
merch_item_pos_2_end = (int(1142 * scale_w), int(994 * scale_h))
merch_item_pos_2_purchase = ((1024 * scale_w), (986 * scale_h))
merch_item_pos_3 = (int(1160 * scale_w), int(922 * scale_h))
merch_item_pos_3_end = (int(1396 * scale_w), int(994 * scale_h))
merch_item_pos_3_purchase = ((1278 * scale_w), (988 * scale_h))
merch_item_pos_4 = (int(1416 * scale_w), int(922 * scale_h))
merch_item_pos_4_end = (int(1650 * scale_w), int(994 * scale_h))
merch_item_pos_4_purchase = ((1512 * scale_w), (988 * scale_h))
merch_item_pos_5 = (int(1666 * scale_w), int(922 * scale_h))
merch_item_pos_5_end = (int(1898 * scale_w), int(994 * scale_h))
merch_item_pos_5_purchase = ((1762 * scale_w), (986 * scale_h))
menu_btn_pos = ((42 * scale_w), (898 * scale_h))
settings_btn_pos = ((1278 * scale_w), (738 * scale_h))
rolling_conf_pos = ((888 * scale_w), (498 * scale_h))
cutscene_conf_pos = ((1518 * scale_w), (812 * scale_h))
craft_btn_pos = ((764 * scale_w), (764 * scale_h))
hp1_pos_potions = ((1064 * scale_w), (840 * scale_h)) # first add button (-110 * scale_w gives the item input)
hp1_pos_celestial = ((1064 * scale_w), (1024 * scale_h)) # very botton button
hp2_pos_potions = ((1064 * scale_w), (910 * scale_h)) # second add button
auto_btn_pos = ((940 * scale_w), (762 * scale_h))
auto_mode_swap = 5
auto_craft_index = 1
hp1_recipe_pos = ((1516 * scale_w), (684 * scale_h))
hp2_recipe_pos = ((1516 * scale_w), (836 * scale_h))
warp_recipe_pos = ((1516 * scale_w), (980 * scale_h))
merchant_face_pos_1 = (int(841 * scale_w), int(1056 * scale_h))
merchant_face_pos_2 = (int(855 * scale_w), int(1063 * scale_h))
collection_open_pos = ((54 * scale_w), (624 * scale_h))
exit_collection_pos = ((510 * scale_w), (146 * scale_h))
start_btn_pos = ((1252 * scale_w), (1206 * scale_h))
reconnect_btn_pos = ((1370 * scale_w), (800 * scale_h))
bound_recipe_pos = ((1524 * scale_w), (994 * scale_h))
mari_cols = ["#767474", "#767476", "#757474", "#7c7c7c", "#7c7a7c", "#7a7878", "#787678", "#787878"]
jester_cols = ["#e2e2e2", "#e1e1e1", "#e0e0e0"]
biome_cols = {"windy" : (145, 247, 255), "snowy" : (196, 245, 246), "rainy" : (67, 133, 255), "hell" : (74, 23, 34), "starfall" : (103, 132, 224), "corruption" : (144, 66, 255), "null" : (7, 9, 16), "dreamspace" : (234, 108, 188), "glitched" : (100, 252, 100)}
previous_biome = None
previous_aura = None
popping = False
valid_ps = False
item_collection_index = 1
use_ms_rblx = False
rblx_player_log_dir = os.path.expandvars(r"%localappdata%\Roblox\logs") # This is for the Roblox Player
ms_rblx_log_dir = os.path.expandvars(r"%LOCALAPPDATA%\Packages\ROBLOXCorporation.ROBLOX_55nm5eh3cm0pr\LocalState\logs") # This is for the Microsoft Store version of Roblox
ms_rblx_spawn_pos = ((820 * scale_w), (548 * scale_h))
ps_link_code = 0
WINDY_MULTIPLIER = 3
SNOWY_MULTIPLIER = 3
RAINY_MULTIPLER = 4
SANDSTORM_MULTIPLIER = 4
HELL_MULTIPLIER = 6
STARFALL_MULTIPLIER = 5
CORRUPTION_MULTIPLIER = 5
NULL_MULTIPLIER = 1000
GLITCHED_MULTIPLIER = 1
DREAMSPACE_MULTIPLIER = 1
_plugins = []
auto_purchase = {"Void Coin/Lucky Penny": ["#ff92fe", "#ff9e4e"], "Oblivion Potion" : []}
print(f"Starting SolsRNGBot v{LOCALVERSION}")

class SettingsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Baz's Macro")

        try:
            self.root.iconbitmap(f"{MACROPATH}/icon.ico")
        except Exception:
            pass

        self.original_settings = self.load_settings()
        self.entries = {}
        self.listbox_refs = {}
        self.create_ui()
    
    def load_settings(self):
        try:
            with open(f"{MACROPATH}/settings.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def format_key(self, key):
        if " " in key:
            return key
        return key.replace("_", " ").title()


    def create_ui(self):
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.create_widgets(self.original_settings, self.scrollable_frame)

        save_button = ttk.Button(self.root, text="Start Macro", command=self.save_settings)
        save_button.pack(pady=10)

    def create_list_widget(self, parent, key, items):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, expand=True)

        listbox = tk.Listbox(frame, height=5, selectmode=tk.SINGLE)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for item in items:
            listbox.insert(tk.END, item)

        self.entries[key] = items
        self.listbox_refs[key] = listbox

        button_frame = ttk.Frame(frame)
        button_frame.pack(side=tk.RIGHT, padx=5)

        add_entry = ttk.Entry(button_frame, width=15)
        add_entry.pack(pady=2)

        add_button = ttk.Button(button_frame, text="Add", command=lambda: self.add_to_list(key, add_entry))
        add_button.pack(pady=2)

        remove_button = ttk.Button(button_frame, text="Remove", command=lambda: self.remove_from_list(key))
        remove_button.pack(pady=2)

    def add_to_list(self, key, entry):
        new_item = entry.get().strip()
        if new_item:
            listbox = self.listbox_refs[key]
            if new_item not in self.entries[key]:
                self.entries[key].append(new_item)
                listbox.insert(tk.END, new_item)
                entry.delete(0, tk.END)

    def remove_from_list(self, key):
        listbox = self.listbox_refs[key]
        selection = listbox.curselection()

        if selection:
            index = selection[0]
            listbox.delete(index)
            self.entries[key].pop(index)

    def create_widgets(self, settings, parent, entry_dict=None):
        if entry_dict is None:
            entry_dict = self.entries

        for key, value in settings.items():
            if key == "edit_settings_mode":
                continue
            formatted_key = self.format_key(key)

            row = ttk.Frame(parent)
            row.pack(fill=tk.X, pady=2)

            label = ttk.Label(row, text=formatted_key + ":", width=25, anchor="w")
            label.pack(side=tk.LEFT)

            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                checkbox = ttk.Checkbutton(row, variable=var)
                checkbox.pack(side=tk.LEFT)
                entry_dict[key] = var
            elif isinstance(value, dict):
                subframe = ttk.LabelFrame(parent, text=formatted_key, padding=5)
                subframe.pack(fill=tk.X, padx=10, pady=5)
                entry_dict[key] = {}
                self.create_widgets(value, subframe, entry_dict[key])
            elif isinstance(value, list):
                self.create_list_widget(row, key, value)
            else:
                var = tk.StringVar(value=str(value))
                entry = ttk.Entry(row, textvariable=var, width=30)
                entry.pack(side=tk.LEFT)
                entry_dict[key] = var

    def get_updated_values(self, original, entries):
        updated_settings = {}

        for key, widget in entries.items():
            if isinstance(widget, dict):
                sub_updates = self.get_updated_values(original.get(key, {}), widget)
                if sub_updates:
                    updated_settings[key] = sub_updates
            else:
                new_value = widget.get()
                if isinstance(original.get(key), bool):
                    new_value = bool(new_value)
                elif isinstance(original.get(key), (int, float)):
                    try:
                        new_value = int(new_value)
                    except ValueError:
                        try:
                            new_value = float(new_value)
                        except ValueError:
                            pass

                if new_value != original.get(key):
                    updated_settings[key] = new_value

        return updated_settings

    def save_settings(self):
        updated_values = self.get_updated_values(self.original_settings, self.entries)

        if not updated_values:
            self.root.destroy()
            return

        try:
            with open(f"{MACROPATH}/settings.json", "r") as f:
                current_settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            current_settings = {}

        def merge_dicts(original, updates):
            for key, value in updates.items():
                if isinstance(value, dict) and isinstance(original.get(key), dict):
                    merge_dicts(original[key], value)
                else:
                    original[key] = value

        merge_dicts(current_settings, updated_values)

        try:
            with open(f"{MACROPATH}/settings.json", "w") as f:
                json.dump(current_settings, f, indent=4)
            messagebox.showinfo("Baz's Macro Settings Editor", "Settings saved successfully!")
            reload_settings()
            print("Settings were reloaded.")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Baz's Macro Settings Editor", f"Failed to save settings:\n{e}")

if not os.path.exists(f"{MACROPATH}/settings.json"):
    x = open(f"{MACROPATH}/settings.json", "w")
    x.write('{}')
    x.close()
    with open(f"{MACROPATH}/settings.json", "w") as f:
        json.dump(DEFAULTSETTINGS, f, indent=4)
    print("Settings have been created!")


reload_settings()


if settings["__version__"] < LOCALVERSION:
    settings["__version__"] = LOCALVERSION
    settings["edit_settings_mode"] = True
    update_settings(settings)
    reload_settings()
    print(f"The macro has been updated to version {LOCALVERSION}!")

if settings["__version__"] > LOCALVERSION:
    print("You are running newer settings with an older version of this program. This may delete some of your settings. Are you sure you want to continue (y)? ")
    confirm = input("")
    if confirm[0].lower() != "y":
        sys.exit("You are running newer settings with an older version of this program.")
        
# Settings integrity check
validate_settings()

if settings["check_update"]:
    new_ver = requests.get(f"https://api.github.com/repos/bazthedev/SolsRNGBot/releases/latest")
    new_ver_str = new_ver.json()["name"]

    if LOCALVERSION < new_ver_str:
        DOWNLOADS_DIR = Path.home() / "Downloads"
        if not settings["auto_install_update"]:
            confirm_dl = input(f"A new version has been found ({new_ver_str}), would you like to install it (y/n)? ")
        else:
            confirm_dl = "y"
            print("Automatically installing new version...")
        if confirm_dl[0].lower() == "y":
            print(f"Downloading v{new_ver_str}...")
            if not os.path.isfile(f"{DOWNLOADS_DIR}/SolsRNGBot_{new_ver_str}.zip"):
                toupd = requests.get(f"https://github.com/bazthedev/SolsRNGBot/releases/download/{new_ver_str}/SolsRNGBot_{new_ver_str}.zip")
                with open(f"{DOWNLOADS_DIR}/SolsRNGBot_{new_ver_str}.zip", "wb") as p:
                    p.write(toupd.content)
                    p.close()
                print(f"Downloaded v{new_ver_str}")
            else:
                print("New version zip appears to already be downloaded.")
            with zipfile.ZipFile(f"{DOWNLOADS_DIR}/SolsRNGBot_{new_ver_str}.zip", "r") as newverzip:
                if not os.path.exists(f"{DOWNLOADS_DIR}/SolsRNGBot_{new_ver_str}"):
                    os.mkdir(f"{DOWNLOADS_DIR}/SolsRNGBot_{new_ver_str}")
                newverzip.extractall(f"{DOWNLOADS_DIR}/SolsRNGBot_{new_ver_str}/")
                print(f"Extracted v{new_ver_str} to directory {DOWNLOADS_DIR}\\SolsRNGBot_{new_ver_str}")
                print("Cleaning up...")
                os.remove(f"{DOWNLOADS_DIR}/SolsRNGBot_{new_ver_str}.zip")
            sys.exit(f"Downloaded v{new_ver_str}")
    else:
        print(f"You are running the latest version.")

if not os.path.exists(ms_rblx_log_dir):
    print("The Microsoft Store Version of Roblox has not been detected as installed. This will break certain features of the macro, such as the Sniper and joining servers.")

if exists_procs_by_name("Windows10Universal.exe"):
    rblx_log_dir = ms_rblx_log_dir
    print("Using Microsoft Store Roblox (detected as running)")
elif exists_procs_by_name("RobloxPlayerBeta.exe"):
    rblx_log_dir = rblx_player_log_dir
    print("Using Roblox Player (detected as running)")
elif settings["use_rblx_player"]:
    print("Using Roblox player (no Roblox instances were detected as running)")
    rblx_log_dir = rblx_player_log_dir
else:
    print("Using Microsoft Store Roblox (no Roblox instances were detected as running)")
    rblx_log_dir = ms_rblx_log_dir

mkey.enable_failsafekill(settings["failsafe_key"])

if settings["TOKEN"] == "":
    print("You need to add your bot token.")

validate_potions()
root = tk.Tk()
app = SettingsApp(root)
root.mainloop()
print("Validating settings, then starting macro...")
validate_settings()


if settings["sniper_enabled"] and (settings["ROBLOSECURITY_KEY"] == "" or settings["DISCORD_TOKEN"] == "" or settings["sniper_channel_id"] == 0):
    print("You must provide both your ROBLOSECURITY cookie and your Discord Token for the sniper to work. You also need to set a sniper logs channel")
    settings["edit_settings_mode"] = True
    update_settings(settings)
    reload_settings()
    sys.exit()

if settings["ROBLOSECURITY_KEY"] != "":
    format_roblosecurity()

if not settings["skip_aura_download"]:
    get_auras()

if not os.path.exists(f"{MACROPATH}/auras.json") or not os.path.exists(f"{MACROPATH}/auras_new.json"):
    get_auras()

with open(f"{MACROPATH}/auras_new.json", "r", encoding="utf-8") as f:
        auras = json.load(f)

if settings["private_server_link"] != "":
    if not validate_pslink(settings["private_server_link"]):
        print("Invalid Private Server Link")
        valid_ps = False
    else:
        valid_ps = True

__version__ = settings["__version__"]

@client.event
async def on_ready():
    print(random.choice(STARTUP_MSGS))
    print(f"Started at {now.strftime('%d/%m/%Y %H:%M:%S')} running v{__version__} using local version {LOCALVERSION}")
    await client.change_presence(activity=discord.Game(name=f"bazthedev/SolsRNGBot v{LOCALVERSION}"))
    await asyncio.sleep(settings["global_wait_time"])
    if not (exists_procs_by_name("Windows10Universal.exe") or exists_procs_by_name("RobloxPlayerBeta.exe")):
        print("Roblox is not running, waiting for it to start...")
    while not (exists_procs_by_name("Windows10Universal.exe") or exists_procs_by_name("RobloxPlayerBeta.exe")):
        pass
    if rblx_log_dir == ms_rblx_log_dir:
        ps_rblxms = get_process_by_name("Windows10Universal.exe")
    else:
        ps_rblxms = get_process_by_name("RobloxPlayerBeta.exe")
    try:
        rblx_window = match_rblx_hwnd_to_pid(ps_rblxms.pid)
        mkey.activate_window(rblx_window.hwnd)
    except Exception:
        pass
    await asyncio.sleep(settings["global_wait_time"])
    await leave_main_menu()
    await asyncio.sleep(settings["global_wait_time"])
    if settings["log_channel_id"] != 0:
        log_channel = client.get_channel(settings["log_channel_id"])
        emb = discord.Embed(
            title="Bot has started",
            description=f"Mode: Normal\nStarted at {now.strftime('%d/%m/%Y %H:%M:%S')}"
        )
        emb.set_footer(text=f"bazthedev/SolsRNGBot v{LOCALVERSION}")
        if not settings["auto_craft_mode"]:
            await log_channel.send(embed=emb)
        aura_detection.start()
        print("Started Aura Detection")
        for _ in settings["biomes"].keys():
            if settings["biomes"][_]:
                biome_detection.start()
                print("Started Biome Detection")
                break
    else:
        print("You must select a channel ID, you can do this by running the set_log_channel command.")
    if settings["auto_craft_mode"] and not settings["merchant_detection"]:
        crafts = ""
        for item in settings["auto_craft_item"].keys():
            if settings["auto_craft_item"][item]:
                crafts += f"{item}\n"
        if settings["log_channel_id"] != 0:
            log_channel = client.get_channel(settings["log_channel_id"])
            emb = discord.Embed(
                title="Bot has started",
                description=f"Mode: Auto Craft\nAuto Craft item(s):\n{crafts}\nStarted at {now.strftime('%d/%m/%Y %H:%M:%S')}"
            )
            emb.set_footer(text=f"bazthedev/SolsRNGBot v{LOCALVERSION}")
            await log_channel.send(embed=emb)
        print("[WARNING] Auto Craft Mode is on. You will not be able to use certain features whilst this settings is on.")
        print(f"The item(s) you are automatically crafting are:\n{crafts}")
        print("Please ensure that you are standing next to the cauldron so that you can see the \"f\" prompt.")
        if settings["reset_aura"] != "":
            settings["reset_aura"] = ""
            update_settings(settings)
            reload_settings()
        print("Starting auto craft mode. Please click back onto Roblox and wait 5 seconds")
        await asyncio.sleep(5)
        auto_craft.start()
    else:
        if settings["log_channel_id"] != 0:
            if not settings["disable_autokick_prevention"]:
                keep_alive.start()
                print("Started Autokick Prevention")
                await asyncio.sleep(((settings["global_wait_time"] * 7) + 0.7))
        if settings["sniper_enabled"] and settings["sniper_channel_id"] != "":
            yay_joins_sniper.start()
        if settings["disconnect_prevention"]:
            print("Start Disconnect Prevention")
            disconnect_prevention.start()
        if settings["periodic_screenshots"]["inventory"]:
            inventory_screenshot.start()
            print("Start Periodic Inventory Screenshots")
        if settings["periodic_screenshots"]["storage"]:
            storage_screeenshot.start()
            print("Start Periodic Storage Screenshots")
    if settings["auto_biome_randomizer"]:
        biome_randomizer.start()
        print("Started Biome Randomizer")
    if settings["auto_strange_controller"]:
        await asyncio.sleep((settings["global_wait_time"] * 60))
        strange_controller.start()
        print("Started Strange Controller")
    if settings["merchant_detection"] and settings["log_channel_id"] != 0:
        if settings["auto_biome_randomizer"] or settings["auto_strange_controller"]:
            await asyncio.sleep((settings["global_wait_time"] * 60))
        merchant_detection.start()
        print("Started Merchant Detection")
    if settings["clear_logs"]:
        print("Clearing logs")
        for file in os.listdir(f"{MACROPATH}/logs/"):
            try:
                os.remove(f"{MACROPATH}/logs/{file}")
                print("Delete file: " + file)
            except PermissionError:
                pass
    print(f"Started SolsRNGBot v{LOCALVERSION}")
    

@tasks.loop(count=None)
async def yay_joins_sniper():
    await sniper.run()

@client.event
async def on_command_error(ctx, error):
    print(str(error))

@tasks.loop(seconds=2100)
async def biome_randomizer():
    await use_item("Biome Random", 1, True)

@tasks.loop(seconds=1200)
async def strange_controller():
    await use_item("Strange Control", 1, True)

@client.command()
async def get_biome(ctx):
    latest_hovertext = get_latest_hovertext(rblx_log_dir)
    await ctx.send(f"The current biome is: {latest_hovertext}")

@client.command()
async def get_aura(ctx):
    current_aura = get_latest_equipped_aura(rblx_log_dir)
    if current_aura == "In Main Menu":
        await ctx.send("Currently in the main menu.")
    elif current_aura == "_None_":
        await ctx.send("There is no equipped aura.")
    else:
        await ctx.send(f"The currently equipped aura is: {current_aura}")

@client.command()
@commands.is_owner()
async def set_log_channel(ctx):
    await ctx.send("Updating log channel...")
    new_log_channel_id = ctx.message.channel.id
    settings["log_channel_id"] = new_log_channel_id
    update_settings(settings)
    reload_settings()
    await ctx.send(f"Log Channel set to {ctx.message.channel.mention}")

@client.command()
@commands.is_owner()
async def set_sniper_channel(ctx):
    await ctx.send("Updating sniper logs channel...")
    new_sniper_channel_id = ctx.message.channel.id
    settings["sniper_channel_id"] = new_sniper_channel_id
    update_settings(settings)
    reload_settings()
    await ctx.send(f"Sniper Channel set to {ctx.message.channel.mention}! This will change will take place next time the macro is run.")

@client.command()
@commands.is_owner()
async def set_mention(ctx):
    await ctx.send("Updating user to mention...")
    settings["mention_id"] = ctx.author.id
    update_settings(settings)
    reload_settings()
    await ctx.send(f"User to mention is now {ctx.author.mention}")

@client.command()
@commands.is_owner()
async def set_min_roll(ctx, minimum : str):
    try:
        int(minimum)
    except TypeError:
        await ctx.send("The value provided is not a number")
        return
    await ctx.send("Changing minimum roll alert...")
    settings["minimum_roll"] = minimum
    update_settings(settings)
    reload_settings()
    await ctx.send(f"Minimum roll alert is now {minimum}")

@client.command()
@commands.is_owner()
async def set_min_ping(ctx, minimum : str):
    try:
        int(minimum)
    except TypeError:
        await ctx.send("The value provided is not a number")
        return
    await ctx.send("Changing minimum ping alert...")
    settings["minimum_ping"] = minimum
    update_settings(settings)
    reload_settings()
    await ctx.send(f"Minimum ping alert is now {minimum}")

@client.command()
async def mode(ctx):
    if settings["auto_craft_mode"] and not settings["merchant_detection"]:
        crafts = ""
        for item in settings["auto_craft_item"].keys():
            if settings["auto_craft_item"][item]:
                crafts += f"{item}\n"
        await ctx.send(f"The bot is currently running in Auto Craft mode, and the item(s) being crafted are:\n{crafts}")
    else:
        await ctx.send("The bot is running in Normal mode.")

@client.command()
@commands.is_owner()
async def stop(ctx):
    await ctx.send("Manual stop initiated")
    keep_alive.stop()
    await client.close()
    print("Aw dang it")

@client.command()
@commands.is_owner()
async def edit_settings(ctx):
    settings["edit_settings_mode"] = True
    update_settings(settings)
    reload_settings()
    await ctx.send("The next time you run the macro, the settings will be opened.")

@client.command()
@commands.is_owner()
async def storage_scr(ctx):
    await ctx.send("Taking screenshot of Aura Storage, please wait, this will take a few seconds.")
    mkey.left_click_xy_natural(aura_button_pos[0], aura_button_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(search_pos[0], search_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    storimg = pag.screenshot(f"{MACROPATH}/scr/screenshot_storage.png")
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(close_pos[0], close_pos[1])
    await ctx.send(file=discord.File(f"{MACROPATH}/scr/screenshot_storage.png"))

@client.command()
@commands.is_owner()
async def inv_scr(ctx):
    await ctx.send("Taking screenshot of inventory, please wait, this will take a few seconds.")
    mkey.left_click_xy_natural(inv_button_pos[0], inv_button_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(items_pos[0], items_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(search_pos[0], search_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    storimg = pag.screenshot(f"{MACROPATH}/scr/screenshot_inventory.png")
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(close_pos[0], close_pos[1])
    await ctx.send(file=discord.File(f"{MACROPATH}/scr/screenshot_inventory.png"))

@client.command()
@commands.is_owner()
async def get_settings(ctx):
    settings_str = """"""
    for _ in settings:
        if _ == "TOKEN" or _ == "auto_use_items_in_glitch" or _ == "auto_use_items_in_dreamspace" or _ == "ROBLOSECURITY_KEY" or _ == "DISCORD_TOKEN":
            continue
        settings_str += f"Setting: {_}; Value: {settings[_]}\n"
    await ctx.send(f"```\n{settings_str}\n```")

@client.command()
@commands.is_owner()
async def enable(ctx, setting):
    if setting not in VALIDSETTINGSKEYS:
        await ctx.send("That setting does not exist.")
        return
    if "bool" not in str(type(settings[setting])):
        await ctx.send("That setting cannot be toggled.")
        return
    if settings[setting] == True:
        await ctx.send("This setting is already on.")
        return
    settings[setting] = True
    update_settings(settings)
    reload_settings()
    await ctx.send(f"{setting} has been enabled.")

@client.command()
@commands.is_owner()
async def disable(ctx, setting):
    if setting not in VALIDSETTINGSKEYS:
        await ctx.send("That setting does not exist.")
        return
    if "bool" not in str(type(settings[setting])):
        await ctx.send("That setting cannot be toggled.")
        return
    if settings[setting] == False:
        await ctx.send("This setting is already off.")
        return
    settings[setting] = False
    update_settings(settings)
    reload_settings()
    await ctx.send(f"{setting} has been disabled.")

@client.command()
@commands.is_owner()
async def purchase_item(ctx, item : int, amount = 25):
    if not settings["merchant_detection"]:
        await ctx.send("Merchant Detection is disabled. Please enable it to use this feature.")
        return
    if settings["auto_craft_mode"]:
        await ctx.send("Auto Craft mode is enabled. Please disable it to use this feature.")
        return
    if item > 5 or item < 1:
        await ctx.send("A merchant only sells 5 items at a time")
        return
    try:
        int(amount)
    except Exception:
        await ctx.send("You need to provide a number for items to buy.")
        return
    if item == 1:
        mkey.left_click_xy_natural(merch_item_pos_1_purchase[0], merch_item_pos_1_purchase[1])
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(quantity_btn_pos[0], quantity_btn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        _keyboard.type(str(amount))
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(purchase_btn_pos[0], purchase_btn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        log_channel = client.get_channel(settings["log_channel_id"])
        if settings["ping_merchant"] and settings["mention_id"] != 0:
            await log_channel.send(f"<@{settings["mention_id"]}>\nPurchased item in box 1 from merchant")
        else:
            await log_channel.send(f"Purchased item in box 1 from merchant")
        await asyncio.sleep(2)
    elif item == 2:
        mkey.left_click_xy_natural(merch_item_pos_2_purchase[0], merch_item_pos_2_purchase[1])
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(quantity_btn_pos[0], quantity_btn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        _keyboard.type(str(amount))
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(purchase_btn_pos[0], purchase_btn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        log_channel = client.get_channel(settings["log_channel_id"])
        if settings["ping_merchant"] and settings["mention_id"] != 0:
            await log_channel.send(f"<@{settings["mention_id"]}>\nPurchased item in box 2 from merchant")
        else:
            await log_channel.send(f"Purchased item in box 2 from merchant")
        await asyncio.sleep(2)
    elif item == 3:
        mkey.left_click_xy_natural(merch_item_pos_3_purchase[0], merch_item_pos_3_purchase[1])
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(quantity_btn_pos[0], quantity_btn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        _keyboard.type(str(amount))
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(purchase_btn_pos[0], purchase_btn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        log_channel = client.get_channel(settings["log_channel_id"])
        if settings["ping_merchant"] and settings["mention_id"] != 0:
            await log_channel.send(f"<@{settings["mention_id"]}>\nPurchased item in box 3 from merchant")
        else:
            await log_channel.send(f"Purchased item in box 3 from merchant")
        await asyncio.sleep(2)
    elif item == 4:
        mkey.left_click_xy_natural(merch_item_pos_4_purchase[0], merch_item_pos_4_purchase[1])
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(quantity_btn_pos[0], quantity_btn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        _keyboard.type(str(amount))
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(purchase_btn_pos[0], purchase_btn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        log_channel = client.get_channel(settings["log_channel_id"])
        if settings["ping_merchant"] and settings["mention_id"] != 0:
            await log_channel.send(f"<@{settings["mention_id"]}>\nPurchased item in box 4 from merchant")
        else:
            await log_channel.send(f"Purchased item in box 4 from merchant")
        await asyncio.sleep(2)
    elif item == 5:
        mkey.left_click_xy_natural(merch_item_pos_5_purchase[0], merch_item_pos_5_purchase[1])
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(quantity_btn_pos[0], quantity_btn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        _keyboard.type(str(amount))
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(purchase_btn_pos[0], purchase_btn_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        log_channel = client.get_channel(settings["log_channel_id"])
        if settings["ping_merchant"] and settings["mention_id"] != 0:
            await log_channel.send(f"<@{settings["mention_id"]}>\nPurchased item in box 5 from merchant")
        else:
            await log_channel.send(f"Purchased item in box 5 from merchant")
        await asyncio.sleep(2)

@tasks.loop(seconds=577)
async def keep_alive():
    mkey.left_click_xy_natural(close_pos[0], close_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(close_pos[0], close_pos[1])
    await asyncio.sleep(settings["global_wait_time"])

@tasks.loop(seconds=720)
async def obby_blessing():
    await align_camera()
    await asyncio.sleep(settings["global_wait_time"])
    await do_obby_blessing()
    await asyncio.sleep(settings["global_wait_time"])

@tasks.loop(seconds=1200)
async def collect_items():
    pass

@tasks.loop(seconds=1260)
async def storage_screeenshot():
    mkey.left_click_xy_natural(aura_button_pos[0], aura_button_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(search_pos[0], search_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    storimg = pag.screenshot(f"{MACROPATH}/scr/screenshot_storage.png")
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(close_pos[0], close_pos[1])
    log_channel = client.get_channel(settings["log_channel_id"])
    await log_channel.send(file=discord.File(f"{MACROPATH}/scr/screenshot_storage.png"))

@tasks.loop(seconds=1140)
async def inventory_screenshot():
    mkey.left_click_xy_natural(inv_button_pos[0], inv_button_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(items_pos[0], items_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(search_pos[0], search_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    storimg = pag.screenshot(f"{MACROPATH}/scr/screenshot_inventory.png")
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(close_pos[0], close_pos[1])
    log_channel = client.get_channel(settings["log_channel_id"])
    await log_channel.send(file=discord.File(f"{MACROPATH}/scr/screenshot_inventory.png"))

@tasks.loop(seconds=0)
async def disconnect_prevention():
    global rblx_log_dir
    if not exists_procs_by_name("Windows10Universal.exe") and not exists_procs_by_name("RobloxPlayerBeta.exe"):
        print("There are no instances of Roblox running, the macro will now stop.")
        sys.exit()
    if detect_client_disconnect(rblx_log_dir):
        if valid_ps:
            if rblx_log_dir != ms_rblx_log_dir:
                rblx_log_dir = ms_rblx_log_dir
            _attempt = 1
            os.system("taskkill /f /im RobloxPlayerBeta.exe /t")
            while not detect_client_reconnect(rblx_log_dir):
                print(f"Attempting to rejoin private server (Attempt #{str(_attempt)})")
                os.system("taskkill /f /im Windows10Universal.exe /t")
                await asyncio.sleep(5)
                await sniper._join_windows(ps_link_code)
                await asyncio.sleep(5)                
                ps_rblxms = get_process_by_name("Windows10Universal.exe")
                rblxms_window = match_rblx_hwnd_to_pid(ps_rblxms.pid)
                mkey.activate_window(rblxms_window.hwnd)
                await asyncio.sleep(settings["global_wait_time"])
                mkey.left_click_xy_natural(ms_rblx_spawn_pos[0], ms_rblx_spawn_pos[1])
                await asyncio.sleep(settings["global_wait_time"])
                mkey.left_click_xy_natural(ms_rblx_spawn_pos[0], ms_rblx_spawn_pos[1])
                await asyncio.sleep(settings["global_wait_time"])
                _keyboard.press(Key.f11)
                await asyncio.sleep(0.1)
                _keyboard.release(Key.f11)
                if detect_client_reconnect(rblx_log_dir):
                    break
                await asyncio.sleep(45)
                _attempt += 1
            await leave_main_menu()
            print("Successfully rejoined!")

@tasks.loop(seconds=60)
async def auto_craft():
    global auto_mode_swap, auto_craft_index
    items_to_craft = []
    for itm in settings["auto_craft_item"].keys():
        if settings["auto_craft_item"][itm]:
            items_to_craft.append(itm)
    if len(items_to_craft) < 1:
        return
    mkey.left_click_xy_natural(hp1_recipe_pos[0], hp1_recipe_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    _keyboard.press("f")
    await asyncio.sleep(settings["global_wait_time"])
    _keyboard.release("f")
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(hp1_recipe_pos[0], hp1_recipe_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(hp1_recipe_pos[0], hp1_recipe_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    _mouse.scroll(0, 30)
    await asyncio.sleep(0.1)
    while True:
        mkey.left_click_xy_natural(hp1_recipe_pos[0], hp1_recipe_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        _keyboard.press("f")
        await asyncio.sleep(settings["global_wait_time"])
        _keyboard.release("f")
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(hp1_recipe_pos[0], hp1_recipe_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        mkey.left_click_xy_natural(hp1_recipe_pos[0], hp1_recipe_pos[1])
        await asyncio.sleep(settings["global_wait_time"])
        if settings["auto_craft_item"]["Potion of Bound"]:
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(bound_recipe_pos[0], bound_recipe_pos[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(craft_btn_pos[0], craft_btn_pos[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
            await asyncio.sleep(settings["global_wait_time"])
            if auto_craft_index == 1:
                mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                await asyncio.sleep(settings["global_wait_time"])                
            mkey.left_click_xy_natural(hp1_recipe_pos[0], hp1_recipe_pos[1])
            await asyncio.sleep(settings["global_wait_time"])            
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(settings["global_wait_time"])
        if settings["auto_craft_item"]["Heavenly Potion"]:
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(bound_recipe_pos[0], bound_recipe_pos[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(craft_btn_pos[0], craft_btn_pos[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
            await asyncio.sleep(0.1)
            mkey.left_click_xy_natural(hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
            await asyncio.sleep(0.1)
            _keyboard.type("250")
            mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
            await asyncio.sleep(0.1)
            mkey.left_click_xy_natural(hp2_pos_potions[0], hp2_pos_potions[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(hp2_pos_potions[0], hp2_pos_potions[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural((1064 * scale_w), (988 * scale_h))
            await asyncio.sleep(settings["global_wait_time"])
            if auto_craft_index == 2:
                mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(hp1_recipe_pos[0], hp1_recipe_pos[1])
            await asyncio.sleep(settings["global_wait_time"])
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
        if settings["auto_craft_item"]["Godly Potion (Zeus)"]:
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(bound_recipe_pos[0], bound_recipe_pos[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(craft_btn_pos[0], craft_btn_pos[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
            await asyncio.sleep(0.1)
            mkey.left_click_xy_natural(hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
            await asyncio.sleep(0.1)
            _keyboard.type("25")
            mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
            await asyncio.sleep(0.1)
            mkey.left_click_xy_natural(hp2_pos_potions[0] - (110 * scale_w), hp2_pos_potions[1])
            await asyncio.sleep(0.1)
            mkey.left_click_xy_natural(hp2_pos_potions[0] - (110 * scale_w), hp2_pos_potions[1])
            await asyncio.sleep(0.1)
            _keyboard.type("25")
            mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
            await asyncio.sleep(0.1)
            mkey.left_click_xy_natural(hp2_pos_potions[0], hp2_pos_potions[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural((1064 * scale_w), (988 * scale_h))
            await asyncio.sleep(settings["global_wait_time"])
            if auto_craft_index == 3:
                mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                await asyncio.sleep(settings["global_wait_time"])            
            mkey.left_click_xy_natural(hp1_recipe_pos[0], hp1_recipe_pos[1])
            await asyncio.sleep(settings["global_wait_time"])            
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
        if settings["auto_craft_item"]["Godly Potion (Poseidon)"]:
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(bound_recipe_pos[0], bound_recipe_pos[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(craft_btn_pos[0], craft_btn_pos[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
            await asyncio.sleep(0.1)
            mkey.left_click_xy_natural(hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
            await asyncio.sleep(0.1)
            _keyboard.type("50")
            mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
            await asyncio.sleep(0.1)
            mkey.left_click_xy_natural(hp2_pos_potions[0], hp2_pos_potions[1])
            await asyncio.sleep(settings["global_wait_time"])
            if auto_craft_index == 4:
                mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                await asyncio.sleep(settings["global_wait_time"])            
            mkey.left_click_xy_natural(hp1_recipe_pos[0], hp1_recipe_pos[1])
            await asyncio.sleep(settings["global_wait_time"])            
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
        if settings["auto_craft_item"]["Godly Potion (Hades)"]:
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(bound_recipe_pos[0], bound_recipe_pos[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(craft_btn_pos[0], craft_btn_pos[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
            await asyncio.sleep(0.1)
            mkey.left_click_xy_natural(hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
            await asyncio.sleep(0.1)
            _keyboard.type("50")
            mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
            await asyncio.sleep(0.1)
            mkey.left_click_xy_natural(hp2_pos_potions[0], hp2_pos_potions[1])
            await asyncio.sleep(settings["global_wait_time"])
            if auto_craft_index == 5:
                mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                await asyncio.sleep(settings["global_wait_time"])            
            mkey.left_click_xy_natural(hp1_recipe_pos[0], hp1_recipe_pos[1])
            await asyncio.sleep(settings["global_wait_time"])            
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
        if settings["auto_craft_item"]["Warp Potion"]:
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(bound_recipe_pos[0], bound_recipe_pos[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(craft_btn_pos[0], craft_btn_pos[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
            await asyncio.sleep(settings["global_wait_time"])
            _mouse.scroll(0, -30)
            await asyncio.sleep(settings["global_wait_time"])
            _mouse.scroll(0, -30)
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(hp1_pos_celestial[0] - (110 * scale_w), hp1_pos_celestial[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(hp1_pos_celestial[0] - (110 * scale_w), hp1_pos_celestial[1])
            await asyncio.sleep(settings["global_wait_time"])
            _keyboard.type("1000")
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(hp1_pos_celestial[0], hp1_pos_celestial[1])
            await asyncio.sleep(settings["global_wait_time"])
            _mouse.scroll(0, 30)
            await asyncio.sleep(settings["global_wait_time"])
            _mouse.scroll(0, 30)
            await asyncio.sleep(settings["global_wait_time"])
            if auto_craft_index == 6:
                mkey.left_click_xy_natural(auto_btn_pos[0], auto_btn_pos[1])
                await asyncio.sleep(settings["global_wait_time"])            
            mkey.left_click_xy_natural(hp1_recipe_pos[0], hp1_recipe_pos[1])
            await asyncio.sleep(settings["global_wait_time"])            
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
        if settings["auto_craft_item"]["Godlike Potion"]:
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, -30)
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(bound_recipe_pos[0], bound_recipe_pos[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(craft_btn_pos[0], craft_btn_pos[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(hp1_pos_potions[0], hp1_pos_potions[1])
            await asyncio.sleep(0.1)
            mkey.left_click_xy_natural(hp2_pos_potions[0], hp2_pos_potions[1])
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural((1064 * scale_w), (988 * scale_h))
            await asyncio.sleep(settings["global_wait_time"])
            mkey.left_click_xy_natural(bound_recipe_pos[0], bound_recipe_pos[1])
            await asyncio.sleep(settings["global_wait_time"])
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
            _mouse.scroll(0, 30)
            await asyncio.sleep(0.1)
        if auto_craft_index > 6:
            auto_craft_index = 1
        if auto_mode_swap == 5:
            auto_mode_swap = 0
        else:
            auto_mode_swap += 1
        auto_craft_index += 1
        await asyncio.sleep(60)

@tasks.loop(seconds=0)
async def reset_aura():
    reset_aura.stop()

@reset_aura.after_loop
async def on_reset_aura_cancel():
    current_aura = get_latest_equipped_aura(rblx_log_dir)
    if current_aura == settings["reset_aura"]:
        return    
    mkey.left_click_xy_natural(aura_button_pos[0], aura_button_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(search_pos[0], search_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    _keyboard.type(settings["reset_aura"])
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(query_pos[0], query_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(equip_pos[0], equip_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(equip_pos[0], equip_pos[1])
    await asyncio.sleep(settings["global_wait_time"])
    _keyboard.press(Key.cmd)
    await asyncio.sleep(settings["global_wait_time"])
    _keyboard.release(Key.cmd)
    await asyncio.sleep(settings["global_wait_time"])
    _mouse.position = close_pos
    await asyncio.sleep(settings["global_wait_time"])
    _keyboard.press(Key.cmd)
    await asyncio.sleep(settings["global_wait_time"])
    _keyboard.release(Key.cmd)
    await asyncio.sleep(settings["global_wait_time"])
    mkey.left_click_xy_natural(close_pos[0], close_pos[1])
    
@tasks.loop(seconds=150)
async def merchant_detection():
    if settings["log_channel_id"] == 0:
        print("You must select a channel ID, you can do this by running the set_log_channel command.")
        return
    await use_item("Merchant Teleport", 1, False)
    await asyncio.sleep(settings["merchant_detec_wait"])
    px = ImageGrab.grab().load()
    colour = px[default_pos[0], default_pos[1]]
    hex_col = rgb2hex(colour[0], colour[1], colour[2])
    colour2 = px[secondary_pos[0], secondary_pos[1]]
    hex_col2 = rgb2hex(colour2[0], colour2[1], colour2[2])
    if (hex_col == "#000000" and hex_col2 == "#000000"):
        rnow = datetime.now()
        mkey.left_click_xy_natural(close_pos[0], close_pos[1])
        await asyncio.sleep(1)
        _keyboard.press("e")
        await asyncio.sleep(2)
        _keyboard.release("e")
        await asyncio.sleep(3)
        px = ImageGrab.grab().load()
        await asyncio.sleep(2)
        mkey.left_click_xy_natural(open_merch_pos[0], open_merch_pos[1])
        await asyncio.sleep(0.5)
        merchimg = pag.screenshot(f"{MACROPATH}/scr/screenshot_merchant.png")
        await asyncio.sleep(0.2)
        up = discord.File(f"{MACROPATH}/scr/screenshot_merchant.png", filename="merchant.png")
        _break = False
        cols = []
        try:
            for y in range(merchant_face_pos_1[1], merchant_face_pos_2[1]):
                for x in range(merchant_face_pos_1[0], merchant_face_pos_2[0]):
                    if _break:
                        break
                    colour = px[x, y]
                    hex_col = rgb2hex(colour[0], colour[1], colour[2])
                    cols.append(hex_col)
                    print(hex_col)
                    if hex_col in mari_cols:
                        emb = discord.Embed(
                                        title = f"Mari Spawned",
                                        description = f"A Mari selling the following items in the screenshot has been detected at time: {rnow.strftime('%d/%m/%Y %H:%M:%S')}",
                                        colour = discord.Color.from_rgb(255, 255, 255)
                        )
                        emb.set_image(url="attachment://merchant.png")
                        log_channel = client.get_channel(settings["log_channel_id"])
                        if settings["send_mari"]:
                            if settings["ping_jester"] and settings["mention_id"] != 0:
                                await log_channel.send(f"<@{settings["mention_id"]}>", embed=emb, file=up)
                            else:
                                await log_channel.send(embed=emb, file=up)
                        _break = True
                    elif hex_col in jester_cols:
                        emb = discord.Embed(
                                    title = f"Jester Spawned",
                                    description = f"A Jester selling the following items in the screenshot has been detected at time: {rnow.strftime('%d/%m/%Y %H:%M:%S')}",
                                    colour = discord.Color.from_rgb(176, 49, 255)
                        )
                        emb.set_image(url="attachment://merchant.png")
                        log_channel = client.get_channel(settings["log_channel_id"])
                        if settings["send_jester"]:
                            if settings["ping_jester"] and settings["mention_id"] != 0:
                                await log_channel.send(f"<@{settings["mention_id"]}>", embed=emb, file=up)
                            else:
                                await log_channel.send(embed=emb, file=up)
                        _break = True
                if _break:
                    break
        except Exception as e:
            print(e)
    else:
        mkey.left_click_xy_natural(close_pos[0], close_pos[1])

@tasks.loop(seconds=0)
async def biome_detection():
    global previous_biome
    current_biome = get_latest_hovertext(rblx_log_dir)
    if previous_biome == None:
        previous_biome = current_biome
        return
    if current_biome == previous_biome:
        return
    if settings["log_channel_id"] == 0:
        print("You must select a channel ID, you can do this by running the set_log_channel command.")
        return
    try:
        if current_biome.lower() in settings["biomes"].keys():
            previous_biome = current_biome
            if current_biome.lower() == "normal":
                return
            rnow = datetime.now()
            if settings["biomes"][current_biome.lower()]:
                log_channel = client.get_channel(settings["log_channel_id"])
                if valid_ps:
                    emb = discord.Embed(
                        title=f"Biome Started: {current_biome}",
                        description=f"Biome {current_biome} has started at time: {rnow.strftime('%d/%m/%Y %H:%M:%S')}\nServer Invite: {settings['private_server_link']}",
                        colour=discord.Colour.from_rgb(biome_cols[current_biome.lower()][0], biome_cols[current_biome.lower()][1], biome_cols[current_biome.lower()][2])
                    )
                else:
                    emb = discord.Embed(
                        title=f"Biome Started: {current_biome}",
                        description=f"Biome {current_biome} has started at time: {rnow.strftime('%d/%m/%Y %H:%M:%S')}",
                        colour=discord.Colour.from_rgb(biome_cols[current_biome.lower()][0], biome_cols[current_biome.lower()][1], biome_cols[current_biome.lower()][2])
                    )
                if current_biome.lower() == "glitched":
                    await log_channel.send("@everyone", embed=emb)
                    await auto_pop("glitched")
                else:
                    await log_channel.send(embed=emb)
    except KeyError:
        pass
    except AttributeError:
        pass
    except Exception as e:
        print(e)

@tasks.loop(seconds=0)
async def aura_detection():
    global previous_aura
    current_aura = get_latest_equipped_aura(rblx_log_dir)
    if previous_aura == None:
        previous_aura = current_aura
        return
    if current_aura == "In Main Menu":
        return
    if current_aura == settings["reset_aura"] and settings["reset_aura"] != "":
        return
    if current_aura == previous_aura:
        return
    if settings["log_channel_id"] == 0:
        print("You must select a channel ID, you can do this by running the set_log_channel command.")
        return
    try:
        if current_aura.lower() in auras.keys():
            previous_aura = current_aura
            rnow = datetime.now()
            current_biome = get_latest_hovertext(rblx_log_dir)
            if current_biome.lower() == auras[current_aura.lower()]["native_biome"].lower():
                if current_biome.lower() == "snowy":
                    aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / SNOWY_MULTIPLIER)
                elif current_biome.lower() == "windy":
                    aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / WINDY_MULTIPLIER)
                elif current_biome.lower() == "rainy":
                    aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / RAINY_MULTIPLER)
                elif current_biome.lower() == "sand storm":
                    aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / SANDSTORM_MULTIPLIER)
                elif current_biome.lower() == "hell":
                    aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / HELL_MULTIPLIER)
                elif current_biome.lower() == "starfall":
                    aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / STARFALL_MULTIPLIER)
                elif current_biome.lower() == "corruption":
                    aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / CORRUPTION_MULTIPLIER)
                elif current_biome.lower() == "null":
                    aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / NULL_MULTIPLIER)
                elif current_biome.lower() == "glitched":
                    aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / GLITCHED_MULTIPLIER)
                elif current_biome.lower() == "dreamspace":
                    aura_rarity = int(int(auras[current_aura.lower()]["rarity"]) / DREAMSPACE_MULTIPLIER)
                log_channel = client.get_channel(settings["log_channel_id"])
                emb = discord.Embed(
                    title=f"Aura Rolled: {current_aura}",
                    description=f"Rolled Aura: {current_aura}\nWith chances of 1/{str(aura_rarity)} (from {auras[current_aura.lower()]["native_biome"]})\nAt time: {rnow.strftime('%d/%m/%Y %H:%M:%S')}",
                    colour=discord.Colour.from_rgb(hex2rgb(auras[current_aura.lower()]["emb_colour"])[0],hex2rgb(auras[current_aura.lower()]["emb_colour"])[1],hex2rgb(auras[current_aura.lower()]["emb_colour"])[2])
                )
                if auras[current_aura.lower()]["img_url"] != "":
                    emb.set_thumbnail(url=auras[current_aura.lower()]["img_url"])
            else:
                log_channel = client.get_channel(settings["log_channel_id"])
                emb = discord.Embed(
                    title=f"Aura Rolled: {current_aura}",
                    description=f"Rolled Aura: {current_aura}\nWith chances of 1/{auras[current_aura.lower()]["rarity"]}\nAt time: {rnow.strftime('%d/%m/%Y %H:%M:%S')}",
                    colour=discord.Colour.from_rgb(hex2rgb(auras[current_aura.lower()]["emb_colour"])[0],hex2rgb(auras[current_aura.lower()]["emb_colour"])[1],hex2rgb(auras[current_aura.lower()]["emb_colour"])[2])
                )
                if auras[current_aura.lower()]["img_url"] != "":
                    emb.set_thumbnail(url=auras[current_aura.lower()]["img_url"])
            if settings["take_screenshot_on_detection"]:                    
                auraimg = pag.screenshot(f"{MACROPATH}/scr/screenshot_aura.png")
                up = discord.File(f"{MACROPATH}/scr/screenshot_aura.png", filename="aura.png")
                emb.set_image(url="attachment://aura.png")
                if settings["mention"] and settings["mention_id"] != 0 and (int(auras[current_aura.lower()]["rarity"]) > int(settings["minimum_ping"])):
                    await log_channel.send(f"<@{settings["mention_id"]}>", embed=emb, file=up)
                else:
                    await log_channel.send(embed=emb, file=up)
            else:
                if settings["mention"] and settings["mention_id"] != 0 and (int(auras[current_aura.lower()]["rarity"]) > int(settings["minimum_ping"])):
                    await log_channel.send(f"<@{settings["mention_id"]}>", embed=emb)
                else:
                    await log_channel.send(embed=emb)
            print(f"Rolled Aura: {current_aura}\nWith chances of 1/{auras[current_aura.lower()]["rarity"]}\nAt time: {rnow.strftime('%d/%m/%Y %H:%M:%S')}")
            if settings["reset_aura"] != "":
                reset_aura.start()
    except KeyError:
        pass
    except AttributeError:
        pass
    except Exception as e:
        print(e)

@client.command()
async def plugins(ctx):
    await ctx.send("Installed Plugins:")
    for plu in _plugins:
        await ctx.send(plu)

for filename in os.listdir(f"{MACROPATH}/plugins"):
    if filename.endswith(".py"):
        client.load_extension(f"plugins.{filename[:-3]}")
        print(f"Loaded plugin: {filename[:-3]}")
        _plugins.append(filename[:-3])

client.run(settings["TOKEN"])
