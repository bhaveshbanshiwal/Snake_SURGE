import time
import sys
from pathlib import Path
import serial
import serial.tools.list_ports
import platform

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def find_esp32_port():
    default_port = 'COM12' if platform.system() == 'Windows' else '/dev/ttyUSB0'
    for p in serial.tools.list_ports.comports():
        if 'AMA' not in p.device and 'Bluetooth' not in p.description:
            return p.device
    return default_port

def main():
    print("=" * 60)
    print(" Snake SURGE - ST3215 Bus Diagnostic Tool")
    print("=" * 60)
    
    port = find_esp32_port()
    print(f"Connecting to ESP32 on port {port} at 115200 baud...")
    
    try:
        ser = serial.Serial(port, 115200, timeout=1.5)
        time.sleep(2.0)  # Allow ESP32 to finish reset
    except Exception as e:
        print(f"ERROR: Could not open port {port}: {e}")
        print("Ensure the ESP32 is plugged in via USB and no other program (Arduino IDE / App) has the port open.")
        sys.exit(1)
        
    print("Connected. Listening for ESP32 boot/scan logs (5 seconds)...")
    start = time.time()
    while time.time() - start < 5.0:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"  [ESP32]: {line}")
        time.sleep(0.05)
        
    print("\nSending Telemetry Poll ('T') to force motor response check...")
    ser.reset_input_buffer()
    ser.write(b"T\n")
    
    resp = ser.readline().decode('utf-8', errors='ignore').strip()
    print(f"Raw Response: '{resp}'\n")
    
    if resp.startswith("T,"):
        parts = [p for p in resp[2:].split(',') if p]
        if not parts:
            print(">>> RESULT: ZERO motors responded! (Bus is silent or IDs mismatched)")
        else:
            print(f">>> RESULT: Successfully detected {len(parts)} motor(s):")
            for part in parts:
                vals = part.split(':')
                if len(vals) == 4:
                    m_id, load, vel, pos = vals
                    print(f"    - Motor ID {m_id:2s} -> Position: {pos:4s} | Load: {load:4s} | Speed: {vel:4s}")
    else:
        print(">>> RESULT: No valid telemetry packet received.")
        
    print("\n--- Diagnostic Checks to verify ---")
    print("1. If using Waveshare ESP32 board, check the 'Mode' switch: MUST be in Mode A (UART/ESP32), NOT Mode B (USB).")
    print("2. If testing new motors out of the box, disconnect all but ONE motor to rule out ID=1 bus collision.")
    print("3. Ensure ESP32 GND and Motor Power Supply GND are bridged together.")
    print("4. Verify 3-pin X3P cable polarity (DATA / VCC / GND).")
    
    ser.close()

if __name__ == "__main__":
    main()
