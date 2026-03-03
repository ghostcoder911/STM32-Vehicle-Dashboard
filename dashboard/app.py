"""
Vehicle Dashboard Server
Flask application with WebSocket support for real-time vehicle data updates
"""

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from serial_reader import SerialReader
import time
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vehicle-dashboard-secret-2026'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global serial reader instance
serial_reader = None


def on_vehicle_data(data):
    """Callback function when new vehicle data is received"""
    # Broadcast data to all connected clients
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
    # Start serial reader
    print("Starting Vehicle Dashboard Server...")
    start_serial_reader()
    
    # Start Flask-SocketIO server
    print("Dashboard will be available at http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
