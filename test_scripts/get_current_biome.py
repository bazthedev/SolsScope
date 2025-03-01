import os
import json
import glob
import shutil
import tempfile
import re

def get_latest_hovertext(logs_dir):
    
    log_files = glob.glob(os.path.join(logs_dir, "*.log"))
    if not log_files:
        return None

    latest_log_file = max(log_files, key=os.path.getctime)

    try:
        temp_file = os.path.join(tempfile.gettempdir(), "roblox_log_copy.log")
        shutil.copy2(latest_log_file, temp_file)
    except PermissionError:
        return None

    json_pattern = re.compile(r'\{.*\}')
    last_hover_text = None

    try:
        with open(temp_file, "r", encoding="utf-8") as file:
            for line in reversed(file.readlines()):
                match = json_pattern.search(line)
                if match:
                    try:
                        json_data = json.loads(match.group())
                        hover_text = json_data.get("data", {}).get("largeImage", {}).get("hoverText")
                        if hover_text:
                            return hover_text
                    except json.JSONDecodeError:
                        continue
    except Exception:
        return None
    
    return last_hover_text

rblx_logs_dir = os.path.expandvars(r"%localappdata%\\Roblox\\logs")
latest_hovertext = get_latest_hovertext(rblx_logs_dir)

if latest_hovertext:
    print(f"Most Recent Biome: {latest_hovertext}")
else:
    print("No Biome found.")
