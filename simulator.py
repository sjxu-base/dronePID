
import numpy as np
import matplotlib.pyplot as plt

from tuner import PIDTuner
from params import PIDParams
from controller import PIDController
from quadcopter import QuadcopterPID

def simulate_quadcopter():
    """模拟四旋翼无人机控制"""
    print("四旋翼无人机PID控制器模拟")
    print("=" * 50)
    
    # 创建PID控制器
    quadcopter = QuadcopterPID()
    tuner = PIDTuner()
    
    # 调试参数
    tuner.tune_parameters(quadcopter, "hover")
    
    # 设置目标（悬停在5米高度）
    quadcopter.set_target_position(0, 0, 5)
    quadcopter.set_target_attitude(0, 0, 0)
    
    # 模拟初始状态（在地面，有初始误差）
    current_pos = np.array([0.5, -0.3, 0.0])  # 初始位置偏移
    current_att = np.array([2.0, -1.5, 5.0])  # 初始姿态偏移
    
    # 模拟控制循环
    simulation_time = 10.0  # 秒
    dt = 0.02  # 50Hz控制频率
    steps = int(simulation_time / dt)
    
    print(f"\n开始模拟: {simulation_time}秒, {steps}步, {1/dt}Hz")
    print("=" * 50)
    
    for step in range(steps):
        # 更新控制
        motor_outputs, debug_info = quadcopter.update(current_pos, current_att, dt)
        
        # 简化的无人机动力学模型（用于演示）
        pos_error = quadcopter.target_position - current_pos
        att_error = quadcopter.target_attitude - current_att
        
        # 模拟无人机响应（简化的一阶模型）
        current_pos += pos_error * 0.1 * dt
        current_att += att_error * 0.2 * dt
        
        # 添加一些噪声（模拟传感器噪声）
        if step > 100:  # 稳定后添加目标变化
            if step == 200:
                quadcopter.set_target_position(2, 1, 5)  # 移动到新位置
            elif step == 400:
                quadcopter.set_target_attitude(10, 5, 20)  # 改变姿态
        
        # 打印进度
        if step % 100 == 0:
            print(
                f"Time: {step*dt:.1f}s,"
                f"Position: [{current_pos[0]:.2f}, {current_pos[1]:.2f}, {current_pos[2]:.2f}], "
                f"Attitude: [{current_att[0]:.1f}, {current_att[1]:.1f}, {current_att[2]:.1f}]"
            )
    # Performance analysis and plotting
    tuner.analyze_performance(quadcopter)
    quadcopter.plot_results()
    
    return quadcopter

def manual_pid_tuning():
    """手动PID调试示例"""
    print("手动PID调试示例")
    print("=" * 50)
    
    # 创建一个简单的PID控制器进行调试
    pid = PIDController(PIDParams(kp=1.2, ki=1.2, kd=0.3, out_max=10.0, i_max=5.0))
    
    # 模拟系统响应（简单的质量-弹簧-阻尼系统）
    def simulate_system(control_input, state, dt):
        # 二阶系统: m*x'' + b*x' + k*x = u
        m, b, k = 1.0, 0.5, 2.0
        
        # 状态: [位置, 速度]
        x, v = state
        
        # 加速度
        a = (control_input - b*v - k*x) / m
        
        # 更新状态
        v_new = v + a * dt
        x_new = x + v_new * dt
        
        return np.array([x_new, v_new])
    
    # 仿真参数
    target = 1.0  # 目标位置
    state = np.array([0.0, 0.0])  # 初始状态 [位置, 速度]
    dt = 0.01
    time_steps = 10000
    
    # 记录数据
    times = np.linspace(0, time_steps*dt, time_steps)
    positions = np.zeros(time_steps)
    controls = np.zeros(time_steps)
    errors = np.zeros(time_steps)
    
    # 仿真循环
    for i in range(time_steps):
        error = target - state[0]
        
        # PID控制
        control = pid.update(error, dt)
        
        # 系统响应
        state = simulate_system(control, state, dt)
        
        # 记录
        positions[i] = state[0]
        controls[i] = control
        errors[i] = error
    
    # 绘制响应曲线
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))
    
    axes[0].plot(times, positions, 'b-', label='Position Response')
    axes[0].axhline(y=target, color='r', linestyle='--', label='Target Value')
    axes[0].set_ylabel('Position')
    axes[0].set_title(f'PID Response (Kp={pid.params.kp}, Ki={pid.params.ki}, Kd={pid.params.kd})')
    axes[0].legend()
    axes[0].grid(True)
    
    axes[1].plot(times, controls, 'g-', label='Control Input')
    axes[1].plot(times, errors, 'r-', label='Error')
    axes[1].set_xlabel('Time (sec)')
    axes[1].set_ylabel('Control Input / Error')
    axes[1].legend()
    axes[1].grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # 计算性能指标
    steady_state_error = errors[-100:].mean()
    overshoot = max(positions) - target if max(positions) > target else 0
    settling_time = None
    
    # 找到稳定时间（进入2%误差带的时间）
    tolerance = 0.02 * target
    for i, pos in enumerate(positions):
        if abs(pos - target) <= tolerance:
            settling_time = times[i]
            break
    
    print("系统性能分析:")
    print(f"  稳态误差: {steady_state_error:.2f}")
    print(f"  超调量: {overshoot:.4f}")
    if settling_time:
        print(f"  稳定时间: {settling_time:.2f}s")
    print("=" * 50)

if __name__ == "__main__":
    # 运行模拟
    print("选择模拟模式:")
    print("1. 完整四旋翼模拟")
    print("2. 简单PID调试示例")
    
    choice = input("请输入选择 (1 或 2): ")
    
    if choice == "1":
        quad = simulate_quadcopter()
    elif choice == "2":
        manual_pid_tuning()
    else:
        print("无效选择，运行完整模拟...")
        quad = simulate_quadcopter()