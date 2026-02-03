"""
数据处理模块
直接在代码层面处理数据，不依赖AI理解
"""
import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from tools.feishu_bitable_tool import FeishuBitableClient, get_access_token


class DataProcessor:
    """数据处理器"""

    def __init__(self, app_token, table_id):
        self.app_token = app_token
        self.table_id = table_id
        self.client = FeishuBitableClient()
        self.token = get_access_token()

    def fetch_data(self, page_size=200):
        """获取原始数据"""
        try:
            search_response = self.client.search_records(
                self.token,
                self.app_token,
                self.table_id,
                sort=[{"field_name": "日期", "desc": True}],
                page_size=page_size
            )
            return search_response.get("data", {}).get("items", [])
        except Exception as e:
            print(f"获取数据失败: {str(e)}")
            return []

    def parse_record(self, record):
        """解析单条记录"""
        fields_data = record.get("fields", {})

        # 解析日期
        date_value = fields_data.get("日期")
        if isinstance(date_value, (int, float)):
            date_str = datetime.fromtimestamp(date_value / 1000).strftime('%Y-%m-%d')
        else:
            return None

        # 解析渠道
        channel_value = fields_data.get("渠道/国家")
        if isinstance(channel_value, list) and len(channel_value) > 0:
            if isinstance(channel_value[0], dict):
                channel = channel_value[0].get('text', 'Unknown')
            else:
                channel = str(channel_value[0])
        else:
            channel = 'Unknown'

        # 解析DAU
        dau_value = fields_data.get("DAU", 0)
        if isinstance(dau_value, (int, float)):
            dau = int(dau_value)
        elif isinstance(dau_value, dict) and 'value' in dau_value:
            val = dau_value['value']
            dau = int(val[0]) if isinstance(val, list) and len(val) > 0 else int(val)
        else:
            dau = 0

        # 解析新增
        new_value = fields_data.get("新增", 0)
        if isinstance(new_value, (int, float)):
            new_users = int(new_value)
        elif isinstance(new_value, dict) and 'value' in new_value:
            val = new_value['value']
            new_users = int(val[0]) if isinstance(val, list) and len(val) > 0 else int(val)
        else:
            new_users = 0

        # 解析收入
        income_value = fields_data.get("收入(美元)数字")
        if isinstance(income_value, dict) and 'value' in income_value:
            val = income_value['value']
            income = float(val[0]) if isinstance(val, list) and len(val) > 0 else float(val)
        else:
            income = 0.0

        # 解析付费用户
        paid_value = fields_data.get("付费用户", 0)
        if isinstance(paid_value, (int, float)):
            paid_users = int(paid_value)
        elif isinstance(paid_value, dict) and 'value' in paid_value:
            val = paid_value['value']
            paid_users = int(val[0]) if isinstance(val, list) and len(val) > 0 else int(val)
        else:
            paid_users = 0

        return {
            "date": date_str,
            "channel": channel,
            "dau": dau,
            "new_users": new_users,
            "income": income,
            "paid_users": paid_users
        }

    def process_data(self, target_date=None, days=7):
        """处理数据，返回汇总统计"""
        records = self.fetch_data()

        if not records:
            return {"error": "没有数据"}

        # 解析所有记录
        parsed_records = []
        for record in records:
            parsed = self.parse_record(record)
            if parsed:
                parsed_records.append(parsed)

        if not parsed_records:
            return {"error": "没有有效数据"}

        # 按日期汇总
        daily_summary = defaultdict(lambda: {
            "total_dau": 0,
            "total_new": 0,
            "total_income": 0.0,
            "total_paid": 0,
            "channels": {}
        })

        for rec in parsed_records:
            date = rec["date"]
            channel = rec["channel"]

            # 每日汇总
            daily_summary[date]["total_dau"] += rec["dau"]
            daily_summary[date]["total_new"] += rec["new_users"]
            daily_summary[date]["total_income"] += rec["income"]
            daily_summary[date]["total_paid"] += rec["paid_users"]

            # 每日各渠道数据
            daily_summary[date]["channels"][channel] = {
                "dau": rec["dau"],
                "new_users": rec["new_users"],
                "income": rec["income"],
                "paid_users": rec["paid_users"]
            }

        # 排序日期
        sorted_dates = sorted(daily_summary.keys())

        # 确定分析日期
        if target_date and target_date in sorted_dates:
            analysis_date = target_date
        else:
            analysis_date = sorted_dates[-1]  # 最新日期

        # 获取最近N天数据
        recent_dates = sorted_dates[-days:] if len(sorted_dates) >= days else sorted_dates

        # 构建结果
        result = {
            "data_range": {
                "start": sorted_dates[0],
                "end": sorted_dates[-1],
                "total_days": len(sorted_dates)
            },
            "analysis_date": analysis_date,
            "analysis_date_exists": analysis_date in sorted_dates,
            "recent_days": days,
            "recent_dates": recent_dates,
            "daily_data": {}
        }

        # 添加每日数据
        for date in recent_dates:
            summary = daily_summary[date]
            result["daily_data"][date] = {
                "total_dau": summary["total_dau"],
                "total_new": summary["total_new"],
                "total_income": round(summary["total_income"], 2),
                "total_paid": summary["total_paid"],
                "paid_rate": round(summary["total_paid"] / summary["total_dau"] * 100, 2) if summary["total_dau"] > 0 else 0,
                "arpu": round(summary["total_income"] / summary["total_dau"], 2) if summary["total_dau"] > 0 else 0,
                "channels": summary["channels"]
            }

        return result

    def format_for_ai(self, processed_data):
        """格式化数据，便于AI理解"""
        result = []

        result.append(f"【数据范围】")
        result.append(f"起始日期：{processed_data['data_range']['start']}")
        result.append(f"结束日期：{processed_data['data_range']['end']}")
        result.append(f"总天数：{processed_data['data_range']['total_days']}天")

        result.append(f"\n【分析日期】")
        result.append(f"目标分析日期：{processed_data['analysis_date']}")
        result.append(f"该日期数据存在：{'是' if processed_data['analysis_date_exists'] else '否'}")

        result.append(f"\n【最近{processed_data['recent_days']}天数据】")
        result.append(f"日期范围：{processed_data['recent_dates'][0]} 至 {processed_data['recent_dates'][-1]}")

        # 每日数据表格
        result.append(f"\n日期\t总DAU\t新增用户\t总收入\t付费率(%)")
        result.append("-" * 80)

        for date in processed_data['recent_dates']:
            data = processed_data['daily_data'][date]
            result.append(
                f"{date}\t{data['total_dau']:,}\t{data['total_new']:,}\t${data['total_income']:,.2f}\t{data['paid_rate']:.2f}%"
            )

        # 分析日期的各渠道数据
        analysis_date = processed_data['analysis_date']
        if analysis_date in processed_data['daily_data']:
            result.append(f"\n【{analysis_date}各渠道数据】")
            result.append(f"渠道\tDAU\t新增用户\t总收入\t付费率(%)")
            result.append("-" * 80)

            channels = processed_data['daily_data'][analysis_date]['channels']
            for channel, data in sorted(channels.items()):
                paid_rate = round(data['paid_users'] / data['dau'] * 100, 2) if data['dau'] > 0 else 0
                result.append(
                    f"{channel}\t{data['dau']:,}\t{data['new_users']:,}\t${data['income']:,.2f}\t{paid_rate:.2f}%"
                )

        return "\n".join(result)


def test_data_processor():
    """测试数据处理"""
    processor = DataProcessor(
        app_token="LvSAboJTJanJKdssWs8cm49vn8c",
        table_id="tblBiiYpOdRGonPy"
    )

    # 处理数据
    processed = processor.process_data(target_date="2026-02-02", days=7)

    # 格式化输出
    formatted = processor.format_for_ai(processed)

    print("=" * 100)
    print("✅ 数据处理结果")
    print("=" * 100)
    print(formatted)
    print("=" * 100)


if __name__ == "__main__":
    test_data_processor()
