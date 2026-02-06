#!/usr/bin/env python3
"""
配置化数据分析报告生成器
支持通过配置文件管理多个项目
"""

import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from collections import defaultdict

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scripts_dir = os.path.join(project_root, "scripts")
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, scripts_dir)

from multi_table_processor import MultiTableDataProcessor


class ConfigurableReportGenerator:
    """配置化报告生成器"""

    def __init__(self, config_path):
        """初始化生成器"""
        self.config = self._load_config(config_path)
        self.project_id = self.config.get("project_id")
        self.project_name = self.config.get("project_name")
        self.report_config = self.config.get("report", {})
        self.feishu_config = self.config.get("feishu", {})
        self.fields_config = self.config.get("fields", {})
        self.terminology = self.config.get("terminology", {})

        # 初始化数据处理器
        app_token = self.feishu_config.get("app_token")
        self.processor = MultiTableDataProcessor(app_token)

    def _load_config(self, config_path):
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config

    def _get_currency_symbol(self):
        """获取货币符号"""
        return self.report_config.get("currency_symbol", "$")

    def _format_currency(self, value):
        """格式化货币"""
        symbol = self._get_currency_symbol()
        return f"{symbol}{value:,.2f}"

    def _format_value(self, value, is_percentage=False):
        """格式化数值"""
        if is_percentage:
            return f"{value:.2f}%"
        else:
            return f"{value:,}"

    def _format_change_with_values(self, current, previous, is_percentage=False, is_currency=False):
        """格式化变化（显示前日值和昨日值的对比）"""
        if previous == 0:
            if current == 0:
                return "0 → 0 (0, 0%)"
            prev_str = self._format_value(0, is_percentage)
            curr_str = self._format_value(current, is_percentage)
            return f"{prev_str} → {curr_str} (+{current:,}, 新增)"

        change = current - previous
        change_pct = round((change / previous) * 100, 2) if previous > 0 else 0

        # 对变化值进行四舍五入
        if isinstance(change, float):
            change = round(change, 2)

        prev_str = self._format_value(previous, is_percentage)
        curr_str = self._format_value(current, is_percentage)

        # 添加颜色标记：负数为绿色，正数为红色
        change_str = f"{change:,}"
        change_pct_str = f"{change_pct}%"

        if change > 0:
            # 正数用红色
            change_str = f'<font color="red">{change_str}</font>'
            change_pct_str = f'<font color="red">+{change_pct_str}</font>'
            return f"{prev_str} → {curr_str} ({change_str}, {change_pct_str})"
        elif change < 0:
            # 负数用绿色
            change_str = f'<font color="green">{change_str}</font>'
            change_pct_str = f'<font color="green">{change_pct_str}</font>'
            return f"{prev_str} → {curr_str} ({change_str}, {change_pct_str})"
        else:
            return f"{prev_str} → {curr_str} (0, 0%)"

    def _parse_record(self, record, table_type="base"):
        """解析单条记录（支持配置化字段名）"""
        fields_data = record.get("fields", {})

        # 解析日期
        date_value = fields_data.get("日期")
        if isinstance(date_value, (int, float)):
            date_str = datetime.fromtimestamp(date_value / 1000).strftime('%Y-%m-%d')
        else:
            return None

        # 解析分组字段（基础数据/渠道/国家）
        group_value = fields_data.get("渠道/国家") or fields_data.get("分组")
        if isinstance(group_value, list) and len(group_value) > 0:
            if isinstance(group_value[0], dict):
                group = group_value[0].get('text', 'Total')
            else:
                group = str(group_value[0])
        else:
            group = 'Total'

        # 根据配置解析字段
        # DAU
        dau_field = self.fields_config.get("dau", {}).get("aliases", ["DAU"])
        dau = 0
        for field_name in dau_field:
            dau_value = fields_data.get(field_name)
            if dau_value is not None:
                if isinstance(dau_value, (int, float)):
                    dau = int(dau_value)
                elif isinstance(dau_value, dict) and 'value' in dau_value:
                    val = dau_value['value']
                    dau = int(val[0]) if isinstance(val, list) and len(val) > 0 else int(val)
                break

        # 新增
        new_field = self.fields_config.get("new_users", {}).get("aliases", ["新增", "新增角色"])
        new_users = 0
        for field_name in new_field:
            new_value = fields_data.get(field_name)
            if new_value is not None:
                if isinstance(new_value, (int, float)):
                    new_users = int(new_value)
                elif isinstance(new_value, dict) and 'value' in new_value:
                    val = new_value['value']
                    new_users = int(val[0]) if isinstance(val, list) and len(val) > 0 else int(val)
                break

        # 收入/付费金额
        income_field = self.fields_config.get("revenue", {}).get("aliases", ["收入(美元)数字", "付费金额"])
        income = 0.0
        for field_name in income_field:
            income_value = fields_data.get(field_name)
            if income_value is not None:
                if isinstance(income_value, (int, float)):
                    income = float(income_value)
                elif isinstance(income_value, dict) and 'value' in income_value:
                    val = income_value['value']
                    income = float(val[0]) if isinstance(val, list) and len(val) > 0 else float(val)
                break

        # 付费用户/付费人数
        paid_field = self.fields_config.get("paid_users", {}).get("aliases", ["付费用户", "付费人数"])
        paid_users = 0
        for field_name in paid_field:
            paid_value = fields_data.get(field_name)
            if paid_value is not None:
                if isinstance(paid_value, (int, float)):
                    paid_users = int(paid_value)
                elif isinstance(paid_value, dict) and 'value' in paid_value:
                    val = paid_value['value']
                    paid_users = int(val[0]) if isinstance(val, list) and len(val) > 0 else int(val)
                break

        return {
            "date": date_str,
            "group": group,
            "dau": dau,
            "new_users": new_users,
            "income": income,
            "paid_users": paid_users
        }

    def _get_date_summary(self, records, date_str):
        """获取指定日期的汇总数据"""
        if not records:
            return {'dau': 0, 'new_users': 0, 'income': 0, 'paid_users': 0}

        total = {'dau': 0, 'new_users': 0, 'income': 0, 'paid_users': 0}
        for record in records:
            parsed = self._parse_record(record)
            if parsed and parsed.get('date') == date_str:
                total['dau'] += parsed.get('dau', 0)
                total['new_users'] += parsed.get('new_users', 0)
                total['income'] += parsed.get('income', 0)
                total['paid_users'] += parsed.get('paid_users', 0)

        return total

    def _get_date_groups(self, records, date_str):
        """获取指定日期的分组数据（按group字段分组）"""
        if not records:
            return {}

        groups = defaultdict(lambda: {'dau': 0, 'new_users': 0, 'income': 0, 'paid_users': 0})
        for record in records:
            parsed = self._parse_record(record)
            if parsed and parsed.get('date') == date_str:
                group = parsed.get('group', '未知')
                groups[group]['dau'] += parsed.get('dau', 0)
                groups[group]['new_users'] += parsed.get('new_users', 0)
                groups[group]['income'] += parsed.get('income', 0)
                groups[group]['paid_users'] += parsed.get('paid_users', 0)

        return dict(groups)

    def _generate_report(self):
        """生成报告"""
        print("="*80)
        print(f"开始生成 {self.project_name} 数据分析报告")
        print("="*80)

        # 获取当前日期
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        day_before_yesterday = today - timedelta(days=2)

        yesterday_str = yesterday.strftime("%Y-%m-%d")
        day_before_str = day_before_yesterday.strftime("%Y-%m-%d")

        print(f"当前日期: {today}")
        print(f"昨日: {yesterday_str}")
        print(f"前日: {day_before_str}")

        # 获取表格配置
        tables_config = self.feishu_config.get("tables", {})

        # 构造 table_configs 列表
        table_configs = [
            {"name": tables_config.get("base", {}).get("name", "基础数据总览"),
             "table_id": tables_config.get("base", {}).get("table_id"),
             "view_id": tables_config.get("base", {}).get("view_id")},
            {"name": tables_config.get("channel", {}).get("name", "渠道数据"),
             "table_id": tables_config.get("channel", {}).get("table_id"),
             "view_id": tables_config.get("channel", {}).get("view_id")},
            {"name": tables_config.get("country", {}).get("name", "媒体渠道"),
             "table_id": tables_config.get("country", {}).get("table_id"),
             "view_id": tables_config.get("country", {}).get("view_id")}
        ]

        # 获取所有数据
        print("\n获取数据...")
        base_records = self.processor.fetch_data(table_configs[0]['table_id'], table_configs[0]['view_id'])
        channel_records = self.processor.fetch_data(table_configs[1]['table_id'], table_configs[1]['view_id'])
        country_records = self.processor.fetch_data(table_configs[2]['table_id'], table_configs[2]['view_id'])

        # 检查可用日期
        from collections import Counter
        available_dates = set()
        for record in base_records[:50]:
            parsed = self.processor.parse_record(record)
            if parsed:
                available_dates.add(parsed['date'])

        if yesterday_str not in available_dates or day_before_str not in available_dates:
            print(f"\n❌ 未找到指定日期的数据！")
            print(f"最近可用日期: {sorted(list(available_dates), reverse=True)[:5]}")
            return None

        # 获取基础数据
        y_base = self._get_date_summary(base_records, yesterday_str)
        d_base = self._get_date_summary(base_records, day_before_str)

        # 计算付费率、ARPU、ARPPU
        y_dau = y_base['dau']
        y_paid = y_base['paid_users']
        y_income = y_base['income']

        d_dau = d_base['dau']
        d_paid = d_base['paid_users']
        d_income = d_base['income']

        y_paid_rate = round(y_paid / y_dau * 100, 2) if y_dau > 0 else 0
        y_arpu = round(y_income / y_dau, 2) if y_dau > 0 else 0
        y_arppu = round(y_income / y_paid, 2) if y_paid > 0 else 0

        d_paid_rate = round(d_paid / d_dau * 100, 2) if d_dau > 0 else 0
        d_arpu = round(d_income / d_dau, 2) if d_dau > 0 else 0
        d_arppu = round(d_income / d_paid, 2) if d_paid > 0 else 0

        # 获取字段显示名称
        field_names = {}
        for key, field_config in self.fields_config.items():
            field_names[key] = field_config.get("name", key)

        # 生成报告
        report_lines = []

        report_lines.append(f"**昨日（{yesterday_str}）总览数据**")
        report_lines.append(f"- DAU：{y_dau:,}")
        report_lines.append(f"- {field_names.get('new_users', '新增')}：{y_base['new_users']:,}")
        report_lines.append(f"- {field_names.get('revenue', '收入')}：{self._format_currency(y_income)}")
        report_lines.append(f"- {field_names.get('paid_users', '付费用户数')}：{y_paid:,}")
        report_lines.append(f"- 付费率：{y_paid_rate:.2f}%")
        report_lines.append(f"- {field_names.get('arpu', 'ARPU')}：{self._format_currency(y_arpu)}")
        report_lines.append(f"- {field_names.get('arppu', 'ARPPU')}：{self._format_currency(y_arppu)}")

        report_lines.append("")
        report_lines.append(f"**对照前日（{day_before_str}）变化：**")
        report_lines.append(f"- DAU：{self._format_change_with_values(y_dau, d_dau)}")
        report_lines.append(f"- {field_names.get('new_users', '新增')}：{self._format_change_with_values(y_base['new_users'], d_base['new_users'])}")
        report_lines.append(f"- {field_names.get('revenue', '收入')}：{self._format_change_with_values(y_income, d_income, is_currency=True)}")
        report_lines.append(f"- {field_names.get('paid_users', '付费用户数')}：{self._format_change_with_values(y_paid, d_paid)}")
        report_lines.append(f"- 付费率：{self._format_change_with_values(y_paid_rate, d_paid_rate, is_percentage=True)}")
        report_lines.append(f"- {field_names.get('arpu', 'ARPU')}：{self._format_change_with_values(y_arpu, d_arpu, is_currency=True)}")
        report_lines.append(f"- {field_names.get('arppu', 'ARPPU')}：{self._format_change_with_values(y_arppu, d_arppu, is_currency=True)}")

        return "\n".join(report_lines)

    def generate_and_send(self):
        """生成并发送报告"""
        # 生成报告
        report = self._generate_report()

        if report:
            # 生成报告标题
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            yesterday_str = yesterday.strftime("%Y-%m-%d")

            title_template = self.report_config.get("title_template", "{project_name} - {date} 日报")
            title = title_template.format(project_name=self.project_name, date=yesterday_str)

            # 保存到文件
            filename = f"daily_report_{self.project_id}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)

            print("\n" + "="*80)
            print(f"{self.project_name} 分析报告")
            print("="*80)
            print(report)
            print("="*80)
            print("✅ 分析完成！")
            print(f"📄 报告已保存到: {filename}")

            # 发送到飞书
            print("\n正在发送报告到飞书群组...")
            import os
            os.environ["FEISHU_WEBHOOK_URL"] = self.feishu_config.get("webhook_url")

            from daily_report_main import send_to_feishu
            send_to_feishu(f"🎮 {title}", report)
        else:
            print("❌ 报告生成失败")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="生成数据分析报告")
    parser.add_argument("--config", required=True, help="配置文件路径")
    args = parser.parse_args()

    generator = ConfigurableReportGenerator(args.config)
    generator.generate_and_send()


if __name__ == "__main__":
    main()
