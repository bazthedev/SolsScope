"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v2.0.2
Support server: https://discord.gg/8khGXqG7nA
"""

import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))

MACROPATH = os.path.expandvars(r"%localappdata%\\SolsScope") 
LOCALVERSION = "2.0.3"

PLACE_ID = 15532962292
BASE_ROBLOX_URL = f"https://www.roblox.com/games/{PLACE_ID}/"
SHARELINKS_API = "https://apis.roblox.com/sharelinks/v1/resolve-link"
RBLX_PLAYER_LOG_DIR = os.path.expandvars(r"%localappdata%\\Roblox\\logs")
MS_RBLX_LOG_DIR = os.path.expandvars(r"%LOCALAPPDATA%\\Packages\\ROBLOXCorporation.ROBLOX_55nm5eh3cm0pr\\LocalState\\logs")

DISCORD_WS_BASE = "wss://gateway.discord.gg/?v=10&encoding-json"
WEBHOOK_ICON_URL = "https://raw.githubusercontent.com/bazthedev/SolsScope/a93aaa9a42a7184047f12aa4135f3dab0857f05d/Server%20Edition/whicon.png"

PATH_DIR = os.path.expandvars(r"%localappdata%\SolsScope\path")

PYTHON_EXE = os.path.join(MACROPATH, "py", "python.exe")
ASSETDIR = os.path.join(MACROPATH, "assets")
CALIBDIR = os.path.join(MACROPATH, "calibrations.json")

USERDATA = {}

PREFERRED_CLIENT = {}

DEFAULTSETTINGS = {
    "WEBHOOK_URL": "",
    "__version__": LOCALVERSION,
    "use_roblox_player": True,
    "skip_aura_download": False,
    "mention": True,
    "mention_id": 0,
    "minimum_roll": "99998", 
    "minimum_ping": "349999", 
    "reset_aura": "exotic",
    "merchant_detection": False,
    "ping_mari": False,
    "ping_jester": True,
    "clear_logs": False, 
    "pop_in_glitch": False,
    "auto_use_items_in_glitch": {
        "Godlike Potion" : {"use" : True, "amount" : 10},
        "Heavenly Potion": {"use": True, "amount": 200},
        "Wish Star" : {"use" : True, "amount" : 5},
        "Fortune Potion III": {"use": True, "amount": 1},
        "Lucky Potion": {"use": True, "amount": 10},
        "Pumpkin": {"use": True, "amount": 10},
        "Haste Potion III": {"use": False, "amount": 1},
        "Warp Potion": {"use": True, "amount": 1},
        "Transcended Potion": {"use": False, "amount": 1},
        "Mixed Potion": {"use": True, "amount": 10},
        "Stella's Candle": {"use": True, "amount": 1},
        "Santa Claus Potion": {"use": True, "amount": 5},
        "Hwachae": {"use": True, "amount": 1}
    },
    "pop_in_dreamspace": False,
    "auto_use_items_in_dreamspace": {
        "Heavenly Potion": {"use": False, "amount": 1},
        "Fortune Potion III": {"use": True, "amount": 1},
        "Lucky Potion": {"use": True, "amount": 10},
        "Pumpkin": {"use": True, "amount": 10},
        "Haste Potion III": {"use": False, "amount": 1},
        "Warp Potion": {"use": True, "amount": 1},
        "Transcended Potion": {"use": False, "amount": 1},
        "Mixed Potion": {"use": True, "amount": 10},
        "Stella's Candle": {"use": True, "amount": 1},
        "Santa Claus Potion": {"use": True, "amount": 5},
        "Hwachae": {"use": True, "amount": 1}
    },
    "skip_auto_mode_warning": False,
    "auto_craft_item": {
        "Potion of Bound": False,
        "Heavenly Potion": True,
        "Godly Potion (Zeus)": True,
        "Godly Potion (Poseidon)": True,
        "Godly Potion (Hades)": True,
        "Warp Potion": True,
        "Godlike Potion": True
    },
    "auto_biome_randomizer": False,
    "auto_strange_controller": False,
    "failsafe_key": "ctrl+e",
    "private_server_link": "",
    "take_screenshot_on_detection": False,
    "change_cutscene_on_pop": True,
    "disable_autokick_prevention": False,
    "periodic_screenshots": {"inventory": False, "storage": False},
    "disconnect_prevention": False,
    "check_update": True,
    "auto_install_update": False,
    "biomes": { 
        "snowy": True, "windy": True, "rainy": True, "sand storm": True,
        "hell": True, "starfall": True, "corruption": True, "null": True,
        "glitched": True, "dreamspace": True,
    },
    "auto_purchase_items_mari": {
        "Lucky Potion": {"Purchase" : False, "amount" : 25},
        "Lucky Potion L": {"Purchase" : False, "amount" : 10},
        "Lucky Potion XL": {"Purchase" : False, "amount" : 10},
        "Speed Potion": {"Purchase" : False, "amount" : 25},
        "Speed Potion L": {"Purchase" : False, "amount" : 10},
        "Speed Potion XL": {"Purchase" : False, "amount" : 10},
        "Mixed Potion": {"Purchase" : False, "amount" : 25},
        "Fortune Spoid I": {"Purchase" : False, "amount" : 4},
        "Fortune Spoid II": {"Purchase" : False, "amount" : 2},
        "Fortune Spoid III": {"Purchase" : False, "amount" : 1},
        "Gear A": {"Purchase" : False, "amount" : 1},
        "Gear B": {"Purchase" : False, "amount" : 1},
        "Lucky Penny": {"Purchase" : False, "amount" : 3},
        "Void Coin": {"Purchase": True, "amount" : 2}
    },
    "auto_purchase_items_jester": {
        "Lucky Potion": {"Purchase" : False, "amount" : 45},
        "Speed Potion": {"Purchase" : False, "amount" : 45},
        "Random Potion Sack": {"Purchase" : False, "amount" : 10},
        "Stella's Star": {"Purchase" : False, "amount" : 1},
        "Rune of Wind": {"Purchase" : False, "amount" : 1},
        "Rune of Frost": {"Purchase" : False, "amount" : 1},
        "Rune of Rainstorm": {"Purchase" : False, "amount" : 1},
        "Rune of Hell": {"Purchase" : False, "amount" : 1},
        "Rune of Galaxy": {"Purchase" : False, "amount" : 1},
        "Rune of Corruption": {"Purchase" : False, "amount" : 1},
        "Rune of Nothing": {"Purchase" : False, "amount" : 1},
        "Rune of Everything": {"Purchase" : True, "amount" : 1},
        "Strange Potion I": {"Purchase" : True, "amount" : 15},
        "Strange Potion II": {"Purchase" : True, "amount" : 25},
        "Stella's Candle": {"Purchase" : True, "amount" : 5},
        "Potion of Bound": {"Purchase" : True, "amount" : 1},
        "Merchant Tracker": {"Purchase" : False, "amount" : 1},
        "Heavenly Potion": {"Purchase" : True, "amount" : 1},
        "Oblivion Potion": {"Purchase" : True, "amount" : 1}
    },
    "mari_ping_id": 0,
    "jester_ping_id": 0,
    "do_obby": False,
    "SECONDARY_WEBHOOK_URLS": [],
    "disable_aura_detection": False,
    "disable_biome_detection": False,
    "always_on_top": False,
    "skip_biome_download": False,
    "auto_sell_to_jester" : False,
    "amount_of_item_to_sell" : 9999,
    "items_to_sell" : {
        "Icicle" : True,
        "Wind Essence" : True,
        "Rainy Bottle" : True,
        "Eternal Flame" : True,
        "Piece of Star" : True,
        "Curruptaine" : True,
        "Hour Glass" : True,
        "NULL?" : True,
    },
    "skip_merchant_download" : False,
    "redownload_libs_on_run" : False,
    "enable_auto_quest_board" : False,
    "quests_to_accept" : {
        "Basic Hunt": True,
        "Epic Hunt": True,
        "Unique Hunt": True,
        "Legendary Hunt": True,
        "Mythic Hunt": True,
        "Finding a person": True,
        "Meditation I": True,
        "Meditation II": True,
        "Windy Breakthrough": True,
        "Snowy Breakthrough": True,
        "Rainy Breakthrough": True,
        "SandStorm Breakthrough": True,
        "Hell Breakthrough": True,
        "Starfall Breakthrough": True,
        "Corruption Breakthrough": True,
        "Null Breakthrough": True
    },
    "skip_questboard_download" : False,
    "notify_obby_completion" : False,
    "has_abyssal_hunter" : False,
    "do_not_walk_to_stella" : False,
    "current_theme" : "Default",
    "disable_eden_detection_in_limbo" : False,
    "do_not_interact_with_eden" : False,
    "mode" : "Normal",
    "use_reset_aura" : False,
    "use_alternate_uinav" : True,
    "themes" : {
        "Default" : os.path.join(MACROPATH, "theme", "default.ssthm")
    },
    #"vok_taran" : False,
    "enable_ui_nav_key" : "#",
    "skip_autocraft_download" : False,
    "send_item_crafted_notification" : True,
    "delay" : 0.05,
    "vip_status" : "No VIP",
    #"merchant_detection_type" : "Legacy",
    "interaction_type" : "Mouse",
    "enable_player_logger" : True,
    #"calibration" : "",
    #"watch_ad_for_autocraft" : False,
    "typing_delay" : 0.2,
    "typing_hold" : 0.2,
    "typing_jitter" : 0.1,
    "secure_item_usage" : False,
    "ignore_autocraft_safety_check" : False,
    "ignore_fastflags_disabled_check" : False
}

VALIDSETTINGSKEYS = list(DEFAULTSETTINGS.keys())

TOOLTIPS = {
    "WEBHOOK_URL": "The URL that the macro posts notifications to.",
    "use_roblox_player": "Force the Roblox Player logs to be used even if Microsoft Store version is running.",
    "skip_aura_download": "Skip downloading the auras information (recommended if slow startup). This will mean you cannot detect new auras if they are released.",
    "mention": "Mention you when detecting something.",
    "mention_id": "ID of the user to mention. If this needs to be a role, then use & before the ID.",
    "minimum_roll": "Minimum rarity of an aura for it to be sent to the webhook.", 
    "minimum_ping": "Minimum rarity of an aura for it to be sent to the webhook and ping you.", 
    "reset_aura": "The aura to be equipped when a new aura is rolled.",
    "merchant_detection": "Detect merchants spawning by using the Merchant Teleporter item.",
    "ping_mari": "Mention you for when a Mari spawns.",
    "ping_jester": "Mention you for when a Jester spawns.",
    "pop_in_glitch": "Pop potions when a glitch biome spawns.",
    "auto_use_items_in_glitch": "The items to use when the biome spawns.",
    "pop_in_dreamspace": "Pop potions when a dreamspace biome spawns.",
    "auto_use_items_in_dreamspace": "The items to use when the biome spawns.",
    "skip_auto_mode_warning": "Skip the warning that you are using auto craft mode.",
    "auto_biome_randomizer": "Automatically use the Biome Randomizer every 35 minutes.",
    "auto_strange_controller": "Automatically use the Strange Controller every 20 minutes.",
    "failsafe_key": "Press this key combination to instantly terminate the program.",
    "private_server_link": "Your Roblox Private Server URL (to be sent with notifications).",
    "take_screenshot_on_detection": "Take a screenshot of your screen when an aura is rolled.",
    "change_cutscene_on_pop": "Change the cutscene settings to be large to skip long cutscenes whilst popping.",
    "disable_autokick_prevention": "Disable Auto Kick Action (Not recommended, use IDLE mode).",
    "disconnect_prevention": "Check for if you have disconnected and attempt to rejoin the private server.",
    "check_update": "Check for Macro updates.",
    "auto_install_update": "Automatically download the latest macro update.",
    "mari_ping_id": "ID of the role to be pinged when a Mari spawns.",
    "jester_ping_id": "ID of the role to be pinged when a Jester spawns.",
    "do_obby": "Complete the Obby for its blessing.",
    "SECONDARY_WEBHOOK_URLS": "Webhooks to forward messages to (Does not allow Cross Macroing).",
    "disable_aura_detection": "Disable the detection of auras (Not Recommended).",
    "disable_biome_detection": "Disable the detection of biomes (Not Recommended).",
    "skip_biome_download": "Skip downloading the biomes information (recommended if slow startup). This will mean you cannot detect new biomes if they are released.",
    "auto_sell_to_jester" : "Auto sell your items to Jester when he spawns.",
    "amount_of_item_to_sell" : "The amount of an item that should be sold to Jester.",
    "skip_merchant_download" : "Skip downloading the Merchants information (recommended if slow startup). This will cause issues if there are new Merchants added.",
    "enable_auto_quest_board" : "Automatically check the Quest Board every hour and accept/decline/claim quests.",
    "skip_questboard_download" : "Skip downloading the Quests that are offered by the Quest Board.",
    "notify_obby_completion" : "Send a message to the Webhook when you complete the obby.",
    "has_abyssal_hunter" : "Use Abyssal Hunter when executing paths.",
    "do_not_walk_to_stella" : "Do not walk to Stella for auto craft (Recommended if you have issues with paths).",
    "disable_eden_detection_in_limbo" : "Disable the detection of Eden in Limbo Mode (Not Recommended).",
    "do_not_interact_with_eden" : "Detect Eden but do not walk to and accept the contract.",
    "mode" : "The mode that the Macro is currently in.",
    "use_reset_aura" : "Equip the reset aura when a new aura is rolled.",
    "use_alternate_uinav" : "Use the alternate paths for UI navigation. Enable this if pressing the left arrow with UI nav on takes you to the storage button.",
    "themes" : "List of themes that are available to be applied.",
    "vok_taran" : "Types \"vok taran\" in the chat every 30 minutes to spawn a Sand Storm biome.",
    "enable_ui_nav_key" : "The key needed to be pressed to enable UI Navigation.",
    "skip_autocraft_download" : "Skip downloading the Auto Craft Data.",
    "send_item_crafted_notification" : "Send a notification whenever an item is crafted during Auto Craft. This may cause the program to take longer per potion.",
    "delay" : "How long to wait between actions. A larger number is recommended for potato PCs (~0.5).",
    "merchant_detection_type" : "Choose either Legacy (use the Merchant Teleporter every 60/90s) or Logs (scan log file for merchant spawns).",
    "interaction_type" : "Choose how you want the Macro to perform actions in the game.",
    "enable_player_logger" : "Enable the player logger for biomes other than glitched/dreamspace.",
    "calibration" : "How the macro runs based on your screen size.",
    "watch_ad_for_autocraft" : "Watch the add every hour to get increased rates.",
    "typing_delay" : "How long typing waits between each character.",
    "typing_hold" : "How long typing holds a key for (max about 0.3-0.5)",
    "typing_jitter" : "Random amount added to delay to act human.",
    "secure_item_usage" : "Will perform a check to see if the item that is about to be used matches the item detected (slows down macro + not recommended for small screens).",
    "ignore_autocraft_safety_check" : "Do not check that a potion was clicked before trying to add items to the autocraft.",
    "ignore_fastflags_disabled_check" : "Ignore the Macro checking if the required fast flags were enabled (if you are using a bypass to use FFs, then check this box)"
}

DONOTDISPLAY = ["__version__", "current_theme"]
NOTRECOMMENDED = []

GENERAL_KEYS = ["WEBHOOK_URL", "private_server_link", "mode", "themes", "SECONDARY_WEBHOOK_URLS", "failsafe_key", "use_roblox_player", "mention", "mention_id"]
AURAS_KEYS = ["minimum_roll", "minimum_ping", "use_reset_aura", "reset_aura", "take_screenshot_on_detection"]
BIOMES_KEYS = ["auto_biome_randomizer", "auto_strange_controller", "enable_player_logger", "pop_in_glitch", "pop_in_dreamspace"]
SNIPER_KEYS = ["sniper_enabled", "sniper_toggles", "DISCORD_TOKEN", "sniper_logs", "scan_channels"]

ACTIONS_KEYS = ["merchant_detection", "auto_sell_to_jester", "secure_item_usage", "do_obby", "vip_status", "notify_obby_completion", "has_abyssal_hunter"]

MARI_MERCHANT_KEYS = ["ping_mari", "mari_ping_id", "auto_purchase_items_mari"]
JESTER_MERCHANT_KEYS = ["ping_jester", "jester_ping_id", "auto_purchase_items_jester", "amount_of_item_to_sell", "items_to_sell"]
AUTOCRAFT_ITEM_KEYS = ["auto_craft_item", "skip_auto_mode_warning", "do_not_walk_to_stella"]

ACTIONS_CONFIG = ["enable_ui_nav_key", "delay", "typing_delay", "typing_hold", "typing_jitter", "use_alternate_uinav"]

BIOME_CONFIG_KEYS = ["biomes"]
GLITCHED_ITEMS_KEYS = ["auto_use_items_in_glitch"]
DREAMSPACE_ITEMS_KEYS = ["auto_use_items_in_dreamspace"]
LIMBO_KEYS = ["disable_eden_detection_in_limbo", "do_not_interact_with_eden"]

MERCHANT_KEYS = ["merchant_detection", "ping_mari", "mari_ping_id", "auto_purchase_items_mari", "ping_jester", "jester_ping_id", "auto_purchase_items_jester", "auto_sell_to_jester", "amount_of_item_to_sell", "items_to_sell"]
AUTOCRAFT_KEYS = ["auto_craft_item", "ignore_autocraft_safety_check", "send_item_crafted_notification", "skip_auto_mode_warning", "do_not_walk_to_stella"]
PATH_KEYS = ["do_obby", "notify_obby_completion", "has_abyssal_hunter"]
QUEST_KEYS = ["enable_auto_quest_board", "quests_to_accept"]
SKIP_DLS_KEYS = ["skip_aura_download", "skip_biome_download", "skip_merchant_download", "skip_questboard_download", "skip_autocraft_download"]
MACRO_OVERRIDES = ["disable_aura_detection", "disable_biome_detection", "disable_autokick_prevention", "ignore_fastflags_disabled_check"]
OTHER_KEYS = ["periodic_screenshots", "take_screenshot_on_detection", "disconnect_prevention", "always_on_top", "check_update", "auto_install_update"]


STARTUP_MSGS = [
    "Let's go gambling!", "Nah, I'd Roll", "I give my life...", "Take a break",
    "Waste of time", "I can't stop playing this", "Touch the grass", "Eternal time...",
    "Break the Reality", "Finished work for today", "When is payday???",
    "-One who stands before God-", "-Flaws in the world-", "We do a little bit of rolling",
    "Exotic Destiny", "Always bet on yourself", "(Lime shivers quietly in the cold)",
    "There's no way to stop it!", "[Tip]: Get Lucky", "I'm addicted to Sol's RNG",
    "The Lost"
]

ACCEPTEDPOTIONS = [
    "Jewelry Potion", "Zombie Potion", "Rage Potion", "Diver Potion", "Potion of Bound", "Heavenly Potion", "Godly Potion (Zeus)",
    "Godly Potion (Poseidon)", "Godly Potion (Hades)", "Warp Potion", "Godlike Potion", "Forbidden Potion I", "Forbidden Potion II",
    "Forbidden Potion III", "Void Heart"
]

ACCEPTEDAUTOPOP = {
    "Oblivion Potion": {"use": False, "amount": 1},
    "Godlike Potion": {"use": True, "amount": 1},
    "Godly (Zeus)": {"use": False, "amount": 1}, 
    "Godly (Poseidon)": {"use": False, "amount": 1},
    "Godly (Hades)": {"use": False, "amount": 1},
    "Heavenly Potion": {"use": True, "amount": 200},
    "Potion of Bound": {"use": True, "amount": 10},
    "Wish Star": {"use": False, "amount": 1},
    "Fortune Potion III": {"use": True, "amount": 1},
    "Lucky Potion": {"use": True, "amount": 10},
    "Pumpkin": {"use": True, "amount": 10},
    "Haste Potion III": {"use": False, "amount": 1},
    "Warp Potion": {"use": True, "amount": 1},
    "Transcended Potion": {"use": False, "amount": 1},
    "Mixed Potion": {"use": True, "amount": 10},
    "Stella's Candle": {"use": True, "amount": 1},
    "Santa Claus Potion": {"use": True, "amount": 5},
    "Hwachae": {"use": True, "amount": 1}
}

MARI_ITEMS = [
    "Void Coin", "Fortune Spoid I", "Fortune Spoid II", "Fortune Spoid III", "Speed Potion", "Speed Potion L", "Speed Potion XL", "Mixed Potion",
    "Gear B", "Lucky Penny", "Gear A", "Lucky Potion", "Lucky Potion L", "Lucky Potion XL"
]

JESTER_ITEMS = [
    "Lucky Potion", "Speed Potion", "Random Potion Sack", "Stella's Star",
    "Rune of Wind", "Rune of Frost", "Rune of Rainstorm", "Rune of Hell",
    "Rune of Galaxy", "Rune of Corruption", "Rune of Nothing", "Rune of Everything",
    "Strange Potion I", "Strange Potion II", "Stella's Candle", "Merchant Tracker", "Potion of Bound",
    "Heavenly Potion", "Oblivion Potion"
]

JESTER_SELL_ITEMS = [
    "Icicle", "Wind Essence", "Rainy Bottle", "Eternal Flame",
    "Piece of Star", "Curruptaine", "Hour Glass", "NULL?", "Void Coin"
]


POSSIBLE_MERCHANTS = ["Mari", "Jester"]

COORDS = {
    "aura_button_pos": (53, 538),
    "inv_button_pos": (32, 692),
    "default_pos": (1280, 720), 
    "close_pos": (1887, 399),
    "search_pos": (1164, 486), 
    "query_pos": (1086, 572), 
    "equip_pos": (812, 844), 
    "use_pos": (910, 772), 
    "item_amt_pos": (756, 772), 
    "items_pos": (1692, 440), 
    "purchase_btn_pos": (990, 860), 
    "quantity_btn_pos": (910, 796), 
    "open_merch_pos": (876, 1256), 
    "merch_item_pos_1_purchase": (766, 948), 
    "merch_item_pos_2_purchase": (1024, 948),
    "merch_item_pos_3_purchase": (1278, 948),
    "merch_item_pos_4_purchase": (1512, 948),
    "merch_item_pos_5_purchase": (1762, 948),
    "menu_btn_pos": (32, 656), 
    "settings_btn_pos": (1278, 738), 
    "rolling_conf_pos": (888, 498), 
    "cutscene_conf_pos": (1518, 812), 
    "craft_btn_pos": (764, 764), 
    "hp1_pos_potions": (1064, 840), 
    "hp1_pos_celestial": (1064, 1024),
    "hp2_pos_potions": (1064, 910), 
    "auto_btn_pos": (940, 762), 
    "hp1_recipe_pos": (1516, 684), 
    "hp2_recipe_pos": (1516, 836), 
    "warp_recipe_pos": (1516, 980), 
    "merchant_face_pos_1": (841, 1056), 
    "merchant_face_pos_2": (855, 1063), 
    "collection_open_pos": (32, 641), 
    "exit_collection_pos": (510, 146), 
    "start_btn_pos": (1252, 1206), 
    "reconnect_btn_pos": (1370, 800), 
    "bound_recipe_pos": (1524, 994), 
    "potion_search_pos": (1237, 449), 
    "first_potion_pos": (1520, 554), 
    "ms_rblx_spawn_pos": (820, 548), 
    "merchant_box": (1140, 434, 1409, 477), 
    "manual_boxes": { 
        "Box 1": (656, 919, 890, 996),
        "Box 2": (908, 919, 1143, 996),
        "Box 3": (1161, 919, 1396, 996),
        "Box 4": (1416, 919, 1650, 996),
        "Box 5": (1668, 919, 1903, 996)
    },
    "exchange_menu_btn_pos" : (1125, 1255),
    "exchange_btn_pos" : (1151, 785),
    "first_sell_item_click_pos" : (740, 960),
    "first_sell_item_box_pos" : (653, 920, 830, 994),
    "second_sell_item_click_pos" : (927, 961),
    "second_sell_item_box_pos" : (843, 918, 1020, 994),
    "close_merchant_pos" : (1880, 449)
}

COORDS_PERCENT169 = {
    "merchant_box": (971/2560, 918/1440, 1160/2560, 969/1440),
    "manual_boxes": {
        "Box 1": (656/2560, 919/1440, 890/2560, 996/1440),
        "Box 2": (908/2560, 919/1440, 1143/2560, 996/1440),
        "Box 3": (1161/2560, 919/1440, 1396/2560, 996/1440),
        "Box 4": (1416/2560, 919/1440, 1650/2560, 996/1440),
        "Box 5": (1668/2560, 919/1440, 1903/2560, 996/1440)
    },
    "first_sell_item_box_pos": (653/2560, 920/1440, 830/2560, 994/1440),
    "second_sell_item_box_pos": (843/2560, 918/1440, 1020/2560, 994/1440),
    "questboard_title_range" : (2010/2560, 350/1440, 2492/2560, 422/1440),
    "potion_slot_1_add" : (1012/2560, 822/1440, 1115/2560, 858/1440),
    "potion_slot_2_add" : (1014/2560, 894/1440, 1112/2560, 927/1440),
    "potion_slot_3_add" : (1011/2560, 964/1440, 1115/2560, 1002/1440),
    "potion_slot_1_scroll_add" : (1012/2560, 860/1440, 1114/2560, 897/1440),
    "potion_slot_2_scroll_add" : (1015/2560, 933/1440, 1114/2560, 967/1440),
    "potion_slot_3_scroll_add" : (1012/2560, 1004/1440, 1111/2560, 1039/1440),
    "scroll_mouse_position" : (881/2560, 918/1440),
    "check_tab_menu" : (2405/2560, 10/1440, 2507/2560, 47/1440)
}

COORDS_PERCENT43 = {
    "merchant_box": (708/1920, 913/1440, 883/1920, 961/1440),
    "manual_boxes": {
        "Box 1": (490/1920, 869/1440, 669/1920, 927/1440),
        "Box 2": (679/1920, 868/1440, 858/1920, 929/1440),
        "Box 3": (870/1920, 868/1440, 1049/1920, 932/1440),
        "Box 4": (1060/1920, 868/1440, 1241/1920, 930/1440),
        "Box 5": (1251/1920, 870/1440, 1428/1920, 930/1440)
    },
    "first_sell_item_box_pos": (489/1920, 868/1440, 627/1920, 929/1440),
    "second_sell_item_box_pos": (631/1920, 870/1440, 766/1920, 928/1440),
    "questboard_title_range" : (1503/1920, 433/1440, 1873/1920, 511/1440),
    "potion_slot_1_add" : (758/1920, 795/1440, 835/1920, 823/1440),
    "potion_slot_2_add" : (759/1920, 849/1440, 834/1920, 877/1440),
    "potion_slot_3_add" : (756/1920, 904/1440, 836/1920, 932/1440),
    "potion_slot_1_scroll_add" : (757/1920, 824/1440, 835/1920, 852/1440),
    "potion_slot_2_scroll_add" : (758/1920, 877/1440, 836/1920, 907/1440),
    "potion_slot_3_scroll_add" : (757/1920, 932/1440, 836/1920, 959/1440),
    "scroll_mouse_position" : (666/1920, 882/1440),
    "check_tab_menu" : (1803/1920, 9/1440, 1872/1920, 39/1440)
}

COORDS_PERCENT1610 = {
    "merchant_box": (711/1920, 764/1200, 891/1920, 811/1200),
    "manual_boxes": {
        "Box 1": (490/1920, 747/1200, 668/1920, 811/1200),
        "Box 2": (680/1920, 748/1200, 857/1920, 810/1200),
        "Box 3": (869/1920, 748/1200, 1050/1920, 810/1200),
        "Box 4": (1060/1920, 748/1200, 1241/1920, 810/1200),
        "Box 5": (1249/1920, 747/1200, 1432/1920, 810/1200)
    },
    "first_sell_item_box_pos": (487/1920, 750/1200, 623/1920, 811/1200),
    "second_sell_item_box_pos": (631/1920, 747/1200, 767/1920, 810/1200),
    "questboard_title_range" : (1502/1920, 313/1200, 1879/1920, 392/1200),
    "potion_slot_1_add" : (757/1920, 676/1200, 835/1920, 702/1200),
    "potion_slot_2_add" : (756/1920, 730/1200, 835/1920, 758/1200),
    "potion_slot_3_add" : (759/1920, 786/1200, 835/1920, 812/1200),
    "potion_slot_1_scroll_add" : (759/1920, 703/1200, 834/1920, 731/1200),
    "potion_slot_2_scroll_add" : (758/1920, 761/1200, 835/1920, 787/1200),
    "potion_slot_3_scroll_add" : (759/1920, 812/1200, 837/1920, 838/1200),
    "scroll_mouse_position" : (668/1920, 756/1200),
    "check_tab_menu" : (1803/1920, 9/1200, 1873/1920, 42/1200)
}

COMPLETION_COLOURS = [
    "#478e00",
    "#478f00"
]

ALL_QB = [
    "Player Hunt #1",
    "Player Hunt #2",
    "Player Hunt #3",
    "Basic Hunt",
    "Epic Hunt",
    "Unique Hunt",
    "Legendary Hunt",
    "Mythic Hunt",
    "Windy Breakthrough",
    "Snowy Breakthrough",
    "Rainy Breakthrough",
    "SandStorm Breakthrough",
    "Hell Breakthrough",
    "Starfall Breakthrough",
    "Null Breakthrough",
    "Corruption Breakthrough",
    "Finding a person",
    "A symbol of luck #1",
    "A symbol of luck #2",
    "Resonance of Wind",
    "Resonance of Sea",
    "Resonance of Frost",
    "Resonance of Sand",
    "Resonance of Flame",
    "Resonance of Star",
    "Resonance of Darkness",
    "Resonance of Corruption",
    "Meditation I",
    "Meditation II",
    "Delivery I",
    "Delivery II",
    "Delivery III",
    "Delivery IV",
    "Delivery V",
    "Minnow Rookie",
    "Catch 5 Common Fish",
    "Catch 5 Uncommon Fish",
    "Legendary Fisher"
]

ACCEPTED_QUESTBOARD = [
    "Basic Hunt",
    "Epic Hunt",
    "Unique Hunt",
    "Legendary Hunt",
    "Mythic Hunt",
    "Windy Breakthrough",
    "Snowy Breakthrough",
    "Rainy Breakthrough",
    "SandStorm Breakthrough",
    "Hell Breakthrough",
    "Starfall Breakthrough",
    "Null Breakthrough",
    "Corruption Breakthrough",
    "Finding a person",
    "Meditation I",
    "Meditation II",
]

DONOTACCEPT_QB = [
    "Player Hunt #1",
    "Player Hunt #2",
    "Player Hunt #3",
    "A symbol of luck #1",
    "A symbol of luck #2",
    "Resonance of Wind",
    "Resonance of Sea",
    "Resonance of Frost",
    "Resonance of Sand",
    "Resonance of Flame",
    "Resonance of Star",
    "Resonance of Darkness",
    "Resonance of Corruption",
    "Delivery I",
    "Delivery II",
    "Delivery III",
    "Delivery IV",
    "Delivery V",
    "Minnow Rookie",
    "Catch 5 Common Fish",
    "Catch 5 Uncommon Fish",
    "Legendary Fisher"
]

QUESTBOARD_RARITY_COLOURS = [
    "#e3e3e3",
    "#6ae085", 
    "#6ca4ff",
    "#ff4b4b",
    "#928aff"
]

DONOTACCEPTRESET = ["aquatic", "exotic", "undead", "jazz", "bounded", "celestial", "kyuawthuite", "arcane", "virtual", "twilight", "starscourge", "sailor", "stormal", "chromatic", "matrix", "overture", "ruins", "astral", "cosmos"]


ALL_INV_ITEMS = [
    "Void Coin",
    "Lucky Penny",
    "Gear Basing",
    "Gear A",
    "Gear B",
    "Stella's Star",
    "Stella's Candle",
    "Random Potion Sack",
    "Strange Controller",
    "Biome Randomizer",
    "Rainbow Syrup",
    "Hwachae",
    "Merchant Teleporter",
    "Merchant Tracker",
    "Pumpkin",
    "Pump King's Head",
    "Empty Bottle",
    "Wind Essence",
    "Icicle",
    "Rainy Bottle",
    "Eternal Flame",
    "Piece of Star",
    "Curruptaine",
    "NULL?",
    "Hour Glass",
    "Rune of Wind",
    "Rune of Frost",
    "Rune of Rainstorm",
    "Rune of Dust",
    "Rune of Hell",
    "Rune of Galaxy",
    "Rune of Corruption",
    "Rune of Nothing",
    "Rune of Everything",
    "Fortune Potion I",
    "Fortune Potion II",
    "Fortune Potion III",
    "Haste Potion I",
    "Haste Potion II",
    "Haste Potion III",
    "Transcendent Potion",
    "Void Heart",
    "Potion of Bound",
    "Heavenly Potion",
    "Rage Potion",
    "Diver Potion",
    "Jewelry Potion",
    "Zombie Potion",
    "Godly Potion (Zeus)",
    "Godly Potion (Poseidon)",
    "Godly Potion (Hades)",
    "Godlike Potion",
    "Warp Potion",
    "Forbidden Potion I",
    "Forbidden Potion II",
    "Forbidden Potion III"
]