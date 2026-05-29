import math

class Config:
    # ---------------------------
    # Physical Robot Parameters
    # ---------------------------
    NUM_JOINTS = 12
    LINK_LENGTH_M = 0.076  # 76 mm
    MODULE_MASS_KG = 0.2   # 0.2 kg
    
    # ---------------------------
    # Bellows Model Parameters
    # ---------------------------
    # Initial default values for the gait
    K_0 = 0.5           # Curvature amplitude
    K_S = 1.0           # Spatial frequency
    K_T = 2.0           # Temporal frequency (speed)
    PSI_D = 0.0         # Dorsal phase offset
    PSI_L = math.pi / 2 # Lateral phase offset

    # ---------------------------
    # Control Loop Parameters
    # ---------------------------
    CONTROL_HZ = 50
    DT = 1.0 / CONTROL_HZ

    # ---------------------------
    # PID / Torque Control Gains
    # ---------------------------
    # Torque = P_pos * err_pos - D_pos * velocity + P_vel * err_vel
    P_POS = 2.5
    D_POS = 0.1
    P_VEL = 0.5

    # ---------------------------
    # Modification Module Parameters
    # ---------------------------
    # Shape Modification (for narrow spaces)
    MU_MAX = 1.0
    MU_MIN = 0.1
    POS_ERROR_THRESHOLD = 0.3 # Radians

    # Curve Radius Modification (for unstructured pipes)
    K_RADIUS = 0.5            # Scaling factor for radius deviation
    
    # ---------------------------
    # Hardware Limits
    # ---------------------------
    MAX_TORQUE_NM = 3.0       # Max safe torque (assuming budget servos)
    MAX_ANGLE_RAD = math.pi/2 # +/- 90 degrees
