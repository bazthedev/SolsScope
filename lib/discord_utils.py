"""
SolsScope/Baz's Macro
Created by Baz and Cresqnt
v1.2.8
Support server: https://discord.gg/8khGXqG7nA
"""

import sys
import os
sys.path.insert(1, os.path.expandvars(r"%localappdata%/SolsScope/lib"))
import discord
import io
import typing
import json
import re
import asyncio
import requests 
from aiohttp import ClientSession 
from websockets import connect 
from datetime import datetime 

from utils import get_logger, create_discord_file_from_path
from constants import (
    DISCORD_WS_BASE, PLACE_ID, BASE_ROBLOX_URL, LOCALVERSION,
    SHARELINKS_API, WEBHOOK_ICON_URL
)
from roblox_utils import join_private_server_link, detect_client_disconnect 

from settings_manager import load_settings

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

class Sniper:
    def __init__(self, settings: dict, main_webhook: discord.Webhook, sniped_event: asyncio.Event, stop_event: asyncio.Event, channel_id: str):
        self.settings = settings 
        self.main_webhook = main_webhook
        self.sniped_event = sniped_event
        self.stop_event = stop_event 
        self.channel_id = channel_id
        self.logger = get_logger() 
        self.roblox_session: typing.Optional[ClientSession] = None
        self._refresh_task = None 
        self.is_running = False 
        self.ps_link_code = None 

        self.words = ["Glitched", "Dreamspace"] 

        self.link_pattern = re.compile(
            f"https://www.roblox.com/games/{PLACE_ID}/*\\?privateServerLinkCode="
        )
        self.link_pattern_2 = re.compile(r"https://.*&type=Server")

        self.blacklists = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in [

                "need|want|lf|look|stop|how|bait|ste|snip|fak|real|pl|hunt|sho|sea|wait|tho|gone|think|ago|prob|try|dev|adm|or|see|cap|tot|is|us|spa|giv|get|hav|and|str|sc|br|rai|wi|san|star|null|pm|gra|pump|moon|scr|mac|do|did|jk|no|rep|dm|farm|sum|who|if|imag|pro|bot|next|post|was|bae|fae",

                "need|want|lf|look|stop|how|bait|ste|snip|fak|real|pl|hunt|sho|sea|wait|tho|gone|think|ago|prob|try|dev|adm|or|see|cap|tot|is|us|giv|get|hav|and|str|br|rai|wi|san|star|null|pm|gra|pump|moon|scr|mac|do|did|jk|no|rep|dm|farm|sum|who|if|imag|pro|bot|next|post|was|bae|fae"

            ]
        ]

        self.word_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in [
                r"g[liotc]+h", 
                r"d[rea]+ms"
            ]
        ]

    async def setup(self):
        """Initializes the aiohttp session with the Roblox security cookie."""
        roblo_key = self.settings.get("ROBLOSECURITY_KEY", "")
        if not roblo_key:
            self.logger.write_log("[SNIPER] Error: ROBLOSECURITY_KEY is missing in settings. Cannot setup sniper.")
            return False

        self.roblox_session = ClientSession()
        self.roblox_session.cookie_jar.update_cookies({".ROBLOSECURITY": roblo_key})
        self.roblox_session.headers["User-Agent"] = f"SolsScope/{LOCALVERSION} Sniper (github.com/bazthedev/SolsScope)"
        self.logger.write_log("[SNIPER] Roblox session initialized.")
        return True

    async def _identify(self, ws):
        """Sends the IDENTIFY payload to the Discord gateway."""
        discord_token = self.settings.get("DISCORD_TOKEN", "")
        if not discord_token:
            self.logger.write_log("[SNIPER] Error: DISCORD_TOKEN missing. Cannot identify.")
            raise ConnectionAbortedError("Discord token missing") 

        try:
            identify_payload = {
                "op": 2, 
                "d": {
                    "token": discord_token,
                    "properties": {"$os": "windows", "$browser": "chrome", "$device": "pc"},

                }
            }
            await ws.send(json.dumps(identify_payload))
            self.logger.write_log(f"[SNIPER-{self.channel_id}] Identify payload sent.")
        except Exception as e:
            self.logger.write_log(f"[SNIPER-{self.channel_id}] Error sending IDENTIFY: {e}")
            raise 

    async def get_guild_id(self) -> typing.Optional[str]:
        """Fetches the guild ID for the sniper's channel ID using Discord HTTP API."""
        discord_token = self.settings.get("DISCORD_TOKEN", "")
        if not discord_token:
             self.logger.write_log("[SNIPER] Cannot get guild ID: DISCORD_TOKEN missing.")
             return None

        headers = {
            "Authorization": discord_token,
             "User-Agent": f"SolsScope/{LOCALVERSION} (github.com/bazthedev/SolsScope, Guild ID Fetcher)"
        }
        url = f"https://discord.com/api/v10/channels/{self.channel_id}"
        try:

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() 
            data = response.json()
            guild_id = data.get("guild_id")
            if guild_id:
                self.logger.write_log(f"[SNIPER-{self.channel_id}] Found Guild ID: {guild_id}")
                return str(guild_id)
            else:
                self.logger.write_log(f"[SNIPER-{self.channel_id}] Could not find 'guild_id' in response for channel.")
                return None
        except requests.exceptions.Timeout:
            self.logger.write_log(f"[SNIPER-{self.channel_id}] Timeout fetching guild ID.")
        except requests.exceptions.RequestException as e:
            self.logger.write_log(f"[SNIPER-{self.channel_id}] Failed to fetch guild ID. Status: {e.response.status_code if e.response else 'N/A'}, Response: {e.response.text if e.response else 'N/A'}")
        except json.JSONDecodeError:
             self.logger.write_log(f"[SNIPER-{self.channel_id}] Failed to decode JSON response fetching guild ID.")
        except Exception as e:
            self.logger.write_log(f"[SNIPER-{self.channel_id}] Unexpected error fetching guild ID: {e}")
        return None

    async def _subscribe(self, ws):
        """Sends the GUILD_SUBSCRIBE payload (Opcode 14 - undocumented?)."""

        guild_id = await self.get_guild_id()
        if not guild_id:
            self.logger.write_log(f"[SNIPER-{self.channel_id}] Cannot subscribe: Failed to get Guild ID.")
            raise ConnectionAbortedError("Failed to get Guild ID for subscription")

        try:
            subscription_payload = {
                "op": 14, 
                "d": {
                    "guild_id": guild_id,

                    "channels": {str(self.channel_id): [[0, 99]]} 

                }
            }
            await ws.send(json.dumps(subscription_payload))
            self.logger.write_log(f"[SNIPER-{self.channel_id}] Subscribe payload sent for Guild {guild_id}.")
        except Exception as e:
            self.logger.write_log(f"[SNIPER-{self.channel_id}] Error sending SUBSCRIBE: {e}")
            raise 

    async def heartbeat(self, ws, interval):
        """Sends heartbeat payloads at the specified interval."""
        while self.is_running and not self.stop_event.is_set():
            try:
                heartbeat_payload = {
                    'op': 1, 
                    'd': None 
                }
                await ws.send(json.dumps(heartbeat_payload))

                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                 self.logger.write_log(f"[SNIPER-{self.channel_id}] Heartbeat task cancelled.")
                 break
            except Exception as e:

                 if self.is_running and not self.stop_event.is_set(): 
                    self.logger.write_log(f"[SNIPER-{self.channel_id}] Error in heartbeat loop: {e}")

                 self.is_running = False
                 break
        self.logger.write_log(f"[SNIPER-{self.channel_id}] Heartbeat loop stopped.")

    async def _on_message(self, ws):
        """Listens for and processes messages from the Discord gateway."""
        while self.is_running and not self.stop_event.is_set():
            try:
                raw_event = await ws.recv()
                event = json.loads(raw_event)

                op = event.get('op')
                event_type = event.get('t')
                data = event.get('d')

                if op == 10: 
                    interval = data["heartbeat_interval"] / 1000

                    asyncio.create_task(self.heartbeat(ws, interval))
                    self.logger.write_log(f"[SNIPER-{self.channel_id}] Received Hello. Heartbeat interval: {interval}s")

                    await self._identify(ws)

                elif op == 11: 

                    pass

                elif op == 0: 
                    if event_type == "READY":

                         self.logger.write_log(f"[SNIPER-{self.channel_id}] Received READY. Session ID: {data.get('session_id')}")

                         await self._subscribe(ws)

                    elif event_type == "MESSAGE_CREATE":
                        msg_channel_id = data.get("channel_id")
                        content = data.get("content", "")
                        author_id = data.get("author", {}).get("id")
                        is_bot = data.get("author", {}).get("bot", False)

                        if str(msg_channel_id) == self.channel_id and not is_bot:

                            asyncio.create_task(self.process_message(content))

                elif op == 7: 
                     self.logger.write_log(f"[SNIPER-{self.channel_id}] Received Reconnect request from Discord.")
                     self.is_running = False 
                     break 

                elif op == 9: 
                     self.logger.write_log(f"[SNIPER-{self.channel_id}] Received Invalid Session (Op 9). Can resume: {data}")

                     self.is_running = False
                     break 

            except asyncio.CancelledError:
                self.logger.write_log(f"[SNIPER-{self.channel_id}] Message listener task cancelled.")
                break
            except json.JSONDecodeError:
                self.logger.write_log(f"[SNIPER-{self.channel_id}] Error decoding JSON from gateway: {raw_event[:100]}...") 
                continue 
            except Exception as e:
                 if self.is_running and not self.stop_event.is_set():
                    self.logger.write_log(f"[SNIPER-{self.channel_id}] Error in message listener: {e}")
                 self.is_running = False 
                 break 

        self.logger.write_log(f"[SNIPER-{self.channel_id}] Message listener loop stopped.")

    def _should_process_message(self, message: str) -> typing.Optional[int]:
        """Checks if the message matches keywords and isn't blacklisted. Returns choice_id or None."""
        message_lower = message.lower()
        choice_id = None

        for i, pattern in enumerate(self.word_patterns):
            if pattern.search(message_lower):
                choice_id = i
                break

        if choice_id is None:
            return None

        if self.blacklists[choice_id].search(message_lower):
            if self.settings.get("sniper_logs", False):
                self.logger.write_log(f"[SNIPER-{self.channel_id}] Filtered message (blacklist: {self.words[choice_id]}): {message[:50]}...")
            return None 

        return choice_id

    async def _extract_server_code(self, message: str) -> typing.Optional[str]:
        """Extracts the private server link code from a message, resolving share links if necessary."""

        if link_match := self.link_pattern.search(message):
            try:
                code = link_match.group(0).split("LinkCode=")[-1]
                self.logger.write_log(f"[SNIPER-{self.channel_id}] Extracted direct link code: {code[:5]}...")
                return code
            except IndexError:
                 self.logger.write_log(f"[SNIPER-{self.channel_id}] Error parsing direct link code from: {link_match.group(0)}")
                 return None

        if link_match_2 := self.link_pattern_2.search(message):
            try:
                share_code = link_match_2.group(0).split("code=")[-1].split("&")[0]
                self.logger.write_log(f"[SNIPER-{self.channel_id}] Found share link code: {share_code}. Attempting conversion...")
                return await self._convert_link(share_code)
            except IndexError:
                 self.logger.write_log(f"[SNIPER-{self.channel_id}] Error parsing share link code from: {link_match_2.group(0)}")
                 return None

        return None

    async def _convert_link(self, link_id: str) -> typing.Optional[str]:
        """Converts a roblox.com/share link code to a privateServerLinkCode using Roblox API."""
        if not self.roblox_session:
            self.logger.write_log("[SNIPER] Cannot convert link: Roblox session not initialized.")
            return None

        payload = {"linkId": link_id, "linkType": "Server"}
        headers = {"Referer": BASE_ROBLOX_URL} 

        try:
            async with self.roblox_session.post(SHARELINKS_API, json=payload, headers=headers) as response:

                if response.status == 403 and "X-CSRF-TOKEN" in response.headers:
                    csrf_token = response.headers["X-CSRF-TOKEN"]
                    self.logger.write_log("[SNIPER] Received CSRF token. Retrying link conversion...")
                    self.roblox_session.headers["X-CSRF-TOKEN"] = csrf_token

                    async with self.roblox_session.post(SHARELINKS_API, json=payload, headers=headers) as retry_response:
                        retry_response.raise_for_status() 
                        data = await retry_response.json()
                else:
                    response.raise_for_status() 
                    data = await response.json()

            invite_data = data.get("privateServerInviteData")
            if not invite_data:
                 self.logger.write_log(f"[SNIPER] Invalid response format from sharelinks API: {data}")
                 return None

            if invite_data.get("placeId") != PLACE_ID:
                if self.settings.get("sniper_logs", False):
                    self.logger.write_log(f"[SNIPER] Filtered non-Sols link! Place ID: {invite_data.get('placeId')}")
                return None

            link_code = invite_data.get("linkCode")
            if link_code:
                 self.logger.write_log(f"[SNIPER] Converted share link. Private Server Link Code: {link_code[:5]}...")
                 return link_code
            else:
                 self.logger.write_log(f"[SNIPER] 'linkCode' not found in sharelinks API response: {data}")
                 return None

        except ClientSession.ClientResponseError as e:
             self.logger.write_log(f"[SNIPER] HTTP Error converting share link ({e.status}): {e.message}")
        except asyncio.TimeoutError:
             self.logger.write_log(f"[SNIPER] Timeout converting share link.")
        except Exception as e:
            self.logger.write_log(f"[SNIPER] Unexpected error converting share link: {str(e)}")
        return None

    async def _handle_server_join(self, choice_id: int, server_code: str):
        """Initiates the server join and sets the sniped event."""

        global detected_snipe 
        detected_snipe = True

        join_successful = join_private_server_link(server_code)

        if join_successful:
            self.sniped_event.set() 
            self.logger.write_log(f"[SNIPER] Join command issued for {self.words[choice_id]} server. Sniper event set.")

        else:
             self.logger.write_log(f"[SNIPER] Failed to issue join command for {self.words[choice_id]} server.")

    async def _send_notification(self, choice_id: int, server_code: str, msg_content: str):
        """Sends a notification embed to the primary webhook and forwards it."""
        if not self.main_webhook:
            self.logger.write_log("[SNIPER] Cannot send notification: Main webhook not available.")
            return

        colors = [0xABCDEF, 0xFFB6C1] 
        try:
             color = colors[choice_id]
        except IndexError:
             color = 0x808080 

        embed_link = f"{BASE_ROBLOX_URL}?privateServerLinkCode={server_code}"
        embed = discord.Embed(
            title = f'[{datetime.now().strftime("%H:%M:%S")}] {self.words[choice_id]} Link Sniped!',
            description = f"**Link:** [Click to Join]({embed_link})\n**Code:** `{server_code}`",
            colour = color,
            timestamp=datetime.now()
        )

        original_msg_display = msg_content[:1000] + ("..." if len(msg_content) > 1000 else "")
        embed.add_field(name = "Original Message", value = f"```{original_msg_display}```", inline=False)
        embed.set_footer(text=f"SolsScope v{LOCALVERSION} Sniper")

        content_ping = f"<@{self.settings['mention_id']}>" if self.settings.get("mention", False) and self.settings.get("mention_id", 0) else ""

        try:
            self.main_webhook.send(
                content=content_ping,
                embed=embed
            )
            self.logger.write_log(f"[SNIPER] Sent notification for {self.words[choice_id]} link.")

            forward_webhook_msg(
                primary_webhook_url=self.main_webhook.url,
                secondary_urls=self.settings.get("SECONDARY_WEBHOOK_URLS", []),
                content=content_ping,
                embed=embed
            )

        except Exception as e:
            self.logger.write_log(f"[SNIPER] Error sending notification webhook: {e}")

    async def process_message(self, content: str) -> None:
        """Processes a single message content for sniping."""
        if self.sniped_event.is_set(): 
             return

        try:
            choice_id = self._should_process_message(content)
            if choice_id is None:
                return 

            server_code = await self._extract_server_code(content)
            if not server_code:
                if self.settings.get("sniper_logs", False):
                    self.logger.write_log(f"[SNIPER-{self.channel_id}] Found '{self.words[choice_id]}' keyword but no valid link in: {content[:50]}...")
                return 

            self.logger.write_log(f"[SNIPER-{self.channel_id}] !!! Valid {self.words[choice_id]} message found! Code: {server_code[:5]}... !!!")
            self.logger.write_log(f"[SNIPER-{self.channel_id}] Original content: {content[:100]}...")

            await self._send_notification(choice_id, server_code, content)
            await self._handle_server_join(choice_id, server_code)

        except Exception as e:

            self.logger.write_log(f"[SNIPER-{self.channel_id}] Error processing message: {str(e)}")
            import traceback
            self.logger.write_log(traceback.format_exc()) 

    async def run(self):
        """Main execution loop for the sniper instance."""
        self.is_running = True
        self.logger.write_log(f"[SNIPER-{self.channel_id}] Starting sniper run...")

        if not self.settings.get("sniper_enabled", False):
             self.logger.write_log(f"[SNIPER-{self.channel_id}] Sniper is disabled in settings. Exiting run.")
             self.is_running = False
             return
        if not self.settings.get("ROBLOSECURITY_KEY") or not self.settings.get("DISCORD_TOKEN"):
             self.logger.write_log(f"[SNIPER-{self.channel_id}] ROBLOSECURITY_KEY or DISCORD_TOKEN missing. Exiting run.")
             self.is_running = False
             return

        glitch_enabled = self.settings.get("sniper_toggles", {}).get("Glitched", False)
        dream_enabled = self.settings.get("sniper_toggles", {}).get("Dreamspace", False)
        if not glitch_enabled and not dream_enabled:
            self.logger.write_log(f"[SNIPER-{self.channel_id}] No snipe types (Glitched/Dreamspace) enabled. Exiting run.")
            self.is_running = False
            return

        if not await self.setup():
             self.logger.write_log(f"[SNIPER-{self.channel_id}] Failed initial setup (Roblox Session). Exiting run.")
             self.is_running = False
             return

        ps_link = self.settings.get("private_server_link")
        if ps_link and not self.ps_link_code:
            self.logger.write_log(f"[SNIPER-{self.channel_id}] Resolving own private server link code...")
            self.ps_link_code = await self._extract_server_code(ps_link)
            if self.ps_link_code:
                 self.logger.write_log(f"[SNIPER-{self.channel_id}] Resolved own PS code: {self.ps_link_code[:5]}...")
            else:
                 self.logger.write_log(f"[SNIPER-{self.channel_id}] Failed to resolve own PS code from settings.")

        self.logger.write_log(f"[SNIPER-{self.channel_id}] Starting connection loop. Monitoring channel {self.channel_id} for Glitched: {glitch_enabled}, Dreamspace: {dream_enabled}")
        while not self.stop_event.is_set():
            self.is_running = True 
            try:
                async with connect(DISCORD_WS_BASE, max_size=None, ping_interval=None) as ws:
                    self.logger.write_log(f"[SNIPER-{self.channel_id}] WebSocket connected.")

                    await self._on_message(ws)

            except ConnectionRefusedError:
                self.logger.write_log(f"[SNIPER-{self.channel_id}] Connection refused. Retrying in 15s...")
            except ConnectionAbortedError as e:
                 self.logger.write_log(f"[SNIPER-{self.channel_id}] Connection aborted ({e}). Retrying in 15s...")
            except Exception as e:
                 self.logger.write_log(f"[SNIPER-{self.channel_id}] Unexpected WebSocket error: {e}. Retrying in 15s...")
                 import traceback
                 self.logger.write_log(traceback.format_exc())

            self.is_running = False
            if not self.stop_event.is_set():
                 await asyncio.sleep(15) 

        self.is_running = False
        self.logger.write_log(f"[SNIPER-{self.channel_id}] Stop event received. Cleaning up...")
        if self.roblox_session and not self.roblox_session.closed:
            await self.roblox_session.close()
            self.logger.write_log(f"[SNIPER-{self.channel_id}] Roblox session closed.")
        self.logger.write_log(f"[SNIPER-{self.channel_id}] Sniper stopped.")

_SNIPER_TASKS = []

async def start_snipers(settings, main_webhook, sniped_event, stop_event):
    """Creates and starts Sniper tasks for each configured channel."""
    logger = get_logger()
    global _SNIPER_TASKS
    _SNIPER_TASKS = [] 

    if not settings.get("sniper_enabled", False):
        logger.write_log("Sniper feature is disabled in settings.")
        return

    if not settings.get("ROBLOSECURITY_KEY") or not settings.get("DISCORD_TOKEN"):
        logger.write_log("Sniper cannot start: ROBLOSECURITY_KEY or DISCORD_TOKEN is missing.")
        return

    channel_ids = settings.get("scan_channels", [])
    if not channel_ids:
        logger.write_log("Sniper cannot start: No scan channels configured.")
        return

    logger.write_log(f"Starting {len(channel_ids)} sniper instance(s)...")

    sniper_instances = [
        Sniper(settings, main_webhook, sniped_event, stop_event, channel_id)
        for channel_id in channel_ids
    ]

    _SNIPER_TASKS = [asyncio.create_task(sniper.run()) for sniper in sniper_instances]

    if _SNIPER_TASKS:
        try:
            await asyncio.gather(*_SNIPER_TASKS)
        except Exception as e:
             logger.write_log(f"Error occurred during asyncio.gather for sniper tasks: {e}")

    logger.write_log("All sniper tasks have completed or been cancelled.")

async def stop_snipers():
     """Cancels all active sniper tasks."""
     logger = get_logger()
     global _SNIPER_TASKS
     if not _SNIPER_TASKS:
         logger.write_log("No active sniper tasks to stop.")
         return

     logger.write_log(f"Attempting to cancel {len(_SNIPER_TASKS)} sniper task(s)...")
     cancelled_count = 0
     for task in _SNIPER_TASKS:
         if not task.done():
             task.cancel()
             cancelled_count += 1

     if cancelled_count > 0:
         await asyncio.sleep(1) 

     logger.write_log(f"Cancellation requested for {cancelled_count} sniper task(s). Tasks may take time to fully stop.")
     _SNIPER_TASKS = []


def get_webook_info(webhook_url) -> dict:    
    response = requests.get()
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