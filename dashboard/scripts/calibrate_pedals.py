#!/usr/bin/env python3
"""
Interactive G29 pedal calibration — run with dashboard STOPPED.
Prints which pygame/evdev axis changes when you press each pedal.
"""

import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROMPTS = [
    ("ACCELERATOR (gas) only", 8),
    ("BRAKE only", 8),
    ("CLUTCH only", 8),
    ("ALL pedals released", 3),
]


def monitor_pygame(duration: float, label: str) -> dict:
    import pygame

    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print("  ERROR: No joystick found")
        return {}

    joy = pygame.joystick.Joystick(0)
    joy.init()
    n = joy.get_numaxes()
    baseline = [joy.get_axis(i) for i in range(n)]
    min_v = baseline[:]
    max_v = baseline[:]
    print(f"  [{label}] Watching {n} axes for {duration:.0f}s...")

    t0 = time.time()
    while time.time() - t0 < duration:
        pygame.event.pump()
        for i in range(n):
            v = joy.get_axis(i)
            min_v[i] = min(min_v[i], v)
            max_v[i] = max(max_v[i], v)
            if abs(v - baseline[i]) > 0.03:
                norm = (v + 1.0) / 2.0
                print(f"    axis {i}: {baseline[i]:7.4f} -> {v:7.4f}  (norm={norm:.3f})")
                baseline[i] = v
        time.sleep(0.01)

    changed = {}
    for i in range(n):
        delta = max_v[i] - min_v[i]
        if delta > 0.05:
            changed[i] = {
                "min": min_v[i],
                "max": max_v[i],
                "delta": delta,
                "norm_max": (max_v[i] + 1.0) / 2.0,
            }
    return changed


def monitor_evdev(duration: float, label: str) -> dict:
    try:
        from evdev import InputDevice, ecodes, list_devices
    except ImportError:
        print("  (evdev not installed — skipping)")
        return {}

    dev = None
    for path in list_devices():
        d = InputDevice(path)
        if "g29" in d.name.lower() or "logitech" in d.name.lower():
            dev = d
            break
    if not dev:
        return {}

    abs_codes = {
        ecodes.ABS_Z: "ABS_Z",
        ecodes.ABS_RX: "ABS_RX",
        ecodes.ABS_RY: "ABS_RY",
        ecodes.ABS_RZ: "ABS_RZ",
        ecodes.ABS_X: "ABS_X",
        ecodes.ABS_Y: "ABS_Y",
    }
    baseline = {}
    max_v = {}
    for code, name in abs_codes.items():
        try:
            baseline[code] = dev.absinfo(code).value
            max_v[code] = baseline[code]
        except (OSError, TypeError):
            pass

    print(f"  [{label}] evdev {dev.path} for {duration:.0f}s...")
    import select

    t0 = time.time()
    while time.time() - t0 < duration:
        r, _, _ = select.select([dev], [], [], 0.05)
        if r:
            for event in dev.read():
                if event.type == ecodes.EV_ABS and event.code in abs_codes:
                    name = abs_codes[event.code]
                    old = baseline.get(event.code, 0)
                    if event.value != old:
                        print(f"    {name}: {old} -> {event.value}")
                        baseline[event.code] = event.value
                    max_v[event.code] = max(max_v.get(event.code, 0), event.value)
        for code in list(baseline.keys()):
            try:
                v = dev.absinfo(code).value
                max_v[code] = max(max_v.get(code, 0), v)
            except (OSError, TypeError):
                pass
        time.sleep(0.02)

    changed = {}
    for code, name in abs_codes.items():
        if code not in baseline:
            continue
        delta = max_v.get(code, 0) - baseline.get(code, 0)
        if abs(delta) > 5 or max_v.get(code, 0) > 10:
            changed[name] = {"start": baseline[code], "max": max_v.get(code, 0), "delta": delta}
    return changed


def main():
    print("=" * 60)
    print("  G29 PEDAL CALIBRATION")
    print("  Make sure the dashboard is NOT running.")
    print("=" * 60)
    try:
        import pygame
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count():
            j = pygame.joystick.Joystick(0)
            j.init()
            print(f"\nDevice: {j.get_name()}")
            print(f"Axes: {j.get_numaxes()}, Buttons: {j.get_numbuttons()}")
            print("Idle:", [round(j.get_axis(i), 4) for i in range(j.get_numaxes())])
    except Exception as e:
        print(f"pygame error: {e}")
        return 1

    all_pygame = {}
    for prompt, secs in PROMPTS:
        print(f"\n>>> NOW PRESS: {prompt}")
        print("    (starting in 2 seconds...)")
        time.sleep(2)
        ch = monitor_pygame(secs, prompt)
        if ch:
            print(f"    Summary: axes with movement: {ch}")
            for ax, info in ch.items():
                all_pygame.setdefault(ax, []).append((prompt, info))
        else:
            print("    Summary: NO axis movement detected")

        monitor_evdev(secs, prompt)

    print("\n" + "=" * 60)
    print("FINAL RECOMMENDATION (pygame):")
    print("=" * 60)
    for ax in sorted(all_pygame.keys()):
        for prompt, info in all_pygame[ax]:
            print(f"  axis {ax}: {prompt}  delta={info['delta']:.3f}  max_norm={info['norm_max']:.3f}")

    gas_axes = []
    brake_axes = []
    for ax, entries in all_pygame.items():
        for prompt, _ in entries:
            if "ACCELERATOR" in prompt:
                gas_axes.append(ax)
            if "BRAKE" in prompt and "ACCELERATOR" not in prompt:
                brake_axes.append(ax)

    if gas_axes:
        print(f"\n  Suggested AXIS_ACCELERATOR = {gas_axes[0]}")
    if brake_axes:
        print(f"  Suggested AXIS_BRAKE = {brake_axes[0]}")
    if not gas_axes and not brake_axes:
        print("\n  Could not auto-detect — no pedal movement seen.")
        print("  Check: pedals plugged into wheel base, USB connected, dashboard stopped.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
