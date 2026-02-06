#!/usr/bin/env python3
"""
多项目日报定时调度器
支持多个项目，每个项目可以设置独立的调度时间
"""

import time
import schedule
import subprocess
import json
from datetime import datetime
import logging
import sys
import os
import glob

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/multi_project_scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_project_configs():
    """加载所有项目配置"""
    configs = {}
    projects_dir = os.path.join(os.path.dirname(__file__), "projects")

    # 查找所有项目配置文件（排除模板文件）
    config_files = glob.glob(os.path.join(projects_dir, "project_*.json"))

    for config_file in sorted(config_files):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                project_id = config.get("project_id")
                project_name = config.get("project_name")
                schedule_time = config.get("report", {}).get("schedule_time", "10:01")

                if project_id:
                    configs[project_id] = {
                        "config_file": config_file,
                        "project_name": project_name,
                        "schedule_time": schedule_time,
                        "config": config
                    }
                    logger.info(f"✅ 加载项目配置: {project_name} ({project_id}) - 调度时间: {schedule_time}")
                else:
                    logger.warning(f"⚠️  跳过配置文件（缺少 project_id）: {config_file}")
        except Exception as e:
            logger.error(f"❌ 加载配置文件失败: {config_file} - {str(e)}")

    return configs


def run_project_report(project_id, project_name, config_file):
    """执行指定项目的报告生成任务"""
    logger.info("="*80)
    logger.info(f"开始执行 {project_name} ({project_id}) 日报任务")
    logger.info("="*80)

    try:
        # 执行报告生成脚本
        cmd = [sys.executable, "scripts/generate_report.py", "--config", config_file]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # 输出执行结果
        if result.stdout:
            logger.info(result.stdout)
        if result.stderr:
            logger.error(result.stderr)

        if result.returncode == 0:
            logger.info(f"✅ {project_name} 日报任务执行成功")
        else:
            logger.error(f"❌ {project_name} 日报任务执行失败，返回码: {result.returncode}")

    except Exception as e:
        logger.error(f"❌ {project_name} 日报任务执行异常: {str(e)}", exc_info=True)

    logger.info("="*80)


def main():
    """主函数：启动多项目定时调度器"""
    logger.info("="*80)
    logger.info("启动多项目日报定时调度器")
    logger.info("="*80)
    logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 加载所有项目配置
    project_configs = load_project_configs()

    if not project_configs:
        logger.error("❌ 没有找到任何项目配置文件！")
        logger.info("请在 scripts/projects/ 目录下创建 project_*.json 配置文件")
        sys.exit(1)

    logger.info(f"\n共加载 {len(project_configs)} 个项目配置\n")

    # 为每个项目设置定时任务
    current_time = datetime.now().time()

    for project_id, project_info in project_configs.items():
        project_name = project_info["project_name"]
        schedule_time = project_info["schedule_time"]
        config_file = project_info["config_file"]

        # 设置定时任务
        schedule.every().day.at(schedule_time).do(
            run_project_report,
            project_id=project_id,
            project_name=project_name,
            config_file=config_file
        )

        logger.info(f"📅 {project_name} 已设置为每天 {schedule_time} 执行")

    # 检查是否有项目的调度时间已过
    logger.info("\n检查项目调度时间...")
    for project_id, project_info in project_configs.items():
        schedule_time_str = project_info["schedule_time"]
        schedule_time = datetime.strptime(schedule_time_str, "%H:%M").time()

        if current_time > schedule_time:
            logger.info(f"⚠️  {project_info['project_name']} 的调度时间 ({schedule_time_str}) 已过，需等到明天")

    logger.info("\n" + "="*80)
    logger.info("按 Ctrl+C 停止调度器")
    logger.info("="*80)

    # 启动调度循环
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        logger.info("\n调度器已停止")
        sys.exit(0)
    except Exception as e:
        logger.error(f"调度器运行异常: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
