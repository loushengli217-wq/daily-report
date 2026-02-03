"""
测试飞书 webhook 配置
"""
import json
import requests
from coze_workload_identity import Client

def test_webhook():
    """测试 webhook 配置"""
    client = Client()

    try:
        # 获取凭证
        credential = client.get_integration_credential("integration-feishu-message")
        print("✅ 成功获取飞书消息凭证")
        print(f"\n凭证内容:")
        print(json.dumps(json.loads(credential), indent=2, ensure_ascii=False))

        # 解析 webhook_url
        webhook_key = json.loads(credential)["webhook_url"]
        print(f"\nWebhook URL: {webhook_key}")

        # 发送测试消息
        print("\n正在发送测试消息...")
        test_payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "🤖 机器人测试"
                    }
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "plain_text",
                            "content": "这是一条通过机器人 webhook 发送的消息。\n如果看到这条消息，说明机器人配置正确！"
                        }
                    }
                ]
            }
        }

        response = requests.post(webhook_key, json=test_payload)
        result = response.json()

        print(f"\n发送结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if result.get("code") == 0:
            print("\n✅ 消息发送成功！")
            print("\n请检查飞书群组：")
            print("- 消息应该显示为机器人名称")
            print("- 而不是你的个人账号")
            print("- 消息应该有卡片格式")
        else:
            print(f"\n❌ 消息发送失败: {result}")

    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_webhook()
