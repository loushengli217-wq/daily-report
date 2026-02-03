"""
多表格数据处理器
支持从多个表格获取数据并分析
"""
import sys
import os
from datetime import datetime
from collections import defaultdict

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from tools.feishu_bitable_tool import FeishuBitableClient, get_access_token


class MultiTableDataProcessor:
    """多表格数据处理器"""

    def __init__(self, app_token):
        self.app_token = app_token
        self.client = FeishuBitableClient()
        self.token = get_access_token()

    def fetch_data(self, table_id, view_id=None, page_size=200):
        """获取指定表格的数据"""
        try:
            search_response = self.client.search_records(
                self.token,
                self.app_token,
                table_id,
                view_id=view_id,
                sort=[{"field_name": "日期", "desc": True}],
                page_size=page_size
            )
            return search_response.get("data", {}).get("items", [])
        except Exception as e:
            print(f"获取表格 {table_id} 数据失败: {str(e)}")
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

        # 解析分组字段（基础数据/渠道/国家）
        group_value = fields_data.get("渠道/国家") or fields_data.get("分组")
        if isinstance(group_value, list) and len(group_value) > 0:
            if isinstance(group_value[0], dict):
                group = group_value[0].get('text', 'Total')
            else:
                group = str(group_value[0])
        else:
            group = 'Total'

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
            "group": group,
            "dau": dau,
            "new_users": new_users,
            "income": income,
            "paid_users": paid_users
        }

    def process_table_data(self, table_id, view_id=None, last_n=None):
        """处理单个表格的数据"""
        print(f"\n处理表格: {table_id}")
        if view_id:
            print(f"视图ID: {view_id}")

        records = self.fetch_data(table_id, view_id)

        if not records:
            return {"error": f"表格 {table_id} 没有数据"}

        # 解析所有记录
        parsed_records = []
        for record in records:
            parsed = self.parse_record(record)
            if parsed:
                parsed_records.append(parsed)

        if not parsed_records:
            return {"error": f"表格 {table_id} 没有有效数据"}

        # 获取最后N条记录（按原始顺序）
        if last_n and len(parsed_records) >= last_n:
            target_records = parsed_records[-last_n:]
        else:
            target_records = parsed_records

        print(f"  获取最后 {len(target_records)} 条记录")

        # 按日期分组（针对这N条记录）
        date_groups = defaultdict(list)
        for rec in target_records:
            date_groups[rec["date"]].append(rec)

        # 排序日期
        sorted_dates = sorted(date_groups.keys())

        # 汇总数据
        daily_summary = {}
        for date in sorted_dates:
            records_for_date = date_groups[date]

            # 按分组汇总
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

            for rec in records_for_date:
                group = rec["group"]

                group_summary[group]["dau"] += rec["dau"]
                group_summary[group]["new_users"] += rec["new_users"]
                group_summary[group]["income"] += rec["income"]
                group_summary[group]["paid_users"] += rec["paid_users"]

                total_dau += rec["dau"]
                total_new += rec["new_users"]
                total_income += rec["income"]
                total_paid += rec["paid_users"]

            daily_summary[date] = {
                "total": {
                    "dau": total_dau,
                    "new_users": total_new,
                    "income": total_income,
                    "paid_users": total_paid
                },
                "groups": dict(group_summary)
            }

        return {
            "table_id": table_id,
            "view_id": view_id,
            "total_records": len(parsed_records),
            "analyzed_rows": len(target_records),
            "date_range": {
                "start": sorted_dates[0],
                "end": sorted_dates[-1],
                "total_days": len(sorted_dates)
            },
            "target_dates": sorted_dates,
            "daily_summary": daily_summary
        }


def format_multi_table_data(results, table_configs):
    """格式化多个表格的数据"""
    output = []

    output.append("=" * 100)
    output.append("【游戏数据分析报告】")
    output.append("=" * 100)

    for i, (result, config) in enumerate(zip(results, table_configs), 1):
        output.append(f"\n{'=' * 100}")
        output.append(f"【{i}. {config['name']}】")
        output.append(f"{'=' * 100}")

        if "error" in result:
            output.append(f"❌ {result['error']}")
            continue

        output.append(f"表格ID: {result['table_id']}")
        output.append(f"视图ID: {result['view_id']}")
        output.append(f"数据范围: {result['date_range']['start']} 至 {result['date_range']['end']} ({result['date_range']['total_days']}天)")
        output.append(f"分析行数: {result['analyzed_rows']}行")

        # 表格数据
        output.append(f"\n日期\t总DAU\t新增用户\t总收入\t付费率(%)")
        output.append("-" * 80)

        for date in result['target_dates']:
            data = result['daily_summary'][date]['total']
            paid_rate = round(data['paid_users'] / data['dau'] * 100, 2) if data['dau'] > 0 else 0
            output.append(
                f"{date}\t{data['dau']:,}\t{data['new_users']:,}\t${data['income']:,.2f}\t{paid_rate:.2f}%"
            )

        # 分组数据
        output.append(f"\n各维度数据（按最新日期）:")
        latest_date = result['target_dates'][-1]
        groups = result['daily_summary'][latest_date]['groups']

        output.append(f"{'维度':<20} {'DAU':<12} {'新增用户':<12} {'总收入':<15} {'付费率(%)'}")
        output.append("-" * 80)

        for group_name in sorted(groups.keys()):
            group_data = groups[group_name]
            paid_rate = round(group_data['paid_users'] / group_data['dau'] * 100, 2) if group_data['dau'] > 0 else 0
            output.append(
                f"{group_name:<20} {group_data['dau']:<12,} {group_data['new_users']:<12,} ${group_data['income']:<14,.2f} {paid_rate:.2f}%"
            )

    output.append("\n" + "=" * 100)

    return "\n".join(output)


def test_multi_table_processor():
    """测试多表格数据处理"""
    processor = MultiTableDataProcessor(app_token="LvSAboJTJanJKdssWs8cm49vn8c")

    # 配置3个表格
    table_configs = [
        {
            "name": "游戏基础数据",
            "table_id": "tblM5x1uyjwffoBq",
            "view_id": "vew8YRRC3u",
            "last_n": 7  # 倒数7行（7天）
        },
        {
            "name": "游戏渠道数据",
            "table_id": "tblBiiYpOdRGonPy",
            "view_id": "vew8YRRC3u",
            "last_n": 35  # 倒数35行
        },
        {
            "name": "游戏主要国家数据",
            "table_id": "tblgx4cY7LvncsiJ",
            "view_id": "vew8YRRC3u",
            "last_n": 28  # 倒数28行
        }
    ]

    # 处理所有表格
    results = []
    for config in table_configs:
        result = processor.process_table_data(
            config['table_id'],
            config['view_id'],
            config['last_n']
        )
        results.append(result)

    # 格式化输出
    formatted = format_multi_table_data(results, table_configs)

    print(formatted)


if __name__ == "__main__":
    test_multi_table_processor()
