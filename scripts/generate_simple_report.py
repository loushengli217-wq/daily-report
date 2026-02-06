#!/usr/bin/env python3
"""
简化的数据分析报告生成器
只生成昨日数据汇总部分，使用指定格式
"""

import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scripts_dir = os.path.join(project_root, "scripts")
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, scripts_dir)

from multi_table_processor import MultiTableDataProcessor


def format_change(current, previous, is_percentage=False):
    """格式化变化（仅返回变化量和百分比）"""
    if previous == 0:
        if current == 0:
            return "0 (0%)"
        return f"+{round(current, 2):,} (新增)"

    change = current - previous
    change_pct = round((change / previous) * 100, 2) if previous > 0 else 0

    # 对变化值进行四舍五入
    if isinstance(change, float):
        change = round(change, 2)

    if change > 0:
        return f"+{change:,} (+{change_pct}%)"
    elif change < 0:
        return f"{change:,} ({change_pct}%)"
    else:
        return "0 (0%)"


def format_change_with_values(current, previous, is_percentage=False, is_currency=False):
    """格式化变化（显示前日值和昨日值的对比）"""
    if previous == 0:
        if current == 0:
            return "0 → 0 (0, 0%)"
        return f"0 → {format_value(current, is_percentage, is_currency)} (+{current:,}, 新增)"

    change = current - previous
    change_pct = round((change / previous) * 100, 2) if previous > 0 else 0

    # 对变化值进行四舍五入
    if isinstance(change, float):
        change = round(change, 2)

    prev_str = format_value(previous, is_percentage, is_currency)
    curr_str = format_value(current, is_percentage, is_currency)

    # 添加颜色标记：负数为绿色，正数为红色
    change_str = f"{change:,}"
    change_pct_str = f"{change_pct}%"

    if change > 0:
        # 正数用红色
        change_str = f'<font color="red">{change_str}</font>'
        change_pct_str = f'<font color="red">+{change_pct_str}</font>'
        return f"{prev_str} → {curr_str} ({change_str}, {change_pct_str})"
    elif change < 0:
        # 负数用绿色
        change_str = f'<font color="green">{change_str}</font>'
        change_pct_str = f'<font color="green">{change_pct_str}</font>'
        return f"{prev_str} → {curr_str} ({change_str}, {change_pct_str})"
    else:
        return f"{prev_str} → {curr_str} (0, 0%)"


def format_value(value, is_percentage=False, is_currency=False):
    """格式化数值"""
    if is_percentage:
        return f"{value:.2f}%"
    elif is_currency:
        return f"${value:,.2f}"
    else:
        return f"{value:,}"


def format_currency(value):
    """格式化货币"""
    return f"${value:,.2f}"


def get_date_summary(records, date_str, processor):
    """获取指定日期的汇总数据"""
    if not records:
        return {'dau': 0, 'new_users': 0, 'income': 0, 'paid_users': 0}

    total = {'dau': 0, 'new_users': 0, 'income': 0, 'paid_users': 0}
    for record in records:
        parsed = processor.parse_record(record)
        if parsed and parsed.get('date') == date_str:
            total['dau'] += parsed.get('dau', 0)
            total['new_users'] += parsed.get('new_users', 0)
            total['income'] += parsed.get('income', 0)
            total['paid_users'] += parsed.get('paid_users', 0)

    return total


def get_date_groups(records, date_str, processor):
    """获取指定日期的分组数据（按group字段分组）"""
    if not records:
        return {}

    groups = defaultdict(lambda: {'dau': 0, 'new_users': 0, 'income': 0, 'paid_users': 0})
    for record in records:
        parsed = processor.parse_record(record)
        if parsed and parsed.get('date') == date_str:
            group = parsed.get('group', '未知')
            groups[group]['dau'] += parsed.get('dau', 0)
            groups[group]['new_users'] += parsed.get('new_users', 0)
            groups[group]['income'] += parsed.get('income', 0)
            groups[group]['paid_users'] += parsed.get('paid_users', 0)

    return dict(groups)


def generate_simple_report(processor, table_configs):
    """生成简化报告（只包含昨日数据汇总）"""
    print("="*80)
    print("开始生成数据分析报告")
    print("="*80)

    # 获取当前日期
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    day_before_yesterday = today - timedelta(days=2)

    yesterday_str = yesterday.strftime("%Y-%m-%d")
    day_before_str = day_before_yesterday.strftime("%Y-%m-%d")

    print(f"当前日期: {today}")
    print(f"昨日: {yesterday_str}")
    print(f"前日: {day_before_str}")

    # 获取所有数据（记录是按日期倒序的）
    print("\n获取数据...")
    base_records = processor.fetch_data(table_configs[0]['table_id'], table_configs[0]['view_id'])
    channel_records = processor.fetch_data(table_configs[1]['table_id'], table_configs[1]['view_id'])
    country_records = processor.fetch_data(table_configs[2]['table_id'], table_configs[2]['view_id'])

    # 检查可用日期
    from collections import Counter
    available_dates = set()
    for record in base_records[:50]:
        parsed = processor.parse_record(record)
        if parsed:
            available_dates.add(parsed['date'])

    if yesterday_str not in available_dates or day_before_str not in available_dates:
        print(f"\n❌ 未找到指定日期的数据！")
        print(f"最近可用日期: {sorted(list(available_dates), reverse=True)[:5]}")
        return None

    # 获取基础数据
    y_base = get_date_summary(base_records, yesterday_str, processor)
    d_base = get_date_summary(base_records, day_before_str, processor)

    # 计算付费率、ARPU、ARPPU
    y_dau = y_base['dau']
    y_paid = y_base['paid_users']
    y_income = y_base['income']

    d_dau = d_base['dau']
    d_paid = d_base['paid_users']
    d_income = d_base['income']

    y_paid_rate = round(y_paid / y_dau * 100, 2) if y_dau > 0 else 0
    y_arpu = round(y_income / y_dau, 2) if y_dau > 0 else 0
    y_arppu = round(y_income / y_paid, 2) if y_paid > 0 else 0

    d_paid_rate = round(d_paid / d_dau * 100, 2) if d_dau > 0 else 0
    d_arpu = round(d_income / d_dau, 2) if d_dau > 0 else 0
    d_arppu = round(d_income / d_paid, 2) if d_paid > 0 else 0

    # 生成报告
    report_lines = []

    report_lines.append(f"**昨日（{yesterday_str}）总览数据**")
    report_lines.append(f"- DAU：{y_dau:,}")
    report_lines.append(f"- 新增用户：{y_base['new_users']:,}")
    report_lines.append(f"- 总收入：{format_currency(y_income)}")
    report_lines.append(f"- 付费用户数：{y_paid:,}")
    report_lines.append(f"- 付费率：{y_paid_rate:.2f}%")
    report_lines.append(f"- ARPU：{format_currency(y_arpu)}")
    report_lines.append(f"- ARPPU：{format_currency(y_arppu)}")

    report_lines.append("")
    report_lines.append(f"**对照前日（{day_before_str}）变化：**")
    report_lines.append(f"- DAU：{format_change_with_values(y_dau, d_dau)}")
    report_lines.append(f"- 新增用户：{format_change_with_values(y_base['new_users'], d_base['new_users'])}")
    report_lines.append(f"- 总收入：{format_change_with_values(y_income, d_income, is_currency=True)}")
    report_lines.append(f"- 付费用户数：{format_change_with_values(y_paid, d_paid)}")
    report_lines.append(f"- 付费率：{format_change_with_values(y_paid_rate, d_paid_rate, is_percentage=True)}")
    report_lines.append(f"- ARPU：{format_change_with_values(y_arpu, d_arpu, is_currency=True)}")
    report_lines.append(f"- ARPPU：{format_change_with_values(y_arppu, d_arppu, is_currency=True)}")

    # 变化原因细拆
    report_lines.append("")
    report_lines.append("**变化原因细拆：**")

    # 分析渠道数据
    y_channel = get_date_groups(channel_records, yesterday_str, processor)
    d_channel = get_date_groups(channel_records, day_before_str, processor)

    # 收入变化归因
    income_changes = {}
    for channel_name in y_channel:
        y_income = y_channel[channel_name]['income']
        d_income = d_channel.get(channel_name, {}).get('income', 0)
        income_change = y_income - d_income
        if abs(income_change) > 0:
            income_changes[channel_name] = income_change

    # 使用渠道数据表中的总收入变化
    channel_y_income = sum(data['income'] for data in y_channel.values())
    channel_d_income = sum(data['income'] for data in d_channel.values())
    channel_income_change = channel_y_income - channel_d_income

    if income_changes and abs(channel_income_change) > 0:
        # 过滤掉"其他"分类，优先选择具体的渠道
        specific_changes = {k: v for k, v in income_changes.items() if k != "其他"}
        if not specific_changes:
            specific_changes = income_changes

        max_income_change = max(specific_changes.items(), key=lambda x: abs(x[1]))
        contribution_pct = round(abs(max_income_change[1]) / abs(channel_income_change) * 100, 0)
        if contribution_pct > 10:
            channel_name = max_income_change[0]
            change_amount = max_income_change[1]
            if change_amount < 0:
                report_lines.append(f"- 收入下降{contribution_pct:.0f}%来自{channel_name}：该渠道收入减少${abs(change_amount):,.2f}，占总收入下降的{contribution_pct:.0f}%")
            elif change_amount > 0:
                report_lines.append(f"- 收入增长{contribution_pct:.0f}%来自{channel_name}：该渠道收入增长${change_amount:,.2f}，占总收入增长的{contribution_pct:.0f}%")

    # DAU变化归因
    dau_changes = {}
    for channel_name in y_channel:
        y_dau = y_channel[channel_name]['dau']
        d_dau = d_channel.get(channel_name, {}).get('dau', 0)
        dau_change = y_dau - d_dau
        if abs(dau_change) > 0:
            dau_changes[channel_name] = dau_change

    # 使用渠道数据表中的总DAU变化
    channel_y_dau = sum(data['dau'] for data in y_channel.values())
    channel_d_dau = sum(data['dau'] for data in d_channel.values())
    channel_dau_change = channel_y_dau - channel_d_dau

    if dau_changes and abs(channel_dau_change) > 0:
        max_dau_change = max(dau_changes.items(), key=lambda x: abs(x[1]))
        contribution_pct = round(abs(max_dau_change[1]) / abs(channel_dau_change) * 100, 0)
        if contribution_pct > 10:
            channel_name = max_dau_change[0]
            change_amount = max_dau_change[1]
            if change_amount < 0:
                report_lines.append(f"- DAU下降{contribution_pct:.0f}%来自{channel_name}：该渠道DAU减少{abs(change_amount):,}，占总DAU下降的{contribution_pct:.0f}%")
            elif change_amount > 0:
                report_lines.append(f"- DAU增长{contribution_pct:.0f}%来自{channel_name}：该渠道DAU增长{change_amount:,}，占总DAU增长的{contribution_pct:.0f}%")

    # 分析国家数据
    y_country = get_date_groups(country_records, yesterday_str, processor)
    d_country = get_date_groups(country_records, day_before_str, processor)

    # 收入变化归因
    country_income_changes = {}
    for country_name in y_country:
        y_income = y_country[country_name]['income']
        d_income = d_country.get(country_name, {}).get('income', 0)
        income_change = y_income - d_income
        if abs(income_change) > 0:
            country_income_changes[country_name] = income_change

    # 使用国家数据表中的总收入变化（排除"其他"分类）
    specific_y_income = sum(data['income'] for name, data in y_country.items() if name != "其他")
    specific_d_income = sum(data['income'] for name, data in d_country.items() if name != "其他")
    country_income_change = specific_y_income - specific_d_income

    if country_income_changes and abs(country_income_change) > 0:
        # 过滤掉"其他"分类，优先选择具体的渠道
        specific_changes = {k: v for k, v in country_income_changes.items() if k != "其他"}
        if not specific_changes:
            specific_changes = country_income_changes

        max_income_change = max(specific_changes.items(), key=lambda x: abs(x[1]))
        contribution_pct = round(abs(max_income_change[1]) / abs(country_income_change) * 100, 0)
        if contribution_pct > 10:
            country_name = max_income_change[0]
            change_amount = max_income_change[1]
            if change_amount < 0:
                report_lines.append(f"- 收入下降{contribution_pct:.0f}%来自{country_name}：该国家收入减少${abs(change_amount):,.2f}，占总收入下降的{contribution_pct:.0f}%")
            elif change_amount > 0:
                report_lines.append(f"- 收入增长{contribution_pct:.0f}%来自{country_name}：该国家收入增长${change_amount:,.2f}，占总收入增长的{contribution_pct:.0f}%")

    # DAU变化归因
    country_dau_changes = {}
    for country_name in y_country:
        y_dau = y_country[country_name]['dau']
        d_dau = d_country.get(country_name, {}).get('dau', 0)
        dau_change = y_dau - d_dau
        if abs(dau_change) > 0:
            country_dau_changes[country_name] = dau_change

    # 使用国家数据表中的总DAU变化（排除"其他"分类）
    specific_y_dau = sum(data['dau'] for name, data in y_country.items() if name != "其他")
    specific_d_dau = sum(data['dau'] for name, data in d_country.items() if name != "其他")
    country_dau_change = specific_y_dau - specific_d_dau

    if country_dau_changes and abs(country_dau_change) > 0:
        # 过滤掉"其他"分类，优先选择具体的渠道
        specific_changes = {k: v for k, v in country_dau_changes.items() if k != "其他"}
        if not specific_changes:
            specific_changes = country_dau_changes

        max_dau_change = max(specific_changes.items(), key=lambda x: abs(x[1]))
        contribution_pct = round(abs(max_dau_change[1]) / abs(country_dau_change) * 100, 0)
        if contribution_pct > 10:
            country_name = max_dau_change[0]
            change_amount = max_dau_change[1]
            if change_amount < 0:
                report_lines.append(f"- DAU下降{contribution_pct:.0f}%来自{country_name}：该国家DAU减少{abs(change_amount):,}，占总DAU下降的{contribution_pct:.0f}%")
            elif change_amount > 0:
                report_lines.append(f"- DAU增长{contribution_pct:.0f}%来自{country_name}：该国家DAU增长{change_amount:,}，占总DAU增长的{contribution_pct:.0f}%")

    return "\n".join(report_lines)


def main():
    """主函数"""
    # 创建数据处理器
    processor = MultiTableDataProcessor(app_token="LvSAboJTJanJKdssWs8cm49vn8c")

    # 表格配置
    table_configs = [
        {"name": "游戏基础数据", "table_id": "tblM5x1uyjwffoBq", "view_id": "vew8YRRC3u"},
        {"name": "游戏渠道数据", "table_id": "tblBiiYpOdRGonPy", "view_id": "vew8YRRC3u"},
        {"name": "游戏主要国家数据", "table_id": "tblgx4cY7LvncsiJ", "view_id": "vew8YRRC3u"}
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
        # 设置自定义 Webhook URL
        import os
        os.environ["FEISHU_WEBHOOK_URL"] = "https://open.feishu.cn/open-apis/bot/v2/hook/9d70437e-690c-4f96-8601-5b7058db0ebd"
        from daily_report_main import send_to_feishu
        send_to_feishu("🎮 二重螺旋-海外 数据日报", report)


if __name__ == "__main__":
    main()
