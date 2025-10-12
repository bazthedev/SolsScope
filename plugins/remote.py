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
from PyQt6.QtWidgets import QLabel, QLineEdit, QCheckBox, QMessageBox, QPushButton, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt
from packaging.version import parse as parse_version
import screeninfo as si
from pynput import keyboard
import asyncio
import discord
from discord.ext import commands, tasks
import time
import pyautogui as pag
import webbrowser

from uinav import load_delay
from utils import create_discord_file_from_path
import pyautoscope

class Plugin:
    DEFAULTSETTINGS = {
        "enabled": True,
        "TOKEN": "",
        "enabled_commands" : {
            "stop" : True,
            "shutdown" : True,
            "cancel" : True,
            "screenshot" : True,
            "storage_screenshot" : True,
            "inventory_screenshot" : True,
            "purchase_item" : True,
            "get_log" : True
        }
    }
    
    DISPLAYSETTINGS = ["enabled", "TOKEN", "enabled_commands"]

    TOOLTIPS = {
        "enabled" : "Enable this plugin.",
        "TOKEN" : "The token for your Discord Bot.",
        "enabled_commands" : "The commands to be enabled when the bot is running."
    }
    
    def __init__(self, macro):
        self.name = "Remote Bot"
        self.version = "1.0.5"
        self.authors = ["bazthedev"]
        self.requires = "2.0.0"
        self.requirements = []
        self.autocraft_compatible = True
        self.macro = macro
        self.silent = False
        
        self.MACROPATH = os.path.expandvars(r"%localappdata%\SolsScope")
        self.config_path = os.path.join(
            self.MACROPATH, "plugins", "config", f"{self.name}.json"
        )
        
        # Initialize plugin config (completely separate from main settings)
        self.config = self.load_or_create_config()
        self.entries = {}
        screens = si.get_monitors()
        monitor = None
        for mon in screens:
            if mon.is_primary:
                monitor = mon

        self.WEBHOOK_ICON_URL = "https://raw.githubusercontent.com/bazthedev/SolsScope/main/img/solsscope.png"
    
        self._keyboard = keyboard.Controller()
        
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

        button_layout = QHBoxLayout()

        guide_button = QPushButton("Open Tutorial")
        guide_button.setToolTip("Click to open the Remote Bot Plugin setup guide.")
        guide_button.clicked.connect(lambda: webbrowser.open("https://www.youtube.com/watch?v=e8o1PAPZasE"))

        discord_dev_button = QPushButton("Open Discord Dev Portal")
        discord_dev_button.setToolTip("Click to open the Discord Developer Portal.")
        discord_dev_button.clicked.connect(lambda: webbrowser.open("https://discord.com/developers/applications"))

        for btn in (guide_button, discord_dev_button):
            btn.setFixedHeight(26)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button_layout.addWidget(btn)

        button_layout.setSpacing(8)

        parent_layout.addLayout(button_layout)

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
            
        Note:
            - This method should regularly check stop_event.is_set()
            - Use self.macro.logger for logging
            - Access settings through self.config
            - Use self.macro.keyboard_lock for thread-safe input
        """
        try:
            self.macro.logger.write_log(f"[{self.name}] Plugin thread started.")
            
            if not self.config["enabled"]:
                self.macro.logger.write_log("Bot is disabled and not started.")
                return
            if self.config["TOKEN"] == "":
                self.macro.logger.write_log("The TOKEN field is empty, not started.")
                return
            
            
            asyncio.set_event_loop(asyncio.new_event_loop())
            
            client = commands.Bot(command_prefix=commands.when_mentioned, intents=None)

            delay = load_delay()

            if self.config["enabled_commands"]["stop"]:
                @client.command()
                @commands.is_owner()
                async def stop(ctx):
                    await ctx.send("The macro will now be stopped.")
                    self.macro.running = False
                    emb = discord.Embed(
                        title="Macro was stopped remotely.",
                        colour=discord.Colour.red()
                    )
                    emb.set_thumbnail(url=self.WEBHOOK_ICON_URL)
                    emb.set_footer(text=f"SolsScope Remote Bot Plugin v{self.version}", icon_url=self.WEBHOOK_ICON_URL)
                    self.macro.webhook.send(embed=emb)
                    self.macro.logger.write_log("Macro was stopped remotely.")
                    self.macro.stop_event.set()

            @tasks.loop(seconds=0)
            async def stop_checker():
                if self.macro.stop_event.is_set():
                    await client.close()

            if self.config["enabled_commands"]["shutdown"]:
                @client.command()
                @commands.is_owner()
                async def shutdown(ctx, _time : int = 60):
                    emb = discord.Embed(
                        title="Macro was stopped remotely.",
                        colour=discord.Colour.red()
                    )
                    emb.set_thumbnail(url=self.WEBHOOK_ICON_URL)
                    emb.set_footer(text=f"SolsScope Remote Bot Plugin v{self.version}", icon_url=self.WEBHOOK_ICON_URL)
                    self.macro.webhook.send(embed=emb)
                    self.macro.logger.write_log("Macro was stopped remotely.")
                    t = round(time.time())
                    t_z = t + _time
                    await ctx.send(f"Shutting down at <t:{t_z}>")
                    os.system(f"shutdown /s /t {str(_time)}")
            
            if self.config["enabled_commands"]["cancel"]:
                @client.command()
                @commands.is_owner()
                async def cancel(ctx):
                    await ctx.send("Cancelling shutdown")
                    os.system("shutdown /a")

            if self.config["enabled_commands"]["screenshot"]:
                @client.command()
                @commands.is_owner()
                async def scr(ctx):
                    if os.path.exists(f"{self.MACROPATH}/scr/screenshot.png"):
                        os.remove(f"{self.MACROPATH}/scr/screenshot.png")
                        await asyncio.sleep(0.2)
                    img = pag.screenshot(f"{self.MACROPATH}/scr/screenshot.png", allScreens=True)
                    await ctx.send(file=discord.File(f"{self.MACROPATH}/scr/screenshot.png"))

            if self.config["enabled_commands"]["purchase_item"]:
                @client.command()
                @commands.is_owner()
                async def purchase_item(ctx, item_box : int, amount : int):
                    with self.macro.keyboard_lock:
                        pyautoscope.refresh_clients()
                        client = pyautoscope.return_clients()[0]
                        try:
                            coord_key = f"merchant_slot_{item_box}"
                            pyautoscope.click_button(self.macro.mkey, coord_key, client)
                            time.sleep(delay)
                            pyautoscope.click_button(self.macro.mkey, "merchant_amount", client)
                            time.sleep(delay)
                            self.macro.keyboard_controller.type(str(amount))
                            time.sleep(delay)
                            pyautoscope.click_button(self.macro.mkey, "merchant_purchase", client)
                            self.macro.logger.write_log(f"Manually purchased item in Box {str(item_box)}")
                            time.sleep(3)
                        except Exception as buy_e:
                            self.macro.logger.write_log(f"Error during manual purchasing: {buy_e}")
                        await ctx.send(f"Purchased item in box {str(item_box)}")

            if self.config["enabled_commands"]["storage_screenshot"]:
                @client.command()
                @commands.is_owner()
                async def storage_scr(ctx):
                    screenshot_path = os.path.join(self.MACROPATH, "scr", "screenshot_storage.png")
                    with self.macro.keyboard_lock:
                        pyautoscope.refresh_clients()
                        client = pyautoscope.return_clients()[0]
                        await ctx.send("Taking screenshot of Aura Storage, please wait, this will take a few seconds.")
                        pyautoscope.click_button(self.macro.mkey, "open_storage", client)
                        time.sleep(delay)
                        pyautoscope.click_button(self.macro.mkey, "search_bar", client)
                        time.sleep(delay)
                        self.macro.keyboard_controller.press(keyboard.Key.backspace)
                        time.sleep(0.2)
                        self.macro.keyboard_controller.release(keyboard.Key.backspace)
                        time.sleep(delay)
                        pag.screenshot(screenshot_path)
                        time.sleep(delay)
                        pyautoscope.click_button(self.macro.mkey, "close_menu", client)
                        time.sleep(delay)
                        await ctx.send(file=discord.File(f"{self.MACROPATH}/scr/screenshot_storage.png"))

            if self.config["enabled_commands"]["get_log"]:
                @client.command()
                @commands.is_owner()
                async def get_log(ctx):
                    log_file_path = f"{self.MACROPATH}/solsscope.log"

                    try:
                        with open(log_file_path, "r", errors="ignore", encoding="utf-8") as f:
                            lines = f.readlines()

                        last_50_lines = lines[-50:] if len(lines) >= 50 else lines
                        log_content = ''.join(last_50_lines)

                        if len(log_content) > 1990:
                            with open(f"{self.MACROPATH}/temp/upload.log", "w") as temp:
                                temp.writelines(last_50_lines)
                            await ctx.send("Log too long, sending as a file:", file=discord.File(f"{self.MACROPATH}/temp/upload.log"))
                        else:
                            await ctx.send(f"```{log_content}```")

                    except FileNotFoundError:
                        await ctx.send("Log file not found.")
                    except Exception as e:
                        await ctx.send(f"An error occurred: {str(e)}")


            if self.config["enabled_commands"]["inventory_screenshot"]:
                @client.command()
                @commands.is_owner()
                async def inv_scr(ctx):
                    screenshot_path = os.path.join(self.MACROPATH, "scr", "screenshot_inventory.png")
                    with self.macro.keyboard_lock:
                        pyautoscope.refresh_clients()
                        client = pyautoscope.return_clients()[0]
                        await ctx.send("Taking screenshot of Inventory, please wait, this will take a few seconds.")
                        pyautoscope.click_button(self.macro.mkey, "open_inventory", client)
                        time.sleep(delay)
                        pyautoscope.click_button(self.macro.mkey, "items_btn", client)
                        time.sleep(delay)
                        pyautoscope.click_button(self.macro.mkey, "search_bar", client)
                        time.sleep(delay)
                        self.macro.keyboard_controller.press(keyboard.Key.backspace)
                        time.sleep(0.2)
                        self.macro.keyboard_controller.release(keyboard.Key.backspace)
                        time.sleep(delay)
                        pag.screenshot(screenshot_path)
                        time.sleep(delay)
                        pyautoscope.click_button(self.macro.mkey, "close_menu", client)
                        time.sleep(delay)
                        await ctx.send(file=discord.File(f"{self.MACROPATH}/scr/screenshot_inventory.png"))

            
            @client.event
            async def on_ready():
                await client.change_presence(activity=discord.Game(name=f"bazthedev/SolsScope Remote Bot Plugin v{self.version}"))
                self.macro.logger.write_log(f"Remote bot has logged in to {client.user}")
                stop_checker.start()

            client.run(self.config["TOKEN"])
            self.macro.logger.write_log("Remote bot has logged out.")
                
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