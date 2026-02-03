"""
快速测试脚本 - 验证多表格分析功能
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from multi_table_processor import MultiTableDataProcessor, format_multi_table_data


def quick_test():
    """快速测试多表格数据获取"""
    print("=" * 80)
    print("快速测试 - 多表格数据获取")
    print("=" * 80)

    # 初始化处理器
    processor = MultiTableDataProcessor(app_token="LvSAboJTJanJKdssWs8cm49vn8c")

    # 配置3个表格
    table_configs = [
        {
            "name": "游戏基础数据",
            "table_id": "tblM5x1uyjwffoBq",
            "view_id": "vew8YRRC3u",
            "last_n": 7  # 倒数7行
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
    print("\n开始获取数据...\n")
    results = []
    for i, config in enumerate(table_configs, 1):
        print(f"[{i}/3] 处理: {config['name']}")
        result = processor.process_table_data(
            config['table_id'],
            config['view_id'],
            config['last_n']
        )
        results.append(result)

        if "error" in result:
            print(f"  ❌ 错误: {result['error']}")
        else:
            print(f"  ✅ 成功: {result['total_records']} 条记录")
            print(f"     时间范围: {result['date_range']['start']} 至 {result['date_range']['end']} ({result['date_range']['total_days']}天)")
            print(f"     分析行数: {result['analyzed_rows']}行")

    # 格式化并输出摘要
    print("\n" + "=" * 80)
    print("数据摘要")
    print("=" * 80)

    for i, (result, config) in enumerate(zip(results, table_configs), 1):
        if "error" in result:
            continue

        print(f"\n{i}. {config['name']}")
        print(f"   表格ID: {result['table_id']}")
        print(f"   数据范围: {result['date_range']['start']} 至 {result['date_range']['end']} ({result['date_range']['total_days']}天)")
        print(f"   分析行数: {result['analyzed_rows']}行")

        # 获取最新一天的数据
        latest_date = result['target_dates'][-1]
        latest_data = result['daily_summary'][latest_date]['total']

        print(f"   最新数据 ({latest_date}):")
        print(f"   - DAU: {latest_data['dau']:,}")
        print(f"   - 新增用户: {latest_data['new_users']:,}")
        print(f"   - 收入: ${latest_data['income']:,.2f}")
        paid_rate = round(latest_data['paid_users'] / latest_data['dau'] * 100, 2) if latest_data['dau'] > 0 else 0
        print(f"   - 付费率: {paid_rate:.2f}%")

    print("\n" + "=" * 80)
    print("✅ 测试完成！")
    print("=" * 80)

    # 检查是否有错误
    has_error = any("error" in r for r in results)
    if has_error:
        print("\n⚠️  部分表格数据获取失败，请检查配置！")
    else:
        print("\n✅ 所有表格数据获取成功！可以运行完整分析：")
        print("   python scripts/daily_analysis_multi.py")


if __name__ == "__main__":
    quick_test()
