#!/usr/bin/env python3
"""
测试收入下降报警功能
模拟收入下降超过30%的情况
"""

import sys
import os
from datetime import datetime, timedelta

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scripts_dir = os.path.join(project_root, "scripts")
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, scripts_dir)

from generate_simple_report import MultiTableDataProcessor


def test_alert():
    """测试报警功能"""
    print("="*80)
    print("测试收入下降报警功能")
    print("="*80)

    # 模拟数据：收入下降超过30%
    processor = MultiTableDataProcessor(app_token="LvSAboJTJanJKdssWs8cm49vn8c")

    # 获取真实的昨日数据
    yesterday = datetime.now().date() - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")

    base_records = processor.fetch_data('tblM5x1uyjwffoBq', 'vew8YRRC3u')

    def get_date_summary(records, date_str, proc):
        if not records:
            return {'dau': 0, 'new_users': 0, 'income': 0, 'paid_users': 0}

        total = {'dau': 0, 'new_users': 0, 'income': 0, 'paid_users': 0}
        for record in records:
            parsed = proc.parse_record(record)
            if parsed and parsed.get('date') == date_str:
                total['dau'] += parsed.get('dau', 0)
                total['new_users'] += parsed.get('new_users', 0)
                total['income'] += parsed.get('income', 0)
                total['paid_users'] += parsed.get('paid_users', 0)
        return total

    y_base = get_date_summary(base_records, yesterday_str, processor)

    # 模拟前日收入（设为昨日的2倍，这样昨日收入就下降了50%）
    d_income = y_base['income'] * 2
    d_dau = y_base['dau']
    d_paid = y_base['paid_users']
    d_new_users = y_base['new_users']

    # 计算变化百分比
    income_change_pct = round(((y_base['income'] - d_income) / d_income) * 100, 2)

    print(f"模拟前日收入：${d_income:,.2f}")
    print(f"昨日实际收入：${y_base['income']:,.2f}")
    print(f"收入变化：{income_change_pct}%")
    print(f"收入下降超过30%：{'是' if income_change_pct < -30 else '否'}")
    print()

    # 生成报警信息
    alert_user_id = os.getenv("ALERT_USER_ID", "")
    print(f"ALERT_USER_ID: {alert_user_id if alert_user_id else '未配置（将@所有人）'}")
    print()

    if income_change_pct < -30:
        report_lines = []
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("⚠️ **收入异常报警**")

        if alert_user_id:
            report_lines.append(f"<at user_id=\"{alert_user_id}\">@相关同学</at> 请注意！")
        else:
            report_lines.append("<at user_id=\"all\">@所有人</at> 请注意！")

        report_lines.append(f"昨日收入较前日下降 **{abs(income_change_pct):.2f}%**，请及时关注！")
        report_lines.append(f"前日收入：${d_income:,.2f}")
        report_lines.append(f"昨日收入：${y_base['income']:,.2f}")
        report_lines.append(f"下降金额：${d_income - y_base['income']:,.2f}")

        alert_message = "\n".join(report_lines)
        print("="*80)
        print("报警信息（模拟）")
        print("="*80)
        print(alert_message)
        print("="*80)
    else:
        print("收入未下降超过30%，无需报警")


if __name__ == "__main__":
    test_alert()
