import random
import time

class ServoState:
    def __init__(self, joint_id):
        self.joint_id = joint_id
        self.position = 0.0  # radians
        self.velocity = 0.0  # rad/s
        self.load = 0.0      # Torque/Current feedback

class ServoDriver:
    def __init__(self, num_servos, port="/dev/ttyUSB0", baudrate=1000000):
        """
        Hardware Abstraction Layer for Serial Bus Servos.
        Currently implements a Mock interface for software testing.
        Replace the contents of these functions with DynamixelSDK or Feetech SDK calls.
        """
        self.num_servos = num_servos
        self.port = port
        self.baudrate = baudrate
        self.states = [ServoState(i) for i in range(num_servos)]
        
        # Internal state for the mock simulation
        self._target_torques = [0.0] * num_servos

    def connect(self):
        print(f"[ServoDriver] Connecting to servos on {self.port} at {self.baudrate} baud...")
        time.sleep(0.5)
        print("[ServoDriver] Successfully connected to servos.")
        return True

    def set_torque_mode(self):
        """Sets all servos to current/torque control mode."""
        print("[ServoDriver] Setting all servos to Torque Control Mode.")

    def read_all_states(self):
        """
        Reads position, velocity, and load from all servos.
        In a real scenario, use SyncRead to read from all servos at once to save time.
        """
        # MOCK IMPLEMENTATION: Simulate physics based on applied torques
        for i in range(self.num_servos):
            # Simple Euler integration for mock physics
            acceleration = self._target_torques[i] * 5.0 # F=ma mock
            
            # Add some friction/damping
            acceleration -= self.states[i].velocity * 0.5 
            
            self.states[i].velocity += acceleration * 0.02 # dt mock
            self.states[i].position += self.states[i].velocity * 0.02
            
            # Simulate load feedback (proportional to applied torque + noise)
            self.states[i].load = self._target_torques[i] + random.uniform(-0.1, 0.1)
            
        return self.states

    def write_target_torques(self, torques):
        """
        Writes the target torques (currents) to all servos.
        Use SyncWrite in production.
        """
        if len(torques) != self.num_servos:
            raise ValueError("Torque array length must match number of servos.")
            
        # Store for mock physics
        self._target_torques = torques
        
        # print(f"[ServoDriver] Wrote torques: {[round(t, 2) for t in torques]}")
