#!/usr/bin/env python3
"""
测试收入下降报警功能并发送到飞书
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


def test_alert_and_send():
    """测试报警功能并发送到飞书"""
    print("="*80)
    print("测试收入下降报警功能（将发送到飞书）")
    print("="*80)
    print()

    # 模拟数据：收入下降超过30%
    processor = MultiTableDataProcessor(app_token="LvSAboJTJanJKdssWs8cm49vn8c")

    # 获取真实的昨日数据
    yesterday = datetime.now().date() - timedelta(days=1)
    day_before = datetime.now().date() - timedelta(days=2)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    day_before_str = day_before.strftime("%Y-%m-%d")

    # 获取基础数据
    base_records = processor.fetch_data('tblM5x1uyjwffoBq', 'vew8YRRC3u')
    channel_records = processor.fetch_data('tblBiiYpOdRGonPy', 'vew8YRRC3u')
    country_records = processor.fetch_data('tblgx4cY7LvncsiJ', 'vew8YRRC3u')

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

    def get_date_groups(records, date_str, proc):
        if not records:
            return {}
        from collections import defaultdict
        groups = defaultdict(lambda: {'dau': 0, 'new_users': 0, 'income': 0, 'paid_users': 0})
        for record in records:
            parsed = proc.parse_record(record)
            if parsed and parsed.get('date') == date_str:
                group = parsed.get('group', '未知')
                groups[group]['dau'] += parsed.get('dau', 0)
                groups[group]['new_users'] += parsed.get('new_users', 0)
                groups[group]['income'] += parsed.get('income', 0)
                groups[group]['paid_users'] += parsed.get('paid_users', 0)
        return dict(groups)

    y_base = get_date_summary(base_records, yesterday_str, processor)
    d_base = get_date_summary(base_records, day_before_str, processor)

    # 模拟前日收入（设为昨日的2倍，这样昨日收入就下降了50%）
    d_income = y_base['income'] * 2
    d_dau = y_base['dau']
    d_paid = y_base['paid_users']
    d_new_users = y_base['new_users']

    # 计算昨日指标
    y_dau = y_base['dau']
    y_paid = y_base['paid_users']
    y_income = y_base['income']

    y_paid_rate = round(y_paid / y_dau * 100, 2) if y_dau > 0 else 0
    y_arpu = round(y_income / y_dau, 2) if y_dau > 0 else 0
    y_arppu = round(y_income / y_paid, 2) if y_paid > 0 else 0

    # 计算前日指标
    d_paid_rate = round(d_paid / d_dau * 100, 2) if d_dau > 0 else 0
    d_arpu = round(d_income / d_dau, 2) if d_dau > 0 else 0
    d_arppu = round(d_income / d_paid, 2) if d_paid > 0 else 0

    # 计算变化百分比
    income_change_pct = round(((y_income - d_income) / d_income) * 100, 2) if d_income > 0 else 0

    print(f"模拟前日收入：${d_income:,.2f}")
    print(f"昨日实际收入：${y_income:,.2f}")
    print(f"收入变化：{income_change_pct}%")
    print(f"收入下降超过30%：{'是' if income_change_pct < -30 else '否'}")
    print()

    # 生成报告
    def format_currency(value):
        return f"${value:,.2f}"

    def format_change(current, previous, is_percentage=False, is_currency=False):
        if previous == 0:
            if current == 0:
                return "0 → 0 (0, 0%)"
            return f"0 → {format_value(current, is_percentage, is_currency)} (+{current:,}, 新增)"

        change = current - previous
        change_pct = round((change / previous) * 100, 2) if previous > 0 else 0

        if isinstance(change, float):
            change = round(change, 2)

        prev_str = format_value(previous, is_percentage, is_currency)
        curr_str = format_value(current, is_percentage, is_currency)

        if change > 0:
            return f"{prev_str} → {curr_str} (+{change:,}, +{change_pct}%)"
        elif change < 0:
            return f"{prev_str} → {curr_str} ({change:,}, {change_pct}%)"
        else:
            return f"{prev_str} → {curr_str} (0, 0%)"

    def format_value(value, is_percentage=False, is_currency=False):
        if is_percentage:
            return f"{value:.2f}%"
        elif is_currency:
            return f"${value:,.2f}"
        else:
            return f"{value:,}"

    report_lines = []

    # 标题
    report_lines.append(f"**昨日（{yesterday_str}）总览数据**")
    report_lines.append(f"- DAU：{y_dau:,}")
    report_lines.append(f"- 新增用户：{y_base['new_users']:,}")
    report_lines.append(f"- 总收入：{format_currency(y_income)}")
    report_lines.append(f"- 付费用户数：{y_paid:,}")
    report_lines.append(f"- 付费率：{y_paid_rate:.2f}%")
    report_lines.append(f"- ARPU：{format_currency(y_arpu)}")
    report_lines.append(f"- ARPPU：{format_currency(y_arppu)}")

    report_lines.append("")
    report_lines.append(f"对照前日（{day_before_str}）变化（模拟）：")
    report_lines.append(f"- DAU：{format_change(y_dau, d_dau)}")
    report_lines.append(f"- 新增用户：{format_change(y_base['new_users'], d_new_users)}")
    report_lines.append(f"- 总收入：{format_change(y_income, d_income, is_currency=True)}")
    report_lines.append(f"- 付费用户数：{format_change(y_paid, d_paid)}")
    report_lines.append(f"- 付费率：{format_change(y_paid_rate, d_paid_rate, is_percentage=True)}")
    report_lines.append(f"- ARPU：{format_change(y_arpu, d_arpu, is_currency=True)}")
    report_lines.append(f"- ARPPU：{format_change(y_arppu, d_arppu, is_currency=True)}")

    report_lines.append("")
    report_lines.append("**变化原因细拆：**")
    report_lines.append("- 此处为模拟数据，暂不展示具体归因")

    # 添加报警信息
    if income_change_pct < -30:
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("⚠️ **收入异常报警**")
        report_lines.append("<at user_id=\"all\">所有人</at> 请注意！")
        report_lines.append(f"昨日收入较前日下降 **{abs(income_change_pct):.2f}%**，请及时关注！")
        report_lines.append(f"前日收入：${d_income:,.2f}")
        report_lines.append(f"昨日收入：${y_income:,.2f}")
        report_lines.append(f"下降金额：${d_income - y_income:,.2f}")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("*⚠️ 此为测试消息，实际收入数据请以真实日报为准*")

    report = "\n".join(report_lines)

    print("="*80)
    print("生成的测试报告")
    print("="*80)
    print(report)
    print("="*80)
    print()

    # 保存到文件
    with open('test_alert_report.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print("✅ 测试报告已保存到: test_alert_report.md")
    print()

    # 发送到飞书
    print("正在发送测试报告到飞书群组...")
    print()

    os.environ["FEISHU_WEBHOOK_URL"] = "https://open.feishu.cn/open-apis/bot/v2/hook/9d70437e-690c-4f96-8601-5b7058db0ebd"

    from daily_report_main import send_to_feishu

    success = send_to_feishu("🧪 收入报警功能测试（模拟数据）", report)

    if success:
        print()
        print("✅ 测试报告已成功发送到飞书群组！")
        print()
        print("请在飞书群组中查看：")
        print("1. 是否显示@所有人")
        print("2. 报警信息格式是否正确")
        print("3. 收入下降数据是否清晰")
    else:
        print()
        print("❌ 发送失败，请检查网络或配置")


if __name__ == "__main__":
    test_alert_and_send()
