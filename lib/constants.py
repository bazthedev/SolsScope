"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v1.2.7
Support server: https://discord.gg/8khGXqG7nA
"""

import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))

MACROPATH = os.path.expandvars(r"%localappdata%\\SolsScope") 
LOCALVERSION = "1.2.7"

PLACE_ID = 15532962292
BASE_ROBLOX_URL = f"https://www.roblox.com/games/{PLACE_ID}/"
SHARELINKS_API = "https://apis.roblox.com/sharelinks/v1/resolve-link"
RBLX_PLAYER_LOG_DIR = os.path.expandvars(r"%localappdata%\\Roblox\\logs")
MS_RBLX_LOG_DIR = os.path.expandvars(r"%LOCALAPPDATA%\\Packages\\ROBLOXCorporation.ROBLOX_55nm5eh3cm0pr\\LocalState\\logs")

DISCORD_WS_BASE = "wss://gateway.discord.gg/?v=10&encoding-json"
WEBHOOK_ICON_URL = "https://raw.githubusercontent.com/bazthedev/SolsScope/a93aaa9a42a7184047f12aa4135f3dab0857f05d/Server%20Edition/whicon.png"

ALT_TESSERACT_DIR = os.path.expandvars(r"%localappdata%\Programs\Tesseract-OCR")

PATH_DIR = os.path.expandvars(r"%localappdata%\SolsScope\path")

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
        "glitched": True, "dreamspace": True, "blazing sun" : False
    },
    "auto_purchase_items_mari": {
        "Lucky Potion": {"Purchase" : False, "amount" : 25},
        "Speed Potion": {"Purchase" : False, "amount" : 25},
        "Mixed Potion": {"Purchase" : False, "amount" : 25},
        "Fortune Spoid": {"Purchase" : False, "amount" : 4},
        "Gear": {"Purchase" : False, "amount" : 1},
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
        "Strange Potion": {"Purchase" : True, "amount" : 25},
        "Stella's Candle": {"Purchase" : True, "amount" : 5},
        "Potion of Bound": {"Purchase" : True, "amount" : 1},
        "Merchant Tracker": {"Purchase" : False, "amount" : 1},
        "Heavenly Potion": {"Purchase" : True, "amount" : 1},
        "Oblivion Potion": {"Purchase" : True, "amount" : 1}
    },
    "scan_channels": ["1282542323590496277"], 
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
    "idle_mode" : False,
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
        "Meditation III": True,
        "Delivery III": True
    },
    "skip_questboard_download" : False,
    "notify_obby_completion" : False,
    "has_abyssal_hunter" : False,
    "do_no_walk_to_stella" : False
}

VALIDSETTINGSKEYS = list(DEFAULTSETTINGS.keys())

DONOTDISPLAY = ["__version__"]
NOTRECOMMENDED = []

GENERAL_KEYS = ["WEBHOOK_URL", "private_server_link", "SECONDARY_WEBHOOK_URLS", "failsafe_key", "idle_mode", "use_roblox_player", "global_wait_time", "mention", "mention_id", "skip_aura_download", "skip_biome_download", "skip_merchant_download", "skip_questboard_download"]
AURAS_KEYS = ["minimum_roll", "minimum_ping", "reset_aura", "take_screenshot_on_detection"]
BIOMES_KEYS = ["biomes", "auto_biome_randomizer", "auto_strange_controller", "pop_in_glitch", "auto_use_items_in_glitch", "pop_in_dreamspace", "auto_use_items_in_dreamspace"]
SNIPER_KEYS = ["sniper_enabled", "sniper_toggles", "DISCORD_TOKEN", "ROBLOSECURITY_KEY", "sniper_logs", "scan_channels"]
MERCHANT_KEYS = ["merchant_detection", "ping_mari", "mari_ping_id", "auto_purchase_items_mari", "ping_jester", "jester_ping_id", "auto_purchase_items_jester", "auto_sell_to_jester", "amount_of_item_to_sell", "items_to_sell"]
AUTOCRAFT_KEYS = ["auto_craft_mode", "auto_craft_item", "skip_auto_mode_warning", "do_no_walk_to_stella"]
PATH_KEYS = ["do_obby", "notify_obby_completion", "has_abyssal_hunter"]
QUEST_KEYS = ["enable_auto_quest_board", "quests_to_accept"]

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
    "Jewelry Potion", "Zombie Potion", "Rage Potion", "Diver Potion", "Potion of Bound", "Heavenly Potion", "Godly Potion (Zeus)",
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

JESTER_SELL_ITEMS = [
    "Icicle", "Wind Essence", "Rainy Bottle", "Eternal Flame",
    "Piece of Star", "Curruptaine", "Hour Glass", "NULL?", "Void Coin"
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
    },
    "exchange_menu_btn_pos" : (1125, 1255),
    "exchange_btn_pos" : (1151, 785),
    "first_sell_item_click_pos" : (740, 960),
    "first_sell_item_box_pos" : (653, 920, 830, 994),
    "second_sell_item_click_pos" : (927, 961),
    "second_sell_item_box_pos" : (843, 918, 1020, 994),
    "close_merchant_pos" : (1880, 449)
}

COORDS_PERCENT = {
    "aura_button_pos": (53/2560, 538/1440),
    "inv_button_pos": (32/2560, 692/1440),
    "default_pos": (1280/2560, 720/1440),
    "close_pos": (1887/2560, 399/1440),
    "search_pos": (1164/2560, 486/1440),
    "secondary_pos": (564/2560, 401/1440),
    "query_pos": (1086/2560, 572/1440),
    "equip_pos": (812/2560, 844/1440),
    "use_pos": (910/2560, 772/1440),
    "item_amt_pos": (756/2560, 772/1440),
    "items_pos": (1692/2560, 440/1440),
    "purchase_btn_pos": (990/2560, 860/1440),
    "quantity_btn_pos": (910/2560, 796/1440),
    "open_merch_pos": (876/2560, 1256/1440),
    "merch_item_pos_1_purchase": (766/2560, 948/1440),
    "merch_item_pos_2_purchase": (1024/2560, 948/1440),
    "merch_item_pos_3_purchase": (1278/2560, 948/1440),
    "merch_item_pos_4_purchase": (1512/2560, 948/1440),
    "merch_item_pos_5_purchase": (1762/2560, 948/1440),
    "menu_btn_pos": (32/2560, 656/1440),
    "settings_btn_pos": (1278/2560, 738/1440),
    "rolling_conf_pos": (888/2560, 498/1440),
    "cutscene_conf_pos": (1518/2560, 812/1440),
    "craft_btn_pos": (764/2560, 764/1440),
    "hp1_pos_potions": (1064/2560, 840/1440),
    "hp1_pos_celestial": (1064/2560, 1024/1440),
    "hp2_pos_potions": (1064/2560, 910/1440),
    "auto_btn_pos": (940/2560, 762/1440),
    "hp1_recipe_pos": (1516/2560, 684/1440),
    "hp2_recipe_pos": (1516/2560, 836/1440),
    "warp_recipe_pos": (1516/2560, 980/1440),
    "merchant_face_pos_1": (841/2560, 1056/1440),
    "merchant_face_pos_2": (855/2560, 1063/1440),
    "collection_open_pos": (40/2560, 608/1440),
    "exit_collection_pos": (513/2560, 158/1440),
    "start_btn_pos": (1252/2560, 1206/1440),
    "reconnect_btn_pos": (1370/2560, 800/1440),
    "bound_recipe_pos": (1524/2560, 994/1440),
    "potion_search_pos": (1237/2560, 449/1440),
    "first_potion_pos": (1520/2560, 554/1440),
    "ms_rblx_spawn_pos": (820/2560, 548/1440),
    "merchant_box": (1140/2560, 434/1440, 1409/2560, 477/1440),
    "manual_boxes": {
        "Box 1": (656/2560, 919/1440, 890/2560, 996/1440),
        "Box 2": (908/2560, 919/1440, 1143/2560, 996/1440),
        "Box 3": (1161/2560, 919/1440, 1396/2560, 996/1440),
        "Box 4": (1416/2560, 919/1440, 1650/2560, 996/1440),
        "Box 5": (1668/2560, 919/1440, 1903/2560, 996/1440)
    },
    "exchange_menu_btn_pos": (1125/2560, 1255/1440),
    "exchange_btn_pos": (1151/2560, 785/1440),
    "first_sell_item_click_pos": (740/2560, 960/1440),
    "first_sell_item_box_pos": (653/2560, 920/1440, 830/2560, 994/1440),
    "second_sell_item_click_pos": (927/2560, 961/1440),
    "second_sell_item_box_pos": (843/2560, 918/1440, 1020/2560, 994/1440),
    "close_merchant_pos": (1880/2560, 449/1440),
    "questboard_title_range" : (2010/2560, 350/1440, 2492/2560, 422/1440),
    "accept_quest_pos" : (2131/2560, 1085/1440),
    "dismiss_quest_pos" : (2378/2560, 1089/1440),
    "right_arrow_pos" : (1815/2560, 718/1440),
    "left_arrow_pos" : (744/2560, 715/1440),
    "exit_questboard_pos" : (1281/2560, 1250/1440),
    "sidequest_btn_pos" : (40/2560, 750/1440),
    "sidequest_check_complete_pos" : (1076/2560, 510/1440, 1446/2560, 508/1440),
    "quest_completion_title" : (1055/2560, 445/1440, 1459/2560, 471/1440),
    "equip_aura_btn" : (829/2560, 845/1440)
}

COMPLETION_COLOURS = [
    "#478e00",
    "#478f00"
]

ALL_QB = [
    "Basic Hunt",
    "Epic Hunt",
    "Unique Hunt",
    "Legendary Hunt",
    "Mythic Hunt",
    "Finding a person",
    "Meditation I",
    "Meditation II",
    "Meditation III",
    "Delivery III",
    "Delivery I",
    "Delivery II",
    "Delivery IV",
    "Delivery V",
    "Player Hunt #1",
    "Player Hunt #2",
    "Player Hunt #3",
    "Breakthrough",
    "Resonance",
    "A symbol of luck #1",
    "A symbol of luck #2"
]

ACCEPTED_QUESTBOARD = [
    "Basic Hunt",
    "Epic Hunt",
    "Unique Hunt",
    "Legendary Hunt",
    "Mythic Hunt",
    "Finding a person",
    "Meditation I",
    "Meditation II",
    "Meditation III",
    "Delivery III"
]

DONOTACCEPT_QB = [
    "Delivery I",
    "Delivery II",
    "Delivery IV",
    "Delivery V",
    "Player Hunt #1",
    "Player Hunt #2",
    "Player Hunt #3",
    "Breakthrough",
    "Resonance",
    "A symbol of luck #1",
    "A symbol of luck #2"
]

QUESTBOARD_RARITY_COLOURS = [
    "#e3e3e3",
    "#6ae085", 
    "#6ca4ff",
    "#ff4b4b",
    "#928aff"
]