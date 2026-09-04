import serial
import time
import random

try:
    s = serial.Serial('COM12', 115200, timeout=1)
    # Don't assert DTR/RTS to avoid holding standard ESP32 boards in reset
    s.setDTR(False)
    s.setRTS(False)
    print("Opened COM10.")
    time.sleep(2)
    
    for i in range(20):
        # Generate random positions for 10 servos between 1000 and 3000 (safe range)
        positions = [f"{motor_id}:{random.randint(1000, 3000)}" for motor_id in range(1, 11)]
        command_str = "P," + ",".join(positions)
        
        print(f"Sending: {command_str}")
        s.write((command_str + "\n").encode('utf-8'))
        
        time.sleep(1.0) # Wait 1 second between movements
        
        while s.in_waiting:
            print("Response:", s.readline().decode('utf-8', errors='ignore').strip())
            
    s.close()
    print("Done. Snake should have wiggled!")
except Exception as e:
    print("Error:", e)
