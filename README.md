# STM32 Virtual Vehicle ECU

A fully modular, RTOS‑based embedded firmware project for the **STM32F446RE (NUCLEO‑F446RE)**.  
This project simulates a simplified automotive Electronic Control Unit (ECU) with:

- ✔ FreeRTOS (CMSIS‑RTOS2)
- ✔ Virtual Vehicle Model (speed, RPM, coolant temp)
- ✔ CAN Telemetry (bxCAN loopback)
- ✔ UART Command Line Interface (CLI)
- ✔ Modular interface design (`vehicle`, `can_if`, `cli_if`)
- ✔ Doxygen‑ready documentation

---

## 🚗 Project Overview

The goal of this project is to mimic the structure of a **real automotive ECU** in a simplified form.  
It includes:

### **1. Virtual Vehicle Model**
- Simulated speed, RPM, coolant temperature
- Update loop driven by a periodic FreeRTOS task
- Adjustable target speed (via CLI)
- Fault injection function (`veh force`)

### **2. CAN Telemetry (Loopback Mode)**
- Encodes vehicle state into an 8‑byte CAN frame
- Uses HAL CAN API with interrupt‑based RX
- RX messages pushed into an RTOS queue
- CAN frames logged via CLI (`log on`)

### **3. UART CLI**
Commands include:
- `help`
- `veh status`
- `veh speed <value>`
- `veh force`
- `log on/off`
- `clear`

---

## 📁 Folder Structure

```
Core/
 ├── Inc/
 │    ├── main.h
 │    ├── vehicle.h
 │    ├── can_if.h
 │    ├── cli_if.h
 │
 └── Src/
      ├── main.c
      ├── vehicle.c
      ├── can_if.c
      ├── cli_if.c

Docs/
 ├── ARCHITECTURE.md
 ├── CLI_COMMANDS.md
 ├── VEHICLE_MODEL.md
 ├── CAN_PROTOCOL.md
 └── CHANGELOG.md
```

---

## 🛠 Requirements

- **STM32CubeIDE**
- NUCLEO‑F446RE development board
- USB cable
- UART terminal (115200 8‑N‑1)
- *(Optional)* CAN analyzer (not required because loopback mode is used)

---

## ▶️ How to Run

1. Clone the repository:
   ```
   git clone https://github.com/karangandhi-projects/stm32-virtual-vehicle-ecu.git
   ```

2. Open the project using **STM32CubeIDE**.

3. Build + flash the firmware.

4. Open PuTTY / TeraTerm at **115200 8‑N‑1**.

5. You should see:
   ```
   CLI Ready
   ```

6. Try commands:
   ```
   help
   veh status
   veh speed 60
   log on
   ```

---

## 🧪 Example CAN Frame (Loopback)

```
CAN RX: ID=0x100 DLC=6
DATA:  A0 00  1B 07  58 02  00 00
```

Decoded:
- Speed     → 16.0 km/h  
- RPM       → 1819  
- Coolant   → 60.0 °C

---

## 📄 Doxygen Support

All header + source files include:
- `@brief`
- `@param`
- `@return`
- Module descriptions

Use:
```
doxygen Doxyfile
```

---

## 🧩 Future Extensions

You can expand this ECU with:

- PID cruise control
- Multiple CAN frames (wheel speeds, throttle, gear)
- UDS diagnostics (0x7DF request/response)
- CAN FD upgrade (on supported MCUs)
- Simulated faults + diagnostic trouble codes
- Telemetry streaming over BLE/WiFi

---
STM32 Project credits:
**Karan Gandhi**  
Embedded Systems Engineer  
GitHub: https://github.com/karangandhi-projects
Stm code base available in this repo.

---

## 📌 Version

See `Docs/CHANGELOG.md` for full history.

Vehicle Dashboard - Quick Start Guide
Your STM32 Vehicle Dashboard can be accessed at:
http://localhost:5000

The browser should have opened automatically. If not, open your web browser and navigate to the URL above.

🎮 How to Use the Dashboard
Real-Time Monitoring
The dashboard automatically displays:

Speedometer (Left) - Vehicle speed from 0-200 km/h
Green: Normal speeds (0-60 km/h)
Orange: Moderate speeds (60-120 km/h)
Red: High speeds (120-200 km/h)

Tachometer (Right) - Engine RPM from 0-8000

Green: Normal operation (0-3000 RPM)
Orange: High RPM (3000-6000 RPM)
Red: Critical zone (6000-8000 RPM)

Temperature Gauge (Center) - Coolant temperature

Blue: Normal (< 80°C)
Orange: Warm (80-100°C)
Red: Overheating (> 100°C)

Warning Lights

🔧 ENGINE: Activates when RPM > 6000
🌡️ TEMP: Activates when coolant > 100°C
◀ ▶ Indicators: Turn signal indicators (for future use)
Control Panel
Use the buttons to control your STM32 board:

Get Status - Request current vehicle data
Set Speed 60/100 - Set target vehicle speed
🔥 Overheat Test - Test high temperature warning
Enable/Disable Logging - Toggle CAN logging
You can also type custom commands in the input field and press Enter.

🔧 Testing the Dashboard
Try these commands to see the dashboard in action:

Click "Get Status" - See current values
Click "Set Speed 60" - Watch speedometer animate to 60 km/h
Click "Set Speed 100" - Watch it increase to 100 km/h
Click "Overheat Test" - See temperature warning activate
Type veh speed 120 in the custom command box - Set custom speed
📊 Dashboard Features
Live Updates
Data refreshes automatically every 0.5 seconds
Smooth gauge animations
Real-time warning light activation
Visual Indicators
Connection Status (Top right)
🟢 Green: Connected to STM32
🔴 Red: Disconnected
Gauges
Canvas-based analog gauges
Needle animations with smooth interpolation
Color-coded zones for safety
🛑 Stopping the Dashboard
To stop the dashboard server:

Go to the terminal where it's running
Press Ctrl+C
To restart: bash cd dashboard python app.py

Or use the startup script: bash cd dashboard ./run_dashboard.sh

🔍 Troubleshooting
Dashboard shows "Disconnected"
Check: Is your STM32 board connected?
Try: Press the reset button on the board
Verify: Run ls /dev/ttyACM* to check the serial port
No data updates
Refresh the browser page
Check the browser console (F12) for errors
Restart the dashboard server
Serial port access error
If you see "Permission denied": ```bash sudo usermod -a -G dialout $USER

Then log out and log back in
```

PuTTY conflict
Only one program can access the serial port at a time. Make sure PuTTY is closed: bash pkill putty

📁 Dashboard Files
All dashboard files are located in: /home/neeraj/Documents/Dashboard/stm32-virtual-vehicle-ecu/dashboard/

app.py - Main server application
serial_reader.py - Serial communication handler
templates/dashboard.html - Dashboard UI
static/dashboard.css - Styling
static/dashboard.js - Logic and animations
requirements.txt - Python dependencies
README.md - Detailed documentation
🎨 Customization
Change Serial Port
Edit app.py, line 54: python start_serial_reader(port='/dev/ttyACM0', baudrate=115200)

Modify Gauge Ranges
Edit static/dashboard.js: - Speedometer max: Line 100 (const maxSpeed = 200;) - Tachometer max: Line 185 (const maxRpm = 8000;)

Change Update Frequency
Edit serial_reader.py, line 122: python time.sleep(0.5) # Change to desired interval

🚀 Next Steps
Test different speeds: Try various speed commands
Monitor temperature: Watch the coolant temperature gauge
Test warnings: Push the RPM above 6000 to see engine warning
Custom commands: Experiment with the CLI commands
📚 Need Help?
Check dashboard/README.md for detailed documentation
Review STM32 CLI commands in vehicle_ecu_docs/CLI_COMMANDS.md
Check serial communication in vehicle_ecu_docs/ARCHITECTURE.md
Enjoy your Vehicle Dashboard! 🚗💨
