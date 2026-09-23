import time
import math
import sys
import serial.tools.list_ports
import platform

# Import the interface from the existing codebase
from src.st3215_interface import ST3215Interface

def main():
    print("="*50)
    print(" Snake SURGE - Slow Sine Wave Test")
    print("="*50)
    
    # 1. Auto-detect COM port just like the main app does
    default_port = 'COM12' if platform.system() == 'Windows' else '/dev/ttyUSB0'
    for p in serial.tools.list_ports.comports():
        if 'AMA' not in p.device and 'Bluetooth' not in p.description:
            default_port = p.device
            break
            
    print(f"Connecting to ESP32 Bridge on port {default_port}...")
    
    # 2. Initialize Hardware Interface
    iface = ST3215Interface(num_motors=10, port=default_port)
    success, msg = iface.connect()
    
    if not success:
        print(f"Failed to connect: {msg}")
        sys.exit(1)
        
    print("Connected successfully. Starting slow sine wave test.")
    print("Press Ctrl+C to stop.")
    
    try:
        start_time = time.time()
        
        # --- TEST PARAMETERS ---
        # 4096 total range, 2048 is center. 
        # Amplitude of 300 is approx +/- 26 degrees. This is small enough to prevent it from biting its own tail.
        amplitude = 300       
        # Very slow frequency (0.2 Hz = 1 full wave every 5 seconds)
        frequency = 0.2       
        # Phase shift between consecutive motors to create a smooth traveling wave instead of all moving together
        phase_offset = 0.6    
        
        while True:
            t = time.time() - start_time
            
            positions = {}
            for i in range(1, 11):
                # Calculate sine wave for each motor with a phase shift
                sine_val = math.sin(2 * math.pi * frequency * t - (i * phase_offset))
                
                # Convert to ST3215 position
                pos = 2048 + int(amplitude * sine_val)
                positions[i] = pos
                
            # Send positions to servos
            iface.write_positions(positions)
            
            # Print loads for the first 4 motors so you can monitor if they are getting overloaded
            telemetry = iface.read_telemetry()
            if telemetry:
                loads = [f"M{m}:{telemetry.get(m, {}).get('load', 0)}" for m in range(1, 5)]
                print(f"Time: {t:.1f}s | Loads: {' '.join(loads)}    ", end='\r')
            
            # Update at 20Hz
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\nStopping test...")
    finally:
        # Gracefully center all motors on exit so it doesn't stay twisted
        print("Centering motors before exit...")
        center_pos = {i: 2048 for i in range(1, 11)}
        iface.write_positions(center_pos)
        time.sleep(0.5)
        iface.disconnect()
        print("Hardware Shutdown Complete.")

if __name__ == "__main__":
    main()
