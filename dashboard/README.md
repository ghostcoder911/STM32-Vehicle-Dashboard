# STM32 Vehicle Dashboard

A beautiful, real-time web-based dashboard for visualizing data from the STM32 Virtual Vehicle ECU.

## Features

- 🚗 **Realistic Speedometer** - Animated gauge showing vehicle speed (0-200 km/h)
- 🔧 **Tachometer (RPM)** - Engine RPM gauge with red-line zone (0-8000 RPM)
- 🌡️ **Temperature Monitor** - Real-time coolant temperature display with visual warnings
- ⚠️ **Warning Lights** - Engine warning, temperature warning, and turn indicators
- 📊 **Digital Display** - Shows gear, odometer, and trip information
- 🎮 **Control Panel** - Send commands directly to the STM32 board
- 🔄 **Real-time Updates** - WebSocket-based live data streaming

## Requirements

- Python 3.7+
- STM32 board connected via USB (typically `/dev/ttyACM0`)
- Serial communication at 115200 baud

## Installation

1. Install Python dependencies:
```bash
cd dashboard
pip install -r requirements.txt
```

## Usage

### Quick Start

1. Make sure your STM32 board is connected and flashed with the Vehicle ECU firmware

2. Close PuTTY if it's currently open (only one program can access the serial port at a time)

3. Run the dashboard server:
```bash
python app.py
```

4. Open your web browser and navigate to:
```
http://localhost:5000
```

### Using the Dashboard

#### Viewing Data
- The dashboard automatically connects to the STM32 board
- Data updates in real-time (speed, RPM, coolant temperature)
- Warning lights activate automatically based on conditions:
  - **Engine Warning**: RPM > 6000
  - **Temperature Warning**: Coolant > 100°C

#### Sending Commands
Use the control panel buttons to:
- **Get Status**: Request current vehicle status
- **Set Speed 60/100**: Set target vehicle speed
- **Overheat Test**: Inject high coolant temperature for testing
- **Enable/Disable Logging**: Toggle CAN logging on the STM32

You can also send custom commands using the input field at the bottom.

#### Available Commands
- `status` - Get vehicle status
- `veh status` - Get detailed vehicle status
- `veh speed <value>` - Set target speed (e.g., `veh speed 80`)
- `veh cool-hot` - Inject coolant overheat
- `log on` - Enable CAN logging
- `log off` - Disable CAN logging
- `help` - Show all available commands

## Architecture

```
┌─────────────────┐
│  STM32 Board    │
│  (Serial Port)  │
└────────┬────────┘
         │ 115200 baud
         │
┌────────▼────────┐
│  Python Backend │
│  serial_reader  │
└────────┬────────┘
         │
┌────────▼────────┐
│  Flask Server   │
│  + WebSocket    │
└────────┬────────┘
         │
┌────────▼────────┐
│  Web Browser    │
│  Dashboard UI   │
└─────────────────┘
```

## Files

- `app.py` - Flask server with WebSocket support
- `serial_reader.py` - Serial communication handler
- `templates/dashboard.html` - Dashboard HTML structure
- `static/dashboard.css` - Dashboard styling
- `static/dashboard.js` - Dashboard logic and animations
- `requirements.txt` - Python dependencies

## Troubleshooting

### "Permission denied" on serial port
```bash
sudo usermod -a -G dialout $USER
# Log out and log back in
```

Or run with sudo (not recommended):
```bash
sudo python app.py
```

### Serial port not found
Check your serial port:
```bash
ls -la /dev/ttyACM* /dev/ttyUSB*
```

If your board uses a different port, edit `app.py` and change the port parameter in `start_serial_reader()`.

### Dashboard shows "Disconnected"
- Make sure the STM32 board is connected and powered on
- Check that PuTTY or other serial terminals are closed
- Verify the serial port path is correct
- Check that the firmware is flashed on the STM32

### No data updates
- Press the reset button on the STM32 board
- Check the browser console for JavaScript errors (F12)
- Verify the serial connection is working

## Development

To modify the dashboard:

1. **Change serial port**: Edit `app.py`, line with `start_serial_reader()`
2. **Modify gauges**: Edit `static/dashboard.js` functions `drawSpeedometer()` and `drawTachometer()`
3. **Change styling**: Edit `static/dashboard.css`
4. **Add new features**: Edit `templates/dashboard.html` for structure

## License

This project is part of the STM32 Virtual Vehicle ECU project.

## Author

Dashboard created for the STM32 Virtual Vehicle ECU project.
