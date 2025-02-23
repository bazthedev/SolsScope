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
    print(settings)

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

if not os.path.exists("./scr/"):
    os.mkdir("./scr/")

if not os.path.exists("./plugins/"):
    os.mkdir("./plugins/")
    os.mkdir("./plugins/config/")

if not os.path.exists("./logs/"):
    os.mkdir("./logs/")

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
items_pos = ((1702 * scale_w), (446 * scale_h))
purchase_btn_pos = ((918 * scale_w), (852 * scale_h))
quantity_btn_pos = ((906 * scale_w), (796 * scale_h))
open_merch_pos = ((876 * scale_w), (1256 * scale_h))
_plugins = []
local_version = "1.1.0"
default_settings = {"TOKEN": "", "__version__" :  local_version, "log_channel_id": 0, "cd" : str(os.getcwd()), "skip_dl": False, "mention" : True, "mention_id" : 0, "minimum_roll" : "99998", "minimum_ping" : "349999", "reset_aura" : "Glock", "merchant_detection" : True, "ping_merchant" : True}

if not os.path.exists("./settings.json"):
    x = open("settings.json", "w")
    x.write('{}')
    x.close()
    with open("settings.json", "w") as f:
        json.dump(default_settings, f, indent=4)

valid_settings_keys = ["TOKEN", "__version__", "log_channel_id", "cd", "skip_dl", "mention", "mention_id", "minimum_roll", "minimum_ping", "reset_aura", "merchant_detection", "ping_merchant"]

reload_settings()

if settings["__version__"] < local_version:
    settings["__version__"] = local_version
    update_settings(settings)
    reload_settings()

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
    print(f"Started at {now.strftime("%d/%m/%Y %H:%M:%S")} running version {__version__}")
    await client.change_presence(activity=discord.Game(name=f"bazthedev/SolsRNGBot version {__version__}"))
    keep_alive.start()
    print("Started Autokick Prevention")
    await asyncio.sleep(3)
    if settings["log_channel_id"] != 0:
        log_channel = client.get_channel(settings["log_channel_id"])
        emb = discord.Embed(
            title="Bot has started",
            description=f"Started at {now.strftime("%d/%m/%Y %H:%M:%S")}"
        )
        await log_channel.send(embed=emb)
        aura_detection.start()
        print("Started Aura Detection")
        if settings["merchant_detection"]:
            merchant_detection.start()
            print("Started Merchant Detection")
    else:
        print("You must select a channel ID, you can do this by running the set_log_channel command.")
    
    

@client.event
async def on_command_error(ctx, error):
    print(str(error))

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
    if os.path.exists("./scr/screenshot_storage.png"):
        os.remove("./scr/screenshot_storage.png")
        await asyncio.sleep(1)
    storimg = pag.screenshot("./scr/screenshot_storage.png")
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    _mouse.position = close_pos
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
    if os.path.exists("./scr/screenshot_inventory.png"):
        os.remove("./scr/screenshot_inventory.png")
        await asyncio.sleep(1)
    storimg = pag.screenshot("./scr/screenshot_inventory.png")
    await asyncio.sleep(0.1)
    _mouse.click(Button.left)
    _mouse.position = close_pos
    await ctx.send(file=discord.File("./scr/screenshot_inventory.png"))

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
    _keyboard.type("Merchant Teleport")
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
    px = ImageGrab.grab().load()
    colour = px[default_pos[0], default_pos[1]]
    hex_col = rgb2hex(colour[0], colour[1], colour[2])
    colour2 = px[secondary_pos[0], secondary_pos[1]]
    hex_col2 = rgb2hex(colour2[0], colour2[1], colour2[2])
    if hex_col == "#000000" and hex_col2 == "#000000":
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
                await asyncio.sleep(10)
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
