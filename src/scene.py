"""Scene graph data and hierarchical model transforms for the solar system."""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
from .planet_data import PLANETS
from .math3d import identity, translation, scaling, rotation_x, rotation_y, rotation_z, multiply

@dataclass
class BodyState:
    key: str
    name: str
    model: np.ndarray
    color: tuple[float,float,float]
    radius: float
    emissive: bool = False
    selected: bool = False
    world_position: tuple[float,float,float] = (0,0,0)

class SolarScene:
    def __init__(self): self.planet_positions={}; self.planet_models={}; self.moon_model=identity()

    def bodies(self, days: float, selected_key: str | None=None) -> list[BodyState]:
        result=[]
        sun_model=multiply(rotation_y(days*0.025),scaling(1.42))
        result.append(BodyState('sun','Sun',sun_model,(1.0,0.56,0.12),1.42,True,selected_key=='sun',(0,0,0)))
        self.planet_positions={}; self.planet_models={}
        for idx,p in enumerate(PLANETS):
            angle=2*math.pi*days/p.year_days + idx*0.23
            eccentricity=0.025
            orbital_radius=p.orbit_radius*(1-eccentricity**2)/(1+eccentricity*math.cos(angle))
            x=orbital_radius*math.cos(angle); z=orbital_radius*math.sin(angle)
            pos=np.array([x,0.0,z])
            spin=2*math.pi*days*(24.0/max(abs(p.rotation_hours),0.1))
            # Planet local geometry -> spin/axial tilt -> orbit translation (column-vector order).
            model=multiply(translation(x,0,z),rotation_z(math.radians(p.axial_tilt)),rotation_y(spin),scaling(p.radius))
            self.planet_positions[p.key]=pos; self.planet_models[p.key]=model
            result.append(BodyState(p.key,p.name,model,p.color,p.radius,False,selected_key==p.key,tuple(pos)))
            if p.key=='earth':
                # Explicit hierarchy: Earth world transform multiplied by the Moon's local orbit transform.
                moon_angle=days*2*math.pi/27.32
                moon_local=multiply(rotation_y(moon_angle),translation(0,0,2.8),rotation_y(days*.3),scaling(.105))
                self.moon_model=model @ moon_local
                moon_pos=tuple((self.moon_model @ np.array([0,0,0,1]))[:3])
                result.append(BodyState('moon','Moon',self.moon_model,(0.72,0.76,0.82),.105,False,selected_key=='moon',moon_pos))
            elif p.key=='saturn':
                # Ring mesh is a child: it inherits Saturn's translation and tilt, not the sphere's radius scale.
                ring_model=multiply(translation(x,0,z),rotation_z(math.radians(p.axial_tilt)),rotation_x(math.radians(18)))
                result.append(BodyState('saturn_rings','Saturn rings',ring_model,(0.78,0.65,0.43),1.0,False,False,tuple(pos)))
        return result
