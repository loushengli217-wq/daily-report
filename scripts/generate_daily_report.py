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


# 业务场景：海外游戏项目二重螺旋的数据分析师
# 知识库：
# - DAU：游戏日活跃用户数
# - ARPU：平均每用户收入（总收入/DAU）
# - ARPPU：平均每付费用户收入（总收入/付费用户数）
# - 付费率：付费用户数/DAU
# 渠道维度：
# - PC端：PC官包、Steam、Epic
# - 移动端：IOS、安卓


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

    # 计算ARPU和ARPPU
    arpu = round(total_income / total_dau, 2) if total_dau > 0 else 0
    arppu = round(total_income / total_paid, 2) if total_paid > 0 else 0
    paid_rate = round(total_paid / total_dau * 100, 2) if total_dau > 0 else 0

    return {
        "total": {
            "dau": total_dau,
            "new_users": total_new,
            "income": total_income,
            "paid_users": total_paid,
            "paid_rate": paid_rate,
            "arpu": arpu,
            "arppu": arppu
        },
        "groups": dict(group_summary)
    }


def format_change(current, previous, metric_name="", is_percentage=False):
    """格式化变化"""
    if previous == 0:
        return "N/A"

    change = current - previous
    change_pct = round((change / previous) * 100, 2)

    if is_percentage:
        # 如果是百分比，直接显示变化（保留2位小数）
        if change > 0:
            return f"+{change:.2f}% ({change_pct:.1f}%)"
        elif change < 0:
            return f"{change:.2f}% ({change_pct:.1f}%)"
        else:
            return "0.00% (0.0%)"
    else:
        # 如果是数值，显示数值变化
        # 对于金额，保留2位小数；对于其他，保留整数
        if metric_name in ["总收入", "ARPU", "ARPPU"]:
            if change > 0:
                return f"+{change:,.2f} ({change_pct:+.1f}%)"
            else:
                return f"{change:,.2f} ({change_pct:+.1f}%)"
        else:
            if change > 0:
                return f"+{change:,} ({change_pct:+.1f}%)"
            else:
                return f"{change:,} ({change_pct:+.1f}%)"


def format_currency(value):
    """格式化金额"""
    return f"${value:,.2f}"


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
    report_lines.append("📊 二重螺旋游戏数据分析报告")
    report_lines.append("=" * 100)

    # 一、关键指标分析
    report_lines.append("\n## 一、关键指标分析")

    # 1. 昨日总览数据
    report_lines.append(f"\n### 1. 昨日（{yesterday_date}）总览数据")
    y_data = yesterday_summary["total"]
    d_data = day_before_summary["total"]

    report_lines.append(f"- **DAU**：{y_data['dau']:,}")
    report_lines.append(f"- **新增用户**：{y_data['new_users']:,}")
    report_lines.append(f"- **总收入**：{format_currency(y_data['income'])}")
    report_lines.append(f"- **付费用户数**：{y_data['paid_users']:,}")
    report_lines.append(f"- **付费率**：{y_data['paid_rate']:.2f}%")
    report_lines.append(f"- **ARPU**：{format_currency(y_data['arpu'])}")
    report_lines.append(f"- **ARPPU**：{format_currency(y_data['arppu'])}")

    report_lines.append(f"\n**对照前日（{day_before_date}）变化：**")
    report_lines.append(f"- DAU：{format_change(y_data['dau'], d_data['dau'], 'DAU')}")
    report_lines.append(f"- 新增用户：{format_change(y_data['new_users'], d_data['new_users'], '新增用户')}")
    report_lines.append(f"- 总收入：{format_change(y_data['income'], d_data['income'], '总收入')}")
    report_lines.append(f"- 付费用户数：{format_change(y_data['paid_users'], d_data['paid_users'], '付费用户数')}")
    report_lines.append(f"- 付费率：{format_change(y_data['paid_rate'], d_data['paid_rate'], '付费率', is_percentage=True)}")
    report_lines.append(f"- ARPU：{format_change(y_data['arpu'], d_data['arpu'], 'ARPU')}")
    report_lines.append(f"- ARPPU：{format_change(y_data['arppu'], d_data['arppu'], 'ARPPU')}")

    # 2. 渠道表现分析
    report_lines.append(f"\n### 2. 渠道表现分析（{yesterday_date}）")
    report_lines.append(f"| 渠道 | 平台 | DAU | 新增用户 | 总收入 | 付费用户 | 付费率 | ARPU | ARPPU |")
    report_lines.append(f"|------|------|-----|----------|--------|----------|--------|------|-------|")

    channels = yesterday_channel_summary["groups"]
    for channel_name in sorted(channels.keys()):
        c_data = channels[channel_name]
        paid_rate = round(c_data['paid_users'] / c_data['dau'] * 100, 2) if c_data['dau'] > 0 else 0
        arpu = round(c_data['income'] / c_data['dau'], 2) if c_data['dau'] > 0 else 0
        arppu = round(c_data['income'] / c_data['paid_users'], 2) if c_data['paid_users'] > 0 else 0

        # 判断平台类型
        if channel_name in ["PC官包", "Steam", "EPIC"]:
            platform = "PC端"
        else:
            platform = "移动端"

        report_lines.append(
            f"| {channel_name} | {platform} | {c_data['dau']:,} | {c_data['new_users']:,} | {format_currency(c_data['income'])} | {c_data['paid_users']:,} | {paid_rate:.2f}% | {format_currency(arpu)} | {format_currency(arppu)} |"
        )

    report_lines.append(f"\n**渠道亮点分析：**")

    # 找出付费率最高的渠道
    if channels:
        max_paid_rate_channel = max(channels.items(), key=lambda x: x[1]['paid_users'] / x[1]['dau'] if x[1]['dau'] > 0 else 0)
        max_paid_rate = round(max_paid_rate_channel[1]['paid_users'] / max_paid_rate_channel[1]['dau'] * 100, 2)
        report_lines.append(f"- **{max_paid_rate_channel[0]}**：付费率最高（{max_paid_rate:.2f}%），付费转化效果最佳")

        # 找出新增用户最多的渠道
        max_new_channel = max(channels.items(), key=lambda x: x[1]['new_users'])
        report_lines.append(f"- **{max_new_channel[0]}**：新增用户最多（{max_new_channel[1]['new_users']:,}），用户获取能力强")

        # 找出DAU占比最高的渠道
        max_dau_channel = max(channels.items(), key=lambda x: x[1]['dau'])
        max_dau_pct = round(max_dau_channel[1]['dau'] / y_data['dau'] * 100, 1) if y_data['dau'] > 0 else 0
        max_dau_paid_rate = round(max_dau_channel[1]['paid_users'] / max_dau_channel[1]['dau'] * 100, 2) if max_dau_channel[1]['dau'] > 0 else 0
        max_dau_arppu = round(max_dau_channel[1]['income'] / max_dau_channel[1]['paid_users'], 2) if max_dau_channel[1]['paid_users'] > 0 else 0
        report_lines.append(f"- **{max_dau_channel[0]}**：DAU占比最高（{max_dau_pct}%），但付费率（{max_dau_paid_rate:.2f}%）和ARPPU（{format_currency(max_dau_arppu)}）较低，存在较大提升空间")

        # PC端 vs 移动端对比
        pc_dau = sum(c['dau'] for k, c in channels.items() if k in ["PC官包", "Steam", "EPIC"])
        pc_income = sum(c['income'] for k, c in channels.items() if k in ["PC官包", "Steam", "EPIC"])
        mobile_dau = sum(c['dau'] for k, c in channels.items() if k in ["IOS", "安卓"])
        mobile_income = sum(c['income'] for k, c in channels.items() if k in ["IOS", "安卓"])

        if pc_dau > 0 and mobile_dau > 0:
            pc_arpu = round(pc_income / pc_dau, 2)
            mobile_arpu = round(mobile_income / mobile_dau, 2)
            report_lines.append(f"- **平台对比**：PC端DAU {pc_dau:,}，ARPU {format_currency(pc_arpu)}；移动端DAU {mobile_dau:,}，ARPU {format_currency(mobile_arpu)}")

    # 3. 国家表现分析
    report_lines.append(f"\n### 3. 国家表现分析（{yesterday_date}）")
    report_lines.append(f"| 国家 | DAU | 新增用户 | 总收入 | 付费用户 | 付费率 | ARPU | ARPPU |")
    report_lines.append(f"|------|-----|----------|--------|----------|--------|------|-------|")

    countries = yesterday_country_summary["groups"]
    for country_name in sorted(countries.keys()):
        c_data = countries[country_name]
        paid_rate = round(c_data['paid_users'] / c_data['dau'] * 100, 2) if c_data['dau'] > 0 else 0
        arpu = round(c_data['income'] / c_data['dau'], 2) if c_data['dau'] > 0 else 0
        arppu = round(c_data['income'] / c_data['paid_users'], 2) if c_data['paid_users'] > 0 else 0

        report_lines.append(
            f"| {country_name} | {c_data['dau']:,} | {c_data['new_users']:,} | {format_currency(c_data['income'])} | {c_data['paid_users']:,} | {paid_rate:.2f}% | {format_currency(arpu)} | {format_currency(arppu)} |"
        )

    report_lines.append(f"\n**国家亮点分析：**")
    if countries:
        max_paid_rate_country = max(countries.items(), key=lambda x: x[1]['paid_users'] / x[1]['dau'] if x[1]['dau'] > 0 else 0)
        max_paid_rate_c = round(max_paid_rate_country[1]['paid_users'] / max_paid_rate_country[1]['dau'] * 100, 2)
        max_paid_rate_arppu = round(max_paid_rate_country[1]['income'] / max_paid_rate_country[1]['paid_users'], 2) if max_paid_rate_country[1]['paid_users'] > 0 else 0
        report_lines.append(f"- **{max_paid_rate_country[0]}**：付费率最高（{max_paid_rate_c:.2f}%），ARPPU达到{format_currency(max_paid_rate_arppu)}，用户付费意愿强")

        max_dau_country = max(countries.items(), key=lambda x: x[1]['dau'])
        max_dau_income = max_dau_country[1]['income']
        max_dau_arpu = round(max_dau_income / max_dau_country[1]['dau'], 2) if max_dau_country[1]['dau'] > 0 else 0
        report_lines.append(f"- **{max_dau_country[0]}**：DAU最高（{max_dau_country[1]['dau']:,}），贡献收入{format_currency(max_dau_income)}，ARPU为{format_currency(max_dau_arpu)}")

        # 收入贡献分析
        total_country_income = sum(c['income'] for c in countries.values())
        income_ranking = sorted(countries.items(), key=lambda x: x[1]['income'], reverse=True)
        for i, (name, data) in enumerate(income_ranking, 1):
            income_pct = round(data['income'] / total_country_income * 100, 1) if total_country_income > 0 else 0
            report_lines.append(f"- **收入排名**：第{i}名 - {name}，贡献{income_pct}%收入")

    # 二、近七日趋势分析
    report_lines.append("\n## 二、近七日趋势分析")

    # 汇总近7天数据
    dau_values = []
    new_values = []
    income_values = []
    paid_users_values = []
    paid_rate_values = []
    arpu_values = []
    arppu_values = []

    for date in recent_7_days:
        records_for_date = base_date_groups.get(date, [])
        summary = summarize_by_group(records_for_date)
        dau_values.append(summary["total"]["dau"])
        new_values.append(summary["total"]["new_users"])
        income_values.append(summary["total"]["income"])
        paid_users_values.append(summary["total"]["paid_users"])
        paid_rate_values.append(summary["total"]["paid_rate"])
        arpu_values.append(summary["total"]["arpu"])
        arppu_values.append(summary["total"]["arppu"])

    # 1. DAU趋势
    report_lines.append("\n### 1. DAU趋势分析（最近7天）")
    if len(dau_values) >= 2:
        dau_start = dau_values[0]
        dau_end = dau_values[-1]
        dau_change = dau_end - dau_start
        dau_change_pct = round((dau_change / dau_start) * 100, 2) if dau_start > 0 else 0

        if dau_change > 0:
            trend_text = f"上升{abs(dau_change_pct)}%"
            trend_desc = "用户活跃度提升"
        else:
            trend_text = f"下降{abs(dau_change_pct)}%"
            trend_desc = "用户活跃度下滑"

        report_lines.append(f"- **整体趋势**：从{dau_start:,}变化至{dau_end:,}，整体呈{trend_text}，{trend_desc}")
        report_lines.append(f"- **变化幅度**：7天内DAU变化{dau_change:,}，日均变化约{round(dau_change / len(dau_values), 0):,.0f}")

        # 详细的每日变化分析
        report_lines.append(f"- **详细变化**：")
        for i in range(1, len(dau_values)):
            daily_change = dau_values[i] - dau_values[i-1]
            daily_change_pct = round((daily_change / dau_values[i-1]) * 100, 2) if dau_values[i-1] > 0 else 0
            if abs(daily_change_pct) > 5:
                status = "🔴 显著" if daily_change_pct < -5 else "🟢 显著"
                report_lines.append(f"  - {recent_7_days[i]}：{dau_values[i]:,}，日环比{status}{daily_change_pct:+.2f}%")

    # 2. 新增用户趋势
    report_lines.append("\n### 2. 新增用户趋势分析")
    if len(new_values) >= 2:
        new_start = new_values[0]
        new_end = new_values[-1]
        new_change = new_end - new_start
        new_change_pct = round((new_change / new_start) * 100, 2) if new_start > 0 else 0

        if new_change > 0:
            trend_text = f"上升{abs(new_change_pct)}%"
            trend_desc = "用户获取能力增强"
        else:
            trend_text = f"下降{abs(new_change_pct)}%"
            trend_desc = "用户获取能力减弱"

        report_lines.append(f"- **整体趋势**：从{new_start:,}变化至{new_end:,}，整体呈{trend_text}，{trend_desc}")
        report_lines.append(f"- **变化幅度**：7天内新增用户变化{new_change:,}，日均变化约{round(new_change / len(new_values), 0):,.0f}")

        # 检查是否连续下降
        if len(new_values) >= 3 and all(new_values[i] >= new_values[i+1] for i in range(len(new_values)-1)):
            report_lines.append(f"- **持续下降**：新增用户连续{len(new_values)-1}天下降，降幅达到{abs(new_change_pct):.0f}%，需立即关注用户获取渠道效率")
        elif len(new_values) >= 3 and all(new_values[i] <= new_values[i+1] for i in range(len(new_values)-1)):
            report_lines.append(f"- **持续增长**：新增用户连续{len(new_values)-1}天增长，增幅达到{abs(new_change_pct):.0f}%，用户获取效果显著")

    # 3. 收入趋势
    report_lines.append("\n### 3. 收入趋势分析")
    if len(income_values) >= 2:
        income_start = income_values[0]
        income_end = income_values[-1]
        income_change = income_end - income_start
        income_change_pct = round((income_change / income_start) * 100, 2) if income_start > 0 else 0

        report_lines.append(f"- **整体趋势**：从{format_currency(income_start)}变化至{format_currency(income_end)}，7天累计变化{income_change_pct:.1f}%")

        # 检查最近3天的变化
        if len(income_values) >= 3:
            income_last_3_start = income_values[-4] if len(income_values) >= 4 else income_values[0]
            income_last_3_end = income_values[-1]
            income_last_3_change = income_last_3_end - income_last_3_start
            income_last_3_change_pct = round((income_last_3_change / income_last_3_start) * 100, 2) if income_last_3_start > 0 else 0

            if income_last_3_change > 0:
                report_lines.append(f"- **近期趋势**：最近{min(4, len(income_values))}天累计增长{income_last_3_change_pct:.1f}%，变现能力提升")
            elif income_last_3_change < 0:
                report_lines.append(f"- **近期趋势**：最近{min(4, len(income_values))}天累计下降{abs(income_last_3_change_pct):.1f}%，变现能力下降")

        # 波动分析
        income_variance = round((max(income_values) - min(income_values)) / sum(income_values) * 100, 1) if sum(income_values) > 0 else 0
        if income_variance > 30:
            report_lines.append(f"- **波动分析**：收入波动较大（波动幅度{income_variance}%），可能存在促销活动或季节性因素影响")
        elif income_variance < 10:
            report_lines.append(f"- **波动分析**：收入波动较小（波动幅度{income_variance}%），变现能力相对稳定")

    # 4. 付费用户数趋势
    report_lines.append("\n### 4. 付费用户数趋势分析")
    if len(paid_users_values) >= 2:
        paid_start = paid_users_values[0]
        paid_end = paid_users_values[-1]
        paid_change = paid_end - paid_start
        paid_change_pct = round((paid_change / paid_start) * 100, 2) if paid_start > 0 else 0

        report_lines.append(f"- **整体趋势**：从{paid_start:,}变化至{paid_end:,}，7天累计变化{paid_change_pct:.1f}%")

        # 详细分析
        if len(paid_users_values) >= 3:
            # 判断趋势
            increasing_count = sum(1 for i in range(1, len(paid_users_values)) if paid_users_values[i] > paid_users_values[i-1])
            decreasing_count = len(paid_users_values) - 1 - increasing_count

            if increasing_count > decreasing_count:
                report_lines.append(f"- **趋势判断**：付费用户数呈上升态势（{increasing_count}天上升 vs {decreasing_count}天下降），付费用户规模扩大")
            elif decreasing_count > increasing_count:
                report_lines.append(f"- **趋势判断**：付费用户数呈下降态势（{decreasing_count}天下降 vs {increasing_count}天上升），付费用户流失")
            else:
                report_lines.append(f"- **趋势判断**：付费用户数波动较小，相对稳定")

            # 与DAU变化对比
            if len(dau_values) == len(paid_users_values):
                dau_change_pct = round((dau_values[-1] - dau_values[0]) / dau_values[0] * 100, 2) if dau_values[0] > 0 else 0
                if abs(paid_change_pct) > abs(dau_change_pct) + 5:
                    if paid_change_pct > 0:
                        report_lines.append(f"- **对比分析**：付费用户数增长（{paid_change_pct:.1f}%）超过DAU增长（{dau_change_pct:.1f}%），付费转化效率提升")
                    else:
                        report_lines.append(f"- **对比分析**：付费用户数下降（{paid_change_pct:.1f}%）超过DAU下降（{dau_change_pct:.1f}%），付费用户流失严重")
                elif abs(dau_change_pct) > abs(paid_change_pct) + 5:
                    if dau_change_pct > 0:
                        report_lines.append(f"- **对比分析**：DAU增长（{dau_change_pct:.1f}%）超过付费用户增长（{paid_change_pct:.1f}%），但付费转化效率未同步提升")
                    else:
                        report_lines.append(f"- **对比分析**：DAU下降（{dau_change_pct:.1f}%）超过付费用户下降（{paid_change_pct:.1f}%），付费用户相对稳定")

    # 5. 付费率趋势
    report_lines.append("\n### 5. 付费率趋势分析")
    if paid_rate_values:
        min_paid_rate = min(paid_rate_values)
        max_paid_rate = max(paid_rate_values)
        avg_paid_rate = round(sum(paid_rate_values) / len(paid_rate_values), 2)
        current_paid_rate = paid_rate_values[-1]

        report_lines.append(f"- **波动范围**：{min_paid_rate:.2f}% - {max_paid_rate:.2f}%，波动幅度{max_paid_rate - min_paid_rate:.2f}个百分点")
        report_lines.append(f"- **当前水平**：昨日付费率{current_paid_rate:.2f}%，近7天平均值{avg_paid_rate:.2f}%")

        if current_paid_rate > avg_paid_rate + 0.5:
            report_lines.append(f"- **趋势判断**：昨日付费率高于平均值{current_paid_rate - avg_paid_rate:.2f}个百分点，付费转化效果较好")
        elif current_paid_rate < avg_paid_rate - 0.5:
            report_lines.append(f"- **趋势判断**：昨日付费率低于平均值{avg_paid_rate - current_paid_rate:.2f}个百分点，付费转化效果不佳")
        else:
            report_lines.append(f"- **趋势判断**：昨日付费率接近平均水平，付费转化效果稳定")

        # 付费率变化趋势
        if len(paid_rate_values) >= 3:
            rate_increasing = sum(1 for i in range(1, len(paid_rate_values)) if paid_rate_values[i] > paid_rate_values[i-1])
            rate_decreasing = len(paid_rate_values) - 1 - rate_increasing

            if rate_increasing > rate_decreasing:
                report_lines.append(f"- **近期走势**：付费率呈上升趋势（{rate_increasing}天上升 vs {rate_decreasing}天下降）")
            elif rate_decreasing > rate_increasing:
                report_lines.append(f"- **近期走势**：付费率呈下降趋势（{rate_decreasing}天下降 vs {rate_increasing}天上升）")
            else:
                report_lines.append(f"- **近期走势**：付费率波动较小，相对稳定")

    # 6. ARPU和ARPPU趋势
    report_lines.append("\n### 6. ARPU和ARPPU趋势分析")
    if arpu_values and arppu_values:
        arpu_avg = round(sum(arpu_values) / len(arpu_values), 2)
        arppu_avg = round(sum(arppu_values) / len(arppu_values), 2)
        current_arpu = arpu_values[-1]
        current_arppu = arppu_values[-1]

        report_lines.append(f"- **ARPU趋势**：昨日{format_currency(current_arpu)}，7天平均值{format_currency(arpu_avg)}")
        if current_arpu > arpu_avg * 1.1:
            report_lines.append(f"  - 单用户付费能力提升，高于平均值{(current_arpu / arpu_avg - 1) * 100:.1f}%")
        elif current_arpu < arpu_avg * 0.9:
            report_lines.append(f"  - 单用户付费能力下降，低于平均值{(1 - current_arpu / arpu_avg) * 100:.1f}%")

        report_lines.append(f"- **ARPPU趋势**：昨日{format_currency(current_arppu)}，7天平均值{format_currency(arppu_avg)}")
        if current_arppu > arppu_avg * 1.1:
            report_lines.append(f"  - 付费用户付费意愿增强，高于平均值{(current_arppu / arppu_avg - 1) * 100:.1f}%")
        elif current_arppu < arppu_avg * 0.9:
            report_lines.append(f"  - 付费用户付费意愿减弱，低于平均值{(1 - current_arppu / arppu_avg) * 100:.1f}%")

    # 报告说明
    report_lines.append("\n---")
    report_lines.append(f"**报告说明：** 本报告基于{sorted_dates[0]}至{sorted_dates[-1]}期间的实际数据生成，所有分析均基于提供的数据，未编造任何信息。")

    # 关键发现
    report_lines.append("\n## 🔍 关键发现")
    findings = []

    # 1. 新增用户趋势
    if len(new_values) >= 3:
        if all(new_values[i] >= new_values[i+1] for i in range(len(new_values)-1)):
            findings.append(f"新增用户连续{len(new_values)-1}天下降，降幅达{abs(new_change_pct):.0f}%，用户获取面临严重挑战，需立即排查渠道投放效率")
        elif all(new_values[i] <= new_values[i+1] for i in range(len(new_values)-1)):
            findings.append(f"新增用户连续{len(new_values)-1}天增长，增幅达{abs(new_change_pct):.0f}%，用户获取效果显著，建议加大优质渠道投入")

    # 2. 收入趋势
    if len(income_values) >= 3:
        income_last_change = income_values[-1] - income_values[-3]
        income_last_change_pct = round((income_last_change / income_values[-3]) * 100, 2) if income_values[-3] > 0 else 0
        if income_last_change > 0:
            findings.append(f"收入最近3天累计增长{income_last_change_pct:.1f}%，变现能力明显提升，应总结成功经验")
        elif income_last_change < 0:
            findings.append(f"收入最近3天累计下降{abs(income_last_change_pct):.1f}%，变现能力下滑，需关注付费转化效率")

    # 3. 渠道对比
    if channels:
        max_dau_channel = max(channels.items(), key=lambda x: x[1]['dau'])
        max_dau_pct = round(max_dau_channel[1]['dau'] / y_data['dau'] * 100, 1) if y_data['dau'] > 0 else 0
        max_dau_paid_rate = round(max_dau_channel[1]['paid_users'] / max_dau_channel[1]['dau'] * 100, 2) if max_dau_channel[1]['dau'] > 0 else 0
        if max_dau_paid_rate < 2.0:
            findings.append(f"{max_dau_channel[0]} DAU占比高达{max_dau_pct}%但付费率仅{max_dau_paid_rate:.2f}%，付费转化严重不足，是该渠道的核心问题")

        max_paid_rate_channel = max(channels.items(), key=lambda x: x[1]['paid_users'] / x[1]['dau'] if x[1]['dau'] > 0 else 0)
        max_paid_rate = round(max_paid_rate_channel[1]['paid_users'] / max_paid_rate_channel[1]['dau'] * 100, 2)
        max_new_channel = max(channels.items(), key=lambda x: x[1]['new_users'])
        findings.append(f"{max_paid_rate_channel[0]}渠道表现最佳：付费率{max_paid_rate:.2f}%，新增用户{max_new_channel[1]['new_users']:,}，应作为重点发展渠道")

    # 4. 付费用户趋势
    if len(paid_users_values) >= 3:
        paid_increasing = sum(1 for i in range(1, len(paid_users_values)) if paid_users_values[i] > paid_users_values[i-1])
        paid_decreasing = len(paid_users_values) - 1 - paid_increasing
        if paid_decreasing >= 5:
            findings.append(f"付费用户数在7天中有{paid_decreasing}天下降，付费用户持续流失，需立即分析流失原因并采取挽留措施")
        elif paid_increasing >= 5:
            findings.append(f"付费用户数在7天中有{paid_increasing}天增长，付费用户规模持续扩大，应巩固付费转化效果")

    for i, finding in enumerate(findings, 1):
        report_lines.append(f"{i}. {finding}")

    # 业务建议
    report_lines.append("\n## 💡 业务建议")
    recommendations = []

    if len(new_values) >= 3 and all(new_values[i] >= new_values[i+1] for i in range(len(new_values)-1)):
        recommendations.append(f"立即分析新增用户下降原因，排查渠道投放效率、素材质量和推广策略，优化用户获取流程")

    if channels:
        max_dau_channel = max(channels.items(), key=lambda x: x[1]['dau'])
        max_dau_paid_rate = round(max_dau_channel[1]['paid_users'] / max_dau_channel[1]['dau'] * 100, 2) if max_dau_channel[1]['dau'] > 0 else 0
        if max_dau_paid_rate < 2.0:
            recommendations.append(f"针对{max_dau_channel[0]}渠道优化付费转化策略，包括优化新手引导、调整首充优惠、优化付费点设计等")

        max_paid_rate_channel = max(channels.items(), key=lambda x: x[1]['paid_users'] / x[1]['dau'] if x[1]['dau'] > 0 else 0)
        if max_paid_rate_channel[0] != max_dau_channel[0]:
            recommendations.append(f"加大{max_paid_rate_channel[0]}渠道投入，提升其在总DAU中的占比，改善整体付费率")

    if len(income_values) >= 3 and income_values[-1] > income_values[-3]:
        recommendations.append("分析收入增长原因，总结成功经验，包括付费活动设计、礼包定价策略、促销时机等，并推广到其他渠道或时段")

    if len(paid_users_values) >= 3:
        paid_increasing = sum(1 for i in range(1, len(paid_users_values)) if paid_users_values[i] > paid_users_values[i-1])
        paid_decreasing = len(paid_users_values) - 1 - paid_increasing
        if paid_decreasing >= 4:
            recommendations.append("建立付费用户流失预警机制，分析流失用户特征，提供个性化挽留方案，如专属优惠、限时折扣等")

    recommendations.append("建立关键指标预警机制，设置DAU、新增用户、付费率等指标的预警阈值，及时发现异常波动")
    recommendations.append("定期分析ARPU和ARPPU变化，了解用户付费意愿变化趋势，及时调整付费产品和定价策略")

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
