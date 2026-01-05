import numpy as np
import time
import matplotlib.pyplot as plt
from params import PIDParams



class PIDController:
    def __init__(self, params: PIDParams):
        self.params = params
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_time = None
        self.last_output = 0.0
        
    def reset(self):
        """Reset the integral and previous error"""
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_time = None
        self.last_output = 0.0
    
    def update(self, error: float, dt: float = None) -> float:
        """Update the PID controller with the given error and time step"""
        current_time = time.time()
        
        # Calculate dt if not provided
        if dt is None:
            if self.prev_time is None:
                self.prev_time = current_time
                return 0.0
            dt = current_time - self.prev_time
            self.prev_time = current_time
        
        # Limit dt to reasonable bounds
        dt = max(min(dt, 0.1), 0.001)
        
        # Limit integral term
        self.integral += error * dt
        self.integral = np.clip(self.integral, 
                                -self.params.i_max, 
                                self.params.i_max)
        
        # Limit derivative kick
        if dt > 1e-6:
            derivative = (error - self.prev_error) / dt
        else:
            derivative = 0.0
        
        # Calculate PID output
        output = (self.params.kp * error + 
                 self.params.ki * self.integral + 
                 self.params.kd * derivative)
        
        # Output limiting
        output = np.clip(output, -self.params.out_max, self.params.out_max)
        
        # Update error and output
        self.prev_error = error
        self.last_output = output
        
        return output
    
    def debug(self) -> dict:
        return {
            'integral': self.integral,
            'prev_err': self.prev_error,
            'output': self.last_output
        }
