"""
Reads Logitech G29 pedals/buttons via evdev (preferred) or pygame fallback.
"""

from __future__ import annotations

import os
import select
import threading
import time
from typing import Callable, Optional

import gamepad_config as cfg
from wheel_detect import get_g29_usb_info, print_ps4_mode_help

try:
    import pygame
except ImportError:
    pygame = None

try:
    from evdev import InputDevice, ecodes, list_devices
except ImportError:
    InputDevice = None  # type: ignore


def _normalize_released_low(axis_value: float) -> float:
    """
    G29 pedals on Linux can rest at -1.0 or +1.0 depending on driver/mode.
    If they rest at +1.0 and go to -1.0 when pressed: (1.0 - v) / 2.0
    If they rest at -1.0 and go to +1.0 when pressed: (v + 1.0) / 2.0
    
    Based on debug logs, they rest at 1.0 on this system.
    """
    return max(0.0, min(1.0, (1.0 - axis_value) / 2.0))


def _normalize_evdev(value: int, maximum: int = 255) -> float:
    if maximum <= 0:
        return 0.0
    return max(0.0, min(1.0, value / float(maximum)))


class GamepadReader:
    def __init__(self, on_pedals: Callable[[float, float], None],
                 on_button: Callable[[str, bool], None]):
        self._on_pedals = on_pedals
        self._on_button = on_button
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._device_name = ""
        self._backend = ""
        self._joystick = None
        self._evdev: Optional[InputDevice] = None
        self._accel_val = 0.0
        self._brake_val = 0.0
        self._prev_buttons: dict[int, bool] = {}
        self._last_emit = 0.0

    @property
    def connected(self) -> bool:
        return self._running

    @property
    def device_name(self) -> str:
        return self._device_name

    def _find_evdev(self) -> Optional[InputDevice]:
        if InputDevice is None:
            return None
        match = cfg.DEVICE_NAME_MATCH.lower()
        for path in list_devices():
            dev = InputDevice(path)
            if match in dev.name.lower():
                self._device_name = dev.name
                return dev
        return None

    def _find_pygame(self):
        if pygame is None:
            return None
        pygame.init()
        pygame.joystick.init()
        match = cfg.DEVICE_NAME_MATCH.lower()
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            if match in joy.get_name().lower() or pygame.joystick.get_count() == 1:
                self._device_name = joy.get_name()
                return joy
            joy.quit()
        return None

    def start(self) -> bool:
        if self._running:
            return True

        usb = get_g29_usb_info()
        if usb and not usb.pedals_likely_work:
            print(f"Gamepad WARNING: {usb.message}")
            print_ps4_mode_help()

        # Prefer pygame on Linux — matches /dev/input/js0 used by most G29 setups
        self._joystick = self._find_pygame()
        if self._joystick is not None:
            self._backend = "pygame"
        self._running = True
        self._thread = threading.Thread(target=self._pygame_loop, daemon=True)
        self._thread.start()
        print(f"Gamepad: connected via pygame to {self._device_name}")
        self._log_idle_axes()
        return True

        self._evdev = self._find_evdev()
        if self._evdev is not None:
            self._backend = "evdev"
            self._running = True
            self._thread = threading.Thread(target=self._evdev_loop, daemon=True)
            self._thread.start()
            print(f"Gamepad: connected via evdev to {self._device_name}")
            return True

        print("Gamepad: no racing wheel found")
        return False

    def _log_idle_axes(self) -> None:
        if not self._joystick:
            return
        pygame.event.pump()
        axes = [round(self._joystick.get_axis(i), 3) for i in range(self._joystick.get_numaxes())]
        print(f"Gamepad: idle axes {axes} (pedals usually on axes with value -1.0)")

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
        if self._joystick:
            self._joystick.quit()
            self._joystick = None
        if self._evdev:
            self._evdev.close()
            self._evdev = None

    def _emit_pedals(self, force: bool = False) -> None:
        now = time.time()
        if force or (now - self._last_emit) >= cfg.PEDAL_ANALOG_INTERVAL_SEC:
            self._last_emit = now
            self._on_pedals(self._accel_val, self._brake_val)

    def _update_pedal_values(self, accel: float, brake: float) -> None:
        changed = (
            abs(accel - self._accel_val) > 0.01
            or abs(brake - self._brake_val) > 0.01
        )
        self._accel_val = accel
        self._brake_val = brake
        if changed:
            self._emit_pedals(force=True)
        else:
            self._emit_pedals()

    def _evdev_loop(self) -> None:
        dev = self._evdev
        abs_max = {
            cfg.EVDEV_ACCELERATOR: 255,
            cfg.EVDEV_BRAKE: 255,
        }
        for code, info in dev.capabilities().get(ecodes.EV_ABS, []):
            if code in abs_max:
                abs_max[code] = info.max or 255

        try:
            ai = dev.absinfo(cfg.EVDEV_ACCELERATOR)
            self._accel_val = _normalize_evdev(ai.value, abs_max[cfg.EVDEV_ACCELERATOR])
        except (OSError, TypeError):
            pass
        try:
            ai = dev.absinfo(cfg.EVDEV_BRAKE)
            self._brake_val = _normalize_evdev(ai.value, abs_max[cfg.EVDEV_BRAKE])
        except (OSError, TypeError):
            pass
        self._emit_pedals(force=True)

        while self._running and dev:
            try:
                r, _, _ = select.select([dev], [], [], cfg.POLL_INTERVAL_SEC)
                if r:
                    for event in dev.read():
                        if event.type != ecodes.EV_ABS:
                            continue
                        if event.code == cfg.EVDEV_ACCELERATOR:
                            self._accel_val = _normalize_evdev(
                                event.value, abs_max[cfg.EVDEV_ACCELERATOR])
                        elif event.code == cfg.EVDEV_BRAKE:
                            self._brake_val = _normalize_evdev(
                                event.value, abs_max[cfg.EVDEV_BRAKE])
                try:
                    self._accel_val = _normalize_evdev(
                        dev.absinfo(cfg.EVDEV_ACCELERATOR).value,
                        abs_max[cfg.EVDEV_ACCELERATOR])
                    self._brake_val = _normalize_evdev(
                        dev.absinfo(cfg.EVDEV_BRAKE).value,
                        abs_max[cfg.EVDEV_BRAKE])
                except (OSError, TypeError):
                    pass
                self._emit_pedals()
            except (OSError, ValueError) as exc:
                print(f"Gamepad evdev error: {exc}")
                time.sleep(0.5)

    def _pygame_loop(self) -> None:
        button_map = {
            cfg.BUTTON_L2: "l2",
            cfg.BUTTON_R2: "r2",
            cfg.BUTTON_R3: "r3",
        }
        self._prev_buttons = {
            cfg.BUTTON_L2: False,
            cfg.BUTTON_R2: False,
            cfg.BUTTON_R3: False,
        }

        while self._running and self._joystick:
            pygame.event.pump()
            joy = self._joystick

            accel = _normalize_released_low(joy.get_axis(cfg.AXIS_ACCELERATOR))
            brake = _normalize_released_low(joy.get_axis(cfg.AXIS_BRAKE))
            self._update_pedal_values(accel, brake)

            for btn_id, label in button_map.items():
                if btn_id >= joy.get_numbuttons():
                    continue
                pressed = bool(joy.get_button(btn_id))
                prev = self._prev_buttons.get(btn_id, False)
                if pressed != prev:
                    self._prev_buttons[btn_id] = pressed
                    self._on_button(label, pressed)

            time.sleep(cfg.POLL_INTERVAL_SEC)
