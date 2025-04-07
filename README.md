# SolsRNGBot
## A macro for Sols's RNG, boasting Auto craft, Auto purchase, aura/biome detection and much more.
# Features:
- Autokick prevention
- Aura Detection
- Custom Plugins to add custom commands
- Automatic Updating of New Auras
- Mention on aura roll
- Minimum rarity for ping and send message
- Compatibility with most 16:9 monitors
- Merchant Detection and sending a screenshot with their stock (Merchant Teleporter is required)
- Automatic crafting of multiple potions
- Purchase items from merchant via command
- Glitch and Dreamspace Biome Detection
- Auto Pop in Glitch or Dreamspace (untested)
- Automatic Biome Randomizer/Strange Controller uses
- Window for Setting configuration
- Yay joins integration
- Disconnect prevention
- Added Periodic Inventory and/or Storage Screenshots
- Automatically detect if you are using the MSStore version or the Player and will adjust the script accordingly

# TBA:
- Create a feature request if you want something to be added!

# System Requirements:
This macro has been tested on a 1440p display but is known to work on 1080p displays. Screen resolutions below this may be incompatible.
You should have the Microsoft Store version of Roblox installed, the Roblox Player can also be used but the MSStore version is needed for certain features.

# Video Guide
You can watch [this video guide](https://youtu.be/AKva_0biJuk) to help setup the bot.

# Support Server
If you need help with the macro, please join [this server](https://discord.com/invite/y6NV89Na) and message Baz or send a message in the support thread.

# Quick Start
1. Download the [latest release](https://github.com/bazthedev/SolsRNGBot/releases/latest)
2. Make sure you have Python installed. I am using version 3.12 but you should be able to use any version 3.12 or newer.
3. Install the requirements by running `py -m pip install -r requirements.txt`
4. Run the main.py file
5. Create a new webhook and copy its link
6. Add your webhook in the WEBHOOK_URL box
7. And you are done!

# Common Issues:
- Nothing is working on my dual monitor setup: Make sure that Roblox is open on the monitor you marked as PRIMARY. You can check this by typing "Change my primary display" into the Windows search bar.
- The macro does not work on X platform. The macro has only been tested on Windows and is designed with Windows 10 in mind. Windows 11 should run the same.
- The macro freezes when trying to download the auras. You will have to manually download the auras. Click on the auras.json file, then press the download button. Open this path `%localappdata%\Baz's Macro\` and then copy the auras.json file there.
- The Windows menu keeps getting opened. Download the latest version of the macro (this removes using the Windows menu for mouse movement entirely).
## If you are experiencing issues, please create a new issue so that it can be raised, solved and prevented from happening again. If there is no update, then turn skip_dl to true in settings.

# You can read more about how the bot works and the things you can do with it [here](https://github.com/bazthedev/SolsRNGBot/wiki)
