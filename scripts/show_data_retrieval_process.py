"""
展示数据获取和处理的完整过程
"""
import sys
import os
import json
from datetime import datetime, timedelta

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from tools.feishu_bitable_tool import FeishuBitableClient, get_access_token


def show_data_retrieval_process(app_token, table_id):
    """展示完整的数据获取过程"""

    print("="*100)
    print("📊 数据获取过程详解")
    print("="*100)

    # 步骤1：连接飞书API
    print("\n【步骤1】连接飞书多维表格API")
    print("-" * 100)
    client = FeishuBitableClient()
    token = get_access_token()
    print(f"✅ 已获取访问令牌")
    print(f"✅ API Base URL: {client.base_url}")

    # 步骤2：获取表格字段信息
    print("\n【步骤2】获取表格字段信息")
    print("-" * 100)
    fields_response = client.get_fields(token, app_token, table_id)
    fields = fields_response.get("data", {}).get("items", [])
    print(f"✅ 获取到 {len(fields)} 个字段：")
    for field in fields:
        print(f"   - {field.get('field_name')} (ID: {field.get('field_id')})")

    # 步骤3：获取数据（最近200条，按日期降序）
    print("\n【步骤3】获取表格数据")
    print("-" * 100)
    search_response = client.search_records(
        token,
        app_token,
        table_id,
        sort=[{"field_name": "日期", "desc": True}],
        page_size=200
    )

    all_records = search_response.get("data", {}).get("items", [])
    print(f"✅ 获取到 {len(all_records)} 条记录")
    print(f"✅ 已按日期降序排序（最新的在前）")

    # 步骤4：解析数据结构
    print("\n【步骤4】数据结构解析")
    print("-" * 100)
    print("数据格式示例（第一条记录）：")
    first_record = all_records[0]
    print(json.dumps(first_record, indent=2, ensure_ascii=False))

    # 步骤5：提取和汇总数据
    print("\n【步骤5】提取和汇总数据")
    print("-" * 100)

    # 按日期汇总DAU
    daily_dau = {}

    for record in all_records:
        fields_data = record.get("fields", {})

        # 获取日期
        date_value = fields_data.get("日期")
        if isinstance(date_value, (int, float)):
            # 时间戳转日期
            date_str = datetime.fromtimestamp(date_value / 1000).strftime('%Y-%m-%d')
        elif isinstance(date_value, list) and len(date_value) > 0:
            if isinstance(date_value[0], dict):
                date_str = date_value[0].get('text', str(date_value[0]))
            else:
                date_str = str(date_value[0])
        else:
            continue

        # 获取DAU
        dau_value = fields_data.get("DAU")
        if isinstance(dau_value, (int, float)):
            dau = dau_value
        elif isinstance(dau_value, dict) and 'value' in dau_value:
            val = dau_value['value']
            if isinstance(val, list) and len(val) > 0:
                dau = val[0]
            else:
                dau = val
        else:
            continue

        # 汇总同一天的DAU
        if date_str not in daily_dau:
            daily_dau[date_str] = 0
        daily_dau[date_str] += dau

    print(f"✅ 汇总了 {len(daily_dau)} 天的数据")

    # 步骤6：展示过去7天的数据
    print("\n【步骤6】过去7天的DAU数据")
    print("-" * 100)
    print(f"{'日期':<15} {'总DAU':<15} {'环比变化':<15}")
    print("-" * 100)

    sorted_dates = sorted(daily_dau.keys())[-7:]
    prev_dau = None

    for date_str in sorted_dates:
        total_dau = daily_dau[date_str]

        if prev_dau is not None:
            change_pct = ((total_dau - prev_dau) / prev_dau) * 100
            change_str = f"{change_pct:+.1f}%"
        else:
            change_str = "-"

        print(f"{date_str:<15} {total_dau:<15,} {change_str:<15}")
        prev_dau = total_dau

    # 步骤7：获取指定日期的详细数据
    print("\n【步骤7】指定日期的详细数据")
    print("-" * 100)

    target_dates = ["2026-02-02", "2026-01-27"]

    for target_date in target_dates:
        print(f"\n📅 {target_date} 的详细数据：")
        print(f"{'渠道':<10} {'DAU':<10} {'新增':<10} {'收入(美元)':<15}")
        print("-" * 100)

        for record in all_records:
            fields_data = record.get("fields", {})

            # 获取日期
            date_value = fields_data.get("日期")
            if isinstance(date_value, (int, float)):
                record_date = datetime.fromtimestamp(date_value / 1000).strftime('%Y-%m-%d')
            else:
                continue

            if record_date != target_date:
                continue

            # 获取渠道
            channel_value = fields_data.get("渠道/国家")
            if isinstance(channel_value, list) and len(channel_value) > 0:
                if isinstance(channel_value[0], dict):
                    channel = channel_value[0].get('text', 'Unknown')
                else:
                    channel = str(channel_value[0])
            else:
                channel = 'Unknown'

            # 获取DAU
            dau_value = fields_data.get("DAU", 0)
            if isinstance(dau_value, (int, float)):
                dau = dau_value
            elif isinstance(dau_value, dict) and 'value' in dau_value:
                val = dau_value['value']
                dau = val[0] if isinstance(val, list) and len(val) > 0 else val
            else:
                dau = 0

            # 获取新增
            new_value = fields_data.get("新增", 0)
            if isinstance(new_value, (int, float)):
                new_users = new_value
            elif isinstance(new_value, dict) and 'value' in new_value:
                val = new_value['value']
                new_users = val[0] if isinstance(val, list) and len(val) > 0 else val
            else:
                new_users = 0

            # 获取收入
            income_value = fields_data.get("收入(美元)数字")
            if isinstance(income_value, dict) and 'value' in income_value:
                val = income_value['value']
                income = val[0] if isinstance(val, list) and len(val) > 0 else val
            else:
                income = 0

            print(f"{channel:<10} {dau:<10,} {new_users:<10,} ${income:>10,.2f}")

        # 计算当日汇总
        total_dau = sum([dau for d, _ in daily_dau.items() if d == target_date for dau in [fields_data.get("DAU", 0) for fields_data in [r.get("fields", {}) for r in all_records if isinstance(r.get("fields", {}).get("日期"), (int, float)) and datetime.fromtimestamp(r.get("fields", {}).get("日期") / 1000).strftime('%Y-%m-%d') == target_date]] if isinstance(dau, (int, float))])

    print("\n" + "="*100)
    print("✅ 数据获取过程演示完成")
    print("="*100)


if __name__ == "__main__":
    app_token = "LvSAboJTJanJKdssWs8cm49vn8c"
    table_id = "tblBiiYpOdRGonPy"

    show_data_retrieval_process(app_token, table_id)
