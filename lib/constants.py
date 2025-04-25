"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v1.2.5
Support server: https://discord.gg/6cuCu6ymkX
"""

import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))

MACROPATH = os.path.expandvars(r"%localappdata%\\SolsScope") 
LOCALVERSION = "1.2.5"
PRERELEASE = False 

PLACE_ID = 15532962292
BASE_ROBLOX_URL = f"https://www.roblox.com/games/{PLACE_ID}/"
SHARELINKS_API = "https://apis.roblox.com/sharelinks/v1/resolve-link"
RBLX_PLAYER_LOG_DIR = os.path.expandvars(r"%localappdata%\\Roblox\\logs")
MS_RBLX_LOG_DIR = os.path.expandvars(r"%LOCALAPPDATA%\\Packages\\ROBLOXCorporation.ROBLOX_55nm5eh3cm0pr\\LocalState\\logs")

DISCORD_WS_BASE = "wss://gateway.discord.gg/?v=10&encoding-json"
WEBHOOK_ICON_URL = "https://raw.githubusercontent.com/bazthedev/SolsScope/a93aaa9a42a7184047f12aa4135f3dab0857f05d/Server%20Edition/whicon.png"

DEFAULTSETTINGS = {
    "WEBHOOK_URL": "",
    "__version__": LOCALVERSION,
    "use_roblox_player": True,
    "global_wait_time": 0.2,
    "skip_aura_download": False,
    "mention": True,
    "mention_id": 0,
    "minimum_roll": "99998", 
    "minimum_ping": "349999", 
    "reset_aura": "",
    "merchant_detection": False,
    "ping_mari": False,
    "ping_jester": True,
    "clear_logs": False, 
    "pop_in_glitch": False,
    "auto_use_items_in_glitch": {
        "Heavenly Potion": {"use": True, "amount": 200},
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
    "auto_craft_mode": False,
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
    "merchant_detec_wait": 0, 
    "private_server_link": "",
    "take_screenshot_on_detection": False,
    "ROBLOSECURITY_KEY": "",
    "DISCORD_TOKEN": "",
    "collect_items": {"1": False, "2": False, "3": False, "4": False}, 
    "sniper_enabled": False,
    "sniper_toggles": {"Glitched": True, "Dreamspace": False},
    "sniper_logs": True,
    "change_cutscene_on_pop": True,
    "disable_autokick_prevention": False,
    "periodic_screenshots": {"inventory": False, "storage": False},
    "disconnect_prevention": False,
    "check_update": True,
    "auto_install_update": False,
    "biomes": { 
        "snowy": False, "windy": False, "rainy": False, "sand storm": False,
        "hell": False, "starfall": False, "corruption": False, "null": False,
        "glitched": True, "dreamspace": True
    },
    "auto_purchase_items_mari": {
        "Lucky Potion": False, "Lucky Potion L": False, "Lucky Potion XL": False,
        "Speed Potion": False, "Speed Potion L": False, "Speed Potion XL": False,
        "Mixed Potion": False, "Fortune Spoid": False, "Gear": False,
        "Lucky Penny": False, "Void Coin": True
    },
    "auto_purchase_items_jester": {
        "Lucky Potion": False, "Speed Potion": False, "Random Potion Sack": False,
        "Stella's Star": False, "Rune of Wind": False, "Rune of Frost": False,
        "Rune of Rainstorm": False, "Rune of Hell": False, "Rune of Galaxy": False,
        "Rune of Corruption": False, "Rune of Nothing": False, "Rune of Everything": True,
        "Strange Potion": True, "Stella's Candle": True, "Potion of Bound": True,
        "Merchant Tracker": False, "Heavenly Potion": True, "Oblivion Potion": True
    },
    "scan_channels": ["1282542323590496277"], 
    "mari_ping_id": 0,
    "jester_ping_id": 0,
    "vip": False, 
    "do_obby": False, 
    "do_item_collection": False, 
    "SECONDARY_WEBHOOK_URLS": [],
    "disable_aura_detection": False,
    "disable_biome_detection": False,
    "always_on_top": False,
    "skip_biome_download": False
}

VALIDSETTINGSKEYS = list(DEFAULTSETTINGS.keys()) 

GENERAL_KEYS = ["WEBHOOK_URL", "private_server_link", "SECONDARY_WEBHOOK_URLS", "failsafe_key", "use_roblox_player", "global_wait_time", "mention", "mention_id", "skip_aura_download", "skip_biome_download"]
AURAS_KEYS = ["minimum_roll", "minimum_ping", "reset_aura", "take_screenshot_on_detection"]
BIOMES_KEYS = ["biomes", "auto_biome_randomizer", "auto_strange_controller", "pop_in_glitch", "auto_use_items_in_glitch", "pop_in_dreamspace", "auto_use_items_in_dreamspace"]
SNIPER_KEYS = ["sniper_enabled", "sniper_toggles", "DISCORD_TOKEN", "ROBLOSECURITY_KEY", "sniper_logs", "scan_channels"]
MERCHANT_KEYS = ["merchant_detection", "ping_mari", "mari_ping_id", "auto_purchase_items_mari", "ping_jester", "jester_ping_id", "auto_purchase_items_jester"]
AUTOCRAFT_KEYS = ["auto_craft_mode", "auto_craft_item", "skip_auto_mode_warning"]
PATH_KEYS = ["vip", "do_obby", "do_item_collection", "collect_items"]

OTHER_KEYS = ["disconnect_prevention", "disable_autokick_prevention", "disable_aura_detection", "disable_biome_detection", "always_on_top", "periodic_screenshots", "check_update", "auto_install_update"]

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
    "Potion of Bound", "Heavenly Potion", "Godly Potion (Zeus)",
    "Godly Potion (Poseidon)", "Godly Potion (Hades)", "Warp Potion", "Godlike Potion"
]

ACCEPTEDAUTOPOP = {
    "Oblivion Potion": {"use": False, "amount": 1},
    "Godlike Potion": {"use": True, "amount": 1},
    "Godly (Zeus)": {"use": False, "amount": 1}, 
    "Godly (Poseidon)": {"use": False, "amount": 1},
    "Godly (Hades)": {"use": False, "amount": 1},
    "Heavenly Potion": {"use": True, "amount": 200},
    "Potion of Bound": {"use": True, "amount": 10},
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
    "Void Coin", "Fortune Spoid", "Speed Potion", "Mixed Potion",
    "Gear B", "Lucky Penny", "Gear A", "Lucky Potion"
]

JESTER_ITEMS = [
    "Lucky Potion", "Speed Potion", "Random Potion Sack", "Stella's Star",
    "Rune of Wind", "Rune of Frost", "Rune of Rainstorm", "Rune of Hell",
    "Rune of Galaxy", "Rune of Corruption", "Rune of Nothing", "Rune of Everything",
    "Strange Potion", "Stella's Candle", "Merchant Tracker", "Potion of Bound",
    "Heavenly Potion", "Oblivion Potion"
]

POSSIBLE_MERCHANTS = ["Mari's Shop", "Jester's Shop"]

COORDS = {
    "aura_button_pos": (53, 538),
    "inv_button_pos": (32, 692),
    "default_pos": (1280, 720), 
    "close_pos": (1887, 399),
    "search_pos": (1164, 486), 
    "secondary_pos": (564, 401), 
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
    }
}
