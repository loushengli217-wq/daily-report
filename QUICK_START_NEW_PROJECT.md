# 新项目配置检查清单

## ✅ 填写配置文件前，先准备这些信息

- [ ] 项目名称（中文）
- [ ] 项目唯一ID（英文，如：new_miniprogram）
- [ ] 飞书多维表格的 app_token
- [ ] 主表格的 table_id
- [ ] 主表格的 view_id（可选）
- [ ] 飞书群组的 Webhook URL
- [ ] 货币符号（¥ 或 $）
- [ ] 是否包含变化原因分析（是/否）

## ✅ 填写配置文件（scripts/projects/project_template.json）

### 必填项
- [ ] project_id（项目唯一ID）
- [ ] project_name（项目名称）
- [ ] feishu.app_token
- [ ] feishu.table_id
- [ ] feishu.tables.base.table_id
- [ ] feishu.webhook_url
- [ ] report.currency_symbol
- [ ] report.include_reason_analysis

### 可选项
- [ ] feishu.tables.base.view_id
- [ ] feishu.tables.channel.table_id（如果有渠道表格）
- [ ] feishu.tables.channel.view_id
- [ ] feishu.tables.country.table_id（如果有地区表格）
- [ ] feishu.tables.country.view_id

## ✅ 完成后

1. [ ] 将文件重命名为 `project_你的项目ID.json`
2. [ ] 把填写好的配置内容发给我
3. [ ] 我帮你创建并测试

---

## 🚀 快速开始

1. 打开 `scripts/projects/project_template.json`
2. 按照【】标注的位置填写信息
3. 填写完成后发给我

就是这么简单！
