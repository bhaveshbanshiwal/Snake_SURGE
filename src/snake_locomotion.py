import math

class SnakeKinematics:
    def __init__(self, num_motors=10, center_pos=2048):
        """
        Initialize the Snake Kinematics engine.
        Now matches the continuous serpenoid math from the PyBullet simulation.
        """
        self.num_motors = num_motors
        self.center_pos = center_pos
        
        # Locomotion parameters (standardized to SI/radians to match simulation)
        self.amplitude = 0.8       # Amplitude in radians
        self.frequency = 2.0       # Frequency in rad/s
        self.phase_shift = 1.0     # Phase difference between joints
        self.turn_offset = 0.0     # Turning bias in radians

        # Dynamixel XL330 0-4095 represents 0-360 degrees. 
        self.ticks_per_radian = 4096.0 / (2.0 * math.pi)

    def calculate_positions(self, current_time, turn_offset=None):
        """
        Calculates the target position for each motor at time `current_time`.
        Returns:
            positions (dict): Motor ID (1 to num_motors) -> Goal position (0-4095)
            angles (dict): Motor ID -> raw target angle in radians (for simulation)
        """
        positions = {}
        angles = {}
        
        if turn_offset is not None:
            self.turn_offset = turn_offset
            
        for i in range(self.num_motors): 
            # Exact formula from simulate.py
            target_angle = (self.amplitude * math.sin(self.frequency * current_time - i * self.phase_shift)) + self.turn_offset
            
            # Map radian angle to Dynamixel ticks
            ticks = self.center_pos + int(target_angle * self.ticks_per_radian)
            
            # Clamp to safe motor range (0 to 4095)
            clamped_ticks = max(0, min(4095, ticks))
            
            motor_id = i + 1
            positions[motor_id] = clamped_ticks
            angles[motor_id] = target_angle
            
        return positions, angles
