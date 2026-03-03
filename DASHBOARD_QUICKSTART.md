# Vehicle Dashboard - Quick Start Guide

## ✅ Dashboard is Now Running!

Your STM32 Vehicle Dashboard is now live and accessible at:

**http://localhost:5000**

The browser should have opened automatically. If not, open your web browser and navigate to the URL above.

---

## 🎮 How to Use the Dashboard

### Real-Time Monitoring

The dashboard automatically displays:

1. **Speedometer** (Left) - Vehicle speed from 0-200 km/h
   - Green: Normal speeds (0-60 km/h)
   - Orange: Moderate speeds (60-120 km/h)
   - Red: High speeds (120-200 km/h)

2. **Tachometer** (Right) - Engine RPM from 0-8000
   - Green: Normal operation (0-3000 RPM)
   - Orange: High RPM (3000-6000 RPM)
   - Red: Critical zone (6000-8000 RPM)

3. **Temperature Gauge** (Center) - Coolant temperature
   - Blue: Normal (< 80°C)
   - Orange: Warm (80-100°C)
   - Red: Overheating (> 100°C)

4. **Warning Lights**
   - 🔧 **ENGINE**: Activates when RPM > 6000
   - 🌡️ **TEMP**: Activates when coolant > 100°C
   - ◀ ▶ **Indicators**: Turn signal indicators (for future use)

### Control Panel

Use the buttons to control your STM32 board:

- **Get Status** - Request current vehicle data
- **Set Speed 60/100** - Set target vehicle speed
- **🔥 Overheat Test** - Test high temperature warning
- **Enable/Disable Logging** - Toggle CAN logging

You can also type custom commands in the input field and press Enter.

---

## 🔧 Testing the Dashboard

Try these commands to see the dashboard in action:

1. Click **"Get Status"** - See current values
2. Click **"Set Speed 60"** - Watch speedometer animate to 60 km/h
3. Click **"Set Speed 100"** - Watch it increase to 100 km/h
4. Click **"Overheat Test"** - See temperature warning activate
5. Type `veh speed 120` in the custom command box - Set custom speed

---

## 📊 Dashboard Features

### Live Updates
- Data refreshes automatically every 0.5 seconds
- Smooth gauge animations
- Real-time warning light activation

### Visual Indicators
- **Connection Status** (Top right)
  - 🟢 Green: Connected to STM32
  - 🔴 Red: Disconnected

### Gauges
- Canvas-based analog gauges
- Needle animations with smooth interpolation
- Color-coded zones for safety

---

## 🛑 Stopping the Dashboard

To stop the dashboard server:

1. Go to the terminal where it's running
2. Press **Ctrl+C**

To restart:
```bash
cd dashboard
python app.py
```

Or use the startup script:
```bash
cd dashboard
./run_dashboard.sh
```

---

## 🔍 Troubleshooting

### Dashboard shows "Disconnected"
- **Check**: Is your STM32 board connected?
- **Try**: Press the reset button on the board
- **Verify**: Run `ls /dev/ttyACM*` to check the serial port

### No data updates
- **Refresh** the browser page
- **Check** the browser console (F12) for errors
- **Restart** the dashboard server

### Serial port access error
If you see "Permission denied":
```bash
sudo usermod -a -G dialout $USER
# Then log out and log back in
```

### PuTTY conflict
Only one program can access the serial port at a time. Make sure PuTTY is closed:
```bash
pkill putty
```

---

## 📁 Dashboard Files

All dashboard files are located in:
```
/home/neeraj/Documents/Dashboard/stm32-virtual-vehicle-ecu/dashboard/
```

- `app.py` - Main server application
- `serial_reader.py` - Serial communication handler
- `templates/dashboard.html` - Dashboard UI
- `static/dashboard.css` - Styling
- `static/dashboard.js` - Logic and animations
- `requirements.txt` - Python dependencies
- `README.md` - Detailed documentation

---

## 🎨 Customization

### Change Serial Port
Edit `app.py`, line 54:
```python
start_serial_reader(port='/dev/ttyACM0', baudrate=115200)
```

### Modify Gauge Ranges
Edit `static/dashboard.js`:
- Speedometer max: Line 100 (`const maxSpeed = 200;`)
- Tachometer max: Line 185 (`const maxRpm = 8000;`)

### Change Update Frequency
Edit `serial_reader.py`, line 122:
```python
time.sleep(0.5)  # Change to desired interval
```

---

## 🚀 Next Steps

1. **Test different speeds**: Try various speed commands
2. **Monitor temperature**: Watch the coolant temperature gauge
3. **Test warnings**: Push the RPM above 6000 to see engine warning
4. **Custom commands**: Experiment with the CLI commands

---

## 📚 Need Help?

- Check `dashboard/README.md` for detailed documentation
- Review STM32 CLI commands in `vehicle_ecu_docs/CLI_COMMANDS.md`
- Check serial communication in `vehicle_ecu_docs/ARCHITECTURE.md`

---

**Enjoy your Vehicle Dashboard!** 🚗💨
