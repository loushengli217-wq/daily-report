#!/usr/bin/env python3
"""
日报服务（使用 APScheduler，更稳定）
支持进程持久化和自动恢复
"""

import sys
import os
import time
import json
import subprocess
import signal
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/service.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 配置文件
CONFIG_FILES = [
    "scripts/projects/project_ershong.json",
    "scripts/projects/project_pocket.json"
]

# PID 文件
PID_FILE = "logs/service.pid"


def run_report(config_file):
    """执行报告生成"""
    try:
        logger.info(f"========================================")
        logger.info(f"开始执行日报任务: {config_file}")
        logger.info(f"========================================")

        cmd = [sys.executable, "scripts/generate_report.py", "--config", config_file]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        if result.stdout:
            logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)

        if result.returncode == 0:
            logger.info(f"✅ {config_file} 执行成功")
        else:
            logger.error(f"❌ {config_file} 执行失败，返回码: {result.returncode}")

    except Exception as e:
        logger.error(f"❌ 执行异常: {str(e)}", exc_info=True)


def job_listener(event):
    """任务监听器"""
    if event.exception:
        logger.error(f"任务执行异常: {event.exception}")
    else:
        logger.info(f"任务执行成功: {event.job_id}")


def write_pid():
    """写入 PID 文件"""
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))


def cleanup_pid():
    """清理 PID 文件"""
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)


def signal_handler(signum, frame):
    """信号处理器"""
    logger.info(f"收到信号 {signum}，正在停止服务...")
    cleanup_pid()
    sys.exit(0)


def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # 创建日志目录
    os.makedirs("logs", exist_ok=True)

    # 写入 PID
    write_pid()

    logger.info("="*80)
    logger.info("启动日报服务（APScheduler 版本）")
    logger.info("="*80)
    logger.info(f"服务 PID: {os.getpid()}")
    logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 加载配置
    jobs = []
    for config_file in CONFIG_FILES:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                project_name = config.get("project_name", "Unknown")
                schedule_time = config.get("report", {}).get("schedule_time", "10:01")

                logger.info(f"✅ 加载项目: {project_name} - {schedule_time}")
                jobs.append({
                    "name": project_name,
                    "config": config_file,
                    "time": schedule_time
                })
        except Exception as e:
            logger.error(f"❌ 加载配置失败: {config_file} - {str(e)}")

    if not jobs:
        logger.error("❌ 没有找到任何项目配置！")
        cleanup_pid()
        sys.exit(1)

    # 创建调度器
    scheduler = BackgroundScheduler()
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    # 添加任务
    for job in jobs:
        hour, minute = job["time"].split(":")
        scheduler.add_job(
            run_report,
            trigger=CronTrigger(hour=int(hour), minute=int(minute)),
            args=[job["config"]],
            id=job["name"],
            name=job["name"],
            replace_existing=True
        )
        logger.info(f"📅 {job['name']} 已设置为每天 {job['time']} 执行")

    # 添加健康检查任务（每小时记录一次）
    scheduler.add_job(
        lambda: logger.info("💓 服务健康检查：正常运行中"),
        trigger=CronTrigger(minute=0),
        id="health_check"
    )

    logger.info("="*80)
    logger.info("服务已启动，等待定时任务执行...")
    logger.info("按 Ctrl+C 停止服务")
    logger.info("="*80)

    try:
        # 启动调度器
        scheduler.start()

        # 主循环
        while True:
            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭...")
    except Exception as e:
        logger.error(f"服务异常: {str(e)}", exc_info=True)
    finally:
        scheduler.shutdown()
        cleanup_pid()
        logger.info("服务已停止")


if __name__ == "__main__":
    main()
