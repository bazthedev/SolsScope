# Plugins
## A plugin is essentially a discord.py Cog which you can let the bot use
## To install a plugin, place the python file inside the plugins folder
## Make sure that the following code is placed inside the \_\_init\_\_ function of your Cog:
```py
self.name = type(self).__name__
self.cfname = f"{self.name.lower()}.json"
if not os.path.exists(f"{MACROPATH}/plugins/config/{self.cfname}"):
    x = open(f"{MACROPATH}/plugins/config/{self.cfname}", "w")
    x.write('{"__version__" : "1.0.0", "author" : "your_github_username"}') # This can be changed to add your own custom settings. Also add your username here.
    x.close()
with open(f"{MACROPATH}/plugins/config/{self.cfname}", "r") as c:
    self.config = json.load(c)
```
## and the following code is used before creating a Cog class:
```py
import json
import os

MACROPATH = os.path.expandvars(r"%localappdata%\\Baz's Macro")

with open(f"{MACROPATH}/settings.json", "r") as f:
    settings = json.load(f)
```
## These allow the code to access the global configuration and the plugin's own configuration.
## For an example of starting a plugin, please look at [`template.py`](https://github.com/bazthedev/SolsRNGBot/blob/main/plugins/template.py).

## To publish a plugin to this repo, you must reach out to me and send the code in a .txt format, where it will be reviewed before being added.
