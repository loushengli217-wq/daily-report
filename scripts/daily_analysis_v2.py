"""
每日数据分析脚本（重构版）
在代码层面处理数据，然后把处理好的数据交给AI分析
"""
import os
import sys
import json
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from agents.agent import build_agent
from langchain_core.messages import HumanMessage
from data_processor import DataProcessor


def load_config():
    """加载配置文件"""
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, "scripts/daily_analysis_config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_daily_analysis():
    """执行每日数据分析任务"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行每日数据分析任务...")

    try:
        # ========== 日期校验 ==========
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')

        print(f"\n{'='*80}")
        print(f"📅 日期校验")
        print(f"{'='*80}")
        print(f"  今天: {today_str}")
        print(f"  昨天: {yesterday_str}")
        print(f"{'='*80}\n")

        # 加载配置
        config = load_config()
        app_token = config.get("app_token")
        table_id = config.get("table_id")
        base_report_title = config.get("report_title", "每日数据分析报告")
        report_title = f"{base_report_title} - {yesterday_str}"
        custom_prompt = config.get("custom_prompt", "")

        print(f"  - App Token: {app_token}")
        print(f"  - Table ID: {table_id}")
        print(f"  - Report Title: {report_title}\n")

        # ========== 数据处理（代码层面）==========
        print(f"{'='*80}")
        print(f"🔧 数据处理")
        print(f"{'='*80}")

        processor = DataProcessor(app_token, table_id)
        processed_data = processor.process_data(target_date=yesterday_str, days=7)

        if "error" in processed_data:
            print(f"  ❌ {processed_data['error']}")
            return False

        formatted_data = processor.format_for_ai(processed_data)

        print(f"  ✅ 数据处理完成")
        print(f"\n{formatted_data}")
        print(f"\n{'='*80}\n")

        # ========== AI分析报告 ==========
        print(f"{'='*80}")
        print(f"🤖 AI分析")
        print(f"{'='*80}\n")

        # 构建提示词
        prompt = f"""你是一个专业的数据分析师。

【已处理的数据】（数据已由代码层面处理完成，100%准确）
{formatted_data}

【任务】
基于上述数据，生成一份专业的分析报告。

【报告要求】
1. 报告格式：Markdown
2. 包含以下部分：
   - 数据概览（说明数据范围和分析日期）
   - 关键指标分析
   - 趋势分析（分析DAU、新增、收入的变化趋势）
   - 异常发现（找出数据中的异常点）
   - 业务建议（基于分析结果给出建议）

3. 重要：
   - 所有数据已在上面给出，直接使用即可
   - 不要编造任何数据
   - 报告要简洁专业

【报告标题】
{report_title}

请生成报告并发送。"""

        # 构建Agent
        print("  - 正在初始化Agent...")
        agent = build_agent()

        # 发送分析任务
        print("  - 开始分析...\n")
        messages = [HumanMessage(content=prompt)]

        # 配置 thread_id
        agent_config = {
            "configurable": {
                "thread_id": f"daily_analysis_{datetime.now().strftime('%Y%m%d')}"
            }
        }

        response = ""
        for chunk in agent.stream({"messages": messages}, config=agent_config):
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
    """主函数"""
    success = run_daily_analysis()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
