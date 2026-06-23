import tkinter as tk
from tkinter import ttk
import time
import math

from src.snake_locomotion import SnakeKinematics
from src.path_engine import PathEngine
from src.simulation_interface import SimulationInterface
from src.dynamixel_interface import DynamixelInterface

class SnakeDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Snake SURGE - Telemetry & Path Controller")
        self.geometry("1100x800")
        
        self.kinematics = SnakeKinematics()
        self.path_engine = PathEngine()
        self.sim_iface = SimulationInterface()
        self.hw_iface = DynamixelInterface(port='COM3')
        
        self.active_iface = None
        
        self.target_path = [] # list of (world_x, world_y)
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_yaw = 0.0
        
        self.is_running = False
        self.start_time = 0
        
        self.setup_ui()
        self.update_loop()
        
    def setup_ui(self):
        # TOP FRAME: Control Panel
        control_frame = ttk.LabelFrame(self, text="Control Panel")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.mode_var = tk.StringVar(value="SIM")
        ttk.Radiobutton(control_frame, text="Simulation (PyBullet Virtual Telemetry)", variable=self.mode_var, value="SIM").pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Radiobutton(control_frame, text="Hardware (Dynamixel COM3 Telemetry)", variable=self.mode_var, value="HW").pack(side=tk.LEFT, padx=10, pady=10)
        
        self.btn_connect = ttk.Button(control_frame, text="Connect Engine", command=self.toggle_connection)
        self.btn_connect.pack(side=tk.LEFT, padx=20)
        
        self.btn_clear = ttk.Button(control_frame, text="Clear Canvas Path", command=self.clear_path)
        self.btn_clear.pack(side=tk.LEFT, padx=10)
        
        self.status_var = tk.StringVar(value="Status: Disconnected")
        ttk.Label(control_frame, textvariable=self.status_var, font=('Arial', 10, 'bold')).pack(side=tk.RIGHT, padx=20)
        
        # MIDDLE FRAME: Path Engine Canvas
        canvas_frame = ttk.LabelFrame(self, text="Path Engine (Draw Target Path With Mouse)")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#eef2f5", height=500)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<B1-Motion>", self.draw_path)
        self.canvas.bind("<Button-1>", self.draw_path)
        
        # Draw axes
        self.canvas.create_line(550, 0, 550, 600, fill="#ccc", dash=(4, 4))
        self.canvas.create_line(0, 400, 1100, 400, fill="#ccc", dash=(4, 4))
        self.canvas.create_text(560, 10, text="Forward (+X)", anchor="w")
        self.canvas.create_text(10, 390, text="Left (+Y)", anchor="sw")
        
        # BOTTOM FRAME: Telemetry Grid
        telemetry_frame = ttk.LabelFrame(self, text="Live Telemetry Dashboard (10 Actuators)")
        telemetry_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.labels = {}
        for i in range(1, 11):
            f = tk.Frame(telemetry_frame, relief=tk.RAISED, borderwidth=1, bg="white")
            f.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=2, pady=5)
            tk.Label(f, text=f"MOTOR {i}", font=('Arial', 9, 'bold'), bg="#333", fg="white").pack(fill=tk.X)
            self.labels[i] = {
                'pos': tk.Label(f, text="Angle: -", bg="white", font=('Consolas', 9)),
                'vel': tk.Label(f, text="Speed: -", bg="white", font=('Consolas', 9)),
                'load': tk.Label(f, text="Torque: -", bg="white", font=('Consolas', 9))
            }
            self.labels[i]['pos'].pack(anchor="w", padx=5)
            self.labels[i]['vel'].pack(anchor="w", padx=5)
            self.labels[i]['load'].pack(anchor="w", padx=5)
            
    def clear_path(self):
        self.target_path = []
        self.canvas.delete("path")
        self.canvas.delete("target_pt")
        
    def draw_path(self, event):
        x = event.x
        y = event.y
        # Convert Screen (x,y) to World (X:Forward, Y:Left)
        # Assuming robot starts at screen (550, 400) facing UP
        world_x = (400 - y) / 50.0  
        world_y = (550 - x) / 50.0  
        
        self.target_path.append((world_x, world_y))
        
        # Draw waypoint
        r = 3
        self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="#4287f5", outline="", tags="path")

    def toggle_connection(self):
        if self.is_running:
            self.is_running = False
            if self.active_iface: self.active_iface.disconnect()
            self.btn_connect.config(text="Connect Engine")
            self.status_var.set("Status: Disconnected")
            return
            
        if self.mode_var.get() == "SIM":
            self.active_iface = self.sim_iface
        else:
            self.active_iface = self.hw_iface
            
        self.status_var.set("Status: Connecting...")
        self.update_idletasks()
        
        success, msg = self.active_iface.connect()
        self.status_var.set(f"Status: {msg}")
        
        if success:
            self.is_running = True
            self.start_time = time.time()
            self.btn_connect.config(text="Disconnect Engine")
            
    def update_loop(self):
        if self.is_running and self.active_iface:
            curr_time = time.time() - self.start_time
            
            # Odometry update
            if self.mode_var.get() == "SIM":
                self.robot_x, self.robot_y, self.robot_yaw = self.sim_iface.get_robot_pose()
            else:
                pass # Hardware odometry requires external tracking or pure kinematic integration
                
            # 1. Path Engine - Target Path Finder (Pure Pursuit)
            turn_offset = self.path_engine.calculate_pure_pursuit(self.robot_x, self.robot_y, self.robot_yaw, self.target_path)
            
            # 2. Kinematics Engine
            positions, angles = self.kinematics.calculate_positions(curr_time, turn_offset)
            
            # 3. Write Motor Commands
            if self.mode_var.get() == "SIM":
                self.active_iface.write_positions(angles)
            else:
                self.active_iface.write_positions(positions)
                
            # 4. Read Telemetry & Update GUI Grid
            telemetry = self.active_iface.read_telemetry()
            for dxl_id, data in telemetry.items():
                if dxl_id in self.labels:
                    self.labels[dxl_id]['pos'].config(text=f"Angle:  {data['position']}")
                    self.labels[dxl_id]['vel'].config(text=f"Speed:  {data['velocity']}")
                    self.labels[dxl_id]['load'].config(text=f"Torque: {data['load']}")
                    
            # 5. Visualizer
            self.canvas.delete("robot")
            self.canvas.delete("predict")
            
            # Draw robot current pose
            screen_y = 400 - (self.robot_x * 50)
            screen_x = 550 - (self.robot_y * 50)
            self.canvas.create_oval(screen_x-8, screen_y-8, screen_x+8, screen_y+8, fill="red", tags="robot")
            
            # Draw forward prediction trail
            predicted_path = self.path_engine.predict_path(self.robot_x, self.robot_y, self.robot_yaw, speed=0.5, turn_offset=turn_offset)
            for (px, py) in predicted_path:
                sy = 400 - (px * 50)
                sx = 550 - (py * 50)
                self.canvas.create_oval(sx-1, sy-1, sx+1, sy+1, fill="orange", tags="predict")
                
        self.after(50, self.update_loop) # ~20 Hz control loop
        
if __name__ == "__main__":
    app = SnakeDashboard()
    app.mainloop()
