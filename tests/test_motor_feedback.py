#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script to read Dynamixel internal feedback (position, velocity, current).
Used to baseline normal load vs obstacle stall current.
"""

import time
from dynamixel_sdk import *

import sys

# --- Configuration ---
DXL_ID                      = 1                 # Motor ID to test
BAUDRATE                    = 57600             
if sys.platform.startswith('win'):
    DEVICENAME              = 'COM3'
else:
    DEVICENAME              = '/dev/ttyUSB0'

# XL330-M288 Control Table Addresses
ADDR_TORQUE_ENABLE          = 64
ADDR_GOAL_POSITION          = 116
ADDR_PRESENT_POSITION       = 132
ADDR_PRESENT_VELOCITY       = 128
ADDR_PRESENT_CURRENT        = 126

PROTOCOL_VERSION            = 2.0
TORQUE_ENABLE               = 1
TORQUE_DISABLE              = 0

def test_feedback():
    portHandler = PortHandler(DEVICENAME)
    packetHandler = PacketHandler(PROTOCOL_VERSION)

    if not portHandler.openPort() or not portHandler.setBaudRate(BAUDRATE):
        print("Failed to open port/baudrate")
        quit()

    # Enable Torque
    packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
    print(f"Torque enabled on Motor {DXL_ID}")
    
    print("\n--- Reading Feedback (Press Ctrl+C to stop) ---")
    print("Try applying light resistance to the motor horn to see current spike.")
    
    try:
        # Move motor to center (2048 for 0-4095 range)
        packetHandler.write4ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_POSITION, 2048)
        
        while True:
            # Read Present Position (4 bytes)
            dxl_present_position, _, _ = packetHandler.read4ByteTxRx(portHandler, DXL_ID, ADDR_PRESENT_POSITION)
            
            # Read Present Velocity (4 bytes)
            dxl_present_velocity, _, _ = packetHandler.read4ByteTxRx(portHandler, DXL_ID, ADDR_PRESENT_VELOCITY)
            
            # Read Present Current (2 bytes)
            dxl_present_current, _, _ = packetHandler.read2ByteTxRx(portHandler, DXL_ID, ADDR_PRESENT_CURRENT)
            
            # Current comes as unsigned 16bit, handle sign for XL330
            if dxl_present_current > 32767:
                dxl_present_current -= 65536
            
            # In XL330, 1 unit = 1.0 mA
            print(f"Pos: {dxl_present_position:04d} | Vel: {dxl_present_velocity:04d} | Current (mA): {dxl_present_current:04d}")
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopping test...")
    finally:
        # Disable Torque
        packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
        portHandler.closePort()
        print("Test concluded safely.")

if __name__ == '__main__':
    test_feedback()
