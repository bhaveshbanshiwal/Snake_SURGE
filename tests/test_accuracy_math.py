import math
import time
from src.snake_locomotion import SnakeKinematics
from src.path_engine import PathEngine

def test_kinematics_accuracy():
    print("--- TESTING KINEMATICS ACCURACY ---")
    kin = SnakeKinematics(num_motors=10)
    # Compare with raw simulate.py math
    t = 1.0
    turn_offset = 0.5
    
    # Simulate.py math
    simulate_raw = []
    for i in range(10):
        target_angle = (0.8 * math.sin(2.0 * t - i * 1.0)) + turn_offset
        simulate_raw.append(target_angle)
        
    # Our OOP Engine
    positions, angles = kin.calculate_positions(t, turn_offset=turn_offset)
    
    passed = True
    for i in range(10):
        # angles dict is 1-indexed (motor 1-10)
        engine_angle = angles[i+1]
        raw_angle = simulate_raw[i]
        
        diff = abs(engine_angle - raw_angle)
        if diff > 1e-5:
            passed = False
            print(f"FAILED on Motor {i+1}: Engine={engine_angle}, Raw={raw_angle}")
            
    if passed:
        print("[PASS] KINEMATICS MATCH: The OOP engine perfectly replicates the simulate.py math!")
    else:
        print("[FAIL] KINEMATICS FAILED to match.")

def test_pure_pursuit_accuracy():
    print("\n--- TESTING PURE PURSUIT PATHFINDING ---")
    pe = PathEngine()
    
    # Test 1: Target straight ahead
    target_path = [(5.0, 0.0)]
    turn_offset = pe.calculate_pure_pursuit(current_x=0.0, current_y=0.0, current_yaw=0.0, target_path=target_path)
    print(f"Test 1 (Target Straight Ahead): Turn Offset = {turn_offset:.3f}")
    if abs(turn_offset) < 0.01:
        print("[PASS] Passed (Snake goes straight)")
    else:
        print("[FAIL] Failed (Snake turns when it shouldn't)")
        
    # Test 2: Target to the Left (+Y in our coordinate mapping)
    target_path = [(0.0, 5.0)]
    turn_offset = pe.calculate_pure_pursuit(current_x=0.0, current_y=0.0, current_yaw=0.0, target_path=target_path)
    print(f"Test 2 (Target Left): Turn Offset = {turn_offset:.3f}")
    if turn_offset > 0.0:
        print("[PASS] Passed (Snake steers left with positive offset)")
    else:
        print("[FAIL] Failed (Snake steers wrong direction)")
        
    # Test 3: Target to the Right (-Y)
    target_path = [(0.0, -5.0)]
    turn_offset = pe.calculate_pure_pursuit(current_x=0.0, current_y=0.0, current_yaw=0.0, target_path=target_path)
    print(f"Test 3 (Target Right): Turn Offset = {turn_offset:.3f}")
    if turn_offset < 0.0:
        print("[PASS] Passed (Snake steers right with negative offset)")
    else:
        print("[FAIL] Failed (Snake steers wrong direction)")

if __name__ == "__main__":
    print("\n==========================================")
    print(" ENGINE ACCURACY VALIDATOR")
    print("==========================================")
    test_kinematics_accuracy()
    test_pure_pursuit_accuracy()
    print("==========================================\n")
