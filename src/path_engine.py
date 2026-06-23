import math

class PathEngine:
    def __init__(self):
        self.lookahead_distance = 0.5  # meters
        self.max_turn_offset = 0.8     # radians

    def predict_path(self, current_x, current_y, current_yaw, speed, turn_offset, dt=0.1, steps=50):
        """
        Kinematic Forward Model: Predicts the future path of the snake.
        Since the snake slithers along a serpenoid curve, its macroscopic motion 
        behaves like a unicycle model where turn_offset roughly maps to angular velocity.
        """
        predicted_path = []
        x, y, yaw = current_x, current_y, current_yaw
        
        # Empirical conversion factor: steering turn_offset to turning radius/angular velocity
        # (This varies based on friction, but serves as a strong heuristic trace)
        angular_velocity = -turn_offset * speed * 2.0 
        
        for _ in range(steps):
            x += speed * math.cos(yaw) * dt
            y += speed * math.sin(yaw) * dt
            yaw += angular_velocity * dt
            predicted_path.append((x, y))
            
        return predicted_path

    def calculate_pure_pursuit(self, current_x, current_y, current_yaw, target_path):
        """
        Target Path Finder: Pure Pursuit Controller.
        Calculates the necessary `turn_offset` to navigate the snake along a series of (x,y) waypoints.
        """
        if not target_path:
            return 0.0 # Go straight if no path

        # Find the closest point on the path
        closest_dist = float('inf')
        closest_idx = 0
        for i, point in enumerate(target_path):
            d = math.hypot(current_x - point[0], current_y - point[1])
            if d < closest_dist:
                closest_dist = d
                closest_idx = i
                
        # Find the lookahead point (first point further than lookahead_distance from closest point)
        lookahead_pt = target_path[-1] # Default to end
        for i in range(closest_idx, len(target_path)):
            d = math.hypot(current_x - target_path[i][0], current_y - target_path[i][1])
            if d >= self.lookahead_distance:
                lookahead_pt = target_path[i]
                break
                
        # Pure Pursuit Steering calculation
        # Transform lookahead point to robot's local frame
        dx = lookahead_pt[0] - current_x
        dy = lookahead_pt[1] - current_y
        
        local_x = math.cos(-current_yaw) * dx - math.sin(-current_yaw) * dy
        local_y = math.sin(-current_yaw) * dx + math.cos(-current_yaw) * dy
        
        # Avoid division by zero
        dist_sq = local_x**2 + local_y**2
        if dist_sq < 0.001:
            return 0.0
            
        # Curvature calculation: 2 * y / L^2
        curvature = (2.0 * local_y) / dist_sq
        
        # Map curvature to serpenoid turn_offset
        # Negative sign because our math applies +offset to turn Left, but positive local_y is Left
        # Wait, if local_y is positive (target is to the left), curvature is positive.
        # We want a positive turn_offset to turn left (based on our simulate.py arrow keys mapping)
        turn_offset = curvature * 0.3 # Empirical gain
        
        return max(-self.max_turn_offset, min(self.max_turn_offset, turn_offset))
