"""Delta-time simulation clock. Simulation days, not frames, drive every orbit and spin."""
from dataclasses import dataclass

@dataclass
class SimulationClock:
    days_per_second: float = 24.0
    days: float = 0.0
    paused: bool = False
    multipliers: tuple[float, ...] = (0.1, 1.0, 10.0, 100.0)
    speed_index: int = 1

    @property
    def speed(self) -> float:
        return self.multipliers[self.speed_index]

    def update(self, real_dt: float) -> None:
        if not self.paused:
            self.days += max(0.0, min(float(real_dt), 0.1)) * self.days_per_second * self.speed

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def change_speed(self, direction: int) -> None:
        self.speed_index = max(0, min(len(self.multipliers)-1, self.speed_index + direction))

    def reset(self) -> None:
        self.days = 0.0
