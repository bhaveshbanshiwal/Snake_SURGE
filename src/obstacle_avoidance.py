class ObstacleAvoidance:
    def __init__(self, current_threshold=300):
        """
        :param current_threshold: The mA limit before an obstacle collision is triggered.
        """
        self.current_threshold = current_threshold
        self.state = "SLITHER"
        self.state_end_time = 0

    def process_state(self, current_time, motor_currents):
        """
        motor_currents: dictionary mapping motor ID to its current load (in mA)
        Returns the current operational state of the snake:
        "SLITHER" -> "SLITHER_REV" -> "SLITHER_TURN" -> "SLITHER"
        """
        # 1. If we are currently evading, manage the timers to progress the sequence
        if self.state in ["SLITHER_REV", "SLITHER_TURN"]:
            if current_time >= self.state_end_time:
                if self.state == "SLITHER_REV":
                    print("[EVASION] Switching from Reverse to Turn-Slither...")
                    self.state = "SLITHER_TURN"
                    self.state_end_time = current_time + 4.0 # Turn for 4 seconds
                elif self.state == "SLITHER_TURN":
                    print("[EVASION] Evasion complete. Resuming forward slither.")
                    self.state = "SLITHER"
            return self.state
            
        # 2. If slithering normally, check for obstacle collisions
        for motor_id, current in motor_currents.items():
            abs_current = abs(current)
            if abs_current > self.current_threshold:
                print(f"[ALERT] Obstacle collision on Motor {motor_id}! Load: {abs_current}mA")
                print("[EVASION] Initiating Reverse Slither...")
                self.state = "SLITHER_REV"
                self.state_end_time = current_time + 2.5 # Reverse slither for 2.5 seconds
                break
                
        return self.state
