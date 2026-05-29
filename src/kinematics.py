import math
from .robot_config import Config

class Kinematics:
    def __init__(self):
        self.config = Config

    def calculate_target_angles(self, time_t):
        """
        Calculates the theoretical target angles for all joints based on the Bellows Model.
        Odd joints (index 0, 2, 4...) are Dorsal (Pitch)
        Even joints (index 1, 3, 5...) are Lateral (Yaw)
        """
        target_angles = []
        
        for i in range(self.config.NUM_JOINTS):
            # Arc length along the backbone for this joint
            s_i = i * self.config.LINK_LENGTH_M
            
            # The angle is approximately the integral of curvature over link length L.
            # theta_i = L * k(s_i, t)
            
            if i % 2 == 0:
                # Dorsal joint
                k_d = self.config.K_0 * math.cos(self.config.K_S * s_i + self.config.K_T * time_t + self.config.PSI_D)
                theta_target = self.config.LINK_LENGTH_M * k_d
            else:
                # Lateral joint
                k_l = self.config.K_0 * math.sin(self.config.K_S * s_i + self.config.K_T * time_t + self.config.PSI_L)
                theta_target = self.config.LINK_LENGTH_M * k_l
                
            # Clamp to max angle limits
            theta_target = max(-self.config.MAX_ANGLE_RAD, min(self.config.MAX_ANGLE_RAD, theta_target))
            target_angles.append(theta_target)
            
        return target_angles

    def calculate_target_velocities(self, current_targets, previous_targets, dt):
        """
        Calculates target velocities via numerical differentiation of target angles.
        """
        target_velocities = []
        for curr, prev in zip(current_targets, previous_targets):
            vel = (curr - prev) / dt
            target_velocities.append(vel)
        return target_velocities
