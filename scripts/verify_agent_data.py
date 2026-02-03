"""
验证Agent分析的数据准确性
"""
import sys
import os
from datetime import datetime, timedelta

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from tools.feishu_bitable_tool import FeishuBitableClient, get_access_token


def verify_agent_data():
    """验证Agent使用的数据"""

    app_token = "LvSAboJTJanJKdssWs8cm49vn8c"
    table_id = "tblBiiYpOdRGonPy"

    print("="*100)
    print("🔍 验证Agent使用的数据")
    print("="*100)

    client = FeishuBitableClient()
    token = get_access_token()

    # 使用Agent相同的方式获取数据
    search_response = client.search_records(
        token,
        app_token,
        table_id,
        sort=[{"field_name": "日期", "desc": True}],
        page_size=200
    )

    all_records = search_response.get("data", {}).get("items", [])
    print(f"\n✅ Agent获取的数据：{len(all_records)} 条记录")

    # 按日期汇总
    daily_dau = {}
    for record in all_records:
        fields_data = record.get("fields", {})
        date_value = fields_data.get("日期")

        if isinstance(date_value, (int, float)):
            date_str = datetime.fromtimestamp(date_value / 1000).strftime('%Y-%m-%d')
            dau_value = fields_data.get("DAU", 0)

            if isinstance(dau_value, (int, float)):
                if date_str not in daily_dau:
                    daily_dau[date_str] = 0
                daily_dau[date_str] += dau_value

    print(f"\n📊 日期范围：{min(daily_dau.keys())} 到 {max(daily_dau.keys())}")
    print(f"📊 总天数：{len(daily_dau)} 天")

    # 检查报告中的日期
    print("\n" + "="*100)
    print("🔍 检查报告中提到的日期")
    print("="*100)

    report_dates = [
        ("2026-01-27", 1423056),  # 报告中声称的DAU
        ("2026-02-02", 1236502),  # 报告中声称的DAU
    ]

    for date_str, claimed_dau in report_dates:
        actual_dau = daily_dau.get(date_str, 0)
        match = "✅" if actual_dau == claimed_dau else "❌"

        print(f"\n📅 日期: {date_str}")
        print(f"   报告中声称的DAU: {claimed_dau:,}")
        print(f"   实际DAU: {actual_dau:,}")
        print(f"   匹配: {match}")

        if actual_dau != claimed_dau:
            print(f"   ⚠️ 数据不符！差异: {abs(claimed_dau - actual_dau):,}")

    # 展示最近10天的实际数据
    print("\n" + "="*100)
    print("📊 最近10天的实际数据")
    print("="*100)
    print(f"{'日期':<15} {'实际DAU':<15}")
    print("-" * 100)

    sorted_dates = sorted(daily_dau.keys())[-10:]
    for date_str in sorted_dates:
        print(f"{date_str:<15} {daily_dau[date_str]:<15,}")

    print("\n" + "="*100)


if __name__ == "__main__":
    verify_agent_data()
