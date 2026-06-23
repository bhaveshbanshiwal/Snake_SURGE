import time
from src.dynamixel_interface import DynamixelInterface
from src.snake_locomotion import SnakeKinematics

def run_hardware():
    """Initializes hardware and runs a continuous sine wave loop on Dynamixels."""
    print("Initializing Snake SURGE Hardware Engine...")
    
    hardware = DynamixelInterface(num_motors=10, port='COM3', baudrate=57600)
    connected, msg = hardware.connect()
    
    if not connected:
        print(f"HARDWARE ERROR: {msg}")
        return

    print("Hardware Connected. Torque Enabled.")
    print("WARNING: Snake is active. Press Ctrl+C to emergency stop.")

    kinematics = SnakeKinematics(num_motors=10)
    start_time = time.time()
    
    try:
        while True:
            current_time = time.time() - start_time
            positions, _ = kinematics.calculate_positions(current_time)
            hardware.write_positions(positions)
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nEmergency Stop Triggered.")
        hardware.disconnect()
        print("Hardware Shutdown Safely.")

if __name__ == "__main__":
    run_hardware()