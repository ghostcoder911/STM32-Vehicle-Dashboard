"""
Logitech G29 axis/button mapping (Linux).

PS3 mode (USB 046d:c24f): 4 axes, all pedals rest at -1.0, pressed → +1.0
Calibrated on this system:
  - axis 0: steering
  - axis 1: brake
  - axis 2: accelerator (gas)
  - axis 3: clutch (not used for speed)
"""

DEVICE_NAME_MATCH = "logitech g29"

AXIS_STEERING = 0
AXIS_ACCELERATOR = 2
AXIS_BRAKE = 3
AXIS_CLUTCH = 1

# evdev ABS codes (PS3 mode)
EVDEV_ACCELERATOR = 2   # ABS_Z
EVDEV_BRAKE = 1         # ABS_Y
EVDEV_CLUTCH = 3        # ABS_RX

PEDAL_PRESS_THRESHOLD = 0.10
PEDAL_RELEASE_THRESHOLD = 0.05
PEDAL_ANALOG_INTERVAL_SEC = 0.05

BUTTON_L2 = 7
BUTTON_R2 = 6
BUTTON_R3 = 10

POLL_INTERVAL_SEC = 0.02
