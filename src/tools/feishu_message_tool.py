"""
飞书消息工具
用于发送飞书机器人消息
"""
import json
import requests
from langchain.tools import tool, ToolRuntime
from coze_workload_identity import Client


def get_webhook_url() -> str:
    """
    获取飞书消息的webhook URL
    """
    client = Client()
    wechat_bot_credential = client.get_integration_credential("integration-feishu-message")
    webhook_key = json.loads(wechat_bot_credential)["webhook_url"]
    return webhook_key


@tool
def send_feishu_text_message(text: str, at_all: bool = False) -> str:
    """
    发送飞书文本消息
    
    Args:
        text: 要发送的文本内容
        at_all: 是否@所有人，默认False
    
    Returns:
        发送结果
    """
    ctx = None
    
    webhook_url = get_webhook_url()
    
    content = {"text": text}
    if at_all:
        content["text"] = f"<at user_id='all'>所有人</at> {text}"
    
    payload = {
        "msg_type": "text",
        "content": content
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        result = response.json()
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@tool
def send_feishu_rich_text(title: str, content: str) -> str:
    """
    发送飞书富文本消息
    
    Args:
        title: 消息标题
        content: 消息内容（支持Markdown格式）
    
    Returns:
        发送结果
    """
    ctx = None
    
    webhook_url = get_webhook_url()
    
    # 将Markdown内容转换为富文本格式
    # 这里简化处理，将整个内容作为普通文本
    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": [
                        [
                            {
                                "tag": "text",
                                "text": content
                            }
                        ]
                    ]
                }
            }
        }
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        result = response.json()
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@tool
def send_feishu_markdown_message(title: str, markdown_content: str, at_all: bool = False) -> str:
    """
    发送飞书Markdown格式的消息（使用交互式卡片）
    
    Args:
        title: 消息标题
        markdown_content: Markdown格式的内容
        at_all: 是否@所有人，默认False
    
    Returns:
        发送结果
    """
    ctx = None
    
    webhook_url = get_webhook_url()
    
    # 如果需要@所有人，在内容前添加@标签
    if at_all:
        markdown_content = f"<at id='all'></at> {markdown_content}"
    
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
    
    try:
        response = requests.post(webhook_url, json=payload)
        result = response.json()
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@tool
def send_feishu_analysis_report(title: str, analysis_content: str, key_findings: list = None, recommendations: list = None, at_all: bool = False) -> str:
    """
    发送飞书数据分析报告（格式化的Markdown报告）
    
    Args:
        title: 报告标题
        analysis_content: 分析内容（Markdown格式）
        key_findings: 关键发现列表（可选）
        recommendations: 建议列表（可选）
        at_all: 是否@所有人，默认False
    
    Returns:
        发送结果
    """
    ctx = None
    
    webhook_url = get_webhook_url()
    
    # 构建Markdown报告
    markdown_parts = []
    
    # 添加@所有人
    if at_all:
        markdown_parts.append("<at id='all'></at>")
    
    # 添加分析内容
    markdown_parts.append(analysis_content)
    
    # 添加关键发现
    if key_findings:
        markdown_parts.append("\n### 🔍 关键发现")
        for i, finding in enumerate(key_findings, 1):
            markdown_parts.append(f"{i}. {finding}")
    
    # 添加建议
    if recommendations:
        markdown_parts.append("\n### 💡 业务建议")
        for i, rec in enumerate(recommendations, 1):
            markdown_parts.append(f"{i}. {rec}")
    
    markdown_content = "\n".join(markdown_parts)
    
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
                    "content": f"📊 {title}"
                }
            },
            "elements": elements
        }
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        result = response.json()
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
