#!/usr/bin/env python3
"""
获取飞书群组成员的User ID
支持按用户名搜索
"""

import sys
import os
import json
import requests

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scripts_dir = os.path.join(project_root, "scripts")
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, scripts_dir)


def get_feishu_user_list(search_name=""):
    """
    获取飞书用户列表或搜索特定用户
    需要飞书开放平台的API访问权限
    """
    # 注意：这个功能需要飞书开放平台的app_access_token
    # 并且需要获取用户的访问权限
    print("="*80)
    print("获取飞书用户User ID")
    print("="*80)
    print()
    print("注意：此功能需要配置飞书开放平台的API访问权限")
    print()

    # 尝试从集成服务获取凭证
    try:
        from coze_workload_identity import Client

        client = Client()
        credential = client.get_integration_credential("integration-feishu-message")
        webhook_info = json.loads(credential)

        print("当前配置的Webhook URL:")
        print(webhook_info.get("webhook_url", "未配置"))
        print()

    except Exception as e:
        print(f"无法获取集成凭证: {e}")
        print()

    print("由于飞书Webhook机器人没有获取用户信息的权限，")
    print("无法直接通过脚本获取User ID。")
    print()

    print("="*80)
    print("手动获取User ID的方法")
    print("="*80)
    print()
    print("方法一：通过飞书开发者工具")
    print("1. 在浏览器中打开飞书网页版")
    print("2. 按F12打开开发者工具")
    print("3. 点击到 'Console' 标签")
    print("4. 在群组中点击'娄晓鹏'的头像")
    print("5. 在开发者工具的Network标签中查找用户信息请求")
    print("6. 在返回的JSON数据中找到 'user_id' 或 'open_id' 字段")
    print()

    print("方法二：联系飞书管理员")
    print("1. 联系公司的飞书管理员")
    print("2. 请求提供群成员的User ID列表")
    print("3. 管理员可以在飞书管理后台查看")
    print()

    print("方法三：通过PC端飞书客户端")
    print("1. 在PC端飞书中，右键点击群成员的头像")
    print("2. 选择'查看详情'")
    print("3. 在详情页面可能显示用户ID（某些版本）")
    print()

    print("方法四：使用替代方案")
    print("如果无法获取User ID，可以使用以下替代方案：")
    print("- 留空 ALERT_USER_ID，这样会@所有人")
    print("- 修改报警逻辑，改为在群内发送普通消息而非@特定人")
    print()

    print("="*80)
    print("当前配置")
    print("="*80)
    print()

    # 读取当前配置
    script_path = os.path.join(scripts_dir, "start_scheduler.sh")
    if os.path.exists(script_path):
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'ALERT_USER_ID=' in content:
                for line in content.split('\n'):
                    if line.strip().startswith('export ALERT_USER_ID='):
                        print(line)
                        print()
                        break

    print("如需配置User ID，请编辑 scripts/start_scheduler.sh 文件")
    print("修改 ALERT_USER_ID 的值为实际的User ID")


if __name__ == "__main__":
    import sys

    search_name = sys.argv[1] if len(sys.argv) > 1 else ""

    if search_name:
        print(f"尝试搜索用户: {search_name}")
        print()

    get_feishu_user_list(search_name)
