import time
from dynamixel_sdk import *

class DynamixelInterface:
    """Hardware interface for connecting to and controlling Dynamixel servos."""
    def __init__(self, num_motors=10, port='COM3', baudrate=57600):
        self.num_motors = num_motors
        self.port_name = port
        self.baudrate = baudrate
        self.protocol_version = 2.0
        self.ADDR_TORQUE_ENABLE = 64
        self.ADDR_GOAL_POSITION = 116
        self.ADDR_PRESENT_CURRENT = 126
        self.ADDR_PRESENT_VELOCITY = 128
        self.ADDR_PRESENT_POSITION = 132
        self.portHandler = PortHandler(self.port_name)
        self.packetHandler = PacketHandler(self.protocol_version)
        self.is_connected = False
        
    def connect(self):
        """Opens serial port and enables torque for all motors."""
        if not self.portHandler.openPort():
            return False, f"Failed to open port {self.port_name}"
        if not self.portHandler.setBaudRate(self.baudrate):
            return False, "Failed to change baudrate"
        for dxl_id in range(1, self.num_motors + 1):
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, dxl_id, self.ADDR_TORQUE_ENABLE, 1)
            if dxl_comm_result != COMM_SUCCESS:
                print(f"Failed to enable torque on ID {dxl_id}")
        self.is_connected = True
        return True, "Connected successfully"
        
    def disconnect(self):
        """Disables motor torque and closes serial port."""
        if self.is_connected:
            for dxl_id in range(1, self.num_motors + 1):
                self.packetHandler.write1ByteTxRx(self.portHandler, dxl_id, self.ADDR_TORQUE_ENABLE, 0)
            self.portHandler.closePort()
            self.is_connected = False
            
    def write_positions(self, positions_dict):
        """Writes target encoder ticks to all motors."""
        if not self.is_connected: return
        for dxl_id, pos in positions_dict.items():
            self.packetHandler.write4ByteTxRx(self.portHandler, dxl_id, self.ADDR_GOAL_POSITION, int(pos))
            
    def read_telemetry(self):
        """Reads load, velocity, and position from all motors."""
        telemetry = {}
        if not self.is_connected: return telemetry
        for dxl_id in range(1, self.num_motors + 1):
            cur, _, _ = self.packetHandler.read2ByteTxRx(self.portHandler, dxl_id, self.ADDR_PRESENT_CURRENT)
            if cur > 32767: cur -= 65536
            vel, _, _ = self.packetHandler.read4ByteTxRx(self.portHandler, dxl_id, self.ADDR_PRESENT_VELOCITY)
            if vel > 2147483647: vel -= 4294967296
            pos, _, _ = self.packetHandler.read4ByteTxRx(self.portHandler, dxl_id, self.ADDR_PRESENT_POSITION)
            telemetry[dxl_id] = {'load': cur, 'velocity': vel, 'position': pos}
        return telemetry
