#!/usr/bin/env python3
"""Print connected joystick axes/buttons (useful for remapping gamepad_config.py)."""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame


def main():
    pygame.init()
    pygame.joystick.init()
    n = pygame.joystick.get_count()
    if n == 0:
        print("No joysticks found.")
        return 1
    for i in range(n):
        j = pygame.joystick.Joystick(i)
        j.init()
        print(f"[{i}] {j.get_name()}")
        print(f"    axes={j.get_numaxes()} buttons={j.get_numbuttons()}")
    j = pygame.joystick.Joystick(0)
    j.init()
    print("\nMove pedals / press L2, R2, R3 (Ctrl+C to stop)...")
    prev_a = [j.get_axis(k) for k in range(j.get_numaxes())]
    prev_b = [j.get_button(k) for k in range(j.get_numbuttons())]
    try:
        while True:
            pygame.event.pump()
            for k in range(j.get_numaxes()):
                v = j.get_axis(k)
                if abs(v - prev_a[k]) > 0.03:
                    print(f"  axis {k}: {v:.3f}")
                    prev_a[k] = v
            for k in range(j.get_numbuttons()):
                v = j.get_button(k)
                if v != prev_b[k]:
                    print(f"  button {k}: {v}")
                    prev_b[k] = v
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
