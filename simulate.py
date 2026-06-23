import pybullet as p
import pybullet_data
import time
import math
import sys

def simulate_independent():
    """Runs a fully independent PyBullet simulation of the Snake SURGE."""
    physicsClient = p.connect(p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())

    p.configureDebugVisualizer(p.COV_ENABLE_RGB_BUFFER_PREVIEW, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_DEPTH_BUFFER_PREVIEW, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_SEGMENTATION_MARK_PREVIEW, 0)
    p.configureDebugVisualizer(p.COV_ENABLE_MOUSE_PICKING, 0)

    p.setGravity(0, 0, -9.81)
    planeId = p.loadURDF("plane.urdf")

    for i in range(0, 81): 
        x = i * 0.5 
        for y_offset in [-10, 0, 10]: 
            if i % 2 == 0:
                p.addUserDebugLine([x, -2+y_offset, 0.01], [x, 2+y_offset, 0.01], [0.3, 0.3, 0.3], 2)
                if y_offset == 0:
                    p.addUserDebugText(f"{x}m", [x, 0, 0.02], textColorRGB=[0,0,0], textSize=1.5)
            else:
                p.addUserDebugLine([x, -2+y_offset, 0.01], [x, 2+y_offset, 0.01], [0.7, 0.7, 0.7], 1)

    startPos = [0, 0, 0.05]
    startOrientation = p.getQuaternionFromEuler([0, 0, 0])
    snakeId = p.loadURDF("snake.urdf", startPos, startOrientation, flags=p.URDF_USE_SELF_COLLISION | p.URDF_USE_SELF_COLLISION_EXCLUDE_PARENT) 
    num_joints = p.getNumJoints(snakeId)

    pov_slider = p.addUserDebugParameter("POV (0:Follow, 1:Top, 2:Side, 3:Free)", 0, 3, 0)
    zoom_slider = p.addUserDebugParameter("Camera Zoom", 0.1, 10.0, 1.5)
    amplitude_slider = p.addUserDebugParameter("Sine Amplitude", 0.1, 1.5, 0.8)
    frequency_slider = p.addUserDebugParameter("Sine Speed (Freq)", 0.1, 5.0, 2.0)
    phase_slider = p.addUserDebugParameter("Phase Lag", 0.1, 3.0, 1.0)
    force_slider = p.addUserDebugParameter("Max Motor Force", 0.1, 20.0, 5.0)
    friction_ratio_slider = p.addUserDebugParameter("Wheel Effect (Lat/Fwd)", 1.0, 50.0, 20.0)

    base_forward_friction = 0.05

    def update_friction(ratio):
        """Updates lateral vs forward friction scaling dynamically."""
        lateral_f = base_forward_friction * ratio
        p.changeDynamics(snakeId, -1, lateralFriction=lateral_f, anisotropicFriction=[1.0/ratio, 1, 1])
        for j in range(num_joints):
            p.changeDynamics(snakeId, j, lateralFriction=lateral_f, anisotropicFriction=[1.0/ratio, 1, 1])

    t = 0
    last_pos = startPos
    last_head_trace_pos = None
    last_tail_trace_pos = None
    turn_offset = 0.0 
    speed_text_id = p.addUserDebugText("Speed: 0.00 m/s", [0,0,0.3], textColorRGB=[0,0,0], textSize=1.5)

    print("\n" + "="*60)
    print(" SNAKE SIMULATION TELEMETRY (Live Data)")
    print(" >> Tap A / D keys to slowly steer! Steering stays constant! <<")
    print("="*60)

    try:
        while p.isConnected():
            p.stepSimulation()
            
            amp = p.readUserDebugParameter(amplitude_slider)
            freq = p.readUserDebugParameter(frequency_slider)
            phase = p.readUserDebugParameter(phase_slider)
            max_force = p.readUserDebugParameter(force_slider)
            fric_ratio = p.readUserDebugParameter(friction_ratio_slider)
            pov_mode = int(p.readUserDebugParameter(pov_slider))
            zoom = p.readUserDebugParameter(zoom_slider) 
            
            update_friction(fric_ratio)
            
            keys = p.getKeyboardEvents()
            steer_speed = 0.005 
            if 97 in keys or p.B3G_LEFT_ARROW in keys:
                turn_offset += steer_speed
            if 100 in keys or p.B3G_RIGHT_ARROW in keys:
                turn_offset -= steer_speed
                
            turn_offset = max(-1.0, min(1.0, turn_offset))
            
            for i in range(num_joints):
                target_angle = (amp * math.sin(freq * t - i * phase)) + turn_offset
                p.setJointMotorControl2(snakeId, i, p.POSITION_CONTROL, targetPosition=target_angle, force=max_force)
                
            base_pos, base_orn = p.getBasePositionAndOrientation(snakeId) 
            tail_state = p.getLinkState(snakeId, num_joints - 1)
            tail_pos = tail_state[0] 
            
            if last_head_trace_pos is None:
                last_head_trace_pos = base_pos
                last_tail_trace_pos = tail_pos
                last_pos = base_pos
            
            if int(t * 240) % 10 == 0: 
                p.addUserDebugLine(last_head_trace_pos, base_pos, lineColorRGB=[1, 0, 0], lineWidth=4, lifeTime=0)
                p.addUserDebugLine(last_tail_trace_pos, tail_pos, lineColorRGB=[0, 1, 0], lineWidth=4, lifeTime=0)
                last_head_trace_pos = base_pos
                last_tail_trace_pos = tail_pos

            if pov_mode == 0: 
                p.resetDebugVisualizerCamera(cameraDistance=zoom, cameraYaw=45, cameraPitch=-30, cameraTargetPosition=base_pos)
            elif pov_mode == 1: 
                p.resetDebugVisualizerCamera(cameraDistance=zoom*1.5, cameraYaw=0, cameraPitch=-89.9, cameraTargetPosition=base_pos)
            elif pov_mode == 2: 
                p.resetDebugVisualizerCamera(cameraDistance=zoom*1.2, cameraYaw=90, cameraPitch=-10, cameraTargetPosition=base_pos)
                
            if int(t * 240) % 30 == 0:
                dist = math.sqrt((base_pos[0]-last_pos[0])**2 + (base_pos[1]-last_pos[1])**2)
                speed = dist / (30.0 / 240.0)
                
                speed_text_id = p.addUserDebugText(f"Vel: {speed:.3f} m/s", [base_pos[0], base_pos[1], base_pos[2]+0.2], textColorRGB=[0,0,0], textSize=2.0, replaceItemUniqueId=speed_text_id)
                last_pos = base_pos
                sys.stdout.write(f"\r[Speed: {speed:.3f} m/s] | Turn: {turn_offset:.2f} | Lat/Fwd Ratio: {fric_ratio:.1f}   ")
                sys.stdout.flush()
                
            t += 1./240.
            time.sleep(1./240.)

    except Exception:
        pass

if __name__ == "__main__":
    simulate_independent()
