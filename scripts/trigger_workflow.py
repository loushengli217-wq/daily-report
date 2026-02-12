#!/usr/bin/env python3
"""
手动触发 GitHub Actions 工作流
使用 GitHub API 手动触发 daily-report.yml 工作流
"""
import requests
import json
import sys
import os
from datetime import datetime

def trigger_workflow():
    """触发 GitHub Actions 工作流"""
    
    # GitHub 配置
    owner = "loushengli217-wq"  # 替换为你的 GitHub 用户名
    repo = "daily-report"      # 替换为你的仓库名称
    workflow_name = "daily-report.yml"
    branch = "main"
    
    # 需要 GitHub Personal Access Token (PAT)
    # 获取方式：GitHub Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
    token = os.getenv("GITHUB_TOKEN")
    
    if not token:
        print("❌ 错误：请设置 GITHUB_TOKEN 环境变量")
        print("获取方式：GitHub Settings -> Developer settings -> Personal access tokens -> Tokens (classic)")
        print("需要权限：repo (workflow)")
        sys.exit(1)
    
    # API 端点
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_name}/dispatches"
    
    # 请求头
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    # 请求体
    data = {
        "ref": branch
    }
    
    try:
        print(f"📤 正在触发工作流: {workflow_name}")
        print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 204:
            print("✅ 工作流触发成功！")
            print(f"🔗 查看执行状态：https://github.com/{owner}/{repo}/actions")
            return True
        else:
            print(f"❌ 触发失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = trigger_workflow()
    sys.exit(0 if success else 1)
