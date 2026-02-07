#!/usr/bin/env python3
"""
调度器守护脚本
功能：监控多项目调度器进程，如果进程挂了自动重启
"""

import time
import subprocess
import psutil
import logging
import sys
import os
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitor_scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 调度器进程名称
SCHEDULER_CMD = "python scripts/multi_project_scheduler.py"
# 检查间隔（秒）
CHECK_INTERVAL = 60


def find_scheduler_process():
    """查找调度器进程"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            if SCHEDULER_CMD in cmdline and 'python' in cmdline:
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None


def start_scheduler():
    """启动调度器"""
    logger.info("🚀 正在启动调度器...")
    try:
        # 使用 nohup 后台启动
        cmd = f"nohup python scripts/multi_project_scheduler.py > logs/scheduler_output.log 2>&1 &"
        subprocess.run(cmd, shell=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        time.sleep(3)  # 等待启动

        # 检查是否启动成功
        pid = find_scheduler_process()
        if pid:
            logger.info(f"✅ 调度器启动成功，PID: {pid}")
            return True
        else:
            logger.error("❌ 调度器启动失败")
            return False
    except Exception as e:
        logger.error(f"❌ 启动调度器时发生异常: {str(e)}", exc_info=True)
        return False


def main():
    """主函数"""
    logger.info("="*80)
    logger.info("启动调度器守护脚本")
    logger.info("="*80)
    logger.info(f"守护进程 PID: {os.getpid()}")
    logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"检查间隔: {CHECK_INTERVAL} 秒")

    # 首次启动，确保调度器在运行
    scheduler_pid = find_scheduler_process()
    if not scheduler_pid:
        logger.warning("⚠️  调度器未运行，正在启动...")
        start_scheduler()
    else:
        logger.info(f"✅ 调度器正在运行，PID: {scheduler_pid}")

    logger.info("="*80)
    logger.info("守护脚本进入监控模式，按 Ctrl+C 停止")
    logger.info("="*80)

    # 监控循环
    while True:
        try:
            scheduler_pid = find_scheduler_process()

            if scheduler_pid:
                # 调度器正常运行
                logger.debug(f"✅ 调度器运行正常，PID: {scheduler_pid}")
            else:
                # 调度器挂了，需要重启
                logger.warning("⚠️  检测到调度器进程不存在，正在重启...")
                start_scheduler()

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            logger.info("\n守护脚本已停止")
            logger.info(f"调度器状态: {'运行中' if find_scheduler_process() else '已停止'}")
            break
        except Exception as e:
            logger.error(f"❌ 守护脚本运行异常: {str(e)}", exc_info=True)
            time.sleep(10)  # 异常后等待10秒再继续


if __name__ == "__main__":
    main()
