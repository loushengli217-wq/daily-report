#!/usr/bin/env python3
"""
搜索飞书群机器人@成员的方法
"""

from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context

ctx = new_context(method="search.web")

client = SearchClient(ctx=ctx)

# 搜索飞书群机器人@成员的方法
query = "飞书机器人 at所有人 at成员 发送消息 open.larksuite.com open.feishu.cn"

print("="*80)
print(f"搜索查询: {query}")
print("="*80)
print()

response = client.web_search(
    query=query,
    count=10,
    need_summary=True
)

if response.summary:
    print("AI 摘要:")
    print("="*80)
    print(response.summary)
    print()

if response.web_items:
    print("="*80)
    print("搜索结果:")
    print("="*80)
    for i, item in enumerate(response.web_items, 1):
        print(f"\n{i}. {item.title}")
        print(f"   来源: {item.site_name}")
        print(f"   URL: {item.url}")
        print(f"   摘要: {item.snippet[:300]}...")
