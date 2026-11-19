"""Approximate, presentation-scaled solar-system data (periods and temperatures are rounded)."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Planet:
    key: str
    name: str
    kind: str
    radius: float
    orbit_radius: float
    year_days: float
    rotation_hours: float
    color: tuple[float, float, float]
    short: str
    detail: str
    temperature_c: str
    moons: str
    atmosphere: str
    axial_tilt: float = 0.0

PLANETS = [
 Planet('mercury','Mercury','Terrestrial',0.19,3.4,88.0,1407.6,(0.62,0.60,0.56),'Smallest planet; heavily cratered.','A rocky world with an ancient, cratered surface and almost no substantial atmosphere. Its orbit is the most eccentric among the eight planets.', '167 °C average (approx.)','0','Very thin exosphere',0.03),
 Planet('venus','Venus','Terrestrial',0.29,5.0,224.7,-5832.5,(0.91,0.68,0.35),'A dense, hot world beneath bright clouds.','Venus has a thick carbon-dioxide atmosphere and a powerful greenhouse effect. It rotates retrograde, so its spin direction is opposite to most planets.', '464 °C surface average','0','Dense CO₂; sulfuric-acid clouds',177.4),
 Planet('earth','Earth','Terrestrial',0.32,6.8,365.25,23.93,(0.20,0.48,0.95),'Our ocean-rich home planet.','Earth has stable surface liquid water, a nitrogen-oxygen atmosphere and a global magnetic field. The Moon is modeled as a child of Earth in this simulation.', '15 °C global mean (approx.)','1','Mostly nitrogen and oxygen',23.44),
 Planet('mars','Mars','Terrestrial',0.25,8.7,687.0,24.62,(0.83,0.31,0.18),'A cold desert world with giant volcanoes.','Mars is a rocky planet with a thin atmosphere, polar caps and evidence of ancient surface water. Its red appearance comes largely from iron-rich dust.', '-65 °C average (approx.)','2','Thin, mostly CO₂',25.19),
 Planet('jupiter','Jupiter','Gas Giant',0.82,11.4,4332.6,9.93,(0.80,0.61,0.43),'The largest planet; a banded gas giant.','Jupiter is a hydrogen-helium giant with powerful storms, including the long-lived Great Red Spot. Its four large Galilean moons are not individually modeled here.', '-110 °C cloud-top approx.','95 known (rounded)','Mostly hydrogen and helium',3.13),
 Planet('saturn','Saturn','Gas Giant',0.70,14.6,10759.2,10.7,(0.85,0.75,0.52),'A gas giant famous for its broad rings.','Saturn’s rings consist mainly of countless icy fragments. The rings are rendered as a separate child mesh and inherit Saturn’s orbit and tilt.', '-140 °C cloud-top approx.','146 known (rounded)','Mostly hydrogen and helium',26.73),
 Planet('uranus','Uranus','Ice Giant',0.53,17.5,30688.5,-17.24,(0.42,0.79,0.82),'An ice giant that rotates on its side.','Uranus has a hydrogen-helium atmosphere with methane and an extreme axial tilt, producing unusual seasonal geometry. Its spin is retrograde.', '-195 °C cloud-top approx.','28 known (rounded)','Hydrogen, helium and methane',97.77),
 Planet('neptune','Neptune','Ice Giant',0.51,20.2,60182.0,16.11,(0.25,0.39,0.88),'A distant ice giant with fast winds.','Neptune is a dark, cold ice giant. Its orbit is shown with a visual scale and a deliberately accelerated clock so its motion remains observable.', '-200 °C cloud-top approx.','16 known (rounded)','Hydrogen, helium and methane',28.32),
]
BY_KEY = {p.key:p for p in PLANETS}
# Approximate public reference sources: NASA Solar System Exploration and NASA/NSSDC planetary fact sheets.
REFERENCES = [
 'NASA Solar System Exploration — Planets: https://solarsystem.nasa.gov/planets/overview/',
 'NASA/NSSDC — Planetary Fact Sheet: https://nssdc.gsfc.nasa.gov/planetary/factsheet/',
 'NASA — The Sun and Solar System: https://science.nasa.gov/solar-system/',
]
