import time
import math
from src.robot_config import Config
from src.servo_driver import ServoDriver
from src.kinematics import Kinematics
from src.torque_controller import TorqueController

def main():
    print("=== Self-Adaptive Snake Robot Controller ===")
    
    # 1. Initialization
    driver = ServoDriver(num_servos=Config.NUM_JOINTS)
    if not driver.connect():
        print("Failed to connect to hardware. Exiting.")
        return
        
    driver.set_torque_mode()
    
    kinematics = Kinematics()
    torque_controller = TorqueController()
    
    start_time = time.time()
    last_time = 0.0
    
    # Keep track of previous targets for velocity calculation
    previous_targets = [0.0] * Config.NUM_JOINTS
    
    print("Starting Main Control Loop...")
    
    try:
        # Run for 10 seconds as a test (or True for infinite loop)
        for _ in range(int(10 / Config.DT)):
            current_time = time.time() - start_time
            dt = current_time - last_time
            if dt < Config.DT:
                time.sleep(Config.DT - dt)
                current_time = time.time() - start_time
                dt = current_time - last_time
                
            last_time = current_time
            
            # 2. Telemetry Loop
            # Read current Position, Velocity, and Load
            states = driver.read_all_states()
            
            # 3. Kinematic Calculation
            # Calculate the desired theoretical backbone curve targets
            target_angles = kinematics.calculate_target_angles(current_time)
            target_velocities = kinematics.calculate_target_velocities(target_angles, previous_targets, dt)
            previous_targets = target_angles
            
            # 4. & 5. PID Calculation and Modification
            # Compute desired torques with Shape and Radius modifications
            target_torques = torque_controller.compute_torques(states, target_angles, target_velocities)
            
            # 6. Actuation
            # Send updated target torques to servos
            driver.write_target_torques(target_torques)
            
            # Print debug for joint 0
            if int(current_time * 100) % 50 == 0:
                print(f"t={current_time:.2f}s | J0 Target Pos: {target_angles[0]:.2f} rad | J0 Actual Pos: {states[0].position:.2f} rad | Cmd Torque: {target_torques[0]:.2f} Nm")
                
    except KeyboardInterrupt:
        print("\n[!] Ctrl+C Detected. Stopping Robot.")
        
    finally:
        # Safely shut down motors (set torque to 0)
        print("Disabling Servos...")
        driver.write_target_torques([0.0] * Config.NUM_JOINTS)
        print("Done.")

if __name__ == "__main__":
    main()
