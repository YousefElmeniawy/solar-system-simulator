"""Solar-wind particle system using semi-implicit Euler integration and respawn."""
from __future__ import annotations
import numpy as np

class SolarWind:
    def __init__(self, count: int=160, seed: int=311):
        self.rng=np.random.default_rng(seed); self.count=count
        self.positions=np.zeros((count,3),dtype=np.float32); self.velocities=np.zeros((count,3),dtype=np.float32)
        self.lifetime=np.zeros(count,dtype=np.float32); self.max_life=np.zeros(count,dtype=np.float32)
        self.colors=np.zeros((count,3),dtype=np.float32)
        for i in range(count): self._respawn(i, initial=True)

    def _respawn(self, i: int, initial: bool=False):
        direction=self.rng.normal(size=3); direction/=max(np.linalg.norm(direction),1e-8)
        self.positions[i]=direction*1.7
        speed=float(self.rng.uniform(1.8,4.3)); self.velocities[i]=direction*speed + self.rng.normal(0,.12,3)
        life=float(self.rng.uniform(3,9)); self.max_life[i]=life
        self.lifetime[i]=float(self.rng.uniform(0,life)) if initial else life
        self.colors[i]=self.rng.choice([(.35,.75,1.0),(1.0,.58,.23),(.85,.88,1.0)])

    def update(self, dt: float, speed: float=1.0):
        dt=min(max(float(dt),0),.05)*speed
        if dt<=0:return
        # Semi-implicit Euler: update velocity under weak radial acceleration, then position.
        r=np.maximum(np.linalg.norm(self.positions,axis=1,keepdims=True),1e-4)
        accel=.06*self.positions/r
        self.velocities += accel*dt
        self.positions += self.velocities*dt
        self.lifetime -= dt
        expired=np.where((self.lifetime<=0)|(np.linalg.norm(self.positions,axis=1)>34))[0]
        for i in expired:self._respawn(int(i))

    def drawable(self):
        alpha=np.clip(self.lifetime/np.maximum(self.max_life,1e-4),0,1)
        sizes=(0.8+1.4*alpha).astype(np.float32)
        return self.positions.copy(), self.colors.copy(), alpha.astype(np.float32), sizes
