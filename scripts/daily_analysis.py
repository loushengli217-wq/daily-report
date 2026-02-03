"""
每日数据分析脚本
自动从飞书多维表格获取数据，分析后发送报告到飞书群组
"""
import os
import sys
import json
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from agents.agent import build_agent
from langchain_core.messages import HumanMessage


def load_config():
    """
    加载配置文件
    """
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, "scripts/daily_analysis_config.json")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}，请先创建该文件并配置参数")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_daily_analysis():
    """
    执行每日数据分析任务
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行每日数据分析任务...")
    
    try:
        # 加载配置
        config = load_config()
        app_token = config.get("app_token")
        table_id = config.get("table_id")
        report_title = config.get("report_title", "每日数据分析报告")
        at_all = config.get("at_all", False)
        custom_prompt = config.get("custom_prompt", "")
        
        if not app_token or not table_id:
            raise ValueError("配置文件中缺少 app_token 或 table_id")
        
        print(f"  - App Token: {app_token}")
        print(f"  - Table ID: {table_id}")
        print(f"  - Report Title: {report_title}")
        
        # 构建分析提示词
        base_prompt = f"""请帮我分析飞书多维表格中的业务数据，具体信息如下：
- App Token: {app_token}
- Table ID: {table_id}

请按照以下步骤进行分析：
1. 先获取表格的字段信息，了解数据结构
2. 获取表格的所有数据
3. 分析数据的关键指标、趋势变化、异常点
4. 生成一份结构化的分析报告，包含：
   - 数据概览
   - 关键指标分析
   - 趋势分析
   - 异常发现
   - 业务建议
5. **重要**：使用 send_feishu_analysis_report 工具将分析报告发送到飞书群组
   - 标题参数使用："{report_title}"
   - 根据分析结果填写 key_findings 和 recommendations

报告标题：{report_title}
报告格式：Markdown格式，要求简洁专业，突出重点

注意：
- 必须调用 send_feishu_analysis_report 工具发送报告
- 不要直接输出原始数据
- 分析要基于实际获取的数据
"""

        if custom_prompt:
            analysis_prompt = base_prompt + f"\n\n额外要求：\n{custom_prompt}"
        else:
            analysis_prompt = base_prompt
        
        # 构建Agent
        print("  - 正在初始化Agent...")
        agent = build_agent()
        
        # 发送分析任务
        print("  - 开始分析数据...")
        messages = [HumanMessage(content=analysis_prompt)]
        
        # 配置 thread_id 用于 checkpointer
        config = {
            "configurable": {
                "thread_id": f"daily_analysis_{datetime.now().strftime('%Y%m%d')}"
            }
        }
        
        response = ""
        for chunk in agent.stream({"messages": messages}, config):
            if hasattr(chunk, 'content') and chunk.content:
                if isinstance(chunk.content, str):
                    print(chunk.content, end="", flush=True)
                    response += chunk.content
        
        print(f"\n\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 分析任务完成！")
        print("报告已自动发送到飞书群组。")
        
        return True
        
    except Exception as e:
        error_msg = f"执行失败: {str(e)}"
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {error_msg}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """
    主函数
    """
    success = run_daily_analysis()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
