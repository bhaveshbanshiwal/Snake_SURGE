import math

class PathEngine:
    """Handles predictive forward kinematics and pure pursuit pathfinding."""
    def __init__(self):
        self.lookahead_distance = 0.5
        self.max_turn_offset = 0.8
        self.progress_idx = 0

    @staticmethod
    def project(x, y, start, end):
        dx, dy = end[0] - start[0], end[1] - start[1]
        length = dx * dx + dy * dy
        t = max(0., min(1., ((x - start[0]) * dx + (y - start[1]) * dy) / length)) if length else 0.
        point = (start[0] + t * dx, start[1] + t * dy)
        return point, math.hypot(x - point[0], y - point[1])

    def deviation(self, x, y, path):
        return min(self.project(x, y, a, b)[1] for a, b in zip(path, path[1:]))

    def progress(self, x, y, path):
        lengths = [math.dist(a, b) for a, b in zip(path, path[1:])]
        if not lengths or sum(lengths) == 0:
            return 0.
        i = min(self.progress_idx, len(lengths) - 1)
        point, _ = self.project(x, y, path[i], path[i + 1])
        return (sum(lengths[:i]) + math.dist(path[i], point)) / sum(lengths)

    def predict_path(self, current_x, current_y, current_yaw, speed, turn_offset, dt=0.1, steps=50):
        """Predicts the future kinematic path of the snake."""
        predicted_path = []
        x, y, yaw = current_x, current_y, current_yaw
        angular_velocity = -turn_offset * speed * 2.0 
        for _ in range(steps):
            x += speed * math.cos(yaw) * dt
            y += speed * math.sin(yaw) * dt
            yaw += angular_velocity * dt
            predicted_path.append((x, y))
        return predicted_path

    def calculate_pure_pursuit(self, current_x, current_y, current_yaw, target_path):
        """Calculates steering curvature needed to reach the next lookahead waypoint."""
        if not target_path:
            return 0.0
        # Advance in route order, including sparse segments and lateral undulation.
        while self.progress_idx < len(target_path) - 2:
            end = target_path[self.progress_idx + 1]
            start = target_path[self.progress_idx]
            dx, dy = end[0] - start[0], end[1] - start[1]
            length = dx * dx + dy * dy
            along = ((current_x - start[0]) * dx + (current_y - start[1]) * dy) / length if length else 1.
            _, cross = self.project(current_x, current_y, start, end)
            if along < .85 or cross > .25:
                break
            self.progress_idx += 1
        closest_idx = min(self.progress_idx, len(target_path) - 1)
        # Look ahead along the polyline, rather than jumping at a route crossing.
        if len(target_path) > 1:
            closest_idx = min(closest_idx, len(target_path) - 2)
            point, _ = self.project(current_x, current_y, target_path[closest_idx], target_path[closest_idx + 1])
            remaining = self.lookahead_distance
            for end in target_path[closest_idx + 1:]:
                length = math.dist(point, end)
                if length >= remaining:
                    lookahead_pt = (point[0] + (end[0] - point[0]) * remaining / length,
                                    point[1] + (end[1] - point[1]) * remaining / length)
                    break
                remaining -= length
                point = end
            else:
                lookahead_pt = target_path[-1]
        else:
            lookahead_pt = target_path[0]
        dx = lookahead_pt[0] - current_x
        dy = lookahead_pt[1] - current_y
        local_x = math.cos(-current_yaw) * dx - math.sin(-current_yaw) * dy
        local_y = math.sin(-current_yaw) * dx + math.cos(-current_yaw) * dy
        dist_sq = local_x**2 + local_y**2
        if dist_sq < 0.001:
            return 0.0
        curvature = (2.0 * local_y) / dist_sq
        turn_offset = curvature * 0.3
        return max(-self.max_turn_offset, min(self.max_turn_offset, turn_offset))
