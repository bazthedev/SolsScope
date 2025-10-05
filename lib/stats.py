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

from constants import MACROPATH

from settings_manager import get_biomes_path


def create_stats():
    if not os.path.exists(f"{MACROPATH}\\stats.json"):
        try:
            with open(f"{MACROPATH}\\stats.json", "w") as f:
                f.write("{}")
        except Exception as e:
            print(f"Failed to create stats: {e}")

def load_stats():
    with open(f"{MACROPATH}/stats.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_all_biomes():

    with open(get_biomes_path(), "r", encoding="utf-8") as f:
        return json.load(f)

def init_stats():

    stats = load_stats()

    if stats == {}:

        _ = load_all_biomes()

        for stat in _:

            if stat in _ and stat not in stats:
                stats[stat] = {
                    "amount" : 0,
                    "colour" : _[stat]["colour"]
                }

        save_stats(stats)
        
        return True
    else:
        _ = load_all_biomes()
        for biome in _:
            if biome not in stats:
                stats[biome] = {
                    "amount" : 0,
                    "colour" : _[biome]["colour"]
                }
        
        save_stats(stats)

        todel = []
        for stat in stats:
            if stat not in _:
                todel.append(stat)

        for stat in todel:
            del stats[stat]

        save_stats(stats)
        
        return True
    
def increment_stat(stat):

    stats = load_stats()

    if stat in stats:

        stats[stat]["amount"] += 1
        save_stats(stats)
    
def save_stats(stats):
    with open(f"{MACROPATH}/stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)