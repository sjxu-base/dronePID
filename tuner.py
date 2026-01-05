import numpy as np
import matplotlib.pyplot as plt

from quadcopter import QuadcopterPID



class PIDTuner:
    """PID参数调试工具"""
    
    @staticmethod
    def tune_parameters(controller: QuadcopterPID, scenario: str = "tracking"):
        """
        自动调试PID参数
        
        参数:
            controller: QuadcopterPID实例
            test_scenario: 测试场景 ("hover", "step", "tracking")
        """
        print("开始PID参数调试...")
        print("=" * 50)
        
        if scenario == "hover":
            print("调试场景: 悬停")
            print("建议初始参数:")
            print("  Z轴: kp=2.0, ki=0.2, kd=0.8")
            print("  姿态: kp=2.0, ki=0.5, kd=0.3")
        
        elif scenario == "step":
            print("调试场景: 阶跃响应")
            print("建议初始参数:")
            print("  位置: kp=1.5, ki=0.1, kd=0.5")
            print("  姿态: kp=2.5, ki=0.3, kd=0.4")
        
        elif scenario == "tracking":
            print("调试场景: 轨迹跟踪")
            print("建议初始参数:")
            print("  位置: kp=1.2, ki=0.15, kd=0.6")
            print("  姿态: kp=2.0, ki=0.4, kd=0.35")
        
        print("=" * 50)
    
    @staticmethod
    def analyze_performance(controller: QuadcopterPID):
        """分析控制性能"""
        positions = np.array(controller.history['position'])
        targets = np.array(controller.history['target_pos'])
        
        if len(positions) == 0:
            print("没有数据可供分析")
            return
        
        # 计算误差统计
        errors = targets - positions
        rms_errors = np.sqrt(np.mean(errors**2, axis=0))
        max_errors = np.max(np.abs(errors), axis=0)
        
        print("控制性能分析:")
        print("=" * 50)
        print(f"X轴 - RMS误差: {rms_errors[0]:.4f}, 最大误差: {max_errors[0]:.4f}")
        print(f"Y轴 - RMS误差: {rms_errors[1]:.4f}, 最大误差: {max_errors[1]:.4f}")
        print(f"Z轴 - RMS误差: {rms_errors[2]:.4f}, 最大误差: {max_errors[2]:.4f}")
        print("=" * 50)
