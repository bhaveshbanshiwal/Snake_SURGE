#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script to ping Dynamixel motors.
Ensures USB connection to U2D2 and TTL communication is working safely.
"""

import os
from dynamixel_sdk import * # Uses Dynamixel SDK library

# --- Configuration ---
# Protocol version for XL330 is 2.0
PROTOCOL_VERSION            = 2.0               

# Default baudrate of XL330 is 57600
BAUDRATE                    = 57600             

import sys

# Change this to your U2D2 COM port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
if sys.platform.startswith('win'):
    DEVICENAME          = 'COM3'
else:
    DEVICENAME          = '/dev/ttyUSB0'

def ping_motors():
    # Initialize PortHandler and PacketHandler
    portHandler = PortHandler(DEVICENAME)
    packetHandler = PacketHandler(PROTOCOL_VERSION)

    # Open port
    if portHandler.openPort():
        print(f"Succeeded to open the port: {DEVICENAME}")
    else:
        print(f"Failed to open the port: {DEVICENAME}. Check COM port or permissions.")
        quit()

    # Set port baudrate
    if portHandler.setBaudRate(BAUDRATE):
        print(f"Succeeded to change the baudrate to {BAUDRATE}")
    else:
        print("Failed to change the baudrate")
        quit()

    print("\n--- Pinging Motors (Broadcast) ---")
    # Ping all IDs (1 to 10)
    found_motors = []
    for dxl_id in range(1, 11):
        dxl_model_number, dxl_comm_result, dxl_error = packetHandler.ping(portHandler, dxl_id)
        if dxl_comm_result == COMM_SUCCESS:
            print(f"[SUCCESS] Pinged Motor ID: {dxl_id} | Model Number: {dxl_model_number}")
            found_motors.append(dxl_id)
        else:
            pass # Just silently skip motors that aren't there

    if len(found_motors) == 0:
        print("[WARNING] No motors found. Check power to U2D2 PHB and TTL cables.")
    else:
        print(f"Found {len(found_motors)} motors ready for operation.")

    portHandler.closePort()

if __name__ == '__main__':
    ping_motors()
