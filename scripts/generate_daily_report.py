"""
数据处理和报告生成脚本
包含日期校验和格式化输出
"""
import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from multi_table_processor import MultiTableDataProcessor


def get_latest_date(records):
    """获取最新日期"""
    if not records:
        return None

    dates = [r["date"] for r in records if r["date"]]
    if not dates:
        return None

    return max(dates)


def get_records_by_date(records, target_date):
    """获取指定日期的所有记录"""
    return [r for r in records if r["date"] == target_date]


def summarize_by_group(records):
    """按分组汇总数据"""
    group_summary = defaultdict(lambda: {
        "dau": 0,
        "new_users": 0,
        "income": 0.0,
        "paid_users": 0
    })

    total_dau = 0
    total_new = 0
    total_income = 0.0
    total_paid = 0

    for rec in records:
        group = rec["group"]

        group_summary[group]["dau"] += rec["dau"]
        group_summary[group]["new_users"] += rec["new_users"]
        group_summary[group]["income"] += rec["income"]
        group_summary[group]["paid_users"] += rec["paid_users"]

        total_dau += rec["dau"]
        total_new += rec["new_users"]
        total_income += rec["income"]
        total_paid += rec["paid_users"]

    return {
        "total": {
            "dau": total_dau,
            "new_users": total_new,
            "income": total_income,
            "paid_users": total_paid,
            "paid_rate": round(total_paid / total_dau * 100, 2) if total_dau > 0 else 0
        },
        "groups": dict(group_summary)
    }


def format_change(current, previous, metric_name=""):
    """格式化变化"""
    if previous == 0:
        return "N/A"

    change = current - previous
    change_pct = round((change / previous) * 100, 2)

    if change > 0:
        return f"+{change:,} (+{change_pct:.1f}%)"
    elif change < 0:
        return f"{change:,} ({change_pct:.1f}%)"
    else:
        return "0 (0.0%)"


def generate_report(processor, table_configs):
    """生成报告"""
    print("=" * 80)
    print("开始生成数据分析报告")
    print("=" * 80)

    # 获取数据
    all_records = []
    for config in table_configs:
        print(f"\n获取表格数据: {config['name']}")
        result = processor.process_table_data(
            config['table_id'],
            config['view_id'],
            config['last_n']
        )

        if "error" in result:
            print(f"  ❌ 错误: {result['error']}")
            continue

        # 获取所有记录（重新获取原始记录）
        records = processor.fetch_data(config['table_id'], config['view_id'])
        for record in records:
            parsed = processor.parse_record(record)
            if parsed:
                parsed["table_name"] = config['name']
                all_records.append(parsed)

    # 按表格分类
    base_records = [r for r in all_records if r["table_name"] == "游戏基础数据"]
    channel_records = [r for r in all_records if r["table_name"] == "游戏渠道数据"]
    country_records = [r for r in all_records if r["table_name"] == "游戏主要国家数据"]

    # 获取最新日期（昨日）
    latest_date = get_latest_date(base_records)
    if not latest_date:
        print("\n❌ 没有找到有效数据！")
        return None

    print(f"\n最新数据日期: {latest_date}")

    # 获取前日数据
    base_date_groups = defaultdict(list)
    for rec in base_records:
        base_date_groups[rec["date"]].append(rec)

    sorted_dates = sorted(base_date_groups.keys())
    if len(sorted_dates) < 2:
        print("\n❌ 数据不足，无法对比！")
        return None

    yesterday_date = sorted_dates[-1]
    day_before_date = sorted_dates[-2]

    print(f"昨日: {yesterday_date}")
    print(f"前日: {day_before_date}")

    # 汇总昨日和前日的基础数据
    yesterday_records = base_date_groups[yesterday_date]
    day_before_records = base_date_groups[day_before_date]

    yesterday_summary = summarize_by_group(yesterday_records)
    day_before_summary = summarize_by_group(day_before_records)

    # 获取昨日渠道数据
    channel_date_groups = defaultdict(list)
    for rec in channel_records:
        channel_date_groups[rec["date"]].append(rec)

    yesterday_channel_records = channel_date_groups.get(yesterday_date, [])
    yesterday_channel_summary = summarize_by_group(yesterday_channel_records)

    # 获取昨日国家数据
    country_date_groups = defaultdict(list)
    for rec in country_records:
        country_date_groups[rec["date"]].append(rec)

    yesterday_country_records = country_date_groups.get(yesterday_date, [])
    yesterday_country_summary = summarize_by_group(yesterday_country_records)

    # 获取近7天数据
    recent_7_days = sorted_dates[-7:] if len(sorted_dates) >= 7 else sorted_dates

    # 生成报告
    report_lines = []

    report_lines.append("=" * 100)
    report_lines.append("📊 游戏数据分析报告")
    report_lines.append("=" * 100)

    # 一、关键指标分析
    report_lines.append("\n## 一、关键指标分析")

    # 1. 昨日总览数据
    report_lines.append(f"\n### 1. 昨日（{yesterday_date}）总览数据")
    y_data = yesterday_summary["total"]
    d_data = day_before_summary["total"]

    report_lines.append(f"- 总DAU：{y_data['dau']:,}")
    report_lines.append(f"- 新增用户：{y_data['new_users']:,}")
    report_lines.append(f"- 总收入：${y_data['income']:,.2f}")
    report_lines.append(f"- 付费率：{y_data['paid_rate']:.2f}%")

    report_lines.append(f"\n**对照前日（{day_before_date}）变化：**")
    report_lines.append(f"- DAU：{format_change(y_data['dau'], d_data['dau'], 'DAU')}")
    report_lines.append(f"- 新增用户：{format_change(y_data['new_users'], d_data['new_users'], '新增用户')}")
    report_lines.append(f"- 总收入：{format_change(y_data['income'], d_data['income'], '收入')}")
    report_lines.append(f"- 付费率：{format_change(y_data['paid_rate'], d_data['paid_rate'], '付费率')}")

    # 2. 渠道表现分析
    report_lines.append(f"\n### 2. 渠道表现分析（{yesterday_date}）")
    report_lines.append(f"| 渠道 | DAU | 新增用户 | 总收入 | 付费率 |")
    report_lines.append(f"|------|-----|----------|--------|--------|")

    channels = yesterday_channel_summary["groups"]
    for channel_name in sorted(channels.keys()):
        c_data = channels[channel_name]
        paid_rate = round(c_data['paid_users'] / c_data['dau'] * 100, 2) if c_data['dau'] > 0 else 0
        report_lines.append(
            f"| {channel_name} | {c_data['dau']:,} | {c_data['new_users']:,} | ${c_data['income']:,.2f} | {paid_rate:.2f}% |"
        )

    report_lines.append(f"\n**渠道亮点：**")

    # 找出付费率最高的渠道
    max_paid_rate_channel = max(channels.items(), key=lambda x: x[1]['paid_users'] / x[1]['dau'] if x[1]['dau'] > 0 else 0)
    max_paid_rate = round(max_paid_rate_channel[1]['paid_users'] / max_paid_rate_channel[1]['dau'] * 100, 2)
    report_lines.append(f"- {max_paid_rate_channel[0]}渠道：付费率最高（{max_paid_rate:.2f}%）")

    # 找出新增用户最多的渠道
    max_new_channel = max(channels.items(), key=lambda x: x[1]['new_users'])
    report_lines.append(f"- {max_new_channel[0]}渠道：新增用户最多（{max_new_channel[1]['new_users']:,}）")

    # 找出DAU占比最高的渠道
    max_dau_channel = max(channels.items(), key=lambda x: x[1]['dau'])
    max_dau_pct = round(max_dau_channel[1]['dau'] / y_data['dau'] * 100, 1) if y_data['dau'] > 0 else 0
    max_dau_paid_rate = round(max_dau_channel[1]['paid_users'] / max_dau_channel[1]['dau'] * 100, 2) if max_dau_channel[1]['dau'] > 0 else 0
    report_lines.append(f"- {max_dau_channel[0]}：DAU占比最高（{max_dau_pct}%），但付费率{max_dau_paid_rate:.2f}%")

    # 3. 国家表现分析
    report_lines.append(f"\n### 3. 国家表现分析（{yesterday_date}）")
    report_lines.append(f"| 国家 | DAU | 新增用户 | 总收入 | 付费率 |")
    report_lines.append(f"|------|-----|----------|--------|--------|")

    countries = yesterday_country_summary["groups"]
    for country_name in sorted(countries.keys()):
        c_data = countries[country_name]
        paid_rate = round(c_data['paid_users'] / c_data['dau'] * 100, 2) if c_data['dau'] > 0 else 0
        report_lines.append(
            f"| {country_name} | {c_data['dau']:,} | {c_data['new_users']:,} | ${c_data['income']:,.2f} | {paid_rate:.2f}% |"
        )

    report_lines.append(f"\n**国家亮点：**")
    if countries:
        max_paid_rate_country = max(countries.items(), key=lambda x: x[1]['paid_users'] / x[1]['dau'] if x[1]['dau'] > 0 else 0)
        max_paid_rate_c = round(max_paid_rate_country[1]['paid_users'] / max_paid_rate_country[1]['dau'] * 100, 2)
        report_lines.append(f"- {max_paid_rate_country[0]}：付费率最高（{max_paid_rate_c:.2f}%）")

        max_dau_country = max(countries.items(), key=lambda x: x[1]['dau'])
        report_lines.append(f"- {max_dau_country[0]}：DAU最高（{max_dau_country[1]['dau']:,}）")

    # 二、近七日趋势分析
    report_lines.append("\n## 二、近七日趋势分析")

    # 1. DAU趋势
    report_lines.append("\n### 1. DAU趋势（最近7天）")
    dau_values = []
    for date in recent_7_days:
        records_for_date = base_date_groups.get(date, [])
        summary = summarize_by_group(records_for_date)
        dau_values.append(summary["total"]["dau"])

    if len(dau_values) >= 2:
        dau_start = dau_values[0]
        dau_end = dau_values[-1]
        dau_change = dau_end - dau_start
        dau_change_pct = round((dau_change / dau_start) * 100, 2) if dau_start > 0 else 0

        if dau_change > 0:
            trend_text = f"上升{dau_change_pct}%"
        else:
            trend_text = f"下降{abs(dau_change_pct)}%"

        report_lines.append(f"- 整体呈{trend_text}：从{dau_start:,}至{dau_end:,}")
    else:
        report_lines.append("- 数据不足，无法分析趋势")

    # 2. 新增用户趋势
    report_lines.append("\n### 2. 新增用户趋势")
    new_values = []
    for date in recent_7_days:
        records_for_date = base_date_groups.get(date, [])
        summary = summarize_by_group(records_for_date)
        new_values.append(summary["total"]["new_users"])

    if len(new_values) >= 2:
        new_start = new_values[0]
        new_end = new_values[-1]
        new_change = new_end - new_start
        new_change_pct = round((new_change / new_start) * 100, 2) if new_start > 0 else 0

        if new_change > 0:
            trend_text = f"上升{new_change_pct}%"
        else:
            trend_text = f"下降{abs(new_change_pct)}%"

        report_lines.append(f"- 整体呈{trend_text}：从{new_start:,}至{new_end:,}")

        # 检查是否连续下降
        if len(new_values) >= 3 and all(new_values[i] >= new_values[i+1] for i in range(len(new_values)-1)):
            report_lines.append(f"- 持续下降：降幅{abs(new_change_pct)}%")
    else:
        report_lines.append("- 数据不足，无法分析趋势")

    # 3. 收入趋势
    report_lines.append("\n### 3. 收入趋势")
    income_values = []
    for date in recent_7_days:
        records_for_date = base_date_groups.get(date, [])
        summary = summarize_by_group(records_for_date)
        income_values.append(summary["total"]["income"])

    if len(income_values) >= 2:
        income_start = income_values[0]
        income_end = income_values[-1]
        income_change = income_end - income_start
        income_change_pct = round((income_change / income_start) * 100, 2) if income_start > 0 else 0

        report_lines.append(f"- 从${income_start:,.2f}至${income_end:,.2f}")

        # 检查最近2天的变化
        if len(income_values) >= 3:
            income_last_2_start = income_values[-3]
            income_last_2_end = income_values[-1]
            income_last_2_change = income_last_2_end - income_last_2_start
            income_last_2_change_pct = round((income_last_2_change / income_last_2_start) * 100, 2) if income_last_2_start > 0 else 0
            if income_last_2_change > 0:
                report_lines.append(f"- 最近3天累计增长：{income_last_2_change_pct:.1f}%")
    else:
        report_lines.append("- 数据不足，无法分析趋势")

    # 4. 付费率趋势
    report_lines.append("\n### 4. 付费率趋势")
    paid_rate_values = []
    for date in recent_7_days:
        records_for_date = base_date_groups.get(date, [])
        summary = summarize_by_group(records_for_date)
        paid_rate_values.append(summary["total"]["paid_rate"])

    if paid_rate_values:
        min_paid_rate = min(paid_rate_values)
        max_paid_rate = max(paid_rate_values)
        avg_paid_rate = round(sum(paid_rate_values) / len(paid_rate_values), 2)
        current_paid_rate = paid_rate_values[-1]

        report_lines.append(f"- 波动范围：{min_paid_rate:.2f}% - {max_paid_rate:.2f}%")
        report_lines.append(f"- 昨日付费率{current_paid_rate:.2f}%，近7天平均值{avg_paid_rate:.2f}%")

        if current_paid_rate > avg_paid_rate:
            report_lines.append(f"- 昨日付费率高于平均值")
        elif current_paid_rate < avg_paid_rate:
            report_lines.append(f"- 昨日付费率低于平均值")
    else:
        report_lines.append("- 数据不足，无法分析趋势")

    # 报告说明
    report_lines.append("\n---")
    report_lines.append(f"**报告说明：** 本报告基于{sorted_dates[0]}至{sorted_dates[-1]}期间的实际数据生成，所有分析均基于提供的数据，未编造任何信息。")

    # 关键发现
    report_lines.append("\n## 🔍 关键发现")
    findings = []

    # 1. 新增用户趋势
    if len(new_values) >= 3:
        if all(new_values[i] >= new_values[i+1] for i in range(len(new_values)-1)):
            findings.append(f"新增用户连续{len(new_values)-1}天下降，降幅{abs(new_change_pct):.0f}%")

    # 2. 收入增长
    if len(income_values) >= 3:
        income_last_2_change = income_values[-1] - income_values[-3]
        income_last_2_change_pct = round((income_last_2_change / income_values[-3]) * 100, 2) if income_values[-3] > 0 else 0
        if income_last_2_change > 0:
            findings.append(f"收入最近3天累计增长{income_last_2_change_pct:.1f}%")

    # 3. 渠道对比
    if channels:
        max_dau_channel = max(channels.items(), key=lambda x: x[1]['dau'])
        max_dau_pct = round(max_dau_channel[1]['dau'] / y_data['dau'] * 100, 1) if y_data['dau'] > 0 else 0
        max_dau_paid_rate = round(max_dau_channel[1]['paid_users'] / max_dau_channel[1]['dau'] * 100, 2) if max_dau_channel[1]['dau'] > 0 else 0
        findings.append(f"{max_dau_channel[0]} DAU占比{max_dau_pct}%但付费率仅{max_dau_paid_rate:.2f}%")

        max_paid_rate_channel = max(channels.items(), key=lambda x: x[1]['paid_users'] / x[1]['dau'] if x[1]['dau'] > 0 else 0)
        max_paid_rate = round(max_paid_rate_channel[1]['paid_users'] / max_paid_rate_channel[1]['dau'] * 100, 2)
        max_new_channel = max(channels.items(), key=lambda x: x[1]['new_users'])
        findings.append(f"{max_paid_rate_channel[0]}渠道表现最佳：付费率{max_paid_rate:.2f}%，新增用户{max_new_channel[1]['new_users']:,}")

    for i, finding in enumerate(findings, 1):
        report_lines.append(f"{i}. {finding}")

    # 业务建议
    report_lines.append("\n## 💡 业务建议")
    recommendations = []

    if len(new_values) >= 3 and all(new_values[i] >= new_values[i+1] for i in range(len(new_values)-1)):
        recommendations.append("立即分析新增用户下降原因并采取行动")

    if max_dau_paid_rate < 2.0:
        recommendations.append(f"优化{max_dau_channel[0]}付费转化策略")

    if max_paid_rate_channel[0] != max_dau_channel[0]:
        recommendations.append(f"加大{max_paid_rate_channel[0]}渠道投入")

    if len(income_values) >= 3 and income_values[-1] > income_values[-3]:
        recommendations.append("分析收入增长原因并复制成功经验")

    recommendations.append("建立关键指标预警机制")

    for i, rec in enumerate(recommendations, 1):
        report_lines.append(f"{i}. {rec}")

    report_lines.append("\n" + "=" * 100)

    return "\n".join(report_lines)


def main():
    """主函数"""
    processor = MultiTableDataProcessor(app_token="LvSAboJTJanJKdssWs8cm49vn8c")

    # 配置3个表格
    table_configs = [
        {
            "name": "游戏基础数据",
            "table_id": "tblM5x1uyjwffoBq",
            "view_id": "vew8YRRC3u",
            "last_n": 50  # 获取足够多的数据
        },
        {
            "name": "游戏渠道数据",
            "table_id": "tblBiiYpOdRGonPy",
            "view_id": "vew8YRRC3u",
            "last_n": 50
        },
        {
            "name": "游戏主要国家数据",
            "table_id": "tblgx4cY7LvncsiJ",
            "view_id": "vew8YRRC3u",
            "last_n": 50
        }
    ]

    report = generate_report(processor, table_configs)

    if report:
        print("\n" + report)
        print("\n✅ 报告生成完成！")

        # 保存报告
        output_file = "daily_report.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"📄 报告已保存到: {output_file}")

        return report
    else:
        print("\n❌ 报告生成失败！")
        return None


if __name__ == "__main__":
    main()
