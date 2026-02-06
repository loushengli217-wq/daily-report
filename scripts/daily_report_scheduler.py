#!/usr/bin/env python3
"""
每日日报定时调度器
每天上午10点自动生成并发送日报到飞书群组
"""

import time
import schedule
from datetime import datetime
import logging
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.generate_simple_report import main as run_daily_report

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def run_report():
    """执行日报生成和发送任务"""
    logger.info("="*80)
    logger.info("开始执行定时日报任务")
    logger.info("="*80)

    try:
        # 执行日报主程序
        run_daily_report()
        logger.info("✅ 定时日报任务执行成功")
    except Exception as e:
        logger.error(f"❌ 定时日报任务执行失败: {str(e)}", exc_info=True)
        # 发送错误通知到飞书（可选）
        try:
            from tools.feishu_message_tool import send_text_message
            send_text_message(f"❌ 日报生成失败: {str(e)}")
        except:
            pass

    logger.info("="*80)


def main():
    """主函数：启动定时调度器"""
    logger.info("="*80)
    logger.info("启动每日日报定时调度器")
    logger.info("="*80)
    logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("调度规则: 每天上午 10:01 执行")

    # 检查自定义 webhook
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
    if webhook_url:
        logger.info(f"使用自定义 Webhook: {webhook_url[:50]}...")
    else:
        logger.info("使用集成服务 Webhook")

    logger.info("按 Ctrl+C 停止调度器")
    logger.info("="*80)

    # 设置定时任务：每天上午10:01执行
    schedule.every().day.at("10:01").do(run_report)

    # 首次启动时检查是否需要立即执行（如果是10:01之后）
    current_time = datetime.now().time()
    schedule_time = datetime.strptime("10:01", "%H:%M").time()
    if current_time > schedule_time:
        logger.info("当前时间已超过10:01，询问是否立即执行...")
        logger.info("如需立即执行，请手动运行: python scripts/generate_simple_report.py")

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
