"""
每日数据分析主脚本
生成报告并发送到飞书群组
"""
import sys
import os
import requests
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scripts_dir = os.path.join(project_root, "scripts")
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, scripts_dir)

from generate_daily_report import generate_report, MultiTableDataProcessor


def send_to_feishu(title: str, markdown_content: str) -> bool:
    """发送报告到飞书群组"""
    try:
        # 从环境变量获取 Webhook URL，如果没有则使用默认值
        webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
        if not webhook_url:
            # 默认使用二重螺旋群的 Webhook URL
            webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/9d70437e-690c-4f96-8601-5b7058db0ebd"
            print(f"⚠️  未设置 FEISHU_WEBHOOK_URL 环境变量，使用默认 Webhook")

        print(f"📤 使用 Webhook URL: {webhook_url[:50]}...")

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


def main():
    """主函数"""
    print("=" * 80)
    print("开始每日数据分析")
    print("=" * 80)

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

    # 生成报告
    report = generate_report(processor, table_configs)

    if report:
        print("\n" + "=" * 80)
        print("分析报告")
        print("=" * 80)
        print(report)
        print("\n" + "=" * 80)

        # 发送到飞书群组
        print("\n正在发送报告到飞书群组...")
        send_success = send_to_feishu(
            title=f"📊 游戏数据分析报告 - {datetime.now().strftime('%Y-%m-%d')}",
            markdown_content=report
        )

        if send_success:
            print("\n✅ 分析完成！报告已发送到飞书群组。")
        else:
            print("\n✅ 分析完成！但发送到飞书群组失败。")

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
