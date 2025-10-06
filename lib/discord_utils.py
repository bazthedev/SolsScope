"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v2.0.0
Support server: https://discord.gg/8khGXqG7nA
"""

import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))

import discord
import io
import json
import requests

from utils import get_logger, create_discord_file_from_path, hex2rgb
from constants import (
    LOCALVERSION
)

from settings_manager import load_settings, get_autocraftdata_path

def forward_webhook_msg(primary_webhook_url: str, secondary_urls: list, *, file=None, **kwargs):
    """Forwards a webhook message to secondary URLs."""
    logger = get_logger()
    if not secondary_urls:
        return

    image_bytes = None
    filename = None

    if isinstance(file, discord.File):
        try:
            original_pos = file.fp.tell()
            file.fp.seek(0)
            image_bytes = file.fp.read()
            filename = file.filename
            file.fp.seek(original_pos) 
        except (ValueError, AttributeError, io.UnsupportedOperation) as e:
            logger.write_log(f"Error preparing file for forwarding: {e}")
            image_bytes = None

    for webhook_url in secondary_urls:

        if not webhook_url or webhook_url == primary_webhook_url:
            continue

        try:
            _webhook = discord.SyncWebhook.from_url(webhook_url)

            current_kwargs = kwargs.copy()
            if image_bytes and filename:
                current_kwargs["file"] = discord.File(io.BytesIO(image_bytes), filename=filename)
            elif "file" in current_kwargs: 
                del current_kwargs["file"]

            _webhook.send(**current_kwargs)
            logger.write_log(f"Forwarded webhook message to: {webhook_url[:30]}...")

        except discord.errors.NotFound:
            logger.write_log(f"Secondary webhook not found: {webhook_url}")
        except discord.errors.HTTPException as e:
            logger.write_log(f"HTTP error forwarding webhook to {webhook_url}: {e}")
        except Exception as e:
            logger.write_log(f"Unexpected error forwarding webhook to {webhook_url}: {e}")


def get_webhook_info(webhook_url) -> dict:    
    response = requests.get(webhook_url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return {}

def validate_glitch_hunts(guild_ids : list):

    matches = 0
    KNOWN_GLITCH_HUNTS = []

    for guild_id in guild_ids:
        if guild_id in KNOWN_GLITCH_HUNTS:
            matches += 1
    
    return True if matches > 1 else False

def get_potion_data(potion_name : str):

    try:
        with open(get_autocraftdata_path(), "r", encoding="utf-8") as f:
            _ = json.load(f)
            return _[potion_name]
    except Exception as e:
        print(e)
        return None
    

def create_autocraft_embed(potion : str) -> discord.Embed:

    data = get_potion_data(potion)
    if not data:
        return None

    description = f"**{potion}** was crafted.\n\n**Effects**:\n"

    for effect in data["effects"]:
        description += f"{effect}\n"

    colour = hex2rgb(data["colour"])

    emb = discord.Embed(
        title=f"Crafted: {potion}",
        description=description,
    colour=discord.Colour.from_rgb(colour[0], colour[1], colour[2])
    )

    emb.set_thumbnail(url=data["img_url"])
    emb.set_footer(text=f"SolsScope v{LOCALVERSION}")

    return emb