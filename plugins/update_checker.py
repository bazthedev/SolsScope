import discord
from discord.ext import commands, tasks
import json
import os
import requests
from colorama import Fore

with open("settings.json", "r") as f:
    settings = json.load(f)

class UpdateChecker(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.name = type(self).__name__
        self.cfname = f"{self.name.lower()}.json"
        if not os.path.exists(f"./plugins/config/{self.cfname}"):
            x = open(f"./plugins/config/{self.cfname}", "w")
            x.write('{"__version__" : "1.0.2", "auto_check" : false, "latest_ver_msg" : true}')
            x.close()
        with open(f"./plugins/config/{self.cfname}", "r") as c:
            self.config = json.load(c)
        cver = settings["__version__"]
        new_ver = requests.get(f"https://api.github.com/repos/bazthedev/SolsRNGBot/releases/latest")
        new_ver_str = new_ver.json()["name"]

        if cver < new_ver_str:
            print(Fore.GREEN + f"[!] A new version has been found ({new_ver_str}), please visit https://github.com/bazthedev/SolsRNGBot/releases/latest to download the newest version." + Fore.RESET)
        else:
            if self.config["latest_ver_msg"]:
                print(Fore.GREEN + f"[*] You are running the latest version." + Fore.RESET)
        if self.config["auto_check"]:
            self.check_update_task.start()
            
    @tasks.loop(seconds=3600)
    async def check_update_task(self):
        if self.config["auto_check"]:
            cver = settings["__version__"]
            new_ver = requests.get(f"https://api.github.com/repos/bazthedev/SolsRNGBot/releases/latest")
            new_ver_str = new_ver.json()["name"]
            if cver < new_ver_str:
                print(Fore.GREEN + f"[!] A new version has been found ({new_ver_str}), please visit https://github.com/bazthedev/SolsRNGBot/releases/latest to download the newest version." + Fore.RESET)
            else:
                if self.config["latest_ver_msg"]:
                    print(Fore.GREEN + f"[*] You are running the latest version." + Fore.RESET)

    @commands.command()
    async def check_update(self, ctx):
        cver = settings["__version__"]
        new_ver = requests.get(f"https://api.github.com/repos/bazthedev/SolsRNGBot/releases/latest")
        new_ver_str = new_ver.json()["name"]

        if cver < new_ver_str:
            await ctx.send(f"A new version has been found ({new_ver_str}), please visit https://github.com/bazthedev/SolsRNGBot/releases/latest to download the newest version.")
        else:
            await ctx.send("You are running the latest version.")


def setup(client):
    client.add_cog(UpdateChecker(client))
