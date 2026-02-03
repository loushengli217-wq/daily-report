"""
每日数据分析脚本 - 多表格版本
自动获取3个表格的数据并生成分析报告
"""
import sys
import os
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from multi_table_processor import MultiTableDataProcessor, format_multi_table_data
from src.agents.agent import build_agent
import json
from coze_workload_identity import Client
import requests


def send_to_feishu_report(title: str, markdown_content: str, at_all: bool = False) -> bool:
    """发送报告到飞书群组"""
    try:
        client = Client()
        credential = client.get_integration_credential("integration-feishu-message")
        webhook_url = json.loads(credential)["webhook_url"]

        # 构建交互式卡片
        elements = [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": markdown_content
                }
            }
        ]

        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    }
                },
                "elements": elements
            }
        }

        response = requests.post(webhook_url, json=payload)
        result = response.json()

        if result.get("code") == 0:
            print("\n✅ 报告已成功发送到飞书群组！")
            return True
        else:
            print(f"\n❌ 发送失败: {result}")
            return False

    except Exception as e:
        print(f"\n❌ 发送报告到飞书失败: {str(e)}")
        return False


def run_daily_analysis():
    """运行每日数据分析"""
    print("=" * 80)
    print("开始多表格数据分析")
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
    print("\n开始获取数据...")
    results = []
    for config in table_configs:
        print(f"\n处理表格: {config['name']} ({config['table_id']})")
        result = processor.process_table_data(
            config['table_id'],
            config['view_id'],
            config['last_n']
        )
        results.append(result)

    # 检查是否有错误
    has_error = any("error" in r for r in results)
    if has_error:
        print("\n⚠️  部分表格数据获取失败！")
        for i, result in enumerate(results):
            if "error" in result:
                print(f"  ❌ {table_configs[i]['name']}: {result['error']}")

    # 格式化数据
    print("\n格式化数据...")
    formatted_data = format_multi_table_data(results, table_configs)

    # 获取数据时间范围
    time_ranges = []
    for result in results:
        if "date_range" in result:
            time_ranges.append(
                f"{result['date_range']['start']} 至 {result['date_range']['end']} "
                f"({result['date_range']['total_days']}天)"
            )

    # 构建Agent分析输入
    print("\n启动AI分析...")
    agent_input = f"""请分析以下游戏数据，生成专业的数据分析报告：

## 数据来源
1. 游戏基础数据 - 倒数7行数据
2. 游戏渠道数据 - 倒数35行数据
3. 游戏主要国家数据 - 倒数28行数据

## 实际数据

{formatted_data}

## 分析要求
1. 必须基于以上实际数据进行分析，不得编造数据
2. 分别分析基础数据、渠道数据和国家数据的变化趋势
3. 识别关键指标的变化规律和异常点
4. 提供基于数据的具体优化建议
5. 明确标注数据分析的时间范围

请生成详细的分析报告。
"""

    # 调用Agent
    try:
        agent = build_agent()
        response = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": agent_input
                    }
                ]
            },
            config={
                "configurable": {
                    "thread_id": f"daily_analysis_{datetime.now().strftime('%Y%m%d')}"
                }
            }
        )

        # 提取分析报告
        analysis_report = ""
        for message in response.get("messages", []):
            if hasattr(message, 'content'):
                analysis_report += str(message.content)

        print("\n" + "=" * 80)
        print("分析报告")
        print("=" * 80)
        print(analysis_report)
        print("\n" + "=" * 80)

        # 发送到飞书群组
        print("\n正在发送报告到飞书群组...")
        send_success = send_to_feishu_report(
            title=f"📊 游戏数据分析报告 - {datetime.now().strftime('%Y-%m-%d')}",
            markdown_content=analysis_report,
            at_all=False
        )

        if send_success:
            print("\n✅ 分析完成！报告已发送到飞书群组。")
        else:
            print("\n✅ 分析完成！但发送到飞书群组失败。")

        return analysis_report

    except Exception as e:
        print(f"\n❌ Agent分析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    report = run_daily_analysis()

    if report:
        print("\n✅ 分析完成！")
    else:
        print("\n❌ 分析失败！")
