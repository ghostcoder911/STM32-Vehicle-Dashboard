# Vehicle Controls Guide

## 🚗 Interactive Vehicle Controls

Your dashboard now includes realistic vehicle controls that simulate driving a real car!

---

## 🔧 Engine Start/Stop Switch

**Location:** Left section of Vehicle Controls

**How to Use:**
1. Click the circular **START** button to start the engine
2. The button turns **green** when the engine is running
3. The text changes to **STOP**
4. Click again to turn off the engine

**Important:**
- You must start the engine before you can accelerate
- Turning off the engine will stop the vehicle and disable indicators

---

## 🚀 Acceleration Pedal (Gas)

**Location:** Center section, left pedal (GREEN)

**How to Use:**
- **Press and hold** the gas pedal (click and hold)
- The vehicle will gradually accelerate
- Speed increases by 5 km/h every 200ms while pressed
- Maximum speed: 180 km/h
- Release to stop accelerating

**Visual Feedback:**
- Pedal moves down when pressed
- Speedometer needle moves up
- Gear display changes automatically (1-6)

**Note:** Engine must be running to accelerate!

---

## 🛑 Brake Pedal

**Location:** Center section, right pedal (RED)

**How to Use:**
- **Press and hold** the brake pedal (click and hold)
- The vehicle will decelerate
- Speed decreases by 8 km/h every 200ms while pressed
- Minimum speed: 0 km/h
- Brake works even if engine is off

**Visual Feedback:**
- Pedal turns bright red when pressed
- Pedal moves down
- Speedometer needle moves down

---

## ◀️ ▶️ Turn Indicators

**Location:** Right section of Vehicle Controls

### Left Indicator
- Click **LEFT** button to activate left turn signal
- Warning light on dashboard blinks green
- Click again to turn off

### Right Indicator
- Click **RIGHT** button to activate right turn signal
- Warning light on dashboard blinks green
- Click again to turn off

**Behavior:**
- Only one indicator can be active at a time
- Activating one side automatically turns off the other
- Engine must be running to use indicators

---

## ⚠️ Hazard Lights

**Location:** Center of indicators section (triangle icon)

**How to Use:**
- Click the **HAZARD** button
- Both left and right indicators activate simultaneously
- Button turns orange and blinks
- Click again to turn off

**Use Cases:**
- Emergency situations
- Parking
- Warning other vehicles

**Note:** Hazard lights override individual turn signals

---

## 🎮 Automatic Features

### Gear Display
The gear display automatically changes based on your speed:
- **P** (Park): Engine off
- **N** (Neutral): Engine on, speed = 0
- **1**: 0-20 km/h
- **2**: 20-40 km/h
- **3**: 40-60 km/h
- **4**: 60-80 km/h
- **5**: 80-100 km/h
- **6**: 100+ km/h

### Warning Lights
- **Engine Warning** (Orange): Activates when RPM > 6000
- **Temperature Warning** (Red): Activates when coolant > 100°C

---

## 💡 Tips & Tricks

### Smooth Driving
1. Start the engine
2. Tap the gas pedal briefly for gentle acceleration
3. Hold longer for faster acceleration
4. Use brake to slow down gradually

### Quick Stop
1. Release gas pedal
2. Hold brake pedal until speed reaches 0

### Highway Driving
1. Hold gas pedal until you reach desired speed (e.g., 120 km/h)
2. Release pedal
3. Vehicle maintains speed (sent to STM32)

### Testing Indicators
1. Start engine
2. Click LEFT indicator - watch dashboard light blink
3. Click RIGHT indicator - left turns off, right blinks
4. Click HAZARD - both blink together

---

## 🎯 Control Flow

```
1. Click START button
   ↓
2. Engine turns ON (green)
   ↓
3. Hold GAS pedal
   ↓
4. Speed increases (0 → 180 km/h)
   ↓
5. Gear changes automatically (1 → 6)
   ↓
6. Release GAS, hold BRAKE
   ↓
7. Speed decreases (→ 0 km/h)
   ↓
8. Click STOP button
   ↓
9. Engine turns OFF
```

---

## ⌨️ Keyboard Shortcuts

Currently, controls are mouse/touch only. Future updates may include:
- Arrow keys for acceleration/braking
- Space bar for brake
- Q/E for indicators
- H for hazard

---

## 🔧 Technical Details

### Update Frequency
- Pedal commands sent every 200ms while pressed
- Smooth acceleration: +5 km/h per update
- Smooth braking: -8 km/h per update

### Speed Limits
- Minimum: 0 km/h
- Maximum: 180 km/h
- Acceleration rate: 25 km/h per second
- Braking rate: 40 km/h per second

### STM32 Commands Sent
- Engine Start: `veh speed 0`
- Acceleration: `veh speed X` (where X increases)
- Braking: `veh speed X` (where X decreases)
- Engine Stop: `veh speed 0`

---

## 🐛 Troubleshooting

### Pedals Not Working
- **Check:** Is the engine started?
- **Try:** Click the START button first
- **Verify:** Connection status shows "Connected"

### Indicators Not Working
- **Check:** Is the engine running?
- **Try:** Start the engine first
- **Note:** Indicators require engine to be on

### Speed Not Changing
- **Check:** Is the STM32 board connected?
- **Try:** Click "Get Status" button
- **Verify:** Check browser console (F12) for errors

### Pedal Stuck
- **Solution:** Release mouse button
- **Alternative:** Refresh the browser page

---

## 🎨 Visual Feedback

### Engine Switch
- **OFF:** Red border, dark background, "START" text
- **ON:** Green border, bright background, "STOP" text, glowing effect

### Gas Pedal
- **Normal:** Dark green
- **Pressed:** Moves down, icon shifts

### Brake Pedal
- **Normal:** Dark red
- **Pressed:** Bright red, moves down, icon shifts

### Indicators
- **OFF:** Gray, dim
- **ON:** Green, blinking, glowing effect

### Hazard
- **OFF:** Gray, dim
- **ON:** Orange, blinking, glowing effect

---

## 📊 Dashboard Integration

All controls are fully integrated with the dashboard:
- **Speedometer** reflects acceleration/braking
- **Tachometer** shows engine RPM
- **Gear Display** changes automatically
- **Warning Lights** activate based on conditions
- **Temperature Gauge** monitors coolant temp

---

**Enjoy your realistic driving experience!** 🚗💨

For more information, see the main README.md in the dashboard folder.
