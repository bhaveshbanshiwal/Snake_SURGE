import os
import sys
from dynamixel_sdk import *

PROTOCOL_VERSION = 2.0               
BAUDRATE = 57600             

if sys.platform.startswith('win'):
    DEVICENAME = 'COM3'
else:
    DEVICENAME = '/dev/ttyUSB0'

def ping_motors():
    """Pings Dynamixel motors to ensure USB/TTL communication is working."""
    portHandler = PortHandler(DEVICENAME)
    packetHandler = PacketHandler(PROTOCOL_VERSION)

    if portHandler.openPort():
        print(f"Succeeded to open the port: {DEVICENAME}")
    else:
        print(f"Failed to open the port: {DEVICENAME}. Check COM port or permissions.")
        quit()

    if portHandler.setBaudRate(BAUDRATE):
        print(f"Succeeded to change the baudrate to {BAUDRATE}")
    else:
        print("Failed to change the baudrate")
        quit()

    print("\n--- Pinging Motors (Broadcast) ---")
    found_motors = []
    for dxl_id in range(1, 11):
        dxl_model_number, dxl_comm_result, dxl_error = packetHandler.ping(portHandler, dxl_id)
        if dxl_comm_result == COMM_SUCCESS:
            print(f"[SUCCESS] Pinged Motor ID: {dxl_id} | Model Number: {dxl_model_number}")
            found_motors.append(dxl_id)

    if len(found_motors) == 0:
        print("[WARNING] No motors found. Check power to U2D2 PHB and TTL cables.")
    else:
        print(f"Found {len(found_motors)} motors ready for operation.")

    portHandler.closePort()

if __name__ == '__main__':
    ping_motors()
