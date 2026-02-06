#!/usr/bin/env python3
"""
简化的数据分析报告生成器
只生成昨日数据汇总部分
"""

import sys
import os
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scripts_dir = os.path.join(project_root, "scripts")
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, scripts_dir)

from multi_table_processor import MultiTableDataProcessor


def format_currency(value):
    """格式化货币"""
    return f"${value:,.2f}"


def format_change(current, previous, label, is_percentage=False):
    """格式化变化"""
    if previous == 0:
        return f"{label}: 新增"

    change = current - previous
    change_pct = round((change / previous) * 100, 2) if previous > 0 else 0

    if is_percentage:
        if change > 0:
            return f"{label}: +{change:.2f}% ↑"
        elif change < 0:
            return f"{label}: {change:.2f}% ↓"
        else:
            return f"{label}: 0%"
    else:
        if change > 0:
            return f"{label}: +{change:,} (+{change_pct:.1f}%) ↑"
        elif change < 0:
            return f"{label}: {change:,} ({change_pct:.1f}%) ↓"
        else:
            return f"{label}: 0 (0%)"


def generate_simple_report(processor, table_configs):
    """生成简化报告（只包含昨日数据汇总）"""
    print("="*80)
    print("开始生成数据分析报告")
    print("="*80)

    # 获取基础数据
    print("\n获取表格数据: 游戏基础数据")
    base_result = processor.process_table_data(
        table_configs[0]['table_id'],
        table_configs[0]['view_id'],
        last_n=50
    )

    # 从 daily_summary 获取日期列表
    daily_summary = base_result.get('daily_summary', {})
    target_dates = base_result.get('target_dates', [])

    if len(target_dates) < 2:
        print("\n❌ 数据不足，无法对比！")
        return None

    yesterday_date = target_dates[-1]
    day_before_date = target_dates[-2]

    print(f"昨日: {yesterday_date}")
    print(f"前日: {day_before_date}")

    # 从 daily_summary 获取昨日和前日数据
    yesterday_data = daily_summary.get(yesterday_date, {})
    day_before_data = daily_summary.get(day_before_date, {})

    # 使用总数据
    y_data = yesterday_data.get('total', {})
    d_data = day_before_data.get('total', {})

    # 生成简化报告
    report_lines = []

    report_lines.append(f"《二重螺旋-海外》 - {yesterday_date} 日报")

    # 昨日数据汇总
    report_lines.append(f"\n**昨日数据汇总（{yesterday_date}）：**")

    report_lines.append(f"- **DAU**：{y_data.get('dau', 0):,}")
    report_lines.append(f"- **新增用户**：{y_data.get('new_users', 0):,}")
    report_lines.append(f"- **总收入**：{format_currency(y_data.get('income', 0))}")
    report_lines.append(f"- **付费用户数**：{y_data.get('paid_users', 0):,}")
    report_lines.append(f"- **付费率**：{y_data.get('paid_rate', 0):.2f}%")
    report_lines.append(f"- **ARPU**：{format_currency(y_data.get('arpu', 0))}")
    report_lines.append(f"- **ARPPU**：{format_currency(y_data.get('arppu', 0))}")

    report_lines.append(f"\n**对照前日（{day_before_date}）变化：**")
    report_lines.append(f"- DAU：{format_change(y_data.get('dau', 0), d_data.get('dau', 0), 'DAU')}")
    report_lines.append(f"- 新增用户：{format_change(y_data.get('new_users', 0), d_data.get('new_users', 0), '新增用户')}")
    report_lines.append(f"- 总收入：{format_change(y_data.get('income', 0), d_data.get('income', 0), '总收入')}")
    report_lines.append(f"- 付费用户数：{format_change(y_data.get('paid_users', 0), d_data.get('paid_users', 0), '付费用户数')}")
    report_lines.append(f"- 付费率：{format_change(y_data.get('paid_rate', 0), d_data.get('paid_rate', 0), '付费率', is_percentage=True)}")
    report_lines.append(f"- ARPU：{format_change(y_data.get('arpu', 0), d_data.get('arpu', 0), 'ARPU')}")
    report_lines.append(f"- ARPPU：{format_change(y_data.get('arppu', 0), d_data.get('arppu', 0), 'ARPPU')}")

    return "\n".join(report_lines)


def main():
    """主函数"""
    # 创建数据处理器
    processor = MultiTableDataProcessor(app_token="LvSAboJTJanJKdssWs8cm49vn8c")

    # 表格配置
    table_configs = [
        {"name": "游戏基础数据", "table_id": "tblM5x1uyjwffoBq", "view_id": "vew8YRRC3u", "last_n": 50}
    ]

    # 生成报告
    report = generate_simple_report(processor, table_configs)

    if report:
        # 保存到文件
        with open('daily_report.md', 'w', encoding='utf-8') as f:
            f.write(report)

        print("\n" + "="*80)
        print("分析报告")
        print("="*80)
        print(report)
        print("="*80)
        print("✅ 分析完成！")
        print(f"📄 报告已保存到: daily_report.md")

        # 发送到飞书
        print("\n正在发送报告到飞书群组...")
        from daily_report_main import send_to_feishu
        send_to_feishu("🎮 二重螺旋-海外 数据日报", report)


if __name__ == "__main__":
    main()
