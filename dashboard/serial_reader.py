"""
Serial Reader Module for STM32 Vehicle ECU Dashboard
Reads data from the STM32 board via serial port and parses vehicle data.
"""

import serial
import re
import time
import threading
from typing import Dict, Optional, Callable


class SerialReader:
    """Handles serial communication with STM32 board"""
    
    def __init__(self, port: str = '/dev/ttyACM0', baudrate: int = 115200):
        """
        Initialize serial reader
        
        Args:
            port: Serial port path (e.g., '/dev/ttyACM0')
            baudrate: Baud rate (default: 115200)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_conn: Optional[serial.Serial] = None
        self.running = False
        self.read_thread: Optional[threading.Thread] = None
        self.data_callback: Optional[Callable] = None
        self.last_data = {
            'speed': 0.0,
            'rpm': 0,
            'coolant': 0.0,
            'warning': False,
            'connected': False
        }
        
    def connect(self) -> bool:
        """
        Connect to the serial port
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            time.sleep(2)  # Wait for connection to stabilize
            self.last_data['connected'] = True
            print(f"Connected to {self.port} at {self.baudrate} baud")
            return True
        except Exception as e:
            print(f"Error connecting to serial port: {e}")
            self.last_data['connected'] = False
            return False
    
    def disconnect(self):
        """Disconnect from the serial port"""
        self.running = False
        if self.read_thread:
            self.read_thread.join(timeout=2)
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("Disconnected from serial port")
        self.last_data['connected'] = False
    
    def send_command(self, command: str):
        """
        Send a command to the STM32 board
        
        Args:
            command: Command string to send
        """
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(f"{command}\r\n".encode())
                print(f"Sent command: {command}")
            except Exception as e:
                print(f"Error sending command: {e}")
    
    def parse_vehicle_data(self, line: str) -> Optional[Dict]:
        """
        Parse vehicle data from serial output
        
        Args:
            line: Line of text from serial port
            
        Returns:
            Dictionary with parsed data or None
        """
        data = {}
        
        # Parse speed (e.g., "Speed   : 42.5 km/h" or "  Speed   : 42.5 km/h")
        speed_match = re.search(r'Speed\s*:\s*([\d.]+)\s*km/h', line)
        if speed_match:
            data['speed'] = float(speed_match.group(1))
        
        # Parse RPM (e.g., "RPM     : 1900" or "  RPM     : 1900")
        rpm_match = re.search(r'RPM\s*:\s*(\d+)', line)
        if rpm_match:
            data['rpm'] = int(rpm_match.group(1))
        
        # Parse coolant temperature (e.g., "Coolant : 68.3 C" or "  Coolant : 68.3 C")
        coolant_match = re.search(r'Coolant\s*:\s*([\d.]+)\s*C', line)
        if coolant_match:
            data['coolant'] = float(coolant_match.group(1))
        
        return data if data else None
    
    def read_loop(self):
        """Continuous reading loop (runs in separate thread)"""
        buffer = ""
        
        # Send initial status command to start getting data
        self.send_command("status")
        
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.in_waiting > 0:
                    chunk = self.serial_conn.read(self.serial_conn.in_waiting).decode('utf-8', errors='ignore')
                    buffer += chunk
                    
                    # Process line by line
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        
                        if line:
                            # Parse vehicle data
                            parsed = self.parse_vehicle_data(line)
                            if parsed:
                                self.last_data.update(parsed)
                                
                                # Check for warning conditions
                                if self.last_data['coolant'] > 100:
                                    self.last_data['warning'] = True
                                else:
                                    self.last_data['warning'] = False
                                
                                # Trigger callback if registered
                                if self.data_callback:
                                    self.data_callback(self.last_data)
                
                # Periodically request status update
                time.sleep(0.5)
                self.send_command("status")
                
            except Exception as e:
                print(f"Error in read loop: {e}")
                self.last_data['connected'] = False
                time.sleep(1)
    
    def start_reading(self, callback: Optional[Callable] = None):
        """
        Start reading data in a background thread
        
        Args:
            callback: Optional callback function to be called with new data
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            print("Serial port not connected!")
            return
        
        self.data_callback = callback
        self.running = True
        self.read_thread = threading.Thread(target=self.read_loop, daemon=True)
        self.read_thread.start()
        print("Started reading from serial port")
    
    def get_last_data(self) -> Dict:
        """
        Get the most recent vehicle data
        
        Returns:
            Dictionary with vehicle data
        """
        return self.last_data.copy()


if __name__ == "__main__":
    # Test the serial reader
    reader = SerialReader()
    
    def print_data(data):
        print(f"Speed: {data['speed']} km/h, RPM: {data['rpm']}, Coolant: {data['coolant']}°C")
    
    if reader.connect():
        reader.start_reading(callback=print_data)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping...")
            reader.disconnect()
