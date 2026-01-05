import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Optional

from controller import PIDController
from params import PIDParams



class QuadcopterPID:
    def __init__(self):
        # Init state: position, attitude, targets and history
        
        # Define position control PID (x, y, z)
        self.pos_pid = {
            'x': PIDController(PIDParams(kp=1.0, ki=0.1, kd=0.5, out_max=10.0)),
            'y': PIDController(PIDParams(kp=1.0, ki=0.1, kd=0.5, out_max=10.0)),
            'z': PIDController(PIDParams(kp=2.0, ki=0.2, kd=0.8, out_max=15.0))
        }
        
        # Define attitude control PID (roll, pitch, yaw)
        self.att_pid = {
            'roll': PIDController(PIDParams(kp=2.0, ki=0.5, kd=0.3, out_max=45.0)),
            'pitch': PIDController(PIDParams(kp=2.0, ki=0.5, kd=0.3, out_max=45.0)),
            'yaw': PIDController(PIDParams(kp=1.5, ki=0.3, kd=0.2, out_max=60.0))
        }
        
        # Define target states: position and attitude
        self.target_position = np.array([0.0, 0.0, 0.0])  # [x, y, z]
        self.target_attitude = np.array([0.0, 0.0, 0.0])  # [roll, pitch, yaw]
        
        # Data history states for analysis and visualization
        self.history = {
            'time': [],
            'position': [],
            'attitude': [],
            'target_pos': [],
            'target_att': [],
            'motor_outputs': []
        }
        
    def set_target_position(self, x: float, y: float, z: float):
        self.target_position = np.array([x, y, z])
    
    def set_target_attitude(self, roll: float, pitch: float, yaw: float):
        self.target_attitude = np.array([roll, pitch, yaw])
    
    def update(self, current_pos: np.ndarray, current_att: np.ndarray, 
               dt: float = 0.01) -> Tuple[np.ndarray, dict]:
        """
        更新PID控制器并计算电机输出
        
        参数:
            current_pos: 当前位置 [x, y, z]
            current_att: 当前姿态 [roll, pitch, yaw] (度)
            dt: 时间步长
            
        返回:
            motor_outputs: 四个电机的输出 [0-1]
            debug_info: 调试信息
        """
        # Position control (outer loop)
        pos_errors = self.target_position - current_pos
        pos_outputs = {}
        
        for i, axis in enumerate(['x', 'y', 'z']):
            pos_outputs[axis] = self.pos_pid[axis].update(pos_errors[i], dt)
        
        # 将位置控制输出转换为姿态设定点
        # 注意：真实物理系统系统中这里会有更复杂的转换
        # todo: Use a more accurate model for position to attitude conversion
        attitude_target = np.array([
            np.clip(pos_outputs['y'] * 0.1, -30, 30),  # roll
            np.clip(pos_outputs['x'] * 0.1, -30, 30),  # pitch
            self.target_attitude[2]                     # yaw
        ])
        
        # Attitude control (inner loop)
        att_errors = attitude_target - current_att
        att_outputs = {}
        
        for i, axis in enumerate(['roll', 'pitch', 'yaw']):
            att_outputs[axis] = self.att_pid[axis].update(att_errors[i], dt)
        
        # 转换为电机输出（简化模型）
        # 四旋翼X模式配置
        # todo: 实际上需要根据具体的动力学模型进行计算
        motor_outputs = self._calculate_motor_outputs(
            att_outputs['roll'], 
            att_outputs['pitch'], 
            att_outputs['yaw'],
            pos_outputs['z']
        )
        
        # Record data for analysis
        self._record_data(dt, current_pos, current_att, motor_outputs)
        
        # Debug info
        debug_info = {
            'pos_errors': pos_errors,
            'att_errors': att_errors,
            'pos_outputs': pos_outputs,
            'att_outputs': att_outputs,
            'motor_outputs': motor_outputs
        }
        
        return motor_outputs, debug_info
    
    def _calculate_motor_outputs(self, roll_out: float, pitch_out: float, 
                                 yaw_out: float, throttle: float) -> np.ndarray:
        """
        计算电机输出（简化模型）
        电机顺序：[前左, 前右, 后右, 后左]
        """
        # 基础油门
        base_throttle = np.clip(throttle + 0.5, 0.0, 1.0)
        
        # Normalize control outputs to [0, 1]
        roll_out = roll_out / 45.0  # 假设最大滚转控制输出为45度
        pitch_out = pitch_out / 45.0  # 假设最大俯仰控制输出为45度
        yaw_out = yaw_out / 60.0  # 假设最大偏航控制输出为60度
        
        # 电机混控（X模式）
        motor1 = base_throttle + pitch_out - roll_out + yaw_out  # 前左
        motor2 = base_throttle + pitch_out + roll_out - yaw_out  # 前右
        motor3 = base_throttle - pitch_out + roll_out + yaw_out  # 后右
        motor4 = base_throttle - pitch_out - roll_out - yaw_out  # 后左
        
        outputs = np.array([motor1, motor2, motor3, motor4])
        
        # Normalize to [0, 1]
        outputs = np.clip(outputs, 0.0, 1.0)
        
        return outputs
    
    def _record_data(self, dt: float, current_pos: np.ndarray, 
                     current_att: np.ndarray, motor_outputs: np.ndarray):
        if not self.history['time']:
            self.history['time'].append(0)
        else:
            self.history['time'].append(self.history['time'][-1] + dt)
        
        self.history['position'].append(current_pos.copy())
        self.history['attitude'].append(current_att.copy())
        self.history['target_pos'].append(self.target_position.copy())
        self.history['target_att'].append(self.target_attitude.copy())
        self.history['motor_outputs'].append(motor_outputs.copy())
    
    def plot_results(self):
        time_data = self.history['time']
        
        fig, axes = plt.subplots(3, 2, figsize=(12, 10))
        
        # 位置跟踪
        positions = np.array(self.history['position'])
        target_positions = np.array(self.history['target_pos'])
        
        axes[0, 0].plot(time_data, positions[:, 0], 'b-', label='Actual X')
        axes[0, 0].plot(time_data, target_positions[:, 0], 'r--', label='Target X')
        axes[0, 0].set_ylabel('X Pos')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        axes[1, 0].plot(time_data, positions[:, 1], 'b-', label='Actual Y')
        axes[1, 0].plot(time_data, target_positions[:, 1], 'r--', label='Target Y')
        axes[1, 0].set_ylabel('Y Pos')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        axes[2, 0].plot(time_data, positions[:, 2], 'b-', label='Actual Z')
        axes[2, 0].plot(time_data, target_positions[:, 2], 'r--', label='Target Z')
        axes[2, 0].set_ylabel('Z Pos')
        axes[2, 0].set_xlabel('Time (sec)')
        axes[2, 0].legend()
        axes[2, 0].grid(True)
        
        # 姿态跟踪
        attitudes = np.array(self.history['attitude'])
        target_attitudes = np.array(self.history['target_att'])
        
        axes[0, 1].plot(time_data, attitudes[:, 0], 'b-', label='Actual Roll')
        axes[0, 1].plot(time_data, target_attitudes[:, 0], 'r--', label='Target Roll')
        axes[0, 1].set_ylabel('Roll (deg)')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        axes[1, 1].plot(time_data, attitudes[:, 1], 'b-', label='Actual Pitch')
        axes[1, 1].plot(time_data, target_attitudes[:, 1], 'r--', label='Target Pitch')
        axes[1, 1].set_ylabel('Pitch (deg)')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        axes[2, 1].plot(time_data, attitudes[:, 2], 'b-', label='Actual Yaw')
        axes[2, 1].plot(time_data, target_attitudes[:, 2], 'r--', label='Target Yaw')
        axes[2, 1].set_ylabel('Yaw (deg)')
        axes[2, 1].set_xlabel('Time (sec)')
        axes[2, 1].legend()
        axes[2, 1].grid(True)
        
        plt.tight_layout()
        plt.show()
        
        # 电机输出
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        motor_outputs = np.array(self.history['motor_outputs'])
        
        ax2.plot(time_data, motor_outputs[:, 0], label='Motor 1 (Front Left)')
        ax2.plot(time_data, motor_outputs[:, 1], label='Motor 2 (Front Right)')
        ax2.plot(time_data, motor_outputs[:, 3], label='Motor 3 (Rear Left)')
        ax2.plot(time_data, motor_outputs[:, 2], label='Motor 4 (Rear Right)')
        ax2.set_xlabel('Time (sec)')
        ax2.set_ylabel('Motor Output [0-1]')
        ax2.set_title('Motor Outputs Over Time')
        ax2.legend()
        ax2.grid(True)
        plt.show()
    
    def reset_history(self):
        for key in self.history:
            self.history[key] = []
