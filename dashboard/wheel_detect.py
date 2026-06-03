"""Detect Logitech G29 USB mode (PS3 vs PS4) on Linux."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class WheelUsbInfo:
    vendor: str
    product: str
    mode: str  # "ps3", "ps4", "unknown"
    pedals_likely_work: bool
    message: str


def get_g29_usb_info() -> Optional[WheelUsbInfo]:
    try:
        out = subprocess.check_output(["lsusb", "-d", "046d:"], text=True, timeout=5)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None

    for line in out.splitlines():
        if "g29" not in line.lower() and "c24f" not in line.lower() and "c260" not in line.lower():
            continue
        m = re.search(r"ID (\w+):(\w+)", line)
        if not m:
            continue
        vendor, product = m.group(1), m.group(2)
        if product.lower() == "c24f":
            return WheelUsbInfo(
                vendor=vendor,
                product=product,
                mode="ps3",
                pedals_likely_work=True,
                message="G29 in PS3 mode — pedals should work on Linux.",
            )
        if product.lower() == "c260":
            return WheelUsbInfo(
                vendor=vendor,
                product=product,
                mode="ps4",
                pedals_likely_work=False,
                message=(
                    "G29 is in PS4 mode (USB 046d:c260). Linux usually does NOT "
                    "report pedal movement in this mode."
                ),
            )
    return None


def print_ps4_mode_help() -> None:
    print("")
    print("=" * 60)
    print("  G29 PEDALS NOT WORKING — SWITCH TO PS3 MODE")
    print("=" * 60)
    print("  1. Unplug the USB cable from the PC")
    print("  2. On the wheel BASE, move the switch from PS4 → PS3")
    print("     (small switch behind the wheel, near the LED strip)")
    print("  3. Plug USB back in")
    print("  4. Run:  lsusb | grep -i logitech")
    print("     You should see 046d:c24f (not c260)")
    print("  5. Restart the dashboard")
    print("=" * 60)
    print("")
