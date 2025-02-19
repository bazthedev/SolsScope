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

def get_auras():
    print("Downloading Aura List")
    dl = requests.get("https://raw.githubusercontent.com/bazthedev/SolsRNGBot/main/auras.json")
    f = open("auras.json", "wb")
    f.write(dl.content)
    f.close()
    print("Downloaded Aura List")

def update_settings(settings, ssnorm : bool, ssstor : bool, ssinv : bool, log_channel_id : int):
    settings["ssnorm"] = ssnorm
    settings["ssstor"] = ssstor
    settings["ssinv"] = ssinv
    settings["log_channel_id"] = log_channel_id
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)

def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def reload_settings():
    global settings, scr_norm, scr_stor, scr_inv, log_channel_id
    with open("settings.json", "r") as f:
        settings = json.load(f)
    scr_norm = settings["ssnorm"]
    scr_stor = settings["ssstor"]
    scr_inv = settings["ssinv"]
    log_channel_id = settings["log_channel_id"]
    print(settings)

if not os.path.exists("./scr/"):
    os.mkdir("./scr/")

if not os.path.exists("./plugins/"):
    os.mkdir("./plugins/")
    os.mkdir("./plugins/config/")

if not os.path.exists("./logs/"):
    os.mkdir("./logs/")

if not os.path.exists("./settings.json"):
    x = open("settings.json", "w")
    x.write('{"TOKEN": "", "__version__" : "1.0.4", "ssnorm" : true, "ssstor" : true, "ssinv" : true, "log_channel_id": 0, "cd" : "' + str(os.getcwd()).replace("\\", "\\\\") + '", "skip_dl": false, "mention" : true, "mention_id" : 0}')
    x.close()

now = datetime.now()
client = commands.Bot(commands.when_mentioned, case_insensitive=True)
_mouse = mouse.Controller()
_keyboard = keyboard.Controller()
aura_button_pos = (53, 538) # change this to the position of your Aura Storage button
inv_button_pos = (67, 732) # change this to the position of your Inventory button
default_pos = (1280, 720) # change this to the position of your mouse after shiftlocking and unshiftlocking
resting_pos = (-942, 604) # change this to a position outside of the game window
close_pos = (1887, 399) # change this to the position of the X after you open aura or inventory menu
# These values can be obtained by using the get_mouse_pos.py script, and moving your mouse over the buttons.
secondary_pos = (564, 401) # You should probably keep these values the same, as adjusting them will break the auras.json file which uses these specific positions to detect colours
tertiary_pos = (2049, 1118) # You should probably keep these values the same, as adjusting them will break the auras.json file which uses these specific positions to detect colours
_plugins = []
local_version = "1.0.4"
reload_settings()

if settings["__version__"] < local_version:
    settings["__version__"] = local_version
    update_settings(settings, scr_norm, scr_stor, scr_inv, log_channel_id)
    reload_settings()

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
    print("Started keep alive")
    await asyncio.sleep(15)
    if log_channel_id != 0:
        log_channel = client.get_channel(log_channel_id)
        emb = discord.Embed(
            title="Bot has started",
            description=f"Started at {now.strftime("%d/%m/%Y %H:%M:%S")}"
        )
        await log_channel.send(embed=emb)
        if settings["ssnorm"] or settings["ssstor"] or settings["ssinv"]:
            await asyncio.sleep(40)
        aura_detection.start()
        print("Started Aura Detection")
    else:
        print("You must select a channel ID, you can do this by running the set_log_channel command.")
    

@client.event
async def on_command_error(ctx, error):
    print(str(error))

@client.command()
@commands.is_owner()
async def set_log_channel(ctx):
    await ctx.send("Updating log channel...")
    global scr_norm, scr_inv, scr_stor, log_channel_id
    new_log_channel_id = ctx.message.channel.id
    update_settings(settings, scr_norm, scr_stor, scr_inv, new_log_channel_id)
    reload_settings()
    await ctx.send(f"Log Channel set to {ctx.message.channel.mention}")
@client.command()
@commands.is_owner()
async def set_mention(ctx):
    await ctx.send("Updating user to mention...")
    global scr_norm, scr_inv, scr_stor, log_channel_id
    settings["mention_id"] = ctx.author.id
    update_settings(settings, scr_norm, scr_stor, scr_inv, log_channel_id)
    reload_settings()
    await ctx.send(f"User to mention is now {ctx.author.mention}")

@client.command()
@commands.is_owner()
async def stop(ctx):
    await ctx.send("Manual stop initiated")
    aura_detection.stop()
    keep_alive.stop()
    await ctx.bot.logout()
    print("Aw dang it")

@client.command()
@commands.is_owner()
async def manual_scr(ctx):
    await ctx.send("Taking screenshots, please wait, this will take about 30 seconds.")
    if settings["ssnorm"]:
        _mouse.position = resting_pos
        await asyncio.sleep(1)
        _mouse.click(Button.left)
        await asyncio.sleep(1)
        _mouse.position = close_pos
        await asyncio.sleep(1)
        _mouse.click(Button.left)
        await asyncio.sleep(1)
        _mouse.position = close_pos
        if os.path.exists("./scr/screenshot_normal.png"):
            os.remove("./scr/screenshot_normal.png")
        normimg = pag.screenshot("./scr/screenshot_normal.png")
        await ctx.send(file=discord.File("./scr/screenshot_normal.png"))
    if settings["ssstor"]:
        _mouse.position = resting_pos
        await asyncio.sleep(1)
        _mouse.click(Button.left)
        await asyncio.sleep(2)
        _mouse.position = aura_button_pos
        await asyncio.sleep(1)
        _mouse.click(Button.left)
        await asyncio.sleep(1)
        _mouse.click(Button.left)
        await asyncio.sleep(1)
        if os.path.exists("./scr/screenshot_storage.png"):
            os.remove("./scr/screenshot_storage.png")
            await asyncio.sleep(1)
        storimg = pag.screenshot("./scr/screenshot_storage.png")
        await asyncio.sleep(1)
        _mouse.click(Button.left)
        _mouse.position = close_pos
        await ctx.send(file=discord.File("./scr/screenshot_storage.png"))
    if settings["ssinv"]:
        _mouse.position = resting_pos
        await asyncio.sleep(1)
        _mouse.click(Button.left)
        await asyncio.sleep(2)
        _mouse.position = inv_button_pos
        await asyncio.sleep(1)
        _mouse.click(Button.left)
        await asyncio.sleep(1)
        _mouse.click(Button.left)
        await asyncio.sleep(1)
        if os.path.exists("./scr/screenshot_inventory.png"):
            os.remove("./scr/screenshot_inventory.png")
            await asyncio.sleep(1)
        storimg = pag.screenshot("./scr/screenshot_inventory.png")
        await asyncio.sleep(1)
        _mouse.click(Button.left)
        _mouse.position = close_pos
        await ctx.send(file=discord.File("./scr/screenshot_inventory.png"))

@tasks.loop(seconds=577)
async def keep_alive():
    _mouse.position = resting_pos
    await asyncio.sleep(1)
    _mouse.click(Button.left)
    await asyncio.sleep(1)
    _mouse.position = close_pos
    await asyncio.sleep(1)
    _mouse.click(Button.left)
    await asyncio.sleep(1)
    _mouse.click(Button.left)
    await asyncio.sleep(1)
    _keyboard.press(Key.space)
    await asyncio.sleep(1)
    _keyboard.release(Key.space)

@tasks.loop(seconds=0)
async def aura_detection():
    if log_channel_id == 0:
        print("You must select a channel ID, you can do this by running the set_log_channel command.")
        return    
    px = ImageGrab.grab().load()
    colour = px[default_pos[0], default_pos[1]]
    hex_col = rgb2hex(colour[0], colour[1], colour[2])
    colour2 = px[secondary_pos[0], secondary_pos[1]]
    hex_col2 = rgb2hex(colour2[0], colour2[1], colour2[2])
    colour3 = px[tertiary_pos[0], tertiary_pos[1]]
    hex_col3 = rgb2hex(colour3[0], colour3[1], colour3[2])
    try:
        check = auras[f"{hex_col},{hex_col2},{hex_col3}"]
        aura_detection.stop()
    except KeyError:
        pass
    except Exception as e:
        print(e)

@client.command()
async def plugins(ctx):
    await ctx.send("Installed Plugins:")
    for plu in _plugins:
        await ctx.send(plu)

@aura_detection.after_loop
async def on_aura_detection_cancel():
    try:
        rnow = datetime.now()
        px = ImageGrab.grab().load()
        colour = px[default_pos[0], default_pos[1]]
        hex_col = rgb2hex(colour[0], colour[1], colour[2])
        colour2 = px[secondary_pos[0], secondary_pos[1]]
        hex_col2 = rgb2hex(colour2[0], colour2[1], colour2[2])
        colour3 = px[tertiary_pos[0], tertiary_pos[1]]
        hex_col3 = rgb2hex(colour3[0], colour3[1], colour3[2])
        await asyncio.sleep(1)
        auraimg = pag.screenshot("./scr/screenshot_aura.png")
        await asyncio.sleep(1)
        up = discord.File("./scr/screenshot_aura.png", filename="aura.png")
        emb = discord.Embed(
                title = f"Aura Rolled: {auras[f"{hex_col},{hex_col2},{hex_col3}"]["name"]}",
                description = f"Rolled Aura: {auras[f"{hex_col},{hex_col2},{hex_col3}"]["name"]}\nWith chances of 1/{auras[f"{hex_col},{hex_col2},{hex_col3}"]["rarity"]}\nAt time: {rnow.strftime("%d/%m/%Y %H:%M:%S")}\nDetected Colours: {hex_col}, {hex_col2}, {hex_col3}",
                colour = discord.Color.from_rgb(colour[0], colour[1], colour[2])
        )
        emb.set_image(url="attachment://aura.png")
        log_channel = client.get_channel(log_channel_id)
        if settings["mention"] and settings["mention_id"] != 0:
            await log_channel.send(f"<@{settings["mention_id"]}>", embed=emb, file=up)
        else:
            await log_channel.send(embed=emb, file=up)
        print(f"Rolled Aura: {auras[f"{hex_col},{hex_col2},{hex_col3}"]["name"]}\nWith chances of 1/{auras[f"{hex_col},{hex_col2},{hex_col3}"]["rarity"]}\nAt time: {rnow.strftime("%d/%m/%Y %H:%M:%S")}\nDetected Colours: {hex_col}, {hex_col2}, {hex_col3}")
        await asyncio.sleep(10)
    except Exception as e:
        print(e)
    finally:
        aura_detection.restart()

for filename in os.listdir("./plugins"):
    if filename.endswith(".py"):
        client.load_extension(f"plugins.{filename[:-3]}")
        print(f"Loaded plugin: {filename[:-3]}")
        _plugins.append(filename[:-3])

client.run(settings["TOKEN"])
