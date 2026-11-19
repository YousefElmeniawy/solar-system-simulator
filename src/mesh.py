"""Procedural mesh builders; static vertex buffers are uploaded once by Renderer."""
from __future__ import annotations
import math
import numpy as np


def uv_sphere(stacks: int = 24, slices: int = 36) -> np.ndarray:
    verts=[]
    for i in range(stacks):
        p0=-math.pi/2+math.pi*i/stacks; p1=-math.pi/2+math.pi*(i+1)/stacks
        for j in range(slices):
            t0=2*math.pi*j/slices; t1=2*math.pi*(j+1)/slices
            def v(p,t): return (math.cos(p)*math.cos(t), math.sin(p), math.cos(p)*math.sin(t))
            a,b,c,d=v(p0,t0),v(p1,t0),v(p1,t1),v(p0,t1)
            verts.extend((a,b,c,a,c,d))
    return np.asarray(verts,dtype=np.float32)


def ring_mesh(inner: float=1.0, outer: float=1.6, segments: int=128) -> np.ndarray:
    verts=[]
    for i in range(segments):
        a=2*math.pi*i/segments; b=2*math.pi*(i+1)/segments
        p0=(inner*math.cos(a),0,inner*math.sin(a)); p1=(outer*math.cos(a),0,outer*math.sin(a))
        p2=(outer*math.cos(b),0,outer*math.sin(b)); p3=(inner*math.cos(b),0,inner*math.sin(b))
        verts.extend((p0,p1,p2,p0,p2,p3))
    return np.asarray(verts,dtype=np.float32)


def orbit_line(radius: float, samples: int=240, eccentricity: float=0.025) -> np.ndarray:
    # Mild eccentricity, with periapsis on +X. Visual units are intentionally not physical.
    out=[]
    for i in range(samples+1):
        theta=2*math.pi*i/samples
        r=radius*(1-eccentricity*eccentricity)/(1+eccentricity*math.cos(theta))
        out.append((r*math.cos(theta),0.0,r*math.sin(theta)))
    return np.asarray(out,dtype=np.float32)
