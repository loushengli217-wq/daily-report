"""
每日数据分析脚本
自动从飞书多维表格获取数据，分析后发送报告到飞书群组
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
from tools.feishu_bitable_tool import FeishuBitableClient, get_access_token


def validate_and_get_data_info(app_token, table_id, target_date):
    """验证数据并返回可用的日期范围"""
    client = FeishuBitableClient()
    token = get_access_token()

    # 获取数据
    search_response = client.search_records(
        token,
        app_token,
        table_id,
        sort=[{"field_name": "日期", "desc": True}],
        page_size=200
    )

    all_records = search_response.get("data", {}).get("items", [])

    # 提取所有日期
    all_dates = set()
    for record in all_records:
        fields_data = record.get("fields", {})
        date_value = fields_data.get("日期")
        if isinstance(date_value, (int, float)):
            date_str = datetime.fromtimestamp(date_value / 1000).strftime('%Y-%m-%d')
            all_dates.add(date_str)

    sorted_dates = sorted(all_dates)

    if not sorted_dates:
        return {
            "has_data": False,
            "message": "表格中没有数据"
        }

    # 检查目标日期
    target_exists = target_date in sorted_dates

    # 最近7天可用日期
    recent_7_days = sorted_dates[-7:] if len(sorted_dates) >= 7 else sorted_dates

    return {
        "has_data": True,
        "data_range": {
            "start": sorted_dates[0],
            "end": sorted_dates[-1],
            "total_days": len(sorted_dates)
        },
        "target_date_exists": target_exists,
        "target_date": target_date,
        "closest_date": sorted_dates[-1] if not target_exists else target_date,
        "recent_7_days": recent_7_days,
        "all_dates": sorted_dates
    }


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
        # ========== 日期校验流程 ==========
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        yesterday_str = yesterday.strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')

        print(f"\n{'='*80}")
        print(f"📅 日期校验信息")
        print(f"{'='*80}")
        print(f"  今天: {today_str}")
        print(f"  昨天: {yesterday_str}")
        print(f"{'='*80}\n")

        print(f"  ✅ 将分析昨日（{yesterday_str}）的数据")

        # 加载配置
        config = load_config()
        app_token = config.get("app_token")
        table_id = config.get("table_id")
        # 在报告标题中添加日期
        base_report_title = config.get("report_title", "每日数据分析报告")
        report_title = f"{base_report_title} - {yesterday_str}"
        at_all = config.get("at_all", False)
        custom_prompt = config.get("custom_prompt", "")

        if not app_token or not table_id:
            raise ValueError("配置文件中缺少 app_token 或 table_id")

        print(f"\n  - App Token: {app_token}")
        print(f"  - Table ID: {table_id}")
        print(f"  - Report Title: {report_title}")

        # ========== 数据验证 ==========
        print(f"\n{'='*80}")
        print(f"🔍 数据验证")
        print(f"{'='*80}")

        data_info = validate_and_get_data_info(app_token, table_id, yesterday_str)

        if not data_info["has_data"]:
            print(f"  ❌ {data_info['message']}")
            return False

        dr = data_info["data_range"]
        print(f"  ✅ 数据验证通过")
        print(f"  📅 数据范围: {dr['start']} 至 {dr['end']}（共{dr['total_days']}天）")

        if data_info["target_date_exists"]:
            print(f"  ✅ 目标日期 {yesterday_str} 数据存在")
            analysis_date = yesterday_str
        else:
            print(f"  ⚠️  目标日期 {yesterday_str} 数据不存在")
            print(f"  📅 将使用最新可用日期: {data_info['closest_date']}")
            analysis_date = data_info['closest_date']

        print(f"  📊 最近7天可用日期: {', '.join(data_info['recent_7_days'])}")
        print(f"{'='*80}\n")
        # 在报告标题中添加日期
        base_report_title = config.get("report_title", "每日数据分析报告")
        report_title = f"{base_report_title} - {yesterday_str}"
        at_all = config.get("at_all", False)
        custom_prompt = config.get("custom_prompt", "")

        if not app_token or not table_id:
            raise ValueError("配置文件中缺少 app_token 或 table_id")

        print(f"\n  - App Token: {app_token}")
        print(f"  - Table ID: {table_id}")
        print(f"  - Report Title: {report_title}")

        # 构建分析提示词
        base_prompt = f"""请帮我分析飞书多维表格中的业务数据。

【数据源信息】
- App Token: {app_token}
- Table ID: {table_id}
- 数据实际范围: {dr['start']} 至 {dr['end']}
- 目标分析日期: {yesterday_str}
- 实际可用日期: {analysis_date}

【重要数据约束】
- 你的数据只包含以下日期: {', '.join(data_info['recent_7_days'])}
- 最近7天可用日期: {', '.join(data_info['recent_7_days'])}
- **绝对禁止**使用不存在的日期（如2026-05-09、2026-02-02等）
- 如果数据中没有某个日期，必须明确说明"该日期无数据"

请按照以下步骤进行分析：
1. 先获取表格的字段信息，了解数据结构
2. 获取表格的最近数据（获取最近200条，按日期降序排序），不要使用filter参数
3. **数据验证**：确认数据范围是 {dr['start']} 至 {dr['end']}
4. **重点分析**：分析日期 {analysis_date} 的各渠道数据（DAU、新增、收入等）
5. **趋势对比**：对比过去几天的数据（{', '.join(data_info['recent_7_days'])}），识别趋势变化和异常点
6. 生成一份结构化的分析报告，包含：
   - 数据概览（必须明确说明实际数据范围：{dr['start']} 至 {dr['end']}）
   - 关键指标分析（{analysis_date}的各渠道数据）
   - 趋势分析（过去7天：{', '.join(data_info['recent_7_days'])}）
   - 异常发现（异常数据点）
   - 业务建议
7. **重要**：使用 send_feishu_analysis_report 工具将分析报告发送到飞书群组
   - 标题参数使用："{report_title}"
   - 根据分析结果填写 key_findings 和 recommendations

报告标题：{report_title}
报告格式：Markdown格式，要求简洁专业，突出重点

【严格执行】
- 必须调用 send_feishu_analysis_report 工具发送报告
- 不要使用filter参数，直接获取数据后在本地筛选
- 所有数据必须基于实际获取的记录，严禁编造
- 只能使用存在的日期：{', '.join(data_info['all_dates'])}
- 在报告中必须明确说明：实际数据范围是 {dr['start']} 至 {dr['end']}
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
    """
    主函数
    """
    success = run_daily_analysis()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
