import pybullet as p
import pybullet_data
import time
import math

class SimulationInterface:
    def __init__(self, num_motors=10):
        self.num_motors = num_motors
        self.is_connected = False
        self.snake_id = None
        
        # Physics config
        self.base_forward_friction = 0.05
        self.fric_ratio = 20.0
        
    def connect(self):
        try:
            self.client_id = p.connect(p.DIRECT) # Headless backend for GUI!
            p.setAdditionalSearchPath(pybullet_data.getDataPath())
            p.setGravity(0, 0, -9.81)
            p.loadURDF("plane.urdf")
            
            startPos = [0, 0, 0.05]
            startOrientation = p.getQuaternionFromEuler([0, 0, 0])
            self.snake_id = p.loadURDF("snake.urdf", startPos, startOrientation, flags=p.URDF_USE_SELF_COLLISION | p.URDF_USE_SELF_COLLISION_EXCLUDE_PARENT)
            
            # Setup friction
            lateral_f = self.base_forward_friction * self.fric_ratio
            p.changeDynamics(self.snake_id, -1, lateralFriction=lateral_f, anisotropicFriction=[1.0/self.fric_ratio, 1, 1])
            for j in range(self.num_motors):
                p.changeDynamics(self.snake_id, j, lateralFriction=lateral_f, anisotropicFriction=[1.0/self.fric_ratio, 1, 1])
                
            self.is_connected = True
            return True, "Simulation Started Successfully"
        except Exception as e:
            return False, f"Failed to start PyBullet: {e}"
            
    def disconnect(self):
        if self.is_connected:
            p.disconnect(self.client_id)
            self.is_connected = False
            
    def write_positions(self, angles_dict, max_force=5.0):
        """
        Angles dict from kinematics engine: {motor_id: radians}
        """
        if not self.is_connected: return
        
        for dxl_id, angle in angles_dict.items():
            joint_idx = dxl_id - 1 # Pybullet joints are 0-indexed
            p.setJointMotorControl2(self.snake_id, joint_idx, p.POSITION_CONTROL, targetPosition=angle, force=max_force)
            
        p.stepSimulation() # Step the physics engine!
        
    def get_robot_pose(self):
        """Returns physical (x, y, yaw) of the snake's head for Path Engine tracking"""
        if not self.is_connected: return 0, 0, 0
        pos, orn = p.getBasePositionAndOrientation(self.snake_id)
        _, _, yaw = p.getEulerFromQuaternion(orn)
        return pos[0], pos[1], yaw
        
    def read_telemetry(self):
        """Mimics Dynamixel telemetry format but generated from Physics Engine."""
        telemetry = {}
        if not self.is_connected: return telemetry
        
        # To get real forces in PyBullet, we need joint states
        for i in range(self.num_motors):
            state = p.getJointState(self.snake_id, i)
            pos_rad = state[0]
            vel_rads = state[1]
            force = state[3] # Applied motor torque
            
            dxl_id = i + 1
            telemetry[dxl_id] = {
                'load': int(force * 100), # Fake mapping to mA
                'velocity': int(vel_rads * 10), 
                'position': int((pos_rad / (2*math.pi)) * 4096) + 2048
            }
        return telemetry
