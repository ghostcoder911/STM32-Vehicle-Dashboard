"""
Vehicle Dashboard Server
Flask application with WebSocket support for real-time vehicle data updates
"""

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from serial_reader import SerialReader
from gamepad_reader import GamepadReader
from wheel_drive import WheelDriveController

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vehicle-dashboard-secret-2026'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global reader instances
serial_reader = None
gamepad_reader = None
wheel_drive = None


def on_vehicle_data(data):
    """Callback function when new vehicle data is received"""
    if wheel_drive and 'speed' in data:
        wheel_drive.sync_speed_from_vehicle(data['speed'])
    socketio.emit('vehicle_update', data, namespace='/')


@app.route('/')
def index():
    """Serve the dashboard HTML page"""
    return render_template('dashboard.html')


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    # Send current data immediately upon connection
    if serial_reader:
        data = serial_reader.get_last_data()
        emit('vehicle_update', data)
    emit('wheel_status', {
        'connected': gamepad_reader.connected if gamepad_reader else False,
        'device': gamepad_reader.device_name if gamepad_reader else '',
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


@socketio.on('send_command')
def handle_command(data):
    """Handle command from dashboard"""
    command = data.get('command', '')
    if serial_reader and command:
        serial_reader.send_command(command)
        print(f"Sent command from web: {command}")


@socketio.on('engine_state')
def handle_engine_state(data):
    """Browser reports engine on/off so wheel pedals can drive speed."""
    if wheel_drive:
        wheel_drive.set_engine(bool(data.get('running', False)))


def _on_wheel_pedals(accel: float, brake: float):
    if wheel_drive:
        wheel_drive.update_pedals(accel, brake)

    socketio.emit('wheel_pedals', {
        'accelerator': round(accel, 3),
        'brake': round(brake, 3),
    }, namespace='/')


def _on_wheel_button(button: str, pressed: bool):
    socketio.emit('wheel_button', {
        'button': button,
        'pressed': pressed,
    }, namespace='/')


def start_wheel_drive():
    global wheel_drive
    if not serial_reader:
        return
    wheel_drive = WheelDriveController(
        send_command=serial_reader.send_command,
        get_speed=lambda: serial_reader.get_last_data().get('speed', 0.0),
    )
    wheel_drive.start()


def start_gamepad_reader():
    """Initialize racing wheel input (Logitech G29, etc.)."""
    global gamepad_reader
    gamepad_reader = GamepadReader(_on_wheel_pedals, _on_wheel_button)
    if gamepad_reader.start():
        socketio.emit('wheel_status', {
            'connected': True,
            'device': gamepad_reader.device_name,
        })
    return gamepad_reader.connected


def start_serial_reader(port='/dev/ttyACM0', baudrate=115200):
    """Initialize and start the serial reader"""
    global serial_reader
    
    serial_reader = SerialReader(port=port, baudrate=baudrate)
    
    if serial_reader.connect():
        serial_reader.start_reading(callback=on_vehicle_data)
        print(f"Serial reader started on {port}")
        return True
    else:
        print(f"Failed to connect to {port}")
        return False


if __name__ == '__main__':
    print("Starting Vehicle Dashboard Server...")
    start_serial_reader()
    start_wheel_drive()
    start_gamepad_reader()

    print("Dashboard will be available at http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
