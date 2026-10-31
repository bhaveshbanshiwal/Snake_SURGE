import time
import math
import sys
import serial.tools.list_ports
import platform

from src.st3215_interface import ST3215Interface

def main():
    print("=" * 60)
    print(" Snake SURGE - 3D Sidewinding Locomotion Controller")
    print("=" * 60)
    
    # 1. Auto-detect COM port
    default_port = 'COM12' if platform.system() == 'Windows' else '/dev/ttyUSB0'
    for p in serial.tools.list_ports.comports():
        if 'AMA' not in p.device and 'Bluetooth' not in p.description:
            default_port = p.device
            break
            
    print(f"Connecting to ESP32 Bridge on port {default_port}...")
    iface = ST3215Interface(num_motors=10, port=default_port)
    success, msg = iface.connect()
    
    if not success:
        print(f"Failed to connect: {msg}")
        sys.exit(1)
        
    print("Connected successfully.")
    
    try:
        # Phase 1: Soft alignment to mechanical zero (2048)
        iface.enable_torque()
        time.sleep(0.1)
        print("Aligning all servos to center (2048)...")
        center_pos = {i: 2048 for i in range(1, 11)}
        
        for step in range(60):
            iface.write_positions(center_pos, speed=400)
            all_centered = all(iface.last_positions.get(i, 2048) == 2048 for i in range(1, 11))
            if all_centered and step > 10: 
                break
            time.sleep(0.05)
            
        print("Alignment complete. Initiating sidewinding gait...")
        
        # --- SIDEWINDING GAIT PARAMETERS ---
        # Sidewinding generates two orthogonal travelling waves:
        # 1. Horizontal (Yaw) wave: creates lateral body curvature
        # 2. Vertical (Pitch) wave: creates dynamic ground clearance
        # Increased pitch amplitude (1020 ticks ~ 90 deg) and higher hardware speed (2400)
        # provides aggressive vertical arching to lift the 150mm heavy battery module cleanly off the ground.
        amplitude_yaw = 900         # Horizontal sweep (~79 deg peak-to-peak)
        amplitude_pitch = 200      # Deep vertical lift (~90 deg) to clear the heavy battery
        frequency = 0.45            # Undulation frequency (Hz) - 0.45Hz gives high-torque lift time
        spatial_phase = 1.57        # pi/2 spatial shift per segment pair (1 full helical wave across 5 segments)
        sidewind_direction = 1      # +1 = Sidewind Right, -1 = Sidewind Left
        temporal_phase = sidewind_direction * (math.pi / 2.0)
        
        hardware_speed = 2400       # Increased speed headroom for larger vertical angular stroke
        ramp_duration = 2.0         # Seconds to ramp up amplitude smoothly from zero
        
        print("\n" + "=" * 60)
        print(f" GAIT ACTIVE: High-Clearance Sidewinding {'RIGHT' if sidewind_direction > 0 else 'LEFT'}")
        print(f" Yaw Amplitude: {amplitude_yaw} | Pitch Amplitude: {amplitude_pitch} (High Lift)")
        print(f" Frequency: {frequency} Hz | Speed: {hardware_speed}")
        print(" Press Ctrl+C to halt and relax servos.")
        print("=" * 60 + "\n")

        start_time = time.time()
        
        while True:
            t = time.time() - start_time
            
            # Smooth soft-start ramp to prevent high-torque jerking on initial cycle
            ramp = min(1.0, t / ramp_duration) if ramp_duration > 0 else 1.0
            curr_amp_yaw = int(amplitude_yaw * ramp)
            curr_amp_pitch = int(amplitude_pitch * ramp)
            
            positions = {}
            for i in range(1, 11):
                is_yaw = (i % 2 != 0)
                segment_index = (i - 1) // 2
                
                # Invert alternate joint directions to account for alternating mechanical bracket mounting
                direction_mult = 1 if segment_index % 2 == 0 else -1
                
                # Spatial phase progression along the 5 segment pairs
                phase_k = segment_index * spatial_phase
                
                if is_yaw:
                    # Horizontal wave
                    val = math.sin(2.0 * math.pi * frequency * t - phase_k)
                    pos = 2048 + int(curr_amp_yaw * val * direction_mult)
                else:
                    # Vertical wave with 90-degree temporal offset relative to horizontal wave
                    # Extra lift boost on bridge pitch joints 4 & 6 directly supporting the battery bay
                    bridge_boost = 1.08 if i in (4, 6) else 1.0
                    val = math.sin(2.0 * math.pi * frequency * t - phase_k + temporal_phase)
                    pos = 2048 + int(curr_amp_pitch * bridge_boost * val * direction_mult)
                    
                positions[i] = max(0, min(4095, pos))
                
            iface.write_positions(positions, speed=hardware_speed)
            print(f"[SIDEWINDING] Time: {t:5.1f}s | Ramp: {ramp*100:3.0f}% | Pitch Amp: {curr_amp_pitch}   ", end='\r')
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\n\nHalting sidewinding gait...")
    finally:
        iface.disconnect()
        print("Torque-off requested; serial closed.")

if __name__ == "__main__":
    main()
