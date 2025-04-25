import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))
import json
from PyQt6.QtWidgets import QLabel, QLineEdit, QCheckBox, QMessageBox
from PyQt6.QtCore import Qt
from packaging.version import parse as parse_version
import screeninfo as si
from pynput import keyboard
import mousekey as mk
import asyncio
import discord
from discord.ext import commands, tasks
import time
import pyautogui as pag

from constants import WEBHOOK_ICON_URL

class Plugin:
    DEFAULTSETTINGS = {
        "enabled": True,
        "TOKEN": "",
    }
    
    DISPLAYSETTINGS = ["enabled", "TOKEN"]
    
    def __init__(self, macro):
        self.name = "Remote Bot"
        self.version = "1.0.3"
        self.author = "bazthedev"
        self.requires = "1.2.5"
        self.autocraft_compatible = False
        self.macro = macro
        
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
        self.scale_w = monitor.width / 2560
        self.scale_h = monitor.height / 1440

        self.purchase_btn_pos = ((990 * self.scale_w), (860 * self.scale_h))
        self.quantity_btn_pos = ((910 * self.scale_w), (796 * self.scale_h))
        self.open_merch_pos = ((876 * self.scale_w), (1256 * self.scale_h))
        self.merch_item_pos_1_purchase = ((766 * self.scale_w), (948 * self.scale_h))
        self.merch_item_pos_2_purchase = ((1024 * self.scale_w), (948 * self.scale_h))
        self.merch_item_pos_3_purchase = ((1278 * self.scale_w), (948 * self.scale_h))
        self.merch_item_pos_4_purchase = ((1512 * self.scale_w), (948 * self.scale_h))
        self.merch_item_pos_5_purchase = ((1762 * self.scale_w), (948 * self.scale_h))
        self.aura_button_pos = ((53 * self.scale_w), (538 * self.scale_h))
        self.inv_button_pos = ((32 * self.scale_w), (692 * self.scale_h))
        self.close_pos = ((1887 * self.scale_w), (399 * self.scale_h))
        self.search_pos = ((1164 * self.scale_w), (486 * self.scale_h))
        self.items_pos = ((1692 * self.scale_w), (440 * self.scale_h))
    
        self._keyboard = keyboard.Controller()
        self.mkey = mk.MouseKey()
        
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
        create_widgets(settings_to_display, parent_layout, self.entries)
        
        info_label = QLabel(
            f"<i>{self.name} v{self.version} by {self.author}</i>"
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

    def run(self, stop_event, sniped_event):
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
            
            @client.command()
            @commands.is_owner()
            async def stop(ctx):
                await ctx.send("The macro will now be stopped.")
                self.macro.running = False
                emb = discord.Embed(
                    title="Macro was stopped remotely.",
                    colour=discord.Colour.red()
                )
                emb.set_footer(text=f"SolsRNGBot Remote Bot Plugin v{self.version}", icon_url=WEBHOOK_ICON_URL)
                self.macro.webhook.send(avatar_url=WEBHOOK_ICON_URL, embed=emb)
                self.macro.logger.write_log("Macro was stopped remotely.")
                self.macro.stop_event.set()

            @tasks.loop(seconds=0)
            async def stop_checker():
                if self.macro.stop_event.is_set():
                    await client.close()

            @client.command()
            @commands.is_owner()
            async def shutdown(ctx, _time : int):
                emb = discord.Embed(
                    title="Macro was stopped remotely.",
                    colour=discord.Colour.red()
                )
                emb.set_footer(text=f"SolsRNGBot Remote Bot Plugin v{self.version}", icon_url=WEBHOOK_ICON_URL)
                self.macro.webhook.send(avatar_url=WEBHOOK_ICON_URL, embed=emb)
                self.macro.logger.write_log("Macro was stopped remotely.")
                t = round(time.time())
                t_z = t + _time
                await ctx.send(f"Shutting down at <t:{t_z}>")
                os.system(f"shutdown /s /t {str(_time)}")
                    
            @client.command()
            @commands.is_owner()
            async def cancel(ctx):
                await ctx.send("Cancelling shutdown")
                os.system("shutdown /a")

            @client.command()
            @commands.is_owner()
            async def scr(ctx):
                if os.path.exists(f"{self.MACROPATH}/scr/screenshot.png"):
                    os.remove(f"{self.MACROPATH}/scr/screenshot.png")
                    await asyncio.sleep(0.2)
                img = pag.screenshot(f"{self.MACROPATH}/scr/screenshot.png", allScreens=True)
                await ctx.send(file=discord.File(f"{self.MACROPATH}/scr/screenshot.png"))

            @client.command()
            @commands.is_owner()
            async def purchase_item(ctx, item_box : int):
                with self.macro.keyboard_lock:
                    if item_box == 1:
                        self.mkey.left_click_xy_natural(self.merch_item_pos_1_purchase[0], self.merch_item_pos_1_purchase[1], print_coords=False)
                        time.sleep(0.2)
                        self.mkey.left_click_xy_natural(self.quantity_btn_pos[0], self.quantity_btn_pos[1], print_coords=False)
                        time.sleep(0.2)
                        self._keyboard.type("25")
                        time.sleep(0.2)
                        self.mkey.left_click_xy_natural(self.purchase_btn_pos[0], self.purchase_btn_pos[1], print_coords=False)
                        time.sleep(0.2)
                        await ctx.send(f"Purchased item in box {str(item_box)}")
                    elif item_box == 2:
                        self.mkey.left_click_xy_natural(self.merch_item_pos_2_purchase[0], self.merch_item_pos_2_purchase[1], print_coords=False)
                        time.sleep(0.2)
                        self.mkey.left_click_xy_natural(self.quantity_btn_pos[0], self.quantity_btn_pos[1], print_coords=False)
                        time.sleep(0.2)
                        self._keyboard.type("25")
                        time.sleep(0.2)
                        self.mkey.left_click_xy_natural(self.purchase_btn_pos[0], self.purchase_btn_pos[1], print_coords=False)
                        time.sleep(0.2)
                        await ctx.send(f"Purchased item in box {str(item_box)}")
                    elif item_box == 3:
                        self.mkey.left_click_xy_natural(self.merch_item_pos_3_purchase[0], self.merch_item_pos_3_purchase[1], print_coords=False)
                        time.sleep(0.2)
                        self.mkey.left_click_xy_natural(self.quantity_btn_pos[0], self.quantity_btn_pos[1])
                        time.sleep(0.2)
                        self._keyboard.type("25")
                        time.sleep(0.2)
                        self.mkey.left_click_xy_natural(self.purchase_btn_pos[0], self.purchase_btn_pos[1])
                        time.sleep(0.2)
                        await ctx.send(f"Purchased item in box {str(item_box)}")
                    elif item_box == 4:
                        self.mkey.left_click_xy_natural(self.merch_item_pos_4_purchase[0], self.merch_item_pos_4_purchase[1], print_coords=False)
                        time.sleep(0.2)
                        self.mkey.left_click_xy_natural(self.quantity_btn_pos[0], self.quantity_btn_pos[1])
                        time.sleep(0.2)
                        self._keyboard.type("25")
                        time.sleep(0.2)
                        self.mkey.left_click_xy_natural(self.purchase_btn_pos[0], self.purchase_btn_pos[1])
                        time.sleep(0.2)
                        await ctx.send(f"Purchased item in box {str(item_box)}")
                    elif item_box == 5:
                        self.mkey.left_click_xy_natural(self.merch_item_pos_5_purchase[0], self.merch_item_pos_5_purchase[1], print_coords=False)
                        time.sleep(0.2)
                        self.mkey.left_click_xy_natural(self.quantity_btn_pos[0], self.quantity_btn_pos[1])
                        time.sleep(0.2)
                        self._keyboard.type("25")
                        time.sleep(0.2)
                        self.mkey.left_click_xy_natural(self.purchase_btn_pos[0], self.purchase_btn_pos[1])
                        time.sleep(0.2)
                        await ctx.send(f"Purchased item in box {str(item_box)}")

            @client.command()
            @commands.is_owner()
            async def storage_scr(ctx):
                with self.macro.keyboard_lock:
                    await ctx.send("Taking screenshot of Aura Storage, please wait, this will take a few seconds.")
                    self.mkey.left_click_xy_natural(self.aura_button_pos[0], self.aura_button_pos[1])
                    await asyncio.sleep(0.1)
                    self.mkey.left_click_xy_natural(self.search_pos[0], self.search_pos[1])
                    await asyncio.sleep(0.1)
                    storimg = pag.screenshot(f"{self.MACROPATH}/scr/screenshot_storage.png")
                    await asyncio.sleep(0.1)
                    self.mkey.left_click_xy_natural(self.close_pos[0], self.close_pos[1])
                    await ctx.send(file=discord.File(f"{self.MACROPATH}/scr/screenshot_storage.png"))


            @client.command()
            @commands.is_owner()
            async def get_log(ctx):
                log_file_path = f"{self.MACROPATH}/solsrngbot.log"

                try:
                    with open(log_file_path, "r") as f:
                        lines = f.readlines()

                    last_50_lines = lines[-50:] if len(lines) >= 50 else lines
                    log_content = ''.join(last_50_lines)

                    if len(log_content) > 1990:
                        with open("upload.log", "w") as temp:
                            temp.writelines(last_50_lines)
                        await ctx.send("Log too long, sending as a file:", file=discord.File("upload.log"))
                    else:
                        await ctx.send(f"```{log_content}```")

                except FileNotFoundError:
                    await ctx.send("Log file not found.")
                except Exception as e:
                    await ctx.send(f"An error occurred: {str(e)}")


            @client.command()
            @commands.is_owner()
            async def inv_scr(ctx):
                with self.macro.keyboard_lock:
                    await ctx.send("Taking screenshot of inventory, please wait, this will take a few seconds.")
                    self.mkey.left_click_xy_natural(self.inv_button_pos[0], self.inv_button_pos[1])
                    await asyncio.sleep(0.1)
                    self.mkey.left_click_xy_natural(self.items_pos[0], self.items_pos[1])
                    await asyncio.sleep(0.1)
                    self.mkey.left_click_xy_natural(self.search_pos[0], self.search_pos[1])
                    await asyncio.sleep(0.1)
                    self.storimg = pag.screenshot(f"{self.MACROPATH}/scr/screenshot_inventory.png")
                    await asyncio.sleep(0.1)
                    self.mkey.left_click_xy_natural(self.close_pos[0], self.close_pos[1])
                    await ctx.send(file=discord.File(f"{self.MACROPATH}/scr/screenshot_inventory.png"))

            @client.command()
            @commands.is_owner()
            async def join_ps(ctx):
                if self.macro.ps_link_code == 0:
                    await ctx.send("Private server link code is not set.")
                    return
                with self.macro.keyboard_lock:
                    await ctx.send("Rejoining private server...")
                    self.macro.join_private_server_link(self.macro.ps_link_code)
                    await asyncio.sleep(10)
                    self.leave_main_menu()
                    await ctx.send("Rejoined Private server!")
            
            @client.event
            async def on_ready():
                await client.change_presence(activity=discord.Game(name=f"bazthedev/SolsRNGBot Remote Bot Plugin v{self.version}"))
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
