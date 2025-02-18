# Plugins
## A plugin is essentially a discord.py Cog which you can let the bot use
## To install a plugin, place the python file inside the plugins folder
## Make sure that the following code is placed inside the __init__ function of your Cog:
```py
self.name = type(self).__name__
self.cfname = f"{self.name.lower()}.json"
if not os.path.exists(f"./plugins/config/{self.cfname}"):
    x = open(f"./plugins/config/{self.cfname}", "w")
    x.write('{"__version__" : "1.0.0"}') # this can be changed to add your own custom settings
    x.close()
with open(f"./plugins/config/{self.cfname}", "r") as c:
    self.config = json.load(c)
```
## and the following code is used before creating a Cog class:
```py
import json
import os

with open("settings.json", "r") as f:
    settings = json.load(f)
```
## These allow the code to access the global configuration and the plugin's own configuration.
