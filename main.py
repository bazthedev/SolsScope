import os
import discord
from discord.ext import commands, tasks
import pyautogui as pag
from datetime import datetime
import json
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import Key
import asyncio
from PIL import ImageGrab
import requests
import screeninfo as si
import re
import glob
import shutil
import tempfile

def get_auras():
    print("Downloading Aura List")
    dl = requests.get("https://raw.githubusercontent.com/bazthedev/SolsRNGBot/main/auras.json")
    f = open("auras.json", "wb")
    f.write(dl.content)
    f.close()
    print("Downloaded Aura List")

def update_settings(settings):
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)

def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def reload_settings():
    global settings
    with open("settings.json", "r") as f:
        settings = json.load(f)

def validate_settings():
    found_keys = []
    todel = []
    for k in settings.keys():
        if k not in valid_settings_keys:
            todel.append(k)
            print(f"Invalid setting ({k}) detected")
        else:
            found_keys.append(k)
    for _ in todel:
        del settings[_]
        print(f"Invalid setting ({_}) deleted")
    for _ in valid_settings_keys:
        if _ not in found_keys:
            settings[_] = default_settings[_]
            print(f"Missing setting ({_}) added")
    update_settings(settings)
    reload_settings()

async def use_item(item_name : str, amount : int, close_menu : bool):
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.position = inv_button_pos
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.position = items_pos
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.position = search_pos
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _keyboard.type(item_name)
    await asyncio.sleep(0.1)
    _mouse.position = query_pos
    await asyncio.sleep(0.1)
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.position = item_amt_pos
    await asyncio.sleep(0.1)
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _keyboard.press(Key.ctrl)
    _keyboard.press("a")
    await asyncio.sleep(0.1)
    _keyboard.release("a")
    _keyboard.release(Key.ctrl)
    await asyncio.sleep(0.1)
    _keyboard.type(str(amount))
    await asyncio.sleep(0.1)
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.position = use_pos
    await asyncio.sleep(0.1)
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.5)
    if close_menu:
        _mouse.position = close_pos
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)

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

if not os.path.exists("./scr/"):
    os.mkdir("./scr/")

if not os.path.exists("./plugins/"):
    os.mkdir("./plugins/")
    os.mkdir("./plugins/config/")
now = datetime.now()
client = commands.Bot(commands.when_mentioned, case_insensitive=True)
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
search_pos = ((1108 * scale_w), (484 * scale_h))
secondary_pos = ((564 * scale_w), (401 * scale_h))
query_pos = ((1086 * scale_w), (572 * scale_h))
equip_pos = ((812 * scale_w), (844 * scale_h))
use_pos = ((910 * scale_w), (772 * scale_h))
item_amt_pos = ((756 * scale_w), (773 * scale_h))
items_pos = ((1702 * scale_w), (446 * scale_h)) 
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
hp1_pos_potions = ((1064 * scale_w), (840 * scale_h))
hp1_pos_celestial = ((1064 * scale_w), (1024 * scale_h))
hp2_pos_potions = ((1064 * scale_w), (910 * scale_h))
merchant_face_pos_1 = (int(841 * scale_w), int(1056 * scale_h))
merchant_face_pos_2 = (int(855 * scale_w), int(1063 * scale_h))
mari_cols = ["#767474", "#767476", "#757474"]
jester_cols = ["#e2e2e2", "#e0e0e0"]
rblx_log_dir = os.path.expandvars(r"%localappdata%\\Roblox\\logs")
previous_biome = None
popping = False
_plugins = []
local_version = "1.1.3"
default_settings = {"TOKEN": "", "__version__" :  local_version, "log_channel_id": 0, "cd" : str(os.getcwd()), "skip_dl": False, "mention" : True, "mention_id" : 0, "minimum_roll" : "99998", "minimum_ping" : "349999", "reset_aura" : "", "merchant_detection" : True, "auto_purchase_items" : {"Void Coin/Lucky Penny" : True}, "glitch_detector" : True, "ping_on_glitch" : True, "pop_in_glitch" : False, "auto_use_items_in_glitch": {"Heavenly Potion II" : {"use" : True, "amount" : 200}, "Fortune Potion III" : {"use" : True, "amount" : 1}, "Lucky Potion" : {"use" : True, "amount" : 10}, "Pumpkin" : {"use" : True, "amount" : 10}, "Haste Potion III" : {"use" : False, "amount" : 1}, "Warp Potion" : {"use" : True, "amount" : 1}, "Mixed Potion" : {"use" : True, "amount" : 10}, "Stella's Candle" : {"use" : True, "amount" : 1}, "Santa Claus Potion" : {"use" : True, "amount" : 5}}, "Hwachae" : {"use" : True}, "dreamspace_detector" : True, "ping_on_dreamspace" : True, "pop_in_dreamspace" : False, "auto_use_items_in_dreamspace" : {"Heavenly Potion II" : {"use" : False, "amount" : 1}, "Fortune Potion III" : {"use" : True, "amount" : 1}, "Lucky Potion" : {"use" : True, "amount" : 10}, "Pumpkin" : {"use" : True, "amount" : 10}, "Haste Potion III" : {"use" : False, "amount" : 1}, "Warp Potion" : {"use" : True, "amount" : 1}, "Mixed Potion" : {"use" : True, "amount" : 10}, "Stella's Candle" : {"use" : True, "amount" : 1}, "Santa Claus Potion" : {"use" : True, "amount" : 5}}, "Hwachae" : {"use" : True}, "auto_craft_mode" : False, "skip_auto_mode_warning" : False, "auto_craft_item" : {"Heavenly Potion I" : False, "Heavenly Potion II" : True, "Warp Potion" : False}, "auto_biome_randomizer" : False, "auto_strange_controller" : False}
auto_purchase = {"Void Coin/Lucky Penny": ["#ff92fe", "#ff9e4e"]}
print(f"Starting SolsRNGBot v{local_version}")

if not os.path.exists("./settings.json"):
    x = open("settings.json", "w")
    x.write('{}')
    x.close()
    with open("settings.json", "w") as f:
        json.dump(default_settings, f, indent=4)

valid_settings_keys = ["TOKEN", "__version__", "log_channel_id", "cd", "skip_dl", "mention", "mention_id", "minimum_roll", "minimum_ping", "reset_aura", "merchant_detection", "auto_purchase_items", "glitch_detector", "ping_on_glitch", "pop_in_glitch", "auto_use_items_in_glitch", "dreamspace_detector", "ping_on_dreamspace", "pop_in_dreamspace", "auto_use_items_in_dreamspace", "auto_craft_mode", "skip_auto_mode_warning", "auto_craft_item", "auto_biome_randomizer", "auto_strange_controller"]

reload_settings()

if settings["__version__"] < local_version:
    settings["__version__"] = local_version
    update_settings(settings)
    reload_settings()

if settings["__version__"] > local_version:
    print("You are running newer settings with an older version of this program. This may delete some of your settings. Are you sure you want to continue (y)? ")
    confirm = input("")
    if confirm[0].lower() != "y":
        exit("You are running newer settings with an older version of this program.")
        
# Settings integrity check
validate_settings()

if settings["TOKEN"] == "":
    exit("You need to add your bot token in the settings.json file")
if not settings["skip_dl"]:
    get_auras()

with open("auras.json", "r") as f:
    auras = json.load(f)

__version__ = settings["__version__"]

@client.event
async def on_ready():
    print("Let's go gambling!")
    print(f"Started at {now.strftime("%d/%m/%Y %H:%M:%S")} running v{__version__} using local version {local_version}")
    await client.change_presence(activity=discord.Game(name=f"bazthedev/SolsRNGBot v{local_version}"))
    if settings["auto_craft_mode"] and not settings["merchant_detection"]:
        crafts = []
        for item in settings["auto_craft_item"]:
            if settings["auto_craft_item"][item]:
                crafts.append(item)        
        if len(crafts) > 1 or len(crafts) < 1:
            print("You can only auto craft one item at a time, please rerun the program with ONE item from the list selected.")
            exit("Please select one item from the list")        
        print("[WARNING] Auto Craft Mode is on. You will not be able to use certain features whilst this settings is on.")
        print(f"The item you are automatically crafting is {crafts[0]}")
        if not settings["skip_auto_mode_warning"]:
            print("Please ensure that you are on the craft screen for the item you want and have selected Auto mode for it in the craft menu. When you have done this, please press enter.")
            input("")
        else:
            print("Please ensure that you are on the craft screen for the item you want and have selected Auto mode for it in the craft menu.")
        if settings["reset_aura"] != "":
            settings["reset_aura"] = ""
            update_settings(settings)
            reload_settings()
        print("Starting auto craft mode. Please click back onto Roblox and wait 5 seconds")
        await asyncio.sleep(5)
        auto_craft.start()
    else:
        keep_alive.start()
        print("Started Autokick Prevention")
        await asyncio.sleep(3)
    if settings["log_channel_id"] != 0:
        if settings["auto_craft_mode"] and not settings["merchant_detection"]:
            log_channel = client.get_channel(settings["log_channel_id"])
            emb = discord.Embed(
                title="Bot has started",
                description=f"Mode: Auto Craft\nAuto Craft item: {crafts[0]}\nStarted at {now.strftime("%d/%m/%Y %H:%M:%S")}"
            )
            emb.set_footer(text=f"bazthedev/SolsRNGBot v{local_version}")
            await log_channel.send(embed=emb)
        else:
            log_channel = client.get_channel(settings["log_channel_id"])
            emb = discord.Embed(
                title="Bot has started",
                description=f"Mode: Normal\nStarted at {now.strftime("%d/%m/%Y %H:%M:%S")}"
            )
            emb.set_footer(text=f"bazthedev/SolsRNGBot v{local_version}")
            await log_channel.send(embed=emb)
        aura_detection.start()
        print("Started Aura Detection")
        if settings["glitch_detector"]:
            glitch_detector.start()
            print("Started Glitch Biome Detection")
        if settings["dreamspace_detector"]:
            dreamspace_detector.start()
            print("Started Dreamspace Biome Detection")
    else:
        print("You must select a channel ID, you can do this by running the set_log_channel command.")
    if settings["auto_biome_randomizer"]:
        biome_randomizer.start()
        print("Started Biome Randomizer")
    if settings["auto_strange_controller"]:
        await asyncio.sleep(15)
        strange_controller.start()
        print("Started Strange Controller")
    if settings["merchant_detection"]:
        await asyncio.sleep(15)
        merchant_detection.start()
        print("Started Merchant Detection")
    
@tasks.loop(seconds=0)
async def glitch_detector():
    rnow = datetime.now()
    global previous_biome, popping
    latest_hovertext = get_latest_hovertext(rblx_log_dir)
    log_channel = client.get_channel(settings["log_channel_id"])
    if latest_hovertext == "GLITCHED" and previous_biome != "GLITCHED":
        merchant_detection.stop()
        previous_biome = latest_hovertext
        popping = True
        storimg = pag.screenshot("./scr/screenshot_glitch.png")
        up = discord.File("./scr/screenshot_glitch.png", filename="glitch.png")
        print("Glitch biome started")    
        emb = discord.Embed(
                title="GLITCH BIOME DETECTED",
                description=f"A GLITCH biome was detected at {rnow.strftime("%d/%m/%Y %H:%M:%S")}",
                colour=discord.Colour.from_rgb(101, 255, 101)
        )
        if settings["ping_on_glitch"]:
            await log_channel.send(f"<@{settings["mention_id"]}>",embed=emb, file=up)
        else:
            await log_channel.send(embed=emb, file=up)
        if settings["pop_in_glitch"] and popping:
            popping = False
            _keyboard.press(Key.cmd)
            await asyncio.sleep(0.1)
            _keyboard.release(Key.cmd)
            await asyncio.sleep(0.1)
            _mouse.position = menu_btn_pos
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _keyboard.press(Key.cmd)
            await asyncio.sleep(0.1)
            _keyboard.release(Key.cmd)
            await asyncio.sleep(0.1)
            _mouse.position = settings_btn_pos
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _keyboard.press(Key.cmd)
            await asyncio.sleep(0.1)
            _keyboard.release(Key.cmd)
            await asyncio.sleep(0.1)
            _mouse.position = rolling_conf_pos
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _keyboard.press(Key.cmd)
            await asyncio.sleep(0.1)
            _keyboard.release(Key.cmd)
            await asyncio.sleep(0.1)
            _mouse.position = cutscene_conf_pos
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _keyboard.press(Key.ctrl)
            _keyboard.press("a")
            await asyncio.sleep(0.1)
            _keyboard.release("a")
            _keyboard.release(Key.ctrl)
            await asyncio.sleep(0.1)
            _keyboard.type("219999999")
            await asyncio.sleep(0.1)
            _keyboard.press(Key.cmd)
            await asyncio.sleep(0.1)
            _keyboard.release(Key.cmd)
            await asyncio.sleep(0.1)
            _mouse.position = close_pos
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            to_use = []
            for buff in reversed(settings["auto_use_items_in_glitch"].keys()):
                if settings["auto_use_items_in_glitch"][buff]["use"]:
                    to_use.append(buff)
            for item in to_use:
                    await use_item(item, settings["auto_use_items_in_glitch"][item]["amount"], True)
        else:
            popping = False
    elif previous_biome == "GLITCHED" and latest_hovertext != "GLITCHED":
        previous_biome = None
        merchant_detection.start()
        print("Glitch iome ended")
        emb = discord.Embed(
                title="Glitch Biome Ended",
                description=f"A GLITCH biome ended at {rnow.strftime("%d/%m/%Y %H:%M:%S")}",
                colour=discord.Colour.from_rgb(101, 255, 101)
        )
        await log_channel.send(embed=emb)
        

@tasks.loop(seconds=0)
async def dreamspace_detector():
    rnow = datetime.now()
    global previous_biome, popping
    latest_hovertext = get_latest_hovertext(rblx_log_dir)
    log_channel = client.get_channel(settings["log_channel_id"])
    if latest_hovertext == "DREAMSPACE" and previous_biome != "DREAMSPACE":
        merchant_detection.stop()
        previous_biome = latest_hovertext
        popping = True
        storimg = pag.screenshot("./scr/screenshot_dreamspace.png")
        up = discord.File("./scr/screenshot_dreamspace.png", filename="dreamspace.png")
        print("Dreamspace biome started")    
        emb = discord.Embed(
                title="DREAMSPACE BIOME DETECTED",
                description=f"A DREAMSPACE biome was detected at {rnow.strftime("%d/%m/%Y %H:%M:%S")}",
                colour=discord.Colour.from_rgb(255, 105, 180)
        )
        if settings["ping_on_dreamspace"]:
            await log_channel.send(f"<@{settings["mention_id"]}>",embed=emb, file=up)
        else:
            await log_channel.send(embed=emb, file=up)
        if settings["pop_in_dreamspace"] and popping:
            popping = False
            _keyboard.press(Key.cmd)
            await asyncio.sleep(0.1)
            _keyboard.release(Key.cmd)
            await asyncio.sleep(0.1)
            _mouse.position = menu_btn_pos
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _keyboard.press(Key.cmd)
            await asyncio.sleep(0.1)
            _keyboard.release(Key.cmd)
            await asyncio.sleep(0.1)
            _mouse.position = settings_btn_pos
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _keyboard.press(Key.cmd)
            await asyncio.sleep(0.1)
            _keyboard.release(Key.cmd)
            await asyncio.sleep(0.1)
            _mouse.position = rolling_conf_pos
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _keyboard.press(Key.cmd)
            await asyncio.sleep(0.1)
            _keyboard.release(Key.cmd)
            await asyncio.sleep(0.1)
            _mouse.position = cutscene_conf_pos
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _keyboard.press(Key.ctrl)
            _keyboard.press("a")
            await asyncio.sleep(0.1)
            _keyboard.release("a")
            _keyboard.release(Key.ctrl)
            await asyncio.sleep(0.1)
            _keyboard.type("219999999")
            await asyncio.sleep(0.1)
            _keyboard.press(Key.cmd)
            await asyncio.sleep(0.1)
            _keyboard.release(Key.cmd)
            await asyncio.sleep(0.1)
            _mouse.position = close_pos
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            _mouse.click(Button.left)
            await asyncio.sleep(0.1)
            to_use = []
            for buff in reversed(settings["auto_use_items_in_dreamspace"].keys()):
                if settings["auto_use_items_in_dreamspace"][buff]["use"]:
                    to_use.append(buff)
            for item in to_use:
                    await use_item(item, settings["auto_use_items_in_dreamspace"][item]["amount"], True)
        else:
            popping = False
    elif previous_biome == "DREAMSPACE" and latest_hovertext != "DREAMSPACE":
        merchant_detection.start()
        previous_biome = None
        print("Dreamspace biome ended")
        emb = discord.Embed(
                title="Dreamspace Biome Ended",
                description=f"A DREAMSPACE biome ended at {rnow.strftime("%d/%m/%Y %H:%M:%S")}",
                colour=discord.Colour.from_rgb(255, 105, 180)
        )
        await log_channel.send(embed=emb)

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
        crafts = []
        for item in settings["auto_craft_item"]:
            if settings["auto_craft_item"][item]:
                crafts.append(item)
        await ctx.send(f"The bot is currently running in Auto Craft mode, and the item being crafted is: {crafts[0]}")
    else:
        await ctx.send("The bot is running in Normal mode.")

@client.command()
@commands.is_owner()
async def stop(ctx):
    await ctx.send("Manual stop initiated")
    aura_detection.stop()
    keep_alive.stop()
    await client.close()
    print("Aw dang it")

@client.command()
@commands.is_owner()
async def storage_scr(ctx):
    await ctx.send("Taking screenshot of Aura Storage, please wait, this will take a few seconds.")
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.position = aura_button_pos
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.position = search_pos
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    if os.path.exists("./scr/screenshot_storage.png"):
        os.remove("./scr/screenshot_storage.png")
        await asyncio.sleep(1)
    storimg = pag.screenshot("./scr/screenshot_storage.png")
    await asyncio.sleep(0.1)
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.position = close_pos
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await ctx.send(file=discord.File("./scr/screenshot_storage.png"))

@client.command()
@commands.is_owner()
async def inv_scr(ctx):
    await ctx.send("Taking screenshot of inventory, please wait, this will take a few seconds.")
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.position = inv_button_pos
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.position = search_pos
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    if os.path.exists("./scr/screenshot_inventory.png"):
        os.remove("./scr/screenshot_inventory.png")
        await asyncio.sleep(1)
    storimg = pag.screenshot("./scr/screenshot_inventory.png")
    await asyncio.sleep(0.1)
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.position = close_pos
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await ctx.send(file=discord.File("./scr/screenshot_inventory.png"))

@client.command()
async def purchase_item(ctx, item : int):
    if not settings["merchant_detection"]:
        await ctx.send("Merchant Detection is disabled. Please enable it to use this feature.")
        return
    if settings["auto_craft_mode"]:
        await ctx.send("Auto Craft mode is enabled. Please disable it to use this feature.")
        return
    if item > 5 or item < 1:
        await ctx.send("A merchant only sells 5 items at a time")
        return
    if item == 1:
        _mouse.position = merch_item_pos_1_purchase
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.position = quantity_btn_pos
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.type("25")
        await asyncio.sleep(0.1)
        _mouse.position = purchase_btn_pos
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        log_channel = client.get_channel(settings["log_channel_id"])
        if settings["ping_merchant"] and settings["mention_id"] != 0:
            await log_channel.send(f"<@{settings["mention_id"]}>\nPurchased item in box 1 from merchant")
        else:
            await log_channel.send(f"Purchased item in box 1 from merchant")
        await asyncio.sleep(2)
    elif item == 2:
        _mouse.position = merch_item_pos_2_purchase
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.position = quantity_btn_pos
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.type("25")
        await asyncio.sleep(0.1)
        _mouse.position = purchase_btn_pos
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        log_channel = client.get_channel(settings["log_channel_id"])
        if settings["ping_merchant"] and settings["mention_id"] != 0:
            await log_channel.send(f"<@{settings["mention_id"]}>\nPurchased item in box 2 from merchant")
        else:
            await log_channel.send(f"Purchased item in box 2 from merchant")
        await asyncio.sleep(2)
    elif item == 3:
        _mouse.position = merch_item_pos_3_purchase
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.position = quantity_btn_pos
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.type("25")
        await asyncio.sleep(0.1)
        _mouse.position = purchase_btn_pos
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        log_channel = client.get_channel(settings["log_channel_id"])
        if settings["ping_merchant"] and settings["mention_id"] != 0:
            await log_channel.send(f"<@{settings["mention_id"]}>\nPurchased item in box 3 from merchant")
        else:
            await log_channel.send(f"Purchased item in box 3 from merchant")
        await asyncio.sleep(2)
    elif item == 4:
        _mouse.position = merch_item_pos_4_purchase
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.position = quantity_btn_pos
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.type("25")
        await asyncio.sleep(0.1)
        _mouse.position = purchase_btn_pos
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        log_channel = client.get_channel(settings["log_channel_id"])
        if settings["ping_merchant"] and settings["mention_id"] != 0:
            await log_channel.send(f"<@{settings["mention_id"]}>\nPurchased item in box 4 from merchant")
        else:
            await log_channel.send(f"Purchased item in box 4 from merchant")
        await asyncio.sleep(2)
    elif item == 5:
        _mouse.position = merch_item_pos_5_purchase
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.position = quantity_btn_pos
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.type("25")
        await asyncio.sleep(0.1)
        _mouse.position = purchase_btn_pos
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        log_channel = client.get_channel(settings["log_channel_id"])
        if settings["ping_merchant"] and settings["mention_id"] != 0:
            await log_channel.send(f"<@{settings["mention_id"]}>\nPurchased item in box 5 from merchant")
        else:
            await log_channel.send(f"Purchased item in box 5 from merchant")
        await asyncio.sleep(2)

@tasks.loop(seconds=577)
async def keep_alive():
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.position = close_pos
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _keyboard.press(Key.space)
    await asyncio.sleep(0.8)
    _keyboard.release(Key.space)

@tasks.loop(seconds=60)
async def auto_craft():
    item_to_craft = ""
    for itm in settings["auto_craft_item"]:
        if settings["auto_craft_item"][itm]:
            item_to_craft = itm
    if item_to_craft == "":
        return
    if item_to_craft == "Heavenly Potion I":
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.press("f")
        await asyncio.sleep(0.1)
        _keyboard.release("f")
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.position = craft_btn_pos
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.position = (hp1_pos_potions[0] - (110 * scale_w), hp1_pos_potions[1])
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.press(Key.ctrl)
        _keyboard.press("a")
        await asyncio.sleep(0.1)
        _keyboard.release("a")
        _keyboard.release(Key.ctrl)
        await asyncio.sleep(0.1)
        _keyboard.type("100")
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.position = hp1_pos_potions
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.press("d")
        await asyncio.sleep(0.1)
        _keyboard.release("d")
        await asyncio.sleep(0.1)
        _mouse.scroll(0, -10)
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.position = hp1_pos_celestial
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.scroll(0, 10)
        await asyncio.sleep(0.1)
    elif item_to_craft == "Heavenly Potion II":
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.press("f")
        await asyncio.sleep(0.1)
        _keyboard.release("f")
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.position = craft_btn_pos
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.position = hp1_pos_potions
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.position = hp2_pos_potions
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.position = (hp2_pos_potions[0] - (110 * scale_w), hp2_pos_potions[1])
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.press(Key.ctrl)
        _keyboard.press("a")
        await asyncio.sleep(0.1)
        _keyboard.release("a")
        _keyboard.release(Key.ctrl)
        await asyncio.sleep(0.1)
        _keyboard.type("125")
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.position = hp2_pos_potions
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.press("d")
        await asyncio.sleep(0.1)
        _keyboard.release("d")
        await asyncio.sleep(0.1)
        _mouse.scroll(0, 10)
        await asyncio.sleep(0.1)
        _mouse.scroll(0, -10)
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.position = hp1_pos_celestial
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.position = craft_btn_pos
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.position = hp1_pos_celestial
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.scroll(0, 10)
    elif item_to_craft == "Warp Potion":
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.press("f")
        await asyncio.sleep(0.1)
        _keyboard.release("f")
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.position = craft_btn_pos
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.position = hp1_pos_potions
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.scroll(0, -30)
        await asyncio.sleep(0.1)
        _mouse.scroll(0, -30)
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.position = (hp1_pos_celestial[0] - (110 * scale_w), hp1_pos_celestial[1])
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.press(Key.ctrl)
        _keyboard.press("a")
        await asyncio.sleep(0.1)
        _keyboard.release("a")
        _keyboard.release(Key.ctrl)
        await asyncio.sleep(0.1)
        _keyboard.type("1000")
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.position = hp1_pos_potions
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _keyboard.press("d")
        await asyncio.sleep(0.1)
        _keyboard.release("d")
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.position = hp1_pos_celestial
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.scroll(0, 30)
        await asyncio.sleep(0.1)
        _mouse.scroll(0, 30)
        await asyncio.sleep(0.1)
    else:
        print("An invalid item has been selected")

@tasks.loop(seconds=0)
async def reset_aura():
    reset_aura.stop()

@reset_aura.after_loop
async def on_reset_aura_cancel():
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.position = aura_button_pos
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.position = search_pos
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _keyboard.type(settings["reset_aura"])
    await asyncio.sleep(0.1)
    _mouse.position = query_pos    
    await asyncio.sleep(0.1)
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.position = equip_pos
    await asyncio.sleep(0.1)
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.position = close_pos
    await asyncio.sleep(0.1)
    _keyboard.press(Key.cmd)
    await asyncio.sleep(0.1)
    _keyboard.release(Key.cmd)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    
@tasks.loop(seconds=150)
async def merchant_detection():
    if settings["log_channel_id"] == 0:
        print("You must select a channel ID, you can do this by running the set_log_channel command.")
        return    
    if aura_detection.is_being_cancelled():
        return
    await use_item("Merchant Teleport", 1, False)
    px = ImageGrab.grab().load()
    colour = px[default_pos[0], default_pos[1]]
    hex_col = rgb2hex(colour[0], colour[1], colour[2])
    colour2 = px[secondary_pos[0], secondary_pos[1]]
    hex_col2 = rgb2hex(colour2[0], colour2[1], colour2[2])
    if (hex_col == "#000000" and hex_col2 == "#000000"):
        rnow = datetime.now()
        _mouse.position = close_pos
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(1)
        _keyboard.press("e")
        await asyncio.sleep(2)
        _keyboard.release("e")
        await asyncio.sleep(5)
        _mouse.position = open_merch_pos
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.5)
        merchimg = pag.screenshot("./scr/screenshot_merchant.png")
        await asyncio.sleep(0.2)
        up = discord.File("./scr/screenshot_merchant.png", filename="merchant.png")
        emb = discord.Embed(
            title = f"Merchant Spawned",
            description = f"A merchant selling the following items in the screenshot has been detected at time: {rnow.strftime("%d/%m/%Y %H:%M:%S")}",
            colour = discord.Color.from_rgb(255, 255, 255)
        )
        emb.set_image(url="attachment://merchant.png")
        log_channel = client.get_channel(settings["log_channel_id"])
        if settings["ping_merchant"] and settings["mention_id"] != 0:
            await log_channel.send(f"<@{settings["mention_id"]}>", embed=emb, file=up)
        else:
            await log_channel.send(embed=emb, file=up)
    else:
        _mouse.position = close_pos
        await asyncio.sleep(0.1)
        _keyboard.press(Key.cmd)
        await asyncio.sleep(0.1)
        _keyboard.release(Key.cmd)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)
        await asyncio.sleep(0.1)
        _mouse.click(Button.left)

@tasks.loop(seconds=0)
async def aura_detection():
    global hex_col, hex_col2, colour, colour2
    if settings["log_channel_id"] == 0:
        print("You must select a channel ID, you can do this by running the set_log_channel command.")
        return    
    px = ImageGrab.grab().load()
    colour = px[default_pos[0], default_pos[1]]
    hex_col = rgb2hex(colour[0], colour[1], colour[2])
    colour2 = px[secondary_pos[0], secondary_pos[1]]
    hex_col2 = rgb2hex(colour2[0], colour2[1], colour2[2])
    try:
        check = auras[f"{hex_col},{hex_col2}"]
        aura_detection.stop()
    except KeyError:
        for k in auras.keys():
            _ = list(k.split(","))
            if _[0] == hex_col and _[1] == "#******":
                hex_col2 = "#******"
                aura_detection.stop()
    except Exception as e:
        print(e)

@aura_detection.after_loop
async def on_aura_detection_cancel():
    global hex_col, hex_col2, colour, colour2
    try:
        rnow = datetime.now()
        if int(auras[f"{hex_col},{hex_col2}"]["rarity"]) > int(settings["minimum_roll"]):
            if hex_col == "#5bffb0": # overdrive detector
                await asyncio.sleep(5)
                px = ImageGrab.grab().load()
                colour = px[default_pos[0], default_pos[1]]
                hex_col = rgb2hex(colour[0], colour[1], colour[2])
                if hex_col == "#d31e21":
                    hex_col2 = "#******"
                    auraimg = pag.screenshot("./scr/screenshot_aura.png")
                    await asyncio.sleep(1)
                    up = discord.File("./scr/screenshot_aura.png", filename="aura.png")
                    emb = discord.Embed(
                        title = f"Aura Rolled: {auras[f"{hex_col},{hex_col2}"]["name"]}",
                        description = f"Rolled Aura: {auras[f"{hex_col},{hex_col2}"]["name"]}\nWith chances of 1/{auras[f"{hex_col},{hex_col2}"]["rarity"]}\nAt time: {rnow.strftime("%d/%m/%Y %H:%M:%S")}\nDetected Colours: {hex_col}, {hex_col2}",
                        colour = discord.Color.from_rgb(colour[0], colour[1], colour[2])
                    )
                    emb.set_image(url="attachment://aura.png")
                    log_channel = client.get_channel(settings["log_channel_id"])
                    if settings["mention"] and settings["mention_id"] != 0 and (int(auras[f"{hex_col},{hex_col2}"]["rarity"]) > int(settings["minimum_ping"])):
                        await log_channel.send(f"<@{settings["mention_id"]}>", embed=emb, file=up)
                    else:
                        await log_channel.send(embed=emb, file=up)
                    print(f"Rolled Aura: {auras[f"{hex_col},{hex_col2}"]["name"]}\nWith chances of 1/{auras[f"{hex_col},{hex_col2}"]["rarity"]}\nAt time: {rnow.strftime("%d/%m/%Y %H:%M:%S")}\nDetected Colours: {hex_col}, {hex_col2}")
                else:
                    hex_col == "#5bffb0"
                    hex_col2 = "#050e09"
                    auraimg = pag.screenshot("./scr/screenshot_aura.png")
                    await asyncio.sleep(1)
                    up = discord.File("./scr/screenshot_aura.png", filename="aura.png")
                    emb = discord.Embed(
                            title = f"Aura Rolled: {auras[f"{hex_col},{hex_col2}"]["name"]}",
                            description = f"Rolled Aura: {auras[f"{hex_col},{hex_col2}"]["name"]}\nWith chances of 1/{auras[f"{hex_col},{hex_col2}"]["rarity"]}\nAt time: {rnow.strftime("%d/%m/%Y %H:%M:%S")}\nDetected Colour: {hex_col}",
                            colour = discord.Color.from_rgb(colour[0], colour[1], colour[2])
                    )
                    emb.set_image(url="attachment://aura.png")
                    log_channel = client.get_channel(settings["log_channel_id"])
                    if settings["mention"] and settings["mention_id"] != 0 and (int(auras[f"{hex_col},{hex_col2}"]["rarity"]) > int(settings["minimum_ping"])):
                        await log_channel.send(f"<@{settings["mention_id"]}>", embed=emb, file=up)
                    else:
                        await log_channel.send(embed=emb, file=up)
                    print(f"Rolled Aura: {auras[f"{hex_col},{hex_col2}"]["name"]}\nWith chances of 1/{auras[f"{hex_col},{hex_col2}"]["rarity"]}\nAt time: {rnow.strftime("%d/%m/%Y %H:%M:%S")}\nDetected Colour: {hex_col}")
            elif hex_col == "#3c66ff": # history detector
                await asyncio.sleep(1)
                auraimg = pag.screenshot("./scr/screenshot_aura.png")
                await asyncio.sleep(8)
                px = ImageGrab.grab().load()
                colour = px[default_pos[0], default_pos[1]]
                hex_col = rgb2hex(colour[0], colour[1], colour[2])
                if hex_col == "#59ff96":
                    hex_col2 = "#******"
                    auraimg = pag.screenshot("./scr/screenshot_aura.png")
                    await asyncio.sleep(1)
                    up = discord.File("./scr/screenshot_aura.png", filename="aura.png")
                    emb = discord.Embed(
                            title = f"Aura Rolled: {auras[f"{hex_col},{hex_col2}"]["name"]}",
                            description = f"Rolled Aura: {auras[f"{hex_col},{hex_col2}"]["name"]}\nWith chances of 1/{auras[f"{hex_col},{hex_col2}"]["rarity"]}\nAt time: {rnow.strftime("%d/%m/%Y %H:%M:%S")}\nDetected Colour: {hex_col}",
                            colour = discord.Color.from_rgb(colour[0], colour[1], colour[2])
                    )
                    emb.set_image(url="attachment://aura.png")
                    log_channel = client.get_channel(settings["log_channel_id"])
                    if settings["mention"] and settings["mention_id"] != 0 and (int(auras[f"{hex_col},{hex_col2}"]["rarity"]) > int(settings["minimum_ping"])):
                        await log_channel.send(f"<@{settings["mention_id"]}>", embed=emb, file=up)
                    else:
                        await log_channel.send(embed=emb, file=up)
                    print(f"Rolled Aura: {auras[f"{hex_col},{hex_col2}"]["name"]}\nWith chances of 1/{auras[f"{hex_col},{hex_col2}"]["rarity"]}\nAt time: {rnow.strftime("%d/%m/%Y %H:%M:%S")}\nDetected Colour: {hex_col}")
                else:
                    hex_col = "#3c66ff"
                    hex_col2 = "#******"
                    up = discord.File("./scr/screenshot_aura.png", filename="aura.png")
                    emb = discord.Embed(
                            title = f"Aura Rolled: {auras[f"{hex_col},{hex_col2}"]["name"]}",
                            description = f"Rolled Aura: {auras[f"{hex_col},{hex_col2}"]["name"]}\nWith chances of 1/{auras[f"{hex_col},{hex_col2}"]["rarity"]}\nAt time: {rnow.strftime("%d/%m/%Y %H:%M:%S")}\nDetected Colour: {hex_col}",
                            colour = discord.Color.from_rgb(colour[0], colour[1], colour[2])
                    )
                    emb.set_image(url="attachment://aura.png")
                    log_channel = client.get_channel(settings["log_channel_id"])
                    if settings["mention"] and settings["mention_id"] != 0 and (int(auras[f"{hex_col},{hex_col2}"]["rarity"]) > int(settings["minimum_ping"])):
                        await log_channel.send(f"<@{settings["mention_id"]}>", embed=emb, file=up)
                    else:
                        await log_channel.send(embed=emb, file=up)
                    print(f"Rolled Aura: {auras[f"{hex_col},{hex_col2}"]["name"]}\nWith chances of 1/{auras[f"{hex_col},{hex_col2}"]["rarity"]}\nAt time: {rnow.strftime("%d/%m/%Y %H:%M:%S")}\nDetected Colour: {hex_col}")
            elif hex_col2 == "#******":
                auraimg = pag.screenshot("./scr/screenshot_aura.png")
                await asyncio.sleep(1)
                up = discord.File("./scr/screenshot_aura.png", filename="aura.png")
                emb = discord.Embed(
                        title = f"Aura Rolled: {auras[f"{hex_col},{hex_col2}"]["name"]}",
                        description = f"Rolled Aura: {auras[f"{hex_col},{hex_col2}"]["name"]}\nWith chances of 1/{auras[f"{hex_col},{hex_col2}"]["rarity"]}\nAt time: {rnow.strftime("%d/%m/%Y %H:%M:%S")}\nDetected Colour: {hex_col}",
                        colour = discord.Color.from_rgb(colour[0], colour[1], colour[2])
                )
                emb.set_image(url="attachment://aura.png")
                log_channel = client.get_channel(settings["log_channel_id"])
                if settings["mention"] and settings["mention_id"] != 0 and (int(auras[f"{hex_col},{hex_col2}"]["rarity"]) > int(settings["minimum_ping"])):
                    await log_channel.send(f"<@{settings["mention_id"]}>", embed=emb, file=up)
                else:
                    await log_channel.send(embed=emb, file=up)
                print(f"Rolled Aura: {auras[f"{hex_col},{hex_col2}"]["name"]}\nWith chances of 1/{auras[f"{hex_col},{hex_col2}"]["rarity"]}\nAt time: {rnow.strftime("%d/%m/%Y %H:%M:%S")}\nDetected Colour: {hex_col}")
            else:
                auraimg = pag.screenshot("./scr/screenshot_aura.png")
                await asyncio.sleep(1)
                up = discord.File("./scr/screenshot_aura.png", filename="aura.png")
                emb = discord.Embed(
                    title = f"Aura Rolled: {auras[f"{hex_col},{hex_col2}"]["name"]}",
                    description = f"Rolled Aura: {auras[f"{hex_col},{hex_col2}"]["name"]}\nWith chances of 1/{auras[f"{hex_col},{hex_col2}"]["rarity"]}\nAt time: {rnow.strftime("%d/%m/%Y %H:%M:%S")}\nDetected Colours: {hex_col}, {hex_col2}",
                    colour = discord.Color.from_rgb(colour[0], colour[1], colour[2])
                )
                emb.set_image(url="attachment://aura.png")
                log_channel = client.get_channel(settings["log_channel_id"])
                if settings["mention"] and settings["mention_id"] != 0 and (int(auras[f"{hex_col},{hex_col2}"]["rarity"]) > int(settings["minimum_ping"])):
                    await log_channel.send(f"<@{settings["mention_id"]}>", embed=emb, file=up)
                else:
                    await log_channel.send(embed=emb, file=up)
                print(f"Rolled Aura: {auras[f"{hex_col},{hex_col2}"]["name"]}\nWith chances of 1/{auras[f"{hex_col},{hex_col2}"]["rarity"]}\nAt time: {rnow.strftime("%d/%m/%Y %H:%M:%S")}\nDetected Colours: {hex_col}, {hex_col2}")
        else:
            print(f"Rolled Aura: {auras[f"{hex_col},{hex_col2}"]["name"]}\nWith chances of 1/{auras[f"{hex_col},{hex_col2}"]["rarity"]}\nAt time: {rnow.strftime("%d/%m/%Y %H:%M:%S")}\nDetected Colours: {hex_col}, {hex_col2}")
        if int(auras[f"{hex_col},{hex_col2}"]["rarity"]) >= 1000000 and int(auras[f"{hex_col},{hex_col2}"]["rarity"]) <= 99999998:
            await asyncio.sleep(8)
        elif int(auras[f"{hex_col},{hex_col2}"]["rarity"]) >= 99999 and int(auras[f"{hex_col},{hex_col2}"]["rarity"]) <= 999999:
            await asyncio.sleep(10)
        elif int(auras[f"{hex_col},{hex_col2}"]["rarity"]) >= 9999999:
            await asyncio.sleep(10)
        if settings["reset_aura"] != "":
            reset_aura.start()
    except Exception as e:
        print(e)
    finally:
        aura_detection.restart()

@client.command()
async def plugins(ctx):
    await ctx.send("Installed Plugins:")
    for plu in _plugins:
        await ctx.send(plu)

for filename in os.listdir("./plugins"):
    if filename.endswith(".py"):
        client.load_extension(f"plugins.{filename[:-3]}")
        print(f"Loaded plugin: {filename[:-3]}")
        _plugins.append(filename[:-3])

client.run(settings["TOKEN"])
