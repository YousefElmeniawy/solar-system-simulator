"""Interactive orbit camera with bounded dolly and projection switching."""
from __future__ import annotations
import math
from .math3d import vec3, look_at, perspective, orthographic

class OrbitCamera:
    def __init__(self):
        self.target = vec3(0,0,0); self.yaw = 0.48; self.pitch = 0.48; self.distance = 38.0
        self.orthographic_mode = False; self.ortho_scale = 26.0
        self.min_distance, self.max_distance = 3.5, 100.0

    @property
    def eye(self):
        cp = math.cos(self.pitch)
        return self.target + vec3(self.distance*cp*math.sin(self.yaw), self.distance*math.sin(self.pitch), self.distance*cp*math.cos(self.yaw))

    def view_matrix(self):
        return look_at(self.eye, self.target, vec3(0,1,0))

    def projection_matrix(self, width: int, height: int):
        aspect = max(1, width) / max(1, height)
        if self.orthographic_mode:
            half_h = self.ortho_scale / 2
            half_w = half_h * aspect
            return orthographic(-half_w, half_w, -half_h, half_h, 0.1, 300.0)
        return perspective(48.0, aspect, 0.1, 300.0)

    def orbit(self, dx: float, dy: float):
        self.yaw += dx * 0.006; self.pitch = max(-1.42, min(1.42, self.pitch + dy * 0.006))

    def zoom(self, amount: float):
        if self.orthographic_mode:
            self.ortho_scale = max(3.5, min(120.0, self.ortho_scale * math.exp(-amount*0.12)))
        else:
            self.distance = max(self.min_distance, min(self.max_distance, self.distance * math.exp(-amount*0.12)))

    def reset(self):
        self.target = vec3(0,0,0); self.yaw = 0.48; self.pitch = 0.48; self.distance = 38.0; self.ortho_scale = 26.0

    def focus(self, point, distance: float | None = None):
        self.target = vec3(*point)
        if distance is not None: self.distance = max(self.min_distance, min(self.max_distance, distance))
