import math
import time

class SnakeKinematics:
    def __init__(self, num_motors=10, center_pos=2048):
        """
        Initialize the Snake Kinematics engine.
        :param num_motors: Total number of Dynamixel motors in the snake.
        :param center_pos: The encoder value that represents 0 degrees (straight).
                           For XL330, the range is 0-4095, so 2048 is center.
        """
        self.num_motors = num_motors
        self.center_pos = center_pos
        
        # Locomotion parameters (can be tuned for different gaits)
        self.amplitude = 400       # How wide the wave is (in encoder ticks)
        self.frequency = 3.0       # How fast the wave propagates
        self.phase_shift = 1.2     # Phase difference between adjacent segments
        self.turn_offset = 300     # Encoder ticks to bend the spine during a turn

    def calculate_positions(self, current_time, mode="SLITHER"):
        """
        Calculates the target position for each motor at a given time `t` 
        to produce a 2D lateral undulation (slithering) gait relying on friction anisotropy.
        
        mode: "SLITHER", "SLITHER_REV", "SLITHER_TURN"
        
        Returns a dictionary mapping motor index (1 to num_motors) to goal position.
        """
        positions = {}
        
        # Determine wave direction and turning bend based on the mode
        wave_dir = 1
        bend = 0
        
        if mode == "SLITHER_REV":
            wave_dir = -1  # Invert time to slither backward
        elif mode == "SLITHER_TURN":
            wave_dir = 1   # Keep slithering forward, but add a bend to curve around the obstacle
            bend = self.turn_offset 
            
        for i in range(1, self.num_motors + 1):
            is_yaw = (i % 2 != 0)
            
            if is_yaw:
                # Yaw joints get the lateral undulation sine wave
                wave_phase = (wave_dir * self.frequency * current_time) - (i * self.phase_shift)
                wave = self.amplitude * math.sin(wave_phase) + bend
                pos = int(self.center_pos + wave)
            else:
                # Pitch joints stay flat against the ground
                pos = self.center_pos
                
            # Clamp values to valid XL330 limits (0 - 4095)
            positions[i] = max(0, min(4095, pos))
            
        return positions
