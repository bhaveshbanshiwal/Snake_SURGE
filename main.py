#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys
import os

from dynamixel_sdk import *

from src.snake_locomotion import SnakeKinematics
from src.obstacle_avoidance import ObstacleAvoidance

if sys.platform.startswith('win'):
    DEVICENAME          = 'COM3'
else:
    DEVICENAME          = '/dev/ttyUSB0'  
BAUDRATE            = 57600
PROTOCOL_VERSION    = 2.0

NUM_MOTORS          = 10  

ADDR_TORQUE_ENABLE      = 64
ADDR_GOAL_POSITION      = 116
ADDR_PRESENT_CURRENT    = 126

def init_motors(packetHandler, portHandler):
    for dxl_id in range(1, NUM_MOTORS + 1):
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, 1)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to enable torque for motor {dxl_id}. Is it connected?")
        else:
            print(f"Torque enabled for motor {dxl_id}")

def disable_motors(packetHandler, portHandler):
    for dxl_id in range(1, NUM_MOTORS + 1):
        packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, 0)

def main():
    print("--- SURGE-SNAKE Initializing ---")
    
    portHandler = PortHandler(DEVICENAME)
    packetHandler = PacketHandler(PROTOCOL_VERSION)
    
    if not portHandler.openPort() or not portHandler.setBaudRate(BAUDRATE):
        print("Failed to open port. Check connection and COM port.")
        return

    init_motors(packetHandler, portHandler)
    
    kinematics = SnakeKinematics(num_motors=NUM_MOTORS)
    avoidance = ObstacleAvoidance(current_threshold=350)
    
    start_time = time.time()
    
    print("\nStarting Main Control Loop. Press Ctrl+C to stop.")
    try:
        while True:
            current_time = time.time() - start_time
            
            motor_currents = {}
            for dxl_id in range(1, NUM_MOTORS + 1):
                cur, _, _ = packetHandler.read2ByteTxRx(portHandler, dxl_id, ADDR_PRESENT_CURRENT)
                if cur > 32767:
                    cur -= 65536
                motor_currents[dxl_id] = cur
                
            current_state = avoidance.process_state(current_time, motor_currents)
            
            target_positions = kinematics.calculate_positions(current_time, mode=current_state)
                
            for dxl_id, pos in target_positions.items():
                packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_POSITION, pos)
                
            time.sleep(0.02)
            
    except KeyboardInterrupt:
        print("\nHalting Snake...")
    finally:
        disable_motors(packetHandler, portHandler)
        portHandler.closePort()
        print("Shutdown complete.")

if __name__ == '__main__':
    main()