import discord
from discord.ext import commands
import json
import os
import asyncio
import pyautogui as pag
import time


MACROPATH = os.path.expandvars(r"%localappdata%\\Baz's Macro") # Windows Roaming Path

with open(f"{MACROPATH}/settings.json", "r") as f:
    settings = json.load(f)

class Remote(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.name = type(self).__name__
        self.cfname = f"{self.name.lower()}.json"
        if not os.path.exists(f"{MACROPATH}/plugins/config/{self.cfname}"):
            x = open(f"{MACROPATH}/plugins/config/{self.cfname}", "w")
            x.write('{"__version__" : "1.0.1", "author" : "bazthedev"}')
            x.close()
        with open(f"{MACROPATH}/plugins/config/{self.cfname}", "r") as c:
            self.config = json.load(c)

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx, _time : int):
        t = round(time.time())
        t_z = t + _time
        await ctx.send(f"Shutting down at <t:{t_z}>")
        os.system(f"shutdown /s /t {str(_time)}")

    @commands.command()
    @commands.is_owner()
    async def cancel(self, ctx):
        await ctx.send("Cancelling shutdown")
        os.system("shutdown /a")

    @commands.command()
    @commands.is_owner()
    async def scr(self, ctx):
        if os.path.exists("{MACROPATH}/scr/screenshot.png"):
            os.remove("{MACROPATH}/scr/screenshot.png")
            await asyncio.sleep(0.2)
        img = pag.screenshot("{MACROPATH}/scr/screenshot.png", allScreens=True)
        await ctx.send(file=discord.File("{MACROPATH}/scr/screenshot.png"))

def setup(client):
    client.add_cog(Remote(client))
