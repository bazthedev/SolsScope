import discord
from discord.ext import commands
import json
import os

with open("settings.json", "r") as f:
    settings = json.load(f)

class Template(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.name = type(self).__name__
        self.cfname = f"{self.name.lower()}.json"
        if not os.path.exists(f"./plugins/config/{self.cfname}"):
            x = open(f"./plugins/config/{self.cfname}", "w")
            x.write('{"__version__" : "1.0.0", "author" : "your_github_username"}')
            x.close()
        with open(f"./plugins/config/{self.cfname}", "r") as c:
            self.config = json.load(c)

def setup(client):
    client.add_cog(Template(client))
