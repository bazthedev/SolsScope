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
    dl = requests.get("https://github.com/bazthedev/SolsRNGBot/raw/refs/heads/main/auras.json")
    f = open("auras.json", "wb")
    f.write(dl.content)
    f.close()
    print("Downloaded Aura List")

def update_settings(settings, timer : int, ssnorm : bool, ssstor : bool, ssinv : bool, log_channel_id : int):
    settings["timer"] = timer
    settings["ssnorm"] = ssnorm
    settings["ssstor"] = ssstor
    settings["ssinv"] = ssinv
    settings["log_channel_id"] = log_channel_id
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)

async def reset_mouse_pos():
    _keyboard.press(Key.shift_l)
    _keyboard.release(Key.shift_l)
    await asyncio.sleep(1)
    _keyboard.press(Key.shift_l)
    _keyboard.release(Key.shift_l)
    await asyncio.sleep(2)
    _mouse.position = default_pos

if not os.path.exists("./scr/"):
    os.mkdir("./scr/")

if not os.path.exists("./plugins/"):
    os.mkdir("./plugins/")

if not os.path.exists("./settings.json"):
    x = open("settings.json", "w")
    x.write('{"TOKEN": "", "__version__" : "1.0.1", "timer" : 1800, "ssnorm" : true, "ssstor" : true, "ssinv" : true, "log_channel_id": 0}')
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
_plugins = []


def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def reload_settings():
    global settings, wait_time, scr_norm, scr_stor, scr_inv, log_channel_id
    with open("settings.json", "r") as f:
        settings = json.load(f)
    wait_time = settings["timer"]
    scr_norm = settings["ssnorm"]
    scr_stor = settings["ssstor"]
    scr_inv = settings["ssinv"]
    log_channel_id = settings["log_channel_id"]
    print(settings)

reload_settings()
if settings["TOKEN"] == "":
    exit("You need to add your bot token in the settings.json file")
get_auras()

with open("auras.json", "r") as f:
    auras = json.load(f)

__version__ = settings["__version__"]
@client.event
async def on_ready():
    print("Let's go gambling!")
    print(f"Started at {now.strftime("%d/%m/%Y %H:%M:%S")} running version {__version__}")
    await client.change_presence(activity=discord.Game(name=f"bazthedev/SolsRNGBot version {__version__}"))
    if log_channel_id != 0:
        log_channel = client.get_channel(log_channel_id)
        emb = discord.Embed(
            title="Bot has started",
            description=f"Started at {now.strftime("%d/%m/%Y %H:%M:%S")}"
        )
        await log_channel.send(embed=emb)
        if settings["ssnorm"] or settings["ssstor"] or settings["ssinv"]:
            get_screenshots.start()
            print("Started screenshots")
        aura_detection.start()
        print("Started Aura Detection")
    else:
        print("You must select a channel ID, you can do this by running the set_log_channel command.")
    await asyncio.sleep(60)
    keep_alive.start()
    print("Started keep alive")

@client.command()
@commands.is_owner()
async def update_timer(ctx, new_time : int):
    global wait_time, scr_norm, scr_inv, scr_stor, log_channel_id
    if new_time != wait_time:
        update_settings(settings, new_time, scr_norm, scr_stor, scr_inv, log_channel_id)
        reload_settings()
        await ctx.send("Wait duration has been updated.")
    else:
        await ctx.send("Wait duration has not been updated.")

@client.command()
@commands.is_owner()
async def set_log_channel(ctx):
    await ctx.send("Updating log channel...")
    global wait_time, scr_norm, scr_inv, scr_stor, log_channel_id
    new_log_channel_id = ctx.message.channel.id
    update_settings(settings, wait_time, scr_norm, scr_stor, scr_inv, new_log_channel_id)
    reload_settings()
    await ctx.send(f"Log Channel set to {ctx.message.channel.mention}")

@client.command()
@commands.is_owner()
async def stop(ctx):
    await ctx.send("Manual stop initiated")
    get_screenshots.stop()
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
        await reset_mouse_pos()
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
        await reset_mouse_pos()
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
        await reset_mouse_pos()
        await ctx.send(file=discord.File("./scr/screenshot_inventory.png"))

@tasks.loop(seconds=wait_time)
async def get_screenshots():
    if log_channel_id == 0:
        print("You must select a channel ID, you can do this by running the set_log_channel command.")
        return
    log_channel = client.get_channel(log_channel_id)
    await log_channel.send("Taking screenshots, please wait, this will take about 30 seconds")
    if settings["ssnorm"]:
        _mouse.position = resting_pos
        await asyncio.sleep(1)
        _mouse.click(Button.left)
        await asyncio.sleep(1)
        _mouse.position = close_pos
        await asyncio.sleep(1)
        _mouse.click(Button.left)
        await asyncio.sleep(1)
        await reset_mouse_pos()
        if os.path.exists("./scr/screenshot_normal.png"):
            os.remove("./scr/screenshot_normal.png")
        normimg = pag.screenshot("./scr/screenshot_normal.png")
        await log_channel.send(file=discord.File("./scr/screenshot_normal.png"))
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
        await reset_mouse_pos()
        await log_channel.send(file=discord.File("./scr/screenshot_storage.png"))
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
        await reset_mouse_pos()
        await log_channel.send(file=discord.File("./scr/screenshot_inventory.png"))

@tasks.loop(seconds=577)
async def keep_alive():
    _mouse.position = resting_pos
    await asyncio.sleep(1)
    _mouse.click(Button.left)
    await asyncio.sleep(1)
    _mouse.position = default_pos
    await asyncio.sleep(1)
    _mouse.click(Button.left)
    await asyncio.sleep(1)
    _mouse.click(Button.left)
    await asyncio.sleep(1)
    _keyboard.press(Key.space)
    await asyncio.sleep(1)
    _keyboard.release(Key.space)

@client.command()
async def shutdown(ctx):
    await ctx.send("Shutting down in 1 minute")
    os.system("shutdown /s /t 60")

@client.command()
async def s(ctx):
    await ctx.send("Shutting down now")
    os.system("shutdown /s /t 0")

@client.command()
async def cancel(ctx):
    await ctx.send("Cancelling shutdown")
    os.system("shutdown /a")

@client.command()
@commands.is_owner()
async def scr(ctx):
    if os.path.exists("./scr/screenshot.png"):
        os.remove("./scr/screenshot.png")
        await asyncio.sleep(1)
    img = pag.screenshot("./scr/screenshot.png", allScreens=True)
    await ctx.send(file=discord.File("./scr/screenshot.png"))

@tasks.loop(seconds=0)
async def aura_detection():
    if log_channel_id == 0:
        print("You must select a channel ID, you can do this by running the set_log_channel command.")
        return    
    px = ImageGrab.grab().load()
    colour = px[default_pos[0], default_pos[1]]
    hex_col = rgb2hex(colour[0], colour[1], colour[2])
    try:
        check = auras[hex_col]
        aura_detection.stop()
    except KeyError:
        pass

@client.command()
async def plugins(ctx):
    await ctx.send("Installed Plugins:")
    for plu in _plugins:
        await ctx.send(plu)
    

@aura_detection.after_loop
async def on_aura_detection_cancel():
        rnow = datetime.now()
        px = ImageGrab.grab().load()
        colour = px[default_pos[0], default_pos[1]]
        hex_col = rgb2hex(colour[0], colour[1], colour[2])
        if os.path.exists("./scr/screenshot_aura.png"):
            os.remove("./scr/screenshot_aura.png")
            await asyncio.sleep(1)
        auraimg = pag.screenshot("./scr/screenshot_aura.png")
        up = discord.File("./scr/screenshot_aura.png", filename="aura.png")
        emb = discord.Embed(
            title = f"Aura Rolled: {auras[hex_col]["name"]}",
            description = f"Rolled Aura: {auras[hex_col]["name"]}\nWith chances of 1/{auras[hex_col]["rarity"]}\nAt time: {rnow.strftime("%d/%m/%Y %H:%M:%S")}\nDetected Colour: {hex_col}",
            colour = discord.Color.from_rgb(colour[0], colour[1], colour[2])
        )
        emb.set_image(url="attachment://aura.png")
        log_channel = client.get_channel(log_channel_id)
        await log_channel.send(embed=emb, file=up)
        await asyncio.sleep(10)
        aura_detection.restart()


for filename in os.listdir("./plugins"):
    if filename.endswith(".py"):
        client.load_extension(f"plugins.{filename[:-3]}")
        print(f"Loaded plugin: {filename[:-3]}")
        _plugins.append(filename[:-3])

client.run(settings["TOKEN"])
