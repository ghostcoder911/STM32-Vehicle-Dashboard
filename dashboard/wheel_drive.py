"""
Applies G29 pedal input to vehicle speed via serial (server-side, reliable).
"""

from __future__ import annotations

import threading
import time
from typing import Optional

import gamepad_config as cfg


class WheelDriveController:
    def __init__(self, send_command, get_speed, max_speed: float = 180.0):
        self._send_command = send_command
        self._get_speed = get_speed
        self._max_speed = max_speed
        self._accel = 0.0
        self._brake = 0.0
        self._target_speed = 0.0
        self._engine_on = False
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def set_engine(self, on: bool) -> None:
        with self._lock:
            self._engine_on = on
            if not on:
                self._target_speed = 0.0
                self._accel = 0.0

    def update_pedals(self, accel: float, brake: float) -> None:
        with self._lock:
            self._accel = accel
            self._brake = brake

    def sync_speed_from_vehicle(self, speed: float) -> None:
        with self._lock:
            # Only sync if pedals are not being pressed significantly
            # This prevents serial feedback from fighting against user input
            if self._accel < cfg.PEDAL_PRESS_THRESHOLD and self._brake < cfg.PEDAL_PRESS_THRESHOLD:
                self._target_speed = speed
            else:
                # If pedals are pressed, we only sync if the difference is huge (e.g. manual reset)
                if abs(self._target_speed - speed) > 50.0:
                    self._target_speed = speed

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

    def _loop(self) -> None:
        last_sent = -1
        while self._running:
            time.sleep(0.2)
            with self._lock:
                accel = self._accel
                brake = self._brake
                engine_on = self._engine_on
                speed = self._target_speed

            # Prioritize braking if brake is pressed significantly
            if brake > cfg.PEDAL_PRESS_THRESHOLD and brake > accel:
                speed = max(0.0, speed - 10.0 * brake)
            # Accelerate if gas is pressed and engine is on
            elif accel > cfg.PEDAL_PRESS_THRESHOLD:
                if engine_on:
                    speed = min(self._max_speed, speed + 6.0 * accel)
                else:
                    pass # Engine must be on
            # Natural deceleration if engine is on but no pedals pressed
            elif engine_on and speed > 0:
                speed = max(0.0, speed - 2.5)

            speed_i = int(round(speed))
            with self._lock:
                self._target_speed = float(speed_i)

            if speed_i != last_sent:
                self._send_command(f"veh speed {speed_i}")
                last_sent = speed_i
