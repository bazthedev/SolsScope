"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v2.0.0
Support server: https://discord.gg/6cuCu6ymkX
"""

import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))
import json
from PyQt6.QtWidgets import QLabel, QLineEdit, QCheckBox, QMessageBox
from PyQt6.QtCore import Qt
from packaging.version import parse as parse_version
import discord
import requests

from discord_utils import get_webhook_info, forward_webhook_msg

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

class Plugin:
    DEFAULTSETTINGS = {
    }
    
    DISPLAYSETTINGS = []

    TOOLTIPS = {
    }
    
    def __init__(self, macro):
        self.name = "Glitch Hunt"
        self.version = "1.0.0"
        self.authors = ["bazthedev"]
        self.requires = "2.0.0"
        self.autocraft_compatible = True
        self.macro = macro
        self.silent = True
        
        self.MACROPATH = os.path.expandvars(r"%localappdata%\SolsScope")
        self.config_path = os.path.join(
            self.MACROPATH, "plugins", "config", f"{self.name}.json"
        )
        
        # Initialize plugin config (completely separate from main settings)
        self.config = self.load_or_create_config()
        self.entries = {}
        
        macro.logger.write_log(f"[{self.name}] Plugin initialized (v{self.version})")

    def load_or_create_config(self):
        """Load only plugin-specific config, completely separate from main settings"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        if not os.path.exists(self.config_path):
            with open(self.config_path, "w") as f:
                json.dump(self.DEFAULTSETTINGS, f, indent=4)
            return self.DEFAULTSETTINGS.copy()

        try:
            with open(self.config_path, "r") as f:
                loaded_config = json.load(f)
                
                # Merge with defaults to ensure new settings are added
                merged_config = self.DEFAULTSETTINGS.copy()
                merged_config.update(loaded_config)
                return merged_config
                
        except Exception as e:
            QMessageBox.critical(
                None,
                f"{self.name} Plugin Error",
                f"Failed to load config: {e}\nUsing default settings."
            )
            return self.DEFAULTSETTINGS.copy()

    def init_tab(self, gui_tools):
        """
        Initialize UI using only plugin's own config - don't touch main settings
        """
        QtWidgets = gui_tools["QtWidgets"]
        parent_layout = gui_tools["parent_layout"]
        create_widgets = gui_tools["create_widgets"]
        
        # Use only this plugin's config, not main settings
        settings_to_display = {
            key: self.config.get(key, self.DEFAULTSETTINGS.get(key))
            for key in self.DISPLAYSETTINGS
        }
        
        # Create widgets using plugin's isolated config
        create_widgets(settings_to_display, parent_layout, self.entries, self.TOOLTIPS)
        
        label_text = f"{self.name} v{self.version} by"
        for author in self.authors:
            if self.authors.index(author) == len(self.authors) - 1:
                label_text += f" {author}."
            else:
                label_text += f" {author},"

        info_label = QLabel(
            f"<i>{label_text}</i>"
        )   
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_layout.addWidget(info_label)

    def save_config(self):
        """Save only to plugin's own config file, don't touch main settings"""
        updated_values = self.get_updated_values()
        
        if not updated_values:
            return False
            
        try:
            # Merge updates with existing PLUGIN config only
            current_config = self.load_or_create_config()
            self.merge_dicts(current_config, updated_values)
            
            # Save only to plugin's config file
            with open(self.config_path, "w") as f:
                json.dump(current_config, f, indent=4)
                
            # Update in-memory PLUGIN config only
            self.config.update(current_config)
            
            self.macro.logger.write_log(f"[{self.name}] Plugin config saved to {self.config_path}")
            return True
            
        except Exception as e:
            self.macro.logger.write_log(
                f"[{self.name}] Failed to save plugin config: {e}", 
                level="ERROR"
            )
            QMessageBox.critical(
                self.macro,
                f"{self.name} Plugin Error",
                f"Failed to save plugin config:\n{e}"
            )
            return False

    def get_updated_values(self):
        """Get values only from plugin's UI widgets"""
        updated_values = {}
        
        for key, widget in self.entries.items():
            if isinstance(widget, QLineEdit):
                value = widget.text()
                default_type = type(self.DEFAULTSETTINGS.get(key, ""))
                try:
                    if default_type == int:
                        value = int(value) if value else 0
                    elif default_type == float:
                        value = float(value) if value else 0.0
                    elif default_type == bool:
                        value = value.lower() in ("true", "1", "yes")
                except ValueError:
                    value = str(value)
                updated_values[key] = value

            elif isinstance(widget, QCheckBox):
                updated_values[key] = widget.isChecked()

            elif isinstance(widget, dict) and "list_widget" in widget:
                list_widget = widget["list_widget"]
                updated_values[key] = [list_widget.item(i).text() for i in range(list_widget.count())]

        return updated_values

    def merge_dicts(self, original, updates):
        """Recursively merges dictionaries."""
        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(original.get(key), dict):
                self.merge_dicts(original[key], value)
            else:
                original[key] = value

    def run(self, stop_event, sniped_event, pause_event):
        """
        Main plugin logic that runs in a separate thread.
        
        Args:
            stop_event (threading.Event): Set when macro is stopping
            sniped_event (threading.Event): Set when a snipe occurs
            pause_event (threading.Event): Set when something wants to pause the macro
            
        Note:
            - This method should regularly check stop_event.is_set()
            - Use self.macro.logger for logging
            - Access settings through self.config
            - Use self.macro.keyboard_lock for thread-safe input
        """
        try:
            self.macro.logger.write_log(f"[{self.name}] Plugin thread started.")
            
            primary_data = get_webhook_info(self.macro.settings.get("WEBHOOK_URL"))

            webhook_data = []

            for webhook in self.macro.settings.get("SECONDARY_WEBHOOK_URLS", []):
                webhook_data.append(get_webhook_info(webhook))

            if IS_SS_UP["primary"]:
                try:
                    rgh = requests.get(f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('primary')}/SolsScope/main/glitch_hunts.json", timeout=10)
                    glitch_hunts = rgh.json()
                except Exception as e:
                    glitch_hunts = {}
                    embed = discord.Embed(
                        title="Glitch Hunt Plugin",
                        description="Failed to download Glitch Hunt data (plugin may be modded).",
                        colour=discord.Colour.red()
                    )
                    self.macro.webhook.send(embed=embed)
                    forward_webhook_msg(self.macro.settings.get("WEBHOOK_URL"), self.macro.settings.get("SECONDARY_WEBHOOK_URLS", []), embed=embed)
                    return
            elif IS_SS_UP["mirror"]:
                try:
                    rgh = requests.get(f"https://raw.githubusercontent.com/{GITHUB_USERNAMES.get('mirror')}/SolsScope/main/glitch_hunts.json", timeout=10)
                    glitch_hunts = rgh.json()
                except Exception as e:
                    glitch_hunts = {}
                    embed = discord.Embed(
                        title="Glitch Hunt Plugin",
                        description="Failed to download Glitch Hunt data (plugin may be modded).",
                        colour=discord.Colour.red()
                    )
                    self.macro.webhook.send(embed=embed)
                    forward_webhook_msg(self.macro.settings.get("WEBHOOK_URL"), self.macro.settings.get("SECONDARY_WEBHOOK_URLS", []), embed=embed)
                    return
            else:
                glitch_hunts = {}
                embed = discord.Embed(
                    title="Glitch Hunt Plugin",
                    description="Failed to download Glitch Hunt data (plugin may be modded).",
                    colour=discord.Colour.red()
                )
                self.macro.webhook.send(embed=embed)
                forward_webhook_msg(self.macro.settings.get("WEBHOOK_URL"), self.macro.settings.get("SECONDARY_WEBHOOK_URLS", []), embed=embed)
                return
            
            if len(glitch_hunts) == 0:
                embed = discord.Embed(
                    title="Glitch Hunt Plugin",
                    description="Failed to download Glitch Hunt data (plugin may be modded).",
                    colour=discord.Colour.red()
                )
                self.macro.webhook.send(embed=embed)
                forward_webhook_msg(self.macro.settings.get("WEBHOOK_URL"), self.macro.settings.get("SECONDARY_WEBHOOK_URLS", []), embed=embed)
                return

            embed = discord.Embed(
                title="Glitch Hunt Plugin",
                colour=discord.Colour.teal()
            )
            content = ""

            cross_macros = 0

            if primary_data.get("guild_id") in glitch_hunts:
                embed.add_field(name="Primary Webhook", value=f"Primary Webhook is set up in: {glitch_hunts.get(primary_data.get('guild_id')).get('server_name')}")
                content += f"<&{glitch_hunts.get(primary_data.get('guild_id')).get('cmr_id')} "
                cross_macros += 1
            else:
                embed.add_field(name="Primary Webhook", value=f"Primary Webhook is set up in a private or unlisted macro server.")
            
            count = 1
            for data in webhook_data:
                if data.get("guild_id") in glitch_hunts:
                    embed.add_field(name=f"Secondary Webhook #{count}", value=f"Secondary Webhook #{count} is set up in: {glitch_hunts.get(data.get('guild_id')).get('server_name')}")
                    content += f"<&{glitch_hunts.get(data.get('guild_id')).get('cmr_id')} "
                    cross_macros += 1
                else:
                    embed.add_field(name=f"Secondary Webhook #{count}", value=f"Secondary Webhook #{count} is set up in a private or unlisted macro server.")

                count += 1

            embed.set_footer(text=f"SolsScope Glitch Hunt Plugin v{self.version}")
            embed.set_thumbnail(url="https://raw.githubusercontent.com/bazthedev/SolsScope/main/img/solsscope.png")

            if cross_macros > 1:
                self.macro.webhook.send(content=content, embed=embed)
                forward_webhook_msg(primary_data.get("url"), self.macro.settings.get("SECONDARY_WEBHOOK_URLS", []), content=content, embed=embed)
            else:
                self.macro.webhook.send(embed=embed)
                forward_webhook_msg(primary_data.get("url"), self.macro.settings.get("SECONDARY_WEBHOOK_URLS", []), embed=embed)

            self.macro.logger.write_log(f"[{self.name}] Sent webhook summary.")

        except Exception as e:
            self.macro.logger.write_log(
                f"[{self.name}] Plugin error: {e}", 
                level="ERROR"
            )
        finally:
            self.macro.logger.write_log(f"[{self.name}] Plugin thread stopped.")

    def unload(self):
        """Called when plugin is being unloaded/reloaded."""
        self.macro.logger.write_log(f"[{self.name}] Plugin unloaded.")
        # Clean up any resources if needed