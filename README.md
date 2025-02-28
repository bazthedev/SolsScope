# SolsRNGBot
## A discord bot to detect the cutscene of an aura on Sol's RNG on roblox, and then send them to a discord server. It can take screenshots of your screen, your storage, and your inventory and automatically alerts you if you roll a new aura, as well as more soon to come!
# Features:
- Manual screenshots of game, storage, and inventory
- Autokick prevention
- Aura Detection
- Sending of Discord Messages to server
- Custom Plugins to add custom commands
- Automatic Updating of New Auras
- Mention on aura roll
- Minimum rarity for ping and send message
- Compatibility with all kinds of monitor sizes
- Matrix: Overdrive or Overture: History Detection
- Merchant Detection and sending a screenshot with their stock (Merchant Teleporter is required)
- Automatic crafting of potions
- Purchase items from merchant via command

# TBA:
- Auto Purchase from merchant (???) will start only for void coins. If you do not have Merchant Teleporter, then this will not work.
- Mari/Jester Detection. You will be able to choose to only buy items from Mari, Jester or both.
- Biome Detection (maybe). I'm going to study Noteab to see how they managed to get theirs working.
- Create a feature request if you want something to be added!

# Quick Start
1. Download the [latest release](https://github.com/bazthedev/SolsRNGBot/releases/latest)
2. Install the requirements by running `py -m pip install -r requirements.txt`
3. Run the main.py file
4. Create a new Discord Bot and copy its token
5. Edit the newly created `settings.json` file and paste your discord bot token in the "TOKEN" key.
6. Run the main.py file again
7. Add the bot to a server
8. Run the set_log_channel command in the channel you want the bot to automatically post in
9. And you are done! You can customize the settings by editing the `settings.json` file or by using some of the built in commands.

# Common Issues:
- Chromatic does not get detected: Chromatic is bugged, due to the amount of different colours there is only a very small chance that it will detect the Chromatic cutscene.
- Nothing is working on my dual monitor setup: Make sure that Roblox is open on the monitor you marked as PRIMARY. You can check this by typing "Change my primary display" into the Windows search bar.
## If you are experiencing issues, please create a new issue so that it can be raised, solved and prevented from happening again.

# You can read more about how the bot works and the things you can do with it [here](https://github.com/bazthedev/SolsRNGBot/wiki)

# Help with the project:
## If you want to help to implement some features, then please reach out and I would be happy to add you as a contributor to help!
## If anyone has any of the auras listed below and is willing to help add them to the aura database, then please reach out to me!
- Matrix: Reality
