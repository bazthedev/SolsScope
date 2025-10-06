"""
SolsScope/Baz's Macro
Created by Meklows
v2.0.0
Support server: https://discord.gg/8khGXqG7nA
"""

from __future__ import annotations
from typing import Dict, Tuple, Iterable
import os
import json
import difflib
import mss
import numpy as np
import cv2
import threading
import easyocr
import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

from constants import MACROPATH
# ---------------------------------------------------------
# Globals
# ---------------------------------------------------------


# ---------------------------------------------------------
# Utils
# ---------------------------------------------------------


_thread_local = threading.local()

def _ensure_sct() -> mss:
    if not hasattr(_thread_local, "_sct"):
        _thread_local._sct = mss.mss()
    return _thread_local._sct

def capture_region(rect: Iterable[float]) -> np.ndarray:
    l, t, w, h = map(int, rect)
    if w <= 0 or h <= 0:
        raise ValueError(f"Invalid region size: {rect}")
    frame = np.array(_ensure_sct().grab({
        "left": l, "top": t, "width": w, "height": h
    }))[:, :, :3]
    return frame

def max_channel_lum(img: np.ndarray) -> np.ndarray:
    return np.max(img, axis=2).astype("uint8")

def get_valid_groups() -> list:
    try:
        with open(f"{MACROPATH}/valid_lists.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {}
# ---------------------------------------------------------
# OCR + Validation
# ---------------------------------------------------------
def match_valid_item(text: str, group: str) -> str:
    
    """Fuzzy match OCR text against the selected group list."""
    if not text:
        return "[invalid]"

    # Map alias
    if group == "validPotions":
        group = "craftingPotions"

    choices = get_valid_groups().get(group, get_valid_groups()["validInventoryItems"])
    match = difflib.get_close_matches(text, choices, n=1, cutoff=0.6)
    return match[0] if match else "[invalid]"

def run_ocr_on_image(image : np.ndarray, group: str, reader : easyocr.Reader) -> str:
    results = reader.readtext(image)
    texts = [txt for (_, txt, conf) in results]
    joined = " ".join(texts) if texts else ""
    return match_valid_item(joined, group)

def _pad_image_gray(img: np.ndarray, pad: int) -> np.ndarray:
    """Pad a single-channel image with constant black border."""
    if pad <= 0:
        return img
    return cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def read_ocr(
    reader : easyocr.Reader,
    locations: Dict[str, Tuple[int, int, int, int, str]],
    scale_up: float = 1.0,
    pad: int = 0,
) -> Dict[str, str]:
    """
    locations:
      {
        "slot1": (x,y,w,h),
        "slot2": (x,y,w,h,"validAuras"),
        "slot3": (x,y,w,h,"craftingPotions"),
      }

    scale_up: magnification factor applied to the luminance image before OCR (e.g., 1.5, 2.0, 3.0)
    pad: pixels of black border added around the luminance image before scaling
    """
    results: Dict[str, tuple[str]] = {}

    # sanitize knobs
    try:
        scale_up = float(scale_up)
    except Exception:
        scale_up = 1.0
    if scale_up <= 0:
        scale_up = 1.0
    try:
        pad = int(pad)
    except Exception:
        pad = 0
    pad = max(0, pad)

    for key, values in locations.items():
        try:
            if len(values) == 5:
                x, y, w, h, group = values
            else:
                x, y, w, h = values
                group = "validInventoryItems"

            #print(f"\n[DEBUG] Processing {key}: rect=({x},{y},{w},{h}), group={group}")
            img = capture_region((x, y, w, h))

            raw_path = f"{MACROPATH}/temp/raw_{key}.png"
            cv2.imwrite(str(raw_path), img)

            # Max-channel luminance -> pad -> scale
            lum = max_channel_lum(img)

            if pad > 0:
                lum = _pad_image_gray(lum, pad)

            if scale_up != 1.0:
                # Use fx/fy so we don't need integer size
                lum = cv2.resize(lum, None, fx=scale_up, fy=scale_up, interpolation=cv2.INTER_CUBIC)

            lum_path = f"{MACROPATH}/temp/lum_{key}.png"
            cv2.imwrite(str(lum_path), lum)
            #print(f"[DEBUG] Saved lum {lum_path}: shape={lum.shape}, scale_up={scale_up}, pad={pad}")

            matched = run_ocr_on_image(lum, group, reader)
            results[key] = matched
            #print(f"[OCR-{group}] {key}: {matched}")

        except Exception as e:
            print(f"[ERROR] Could not process {key}: {e}")
            results[key] = "[error]"

    return results