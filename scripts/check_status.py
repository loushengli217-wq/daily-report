#!/usr/bin/env python3
"""
系统状态检查脚本
快速检查调度器和守护脚本的运行状态
"""

import sys
import os
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.monitor_scheduler import find_scheduler_process


def check_process(pid):
    """检查进程是否在运行"""
    try:
        result = subprocess.run(['ps', '-p', str(pid), '-o', 'pid,etime,cmd'],
                                capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False


def find_monitor_process():
    """查找守护进程"""
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True, text=True
        )
        for line in result.stdout.split('\n'):
            if 'monitor_scheduler.py' in line and 'grep' not in line:
                parts = line.split()
                if parts:
                    return int(parts[1])
    except:
        pass
    return None


def main():
    """主函数"""
    print("="*80)
    print("📊 日报系统状态检查")
    print("="*80)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 检查调度器
    scheduler_pid = find_scheduler_process()
    print("📅 调度器状态:")
    if scheduler_pid:
        if check_process(scheduler_pid):
            print(f"  ✅ 运行中 (PID: {scheduler_pid})")
        else:
            print(f"  ❌ 进程不存在 (PID: {scheduler_pid})")
    else:
        print("  ❌ 未运行")

    # 检查守护脚本
    monitor_pid = find_monitor_process()
    print("\n🛡️  守护脚本状态:")
    if monitor_pid:
        if check_process(monitor_pid):
            print(f"  ✅ 运行中 (PID: {monitor_pid})")
            print(f"  📝 监控调度器，自动重启")
        else:
            print(f"  ❌ 进程不存在 (PID: {monitor_pid})")
    else:
        print("  ❌ 未运行")

    # 总体状态
    print("\n" + "="*80)
    if scheduler_pid and monitor_pid and check_process(scheduler_pid) and check_process(monitor_pid):
        print("✅ 系统状态正常！")
        print("   - 调度器正在运行，每天 10:01 自动发送日报")
        print("   - 守护脚本正在监控，确保调度器持续运行")
    else:
        print("⚠️  系统状态异常！")
        if not scheduler_pid or not check_process(scheduler_pid):
            print("   ⚠️  调度器未运行，需要启动")
        if not monitor_pid or not check_process(monitor_pid):
            print("   ⚠️  守护脚本未运行，需要启动")
    print("="*80)

    # 显示日志路径
    print("\n📄 日志文件:")
    print("  - 调度器日志: logs/multi_project_scheduler.log")
    print("  - 调度器输出: logs/scheduler_output.log")
    print("  - 守护日志: logs/monitor_scheduler.log")
    print("  - 守护输出: logs/monitor_output.log")


if __name__ == "__main__":
    main()
