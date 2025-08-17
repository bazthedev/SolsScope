"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v1.2.8
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
            f = open(f"{MACROPATH}\\stats.json", "w")
            f.write("{}")
            f.close()
        except Exception as e:
            print(f"Failed to create stats: {e}")
        finally:
            f.close()

def load_stats():
    with open(f"{MACROPATH}/stats.json", "r") as f:
        return json.load(f)

def load_all_biomes():

    with open(get_biomes_path(), "r") as f:
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
    
    return False
    
def increment_stat(stat):

    stats = load_stats()

    if stat in stats:

        stats[stat]["amount"] += 1
        save_stats(stats)
    
def save_stats(stats):
    with open(f"{MACROPATH}/stats.json", "w") as f:
        json.dump(stats, f, indent=4)