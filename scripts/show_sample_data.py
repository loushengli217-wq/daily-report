"""
显示表格的样本数据
"""
import sys
import os
import json

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from tools.feishu_bitable_tool import FeishuBitableClient, get_access_token


def show_sample_data(app_token, table_id, sample_size=5):
    """显示表格的样本数据"""
    client = FeishuBitableClient()
    token = get_access_token()

    print(f"正在获取数据样本...")
    print(f"App Token: {app_token}")
    print(f"Table ID: {table_id}\n")

    try:
        # 获取字段信息
        fields_response = client.get_fields(token, app_token, table_id)
        fields = fields_response.get("data", {}).get("items", [])

        print("=" * 100)
        print(f"📋 表格字段信息（共 {len(fields)} 个字段）：")
        print("=" * 100)
        for field in fields:
            print(f"  • {field.get('field_name'):<15} (类型: {field.get('type')}, ID: {field.get('field_id')})")

        print("\n" + "=" * 100)
        print(f"📊 最近 {sample_size} 条数据记录：")
        print("=" * 100)

        # 获取数据（按日期排序，取最后N条）
        search_response = client.search_records(
            token,
            app_token,
            table_id,
            sort=[{"field_name": "日期", "desc": True}],
            page_size=sample_size
        )

        records = search_response.get("data", {}).get("items", [])

        if not records:
            print("❌ 没有找到数据记录")
            return

        for i, record in enumerate(records, 1):
            print(f"\n【记录 #{i}】")
            print(f"  Record ID: {record.get('record_id')}")
            print(f"  最后修改: {record.get('last_modified_time')}")

            fields_data = record.get("fields", {})
            for field in fields:
                field_name = field.get('field_name')
                # 使用字段名称而不是field_id来获取值
                value = fields_data.get(field_name, "N/A")

                # 格式化输出
                if value is None:
                    value = "空"
                elif isinstance(value, dict):
                    # 处理数字类型的字段
                    if value.get('type') == 2 and 'value' in value:
                        val = value['value']
                        if isinstance(val, list) and len(val) > 0:
                            value = val[0]
                        else:
                            value = val
                    else:
                        value = json.dumps(value, ensure_ascii=False)
                elif isinstance(value, list):
                    # 处理文本类型的字段
                    if len(value) > 0 and isinstance(value[0], dict):
                        value = value[0].get('text', str(value))
                    else:
                        value = ", ".join([str(v) for v in value])
                elif isinstance(value, (int, float)):
                    # 处理数字
                    if field_name == "日期":
                        # 转换时间戳为日期
                        import datetime
                        value = datetime.datetime.fromtimestamp(value / 1000).strftime('%Y-%m-%d')
                    else:
                        value = str(value)

                print(f"  {field_name}: {value}")

        print("\n" + "=" * 100)
        print(f"📈 数据统计：")
        print("=" * 100)
        total_response = client.search_records(token, app_token, table_id, page_size=100)
        total_records = total_response.get("data", {}).get("items", [])
        print(f"  总记录数: {len(total_records)}")

        # 统计各渠道记录数
        channel_counts = {}
        for record in total_records:
            fields_data = record.get("fields", {})
            # 直接使用字段名称"渠道/国家"来获取值
            channel_value = fields_data.get("渠道/国家", "Unknown")

            # 处理渠道值（可能是文本格式）
            if isinstance(channel_value, list) and len(channel_value) > 0:
                if isinstance(channel_value[0], dict):
                    channel = channel_value[0].get('text', "Unknown")
                else:
                    channel = str(channel_value[0])
            else:
                channel = str(channel_value)

            channel_counts[channel] = channel_counts.get(channel, 0) + 1

        print(f"\n  各渠道数据量:")
        for channel, count in sorted(channel_counts.items()):
            print(f"    • {channel}: {count} 条记录")

    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    app_token = "LvSAboJTJanJKdssWs8cm49vn8c"
    table_id = "tblBiiYpOdRGonPy"

    show_sample_data(app_token, table_id, sample_size=3)
