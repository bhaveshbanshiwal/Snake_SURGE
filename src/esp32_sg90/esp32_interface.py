import serial
import time

class DynamixelInterface:
    """
    Hardware interface for connecting to an ESP32 controlling SG90 servos via serial.
    This class is named DynamixelInterface to act as a drop-in replacement 
    for the original dynamixel_interface.py used by app.py.
    """
    def __init__(self, num_motors=10, port='COM3', baudrate=115200):
        self.num_motors = num_motors
        self.port_name = port
        self.baudrate = baudrate
        self.serial_port = None
        self.is_connected = False
        
    def connect(self):
        """Opens serial port to the ESP32."""
        try:
            self.serial_port = serial.Serial(self.port_name, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for ESP32 to reset upon serial connection
            self.is_connected = True
            return True, "Connected successfully"
        except Exception as e:
            return False, f"Failed to open port {self.port_name}: {e}"
            
    def disconnect(self):
        """Closes serial port."""
        if self.is_connected and self.serial_port:
            self.serial_port.close()
            self.is_connected = False
            
    def write_positions(self, positions_dict):
        """
        Translates target encoder ticks (Dynamixel 0-4095 range) to ESP32 PWM pulse widths 
        for SG90 servos (500us to 2500us) and sends them over serial.
        
        Dynamixel: 2048 is center (180 degrees for XL330, but SG90 is only 0-180 degrees total).
        We'll map 1024 -> 500us (0 deg), 2048 -> 1500us (90 deg center), 3072 -> 2500us (180 deg).
        """
        if not self.is_connected: return
        
        for motor_id, pos in positions_dict.items():
            # Map the dynamixel tick position to SG90 pulse width (us)
            # Center: 2048 -> 1500us
            # Range: 1024-3072 ticks maps to 500-2500us
            
            pulse_width = int(((pos - 1024) * 2000 / 2048) + 500)
            
            # Clamp to safe SG90 limits
            pulse_width = max(500, min(2500, pulse_width))
            
            # Send command in format: <motor_id>:<pulse_width>\n
            command = f"{motor_id}:{pulse_width}\n"
            self.serial_port.write(command.encode('utf-8'))
            
    def read_telemetry(self):
        """
        SG90 servos do not have hardware telemetry (no load, velocity, or position feedback).
        We return empty/zeroed telemetry to keep compatibility with app.py.
        """
        telemetry = {}
        if not self.is_connected: return telemetry
        for motor_id in range(1, self.num_motors + 1):
            # Return dummy telemetry so app.py doesn't crash expecting these keys
            telemetry[motor_id] = {'load': 0, 'velocity': 0, 'position': 2048}
        return telemetry
