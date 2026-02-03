"""
数据验证工具
强制验证数据的准确性和完整性
"""
import sys
import os
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from tools.feishu_bitable_tool import FeishuBitableClient, get_access_token


def validate_data(app_token, table_id, target_date=None):
    """
    验证数据并返回可用的日期范围

    Args:
        app_token: 飞书表格的app_token
        table_id: 数据表的table_id
        target_date: 目标分析日期（可选，格式：YYYY-MM-DD）

    Returns:
        dict: 包含验证结果和可用数据信息
    """
    client = FeishuBitableClient()
    token = get_access_token()

    try:
        # 获取数据
        search_response = client.search_records(
            token,
            app_token,
            table_id,
            sort=[{"field_name": "日期", "desc": True}],
            page_size=200
        )

        all_records = search_response.get("data", {}).get("items", [])

        # 提取所有日期
        all_dates = set()
        daily_data = {}

        for record in all_records:
            fields_data = record.get("fields", {})
            date_value = fields_data.get("日期")

            if isinstance(date_value, (int, float)):
                date_str = datetime.fromtimestamp(date_value / 1000).strftime('%Y-%m-%d')
                all_dates.add(date_str)

                # 汇总每日DAU
                dau_value = fields_data.get("DAU", 0)
                if isinstance(dau_value, (int, float)):
                    if date_str not in daily_data:
                        daily_data[date_str] = 0
                    daily_data[date_str] += dau_value

        # 排序日期
        sorted_dates = sorted(all_dates)

        if not sorted_dates:
            return {
                "status": "error",
                "message": "表格中没有数据",
                "data_range": None
            }

        data_range = {
            "start": sorted_dates[0],
            "end": sorted_dates[-1],
            "total_days": len(sorted_dates),
            "all_dates": sorted_dates
        }

        # 检查目标日期是否存在
        if target_date:
            if target_date in sorted_dates:
                return {
                    "status": "success",
                    "message": f"目标日期 {target_date} 的数据存在",
                    "target_date_exists": True,
                    "target_date_dau": daily_data.get(target_date, 0),
                    "data_range": data_range,
                    "available_dates": sorted_dates
                }
            else:
                # 找到最近的可用日期
                closest_date = min(sorted_dates, key=lambda d: abs(
                    (datetime.strptime(d, '%Y-%m-%d') - datetime.strptime(target_date, '%Y-%m-%d')).days
                ))

                return {
                    "status": "warning",
                    "message": f"目标日期 {target_date} 的数据不存在",
                    "target_date_exists": False,
                    "closest_date": closest_date,
                    "closest_date_dau": daily_data.get(closest_date, 0),
                    "data_range": data_range,
                    "available_dates": sorted_dates[-7:]  # 最近7天可用日期
                }
        else:
            return {
                "status": "success",
                "message": "数据验证完成",
                "data_range": data_range,
                "available_dates": sorted_dates
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"数据验证失败: {str(e)}",
            "data_range": None
        }


def print_validation_result(result):
    """打印验证结果"""
    print("=" * 100)
    print("📊 数据验证结果")
    print("=" * 100)

    if result["status"] == "error":
        print(f"\n❌ {result['message']}")
        return

    print(f"\n✅ {result['message']}")

    if "data_range" in result and result["data_range"]:
        dr = result["data_range"]
        print(f"\n📅 数据范围:")
        print(f"   起始日期: {dr['start']}")
        print(f"   结束日期: {dr['end']}")
        print(f"   总天数: {dr['total_days']}")

    if "target_date_exists" in result:
        if result["target_date_exists"]:
            print(f"\n✅ 目标日期数据存在")
            print(f"   DAU: {result.get('target_date_dau', 0):,}")
        else:
            print(f"\n⚠️  目标日期数据不存在")
            print(f"   最近可用日期: {result.get('closest_date', 'N/A')}")
            print(f"   日期DAU: {result.get('closest_date_dau', 0):,}")

    if "available_dates" in result and result["available_dates"]:
        print(f"\n📋 可用日期（最近7天）:")
        for date in result["available_dates"]:
            print(f"   - {date}")

    print("\n" + "=" * 100)


if __name__ == "__main__":
    from datetime import timedelta

    today = datetime.now()
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')

    app_token = "LvSAboJTJanJKdssWs8cm49vn8c"
    table_id = "tblBiiYpOdRGonPy"

    print(f"验证目标日期: {yesterday_str}\n")

    result = validate_data(app_token, table_id, yesterday_str)
    print_validation_result(result)

    print("\n" + "=" * 100)
    print("💡 重要提醒：")
    print("=" * 100)
    print("在分析报告中，必须使用上述验证通过的日期范围")
    print("严禁使用不存在的日期（如2026-05-09等）")
    print("=" * 100)
