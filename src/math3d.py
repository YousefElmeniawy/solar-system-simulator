"""Educational 3D math utilities. Matrices are row-major NumPy arrays acting on column vectors."""
from __future__ import annotations
import math
import numpy as np

Vec3 = np.ndarray
Mat4 = np.ndarray


def vec3(x: float, y: float, z: float) -> Vec3:
    return np.array([x, y, z], dtype=np.float64)


def dot(a: Vec3, b: Vec3) -> float:
    return float(np.dot(a, b))


def cross(a: Vec3, b: Vec3) -> Vec3:
    return np.cross(a, b)


def normalize(v: Vec3, eps: float = 1e-12) -> Vec3:
    n = float(np.linalg.norm(v))
    if n < eps:
        return np.zeros_like(v, dtype=np.float64)
    return np.asarray(v, dtype=np.float64) / n


def identity() -> Mat4:
    return np.eye(4, dtype=np.float64)


def translation(x: float, y: float, z: float) -> Mat4:
    m = identity(); m[:3, 3] = (x, y, z); return m


def scaling(x: float, y: float | None = None, z: float | None = None) -> Mat4:
    y = x if y is None else y; z = x if z is None else z
    m = identity(); m[0, 0], m[1, 1], m[2, 2] = x, y, z; return m


def rotation_x(a: float) -> Mat4:
    c, s = math.cos(a), math.sin(a)
    return np.array([[1,0,0,0],[0,c,-s,0],[0,s,c,0],[0,0,0,1]], dtype=np.float64)


def rotation_y(a: float) -> Mat4:
    c, s = math.cos(a), math.sin(a)
    return np.array([[c,0,s,0],[0,1,0,0],[-s,0,c,0],[0,0,0,1]], dtype=np.float64)


def rotation_z(a: float) -> Mat4:
    c, s = math.cos(a), math.sin(a)
    return np.array([[c,-s,0,0],[s,c,0,0],[0,0,1,0],[0,0,0,1]], dtype=np.float64)


def multiply(*matrices: Mat4) -> Mat4:
    out = identity()
    for m in matrices:
        out = out @ np.asarray(m, dtype=np.float64)
    return out


def transform_point(m: Mat4, p: Vec3) -> Vec3:
    q = np.asarray(m, dtype=np.float64) @ np.array([p[0], p[1], p[2], 1.0])
    if abs(q[3]) > 1e-12:
        q = q / q[3]
    return q[:3]


def transform_vector(m: Mat4, v: Vec3) -> Vec3:
    return (np.asarray(m, dtype=np.float64) @ np.array([v[0], v[1], v[2], 0.0]))[:3]


def look_at(eye: Vec3, target: Vec3, up: Vec3) -> Mat4:
    """Right-handed view matrix, derived from camera forward/right/up basis."""
    f = normalize(np.asarray(target) - np.asarray(eye))
    if np.linalg.norm(f) < 1e-10: f = vec3(0, 0, -1)
    up_n = normalize(np.asarray(up))
    s = normalize(cross(f, up_n))
    if np.linalg.norm(s) < 1e-10:
        # Pick a reference axis not parallel to forward, including vertical-view edge cases.
        reference = vec3(0, 0, 1) if abs(f[1]) > 0.9 else vec3(0, 1, 0)
        s = normalize(cross(f, reference))
    u = cross(s, f)
    m = identity()
    m[0, :3] = s; m[1, :3] = u; m[2, :3] = -f
    m[0, 3] = -dot(s, eye); m[1, 3] = -dot(u, eye); m[2, 3] = dot(f, eye)
    return m


def perspective(fov_degrees: float, aspect: float, near: float, far: float) -> Mat4:
    if not (0 < fov_degrees < 180) or aspect <= 0 or near <= 0 or far <= near: raise ValueError('invalid perspective frustum')
    f = 1.0 / math.tan(math.radians(fov_degrees) / 2.0)
    m = np.zeros((4, 4), dtype=np.float64)
    m[0, 0] = f / aspect; m[1, 1] = f
    m[2, 2] = (far + near) / (near - far); m[2, 3] = (2 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m


def orthographic(left: float, right: float, bottom: float, top: float, near: float, far: float) -> Mat4:
    if right == left or top == bottom or far == near: raise ValueError('degenerate orthographic volume')
    m = identity()
    m[0,0] = 2/(right-left); m[1,1] = 2/(top-bottom); m[2,2] = -2/(far-near)
    m[0,3] = -(right+left)/(right-left); m[1,3] = -(top+bottom)/(top-bottom); m[2,3] = -(far+near)/(far-near)
    return m
