# SolsRNGBot
## A discord bot that can detect auras, special biomes, merchants and even has an auto crafting mode for the Roblox game Sol's RNG!
# Features:
- Manual screenshots of game, storage, and inventory
- Autokick prevention
- Aura Detection
- Custom Plugins to add custom commands
- Automatic Updating of New Auras
- Mention on aura roll
- Minimum rarity for ping and send message
- Compatibility with all kinds of monitor sizes
- Matrix: Overdrive or Overture: History Detection
- Merchant Detection and sending a screenshot with their stock (Merchant Teleporter is required)
- Mari/Jester Detection. 
- Automatic crafting of potions
- Purchase items from merchant via command
- Glitch and Dreamspace Biome Detection
- Auto Pop in Glitch or Dreamspace (untested)
- Automatic Biome Randomizer/Strange Controller uses

# TBA:
- Auto Purchase from merchant (???) will start only for void coins. If you do not have Merchant Teleporter, then this will not work.
- You will be able to choose to only buy items from Mari, Jester or both.
- Create a feature request if you want something to be added!

# Video Guide
You can watch [this video guide](https://youtu.be/AKva_0biJuk) to help setup the bot.

# Support Server
If you need help with the macro, please join [this server](https://discord.com/invite/y6NV89Na) and message Baz or send a message in the support thread.

# Quick Start
1. Download the [latest release](https://github.com/bazthedev/SolsRNGBot/releases/latest)
2. Make sure you have Python installed. I am using version 3.12 but you should be able to use any version 3.12 or newer.
3. Install the requirements by running `python -m pip install -r requirements.txt`
4. Run the main.py file
5. Create a new Discord Bot and copy its token
6. Edit the newly created `settings.json` file and paste your discord bot token in the "TOKEN" key.
7. Run the main.py file again
8. Add the bot to a server
9. Run the set_log_channel command in the channel you want the bot to automatically post in
10. And you are done! You can customize the settings by editing the `settings.json` file or by using some of the built in commands.

# Common Issues:
- Chromatic does not get detected: Chromatic is bugged, due to the amount of different colours there is only a very small chance that it will detect the Chromatic cutscene.
- Nothing is working on my dual monitor setup: Make sure that Roblox is open on the monitor you marked as PRIMARY. You can check this by typing "Change my primary display" into the Windows search bar.
- The macro does not work on X platform. The macro has only been tested on Windows and is designed with Windows 10 in mind. Windows 11 should run the same.
- The macro freezes when trying to download the auras. You will have to manually download the auras. Click on the auras.json file, then press the download button. Open this path `%localappdata%\Baz's Macro\` and then copy the auras.json file there.
## If you are experiencing issues, please create a new issue so that it can be raised, solved and prevented from happening again. If there is no update, then turn skip_dl to true in settings.

# You can read more about how the bot works and the things you can do with it [here](https://github.com/bazthedev/SolsRNGBot/wiki)

# Help with the project:
## If you want to help to implement some features, then please reach out and I would be happy to add you as a contributor to help!
## If anyone has any of the auras listed below and is willing to help add them to the aura database, then please reach out to me!
- Matrix: Reality
