"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v2.0.0
Support server: https://discord.gg/8khGXqG7nA
"""

import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))

import json
import requests
from tkinter import messagebox

from constants import (
    MACROPATH, DEFAULTSETTINGS, VALIDSETTINGSKEYS,
    ACCEPTEDPOTIONS, ACCEPTEDAUTOPOP, ACCEPTED_QUESTBOARD
)
from utils import get_logger

SETTINGS_PATH = os.path.join(MACROPATH, "settings.json")
LIB_PATH = os.path.join(MACROPATH, "lib")
AURAS_PATH = os.path.join(MACROPATH, "auras_new.json")
BIOMES_PATH = os.path.join(MACROPATH, "biomes.json")
MERCHANT_PATH = os.path.join(MACROPATH, "merchant.json")
QUESTBOARD_PATH = os.path.join(MACROPATH, "questboard.json")
FISHDATA_PATH = os.path.join(MACROPATH, "fish-data.json")
AUTOCRAFT_PATH = os.path.join(MACROPATH, "autocraft.json")
RATIOS_PATH = os.path.join(MACROPATH, "ratios.json")
VALID_LIST_PATH = os.path.join(MACROPATH, "valid_lists.json")

GITHUB_USERNAMES = {
    "primary" : "bazthedev",
    "mirror" : "ScopeDevelopment"
}

IS_SS_UP = {
    "primary" : "DOWN",
    "mirror" : "DOWN"
}

try:
    riu = requests.get(f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/main/requirements.txt", timeout=10)
    if riu.status_code == 200:
        IS_SS_UP["primary"] = "OK"
except Exception as e:
    print(f"Error: {e}")

try:
    riu = requests.get(f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('mirror')}/SolsScope/main/requirements.txt", timeout=10)
    if riu.status_code == 200:
        IS_SS_UP["mirror"] = "OK"
except Exception as e:
    print(f"Error: {e}")

if IS_SS_UP.get("primary") == "OK":
    DOWNLOAD_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/main"
elif IS_SS_UP.get("mirror"):
    DOWNLOAD_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('mirror')}/SolsScope/main"
else:
    DOWNLOAD_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/main"

def get_settings_path():
    return SETTINGS_PATH

def get_lib_path():
    return LIB_PATH

def get_auras_path():
    return AURAS_PATH

def get_biomes_path():
    return BIOMES_PATH

def get_merchant_path():
    return MERCHANT_PATH

def get_questboard_path():
    return QUESTBOARD_PATH

def get_fish_path():
    return FISHDATA_PATH

def get_autocraftdata_path():
    return AUTOCRAFT_PATH

def get_ratios_path():
    return RATIOS_PATH

def get_valid_list_path():
    return VALID_LIST_PATH

def get_auras():
    logger = get_logger()
    logger.write_log("Downloading Aura List...")
    try:

        dl = requests.get(f"{DOWNLOAD_URL}/auras_new.json", timeout=5)
        dl.raise_for_status() 
        with open(AURAS_PATH, "wb") as f:
            f.write(dl.content)
        logger.write_log("Downloaded Aura List successfully.")
        return True
    except requests.exceptions.Timeout:
        logger.write_log("Failed to download Aura List: Request timed out.")
    except requests.exceptions.RequestException as e:
        logger.write_log(f"Failed to download Aura List: {e}")
    except OSError as e:
        logger.write_log(f"Failed to save Aura List: {e}")
    return False

def get_biomes():
    logger = get_logger()
    logger.write_log("Downloading Biome List...")
    try:
        dl = requests.get(f"{DOWNLOAD_URL}/biomes.json", timeout=5)
        dl.raise_for_status()
        with open(BIOMES_PATH, "wb") as f:
            f.write(dl.content)
        logger.write_log("Downloaded Biome List successfully.")
        return True
    except requests.exceptions.Timeout:
        logger.write_log("Failed to download Biome List: Request timed out.")
    except requests.exceptions.RequestException as e:
        logger.write_log(f"Failed to download Biome List: {e}")
    except OSError as e:
        logger.write_log(f"Failed to save Biome List: {e}")
    return False

def get_merchant():
    logger = get_logger()
    logger.write_log("Downloading Merchant List...")
    try:
        dl = requests.get(f"{DOWNLOAD_URL}/merchant.json", timeout=5)
        dl.raise_for_status()
        with open(MERCHANT_PATH, "wb") as f:
            f.write(dl.content)
        logger.write_log("Downloaded Merchant List successfully.")
        return True
    except requests.exceptions.Timeout:
        logger.write_log("Failed to download Merchant List: Request timed out.")
    except requests.exceptions.RequestException as e:
        logger.write_log(f"Failed to download Merchant List: {e}")
    except OSError as e:
        logger.write_log(f"Failed to save Merchant List: {e}")
    return False

def get_questboard():
    logger = get_logger()
    logger.write_log("Downloading Quest Board List...")
    try:
        dl = requests.get(f"{DOWNLOAD_URL}/questboard.json", timeout=5)
        dl.raise_for_status()
        with open(QUESTBOARD_PATH, "wb") as f:
            f.write(dl.content)
        logger.write_log("Downloaded Quest Board List successfully.")
        return True
    except requests.exceptions.Timeout:
        logger.write_log("Failed to download Quest Board List: Request timed out.")
    except requests.exceptions.RequestException as e:
        logger.write_log(f"Failed to download Quest Board List: {e}")
    except OSError as e:
        logger.write_log(f"Failed to save Quest Board List: {e}")
    return False

def get_fishdata():
    logger = get_logger()
    logger.write_log("Downloading Fish Data List...")
    try:
        dl = requests.get("https://raw.githubusercontent.com/cresqnt-sys/FishScope-Macro/main/fish-data.json", timeout=5)
        dl.raise_for_status()
        with open(FISHDATA_PATH, "wb") as f:
            f.write(dl.content)
        logger.write_log("Downloaded Fish Data successfully.")
        return True
    except requests.exceptions.Timeout:
        logger.write_log("Failed to download Fish Data: Request timed out.")
    except requests.exceptions.RequestException as e:
        logger.write_log(f"Failed to download Fish Data: {e}")
    except OSError as e:
        logger.write_log(f"Failed to save Fish Data: {e}")
    return False

def get_autocraft_data():
    logger = get_logger()
    logger.write_log("Downloading Auto Craft Data...")
    try:
        dl = requests.get(f"{DOWNLOAD_URL}/autocraft.json", timeout=5)
        dl.raise_for_status()
        with open(AUTOCRAFT_PATH, "wb") as f:
            f.write(dl.content)
        logger.write_log("Downloaded Auto Craft Data successfully.")
        return True
    except requests.exceptions.Timeout:
        logger.write_log("Failed to download Auto Craft Data: Request timed out.")
    except requests.exceptions.RequestException as e:
        logger.write_log(f"Failed to download Auto Craft Data: {e}")
    except OSError as e:
        logger.write_log(f"Failed to save Auto Craft Data: {e}")
    return False

def get_ratios():
    logger = get_logger()
    logger.write_log("Downloading Ratios...")
    try:
        dl = requests.get(f"{DOWNLOAD_URL}/ratios.json", timeout=5)
        dl.raise_for_status()
        with open(RATIOS_PATH, "wb") as f:
            f.write(dl.content)
        logger.write_log("Downloaded Ratios successfully.")
        return True
    except requests.exceptions.Timeout:
        logger.write_log("Failed to download Ratios: Request timed out.")
    except requests.exceptions.RequestException as e:
        logger.write_log(f"Failed to download Ratios: {e}")
    except OSError as e:
        logger.write_log(f"Failed to save Ratios: {e}")
    return False

def get_valid_list():
    logger = get_logger()
    logger.write_log("Downloading valid list...")
    try:
        dl = requests.get(f"{DOWNLOAD_URL}/valid_lists.json", timeout=5)
        dl.raise_for_status()
        with open(VALID_LIST_PATH, "wb") as f:
            f.write(dl.content)
        logger.write_log("Downloaded valid list successfully.")
        return True
    except requests.exceptions.Timeout:
        logger.write_log("Failed to download valid list: Request timed out.")
    except requests.exceptions.RequestException as e:
        logger.write_log(f"Failed to download valid list: {e}")
    except OSError as e:
        logger.write_log(f"Failed to save valid list: {e}")
    return False

def load_settings():
    logger = get_logger()
    if not os.path.exists(SETTINGS_PATH):
        logger.write_log(f"Settings file not found at {SETTINGS_PATH}. Creating default settings.")
        try:
            with open(SETTINGS_PATH, "w", encoding='utf-8') as f:
                json.dump(DEFAULTSETTINGS, f, indent=4)
            logger.write_log("Default settings file created.")
            return DEFAULTSETTINGS.copy() 
        except OSError as e:
            logger.write_log(f"Error creating default settings file: {e}")
            messagebox.showerror("Settings Error", f"Could not create settings file: {e}")
            sys.exit(1) 
        except Exception as e:
            logger.write_log(f"Unexpected error creating settings file: {e}")
            messagebox.showerror("Settings Error", f"Unexpected error creating settings file: {e}")
            sys.exit(1)

    try:
        with open(SETTINGS_PATH, "r", encoding='utf-8') as f:
            settings = json.load(f)
        logger.write_log("Settings loaded successfully.")

        validated_settings, validation_needed = validate_settings(settings)
        if validation_needed:
            logger.write_log("Settings validation resulted in changes. Resaving.")
            update_settings(validated_settings) 
            return validated_settings
        return settings
    except json.JSONDecodeError:
        logger.write_log("Settings file is corrupt. Attempting to reset.")
        reset_settings = messagebox.askyesno("Settings Error", "Your settings file appears to be corrupt. Would you like to reset it to defaults?")
        if reset_settings:
            try:
                os.remove(SETTINGS_PATH)
                logger.write_log("Removed corrupt settings file.")

                return load_settings()
            except OSError as e:
                logger.write_log(f"Failed to delete corrupt settings file: {e}")
                messagebox.showerror("Settings Error", f"Failed to delete corrupt settings file: {e}")
                sys.exit(1)
        else:
            logger.write_log("User chose not to reset corrupt settings. Exiting.")
            messagebox.showinfo("Settings Error", "Macro cannot run with corrupt settings.")
            sys.exit(1)
    except OSError as e:
        logger.write_log(f"Error reading settings file: {e}")
        messagebox.showerror("Settings Error", f"Could not read settings file: {e}")
        sys.exit(1)
    except Exception as e:
        logger.write_log(f"Unexpected error loading settings: {e}")
        messagebox.showerror("Settings Error", f"Unexpected error loading settings: {e}")
        sys.exit(1)

def update_settings(settings_dict):
    logger = get_logger()
    try:
        with open(SETTINGS_PATH, "w", encoding='utf-8') as f:
            json.dump(settings_dict, f, indent=4)
        logger.write_log("Settings updated successfully.")
        return True
    except OSError as e:
        logger.write_log(f"Error writing settings file: {e}")
        messagebox.showerror("Settings Save Error", f"Could not save settings: {e}")
    except TypeError as e:
        logger.write_log(f"Error saving settings (data type issue): {e}")
        messagebox.showerror("Settings Save Error", f"Data type error saving settings: {e}")
    except Exception as e:
        logger.write_log(f"Unexpected error saving settings: {e}")
        messagebox.showerror("Settings Save Error", f"Unexpected error saving settings: {e}")
    return False

def validate_settings(current_settings):
    logger = get_logger()
    validated_settings = current_settings.copy()
    needs_update = False
    keys_to_remove = []
    keys_added = []

    if isinstance(validated_settings.get("auto_purchase_items_mari", {}).get("Void Coin"), bool):
        validated_settings.pop("auto_purchase_items_mari", None)
        validated_settings.pop("auto_purchase_items_jester", None)

    for key in validated_settings.keys():
        if key not in VALIDSETTINGSKEYS:
            keys_to_remove.append(key)
            logger.write_log(f"Settings Validation: Found invalid key '{key}'. Marked for removal.")
            needs_update = True

    for key in keys_to_remove:
        validated_settings.pop(key, None)

    for default_key in VALIDSETTINGSKEYS:
        if default_key not in validated_settings:
            validated_settings[default_key] = DEFAULTSETTINGS[default_key]
            keys_added.append(default_key)
            logger.write_log(f"Settings Validation: Missing key '{default_key}'. Added default value.")
            needs_update = True

    try:
        validated_settings["auto_use_items_in_glitch"], glitch_pop_updated = _validate_auto_pop_structure(validated_settings.get("auto_use_items_in_glitch", {}))
        validated_settings["auto_use_items_in_dreamspace"], dream_pop_updated = _validate_auto_pop_structure(validated_settings.get("auto_use_items_in_dreamspace", {}))
        if glitch_pop_updated or dream_pop_updated:
             logger.write_log("Settings Validation: Auto pop item structure updated.")
             needs_update = True
    except Exception as e:
         logger.write_log(f"Error during auto pop validation: {e}")

    try:
        validated_settings["auto_craft_item"], craft_updated = _validate_auto_craft_structure(validated_settings.get("auto_craft_item", {}))
        if craft_updated:
            logger.write_log("Settings Validation: Auto craft item structure updated.")
            needs_update = True
    except Exception as e:
         logger.write_log(f"Error during auto craft validation: {e}")

    try:
        if os.path.exists(BIOMES_PATH):
             with open(BIOMES_PATH, "r", encoding='utf-8') as bf:
                 biomes_data = json.load(bf)
             validated_settings["biomes"], biomes_updated = _validate_biome_toggles(validated_settings.get("biomes", {}), biomes_data)
             if biomes_updated:
                 logger.write_log("Settings Validation: Biome toggle structure updated.")
                 needs_update = True
        else:
            logger.write_log("Skipping biome toggle validation: Biomes data file not found.")
    except (json.JSONDecodeError, OSError, KeyError) as e:
         logger.write_log(f"Error during biome toggle validation: {e}")

    try:
        validated_settings["quests_to_accept"], quest_update = _validate_quests(validated_settings.get("quests_to_accept"))
        if quest_update:
            logger.write_log("Settings Validation: Quest toggle structure updated.")
            needs_update = True
    except Exception as e:
        logger.write_log(f"Error during auto quest validation: {e}")

    if needs_update:
        logger.write_log("Settings validation complete. Changes were made.")
    else:
         logger.write_log("Settings validation complete. No changes needed.")

    return validated_settings, needs_update

def _validate_auto_pop_structure(pop_settings):
    logger = get_logger()
    validated_pop = pop_settings.copy()
    needs_update = False
    for item, default_data in ACCEPTEDAUTOPOP.items():
        if item not in validated_pop:
            validated_pop[item] = default_data
            logger.write_log(f"Auto Pop Validation: Added missing item '{item}'.")
            needs_update = True
        elif not isinstance(validated_pop[item], dict) or "use" not in validated_pop[item] or "amount" not in validated_pop[item]:
            logger.write_log(f"Auto Pop Validation: Correcting structure for item '{item}'.")
            validated_pop[item] = default_data 
            needs_update = True

    keys_to_remove = [key for key in validated_pop if key not in ACCEPTEDAUTOPOP]
    if keys_to_remove:
         for key in keys_to_remove:
             del validated_pop[key]
             logger.write_log(f"Auto Pop Validation: Removed invalid item '{key}'.")
             needs_update = True

    return validated_pop, needs_update

def _validate_auto_craft_structure(craft_settings):
    logger = get_logger()

    # Handle case where craft_settings is not a dictionary
    if not isinstance(craft_settings, dict):
        logger.write_log(f"Auto Craft Validation: craft_settings is not a dictionary (type: {type(craft_settings)}). Resetting to default structure.")
        validated_craft = DEFAULTSETTINGS["auto_craft_item"].copy()
        return validated_craft, True

    validated_craft = craft_settings.copy()
    needs_update = False
    for potion in ACCEPTEDPOTIONS:
        if potion not in validated_craft:
            validated_craft[potion] = DEFAULTSETTINGS["auto_craft_item"].get(potion, False)
            logger.write_log(f"Auto Craft Validation: Added missing potion '{potion}'.")
            needs_update = True
        elif not isinstance(validated_craft[potion], bool):
             logger.write_log(f"Auto Craft Validation: Correcting type for potion '{potion}'.")
             validated_craft[potion] = DEFAULTSETTINGS["auto_craft_item"].get(potion, False)
             needs_update = True

    keys_to_remove = [key for key in validated_craft if key not in ACCEPTEDPOTIONS]
    if keys_to_remove:
         for key in keys_to_remove:
             del validated_craft[key]
             logger.write_log(f"Auto Craft Validation: Removed invalid potion '{key}'.")
             needs_update = True

    return validated_craft, needs_update

def _validate_biome_toggles(biome_settings, biomes_data):
    logger = get_logger()
    validated_biomes = biome_settings.copy()
    needs_update = False
    valid_biome_names = list(biomes_data.keys())

    for biome_name in valid_biome_names:
        if biome_name not in validated_biomes:
            if biomes_data[biome_name]["enabled"]:
                validated_biomes[biome_name] = DEFAULTSETTINGS["biomes"].get(biome_name, False)
                logger.write_log(f"Biome Validation: Added missing biome '{biome_name}'.")
                needs_update = True
        elif not isinstance(validated_biomes[biome_name], bool):
             logger.write_log(f"Biome Validation: Correcting type for biome '{biome_name}'.")
             validated_biomes[biome_name] = DEFAULTSETTINGS["biomes"].get(biome_name, False)
             needs_update = True

    keys_to_remove = [key for key in validated_biomes if key not in valid_biome_names or not biomes_data[key]["enabled"]]
    if keys_to_remove:
        for key in keys_to_remove:
            del validated_biomes[key]
            logger.write_log(f"Biome Validation: Removed outdated biome '{key}'.")
            needs_update = True

    return validated_biomes, needs_update

def _validate_quests(quest_settings):
    logger = get_logger()
    validated_quest = quest_settings.copy()
    needs_update = False
    for item in ACCEPTED_QUESTBOARD:
        if item not in validated_quest:
            validated_quest[item] = False
            logger.write_log(f"Auto Quest Validation: Added missing quest '{item}'.")
            needs_update = True
        elif not isinstance(validated_quest[item], bool):
            logger.write_log(f"Auto Quest Validation: Correcting structure for quest '{item}'.")
            validated_quest[item] = False 
            needs_update = True

    keys_to_remove = [key for key in validated_quest if key not in ACCEPTED_QUESTBOARD]
    if keys_to_remove:
         for key in keys_to_remove:
             del validated_quest[key]
             logger.write_log(f"Auto Quest Validation: Removed invalid quest '{key}'.")
             needs_update = True

    return validated_quest, needs_update

def migrate_settings_from_legacy_location():
    logger = get_logger()
    legacy_path = "./settings.json" 
    if os.path.exists(legacy_path) and not os.path.exists(SETTINGS_PATH):
        logger.write_log(f"Found legacy settings file at '{legacy_path}'. Migrating to '{SETTINGS_PATH}'.")
        try:

            os.makedirs(MACROPATH, exist_ok=True)

            os.rename(legacy_path, SETTINGS_PATH)
            logger.write_log("Settings file successfully migrated.")
            return True
        except OSError as e:
            logger.write_log(f"Error migrating settings file: {e}")
            messagebox.showerror("Settings Migration Error", f"Could not move settings from {legacy_path} to {SETTINGS_PATH}:\n{e}")
        except Exception as e:
             logger.write_log(f"Unexpected error during settings migration: {e}")
             messagebox.showerror("Settings Migration Error", f"An unexpected error occurred during migration: {e}")
    legacy_path = os.path.expandvars(r"%localappdata\Baz's Macro\settings.json")
    if os.path.exists(legacy_path) and not os.path.exists(SETTINGS_PATH):
        logger.write_log(f"Found legacy settings file at '{legacy_path}'. Migrating to '{SETTINGS_PATH}'.")
        try:

            os.makedirs(MACROPATH, exist_ok=True)

            os.rename(legacy_path, SETTINGS_PATH)
            logger.write_log("Settings file successfully migrated.")
            return True
        except OSError as e:
            logger.write_log(f"Error migrating settings file: {e}")
            messagebox.showerror("Settings Migration Error", f"Could not move settings from {legacy_path} to {SETTINGS_PATH}:\n{e}")
        except Exception as e:
             logger.write_log(f"Unexpected error during settings migration: {e}")
             messagebox.showerror("Settings Migration Error", f"An unexpected error occurred during migration: {e}")
    return False