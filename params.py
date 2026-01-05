from dataclasses import dataclass

@dataclass
class PIDParams:
    kp: float = 0.0      # Proportional gain
    ki: float = 0.0      # Integral gain
    kd: float = 0.0      # Derivative gain
    i_max: float = 10.0  # Integral term limit
    out_max: float = 100.0  # Output limit