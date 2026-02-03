# 游戏数据分析 Agent

## 概述
基于飞书多维表格的专业游戏数据分析 Agent，支持多维度数据分析、趋势对比、异常检测，并通过飞书机器人发送报告。

## 功能特性
- ✅ **多表格支持**：同时分析游戏基础数据、渠道数据、国家数据
- ✅ **真实数据**：严格使用飞书多维表格的实际数据，拒绝编造
- ✅ **趋势分析**：识别 DAU、新增用户、收入的变化趋势
- ✅ **异常检测**：自动发现数据异常波动并标注
- ✅ **专业报告**：生成 Markdown 格式的专业分析报告
- ✅ **飞书集成**：支持通过飞书机器人发送报告

## 数据源配置

### 游戏基础数据
- **表格ID**: `tblM5x1uyjwffoBq`
- **视图ID**: `vew8YRRC3u`
- **分析范围**: 最近 7 天
- **分析内容**: 整体 DAU、新增用户、收入趋势

### 游戏渠道数据
- **表格ID**: `tblBiiYpOdRGonPy`
- **视图ID**: `vew8YRRC3u`
- **分析范围**: 最近 35 天
- **分析内容**: 各渠道（Steam、PC官包、安卓、IOS、EPIC）的数据对比

### 游戏主要国家数据
- **表格ID**: `tblgx4cY7LvncsiJ`
- **视图ID**: `vew8YRRC3u`
- **分析范围**: 最近 28 天
- **分析内容**: 各国家（美国、韩国、日本、其他）的数据对比

## 快速开始

### 1. 运行多表格数据分析
```bash
python scripts/daily_analysis_multi.py
```

### 2. 测试多表格数据获取
```bash
python scripts/multi_table_processor.py
```

### 3. 手动发送飞书消息
```bash
python scripts/test_feishu_message.py "测试消息"
```

## 项目结构
```
.
├── config/
│   └── agent_llm_config.json          # Agent 配置
├── src/
│   ├── agents/
│   │   └── agent.py                   # Agent 核心逻辑
│   ├── tools/
│   │   ├── feishu_bitable_tool.py    # 飞书多维表格工具
│   │   └── feishu_message_tool.py    # 飞书消息工具
│   └── storage/
│       └── memory/
│           └── memory_saver.py        # 记忆存储
└── scripts/
    ├── multi_table_processor.py       # 多表格数据处理器
    ├── daily_analysis_multi.py        # 多表格每日分析
    └── list_tables.py                 # 列出所有表格
```

## 核心组件

### MultiTableDataProcessor
多表格数据处理器，负责从飞书多维表格获取数据并格式化。

**关键方法**:
- `process_table_data(table_id, view_id, last_n)`: 处理单个表格数据
- `format_multi_table_data(results, table_configs)`: 格式化多个表格的数据

### Agent
数据分析 Agent，使用 DeepSeek-V3 模型生成专业分析报告。

**配置**:
- 模型: `deepseek-v3-2-251201`
- 温度: `0.1`（确保数据准确性）
- 无工具配置（数据通过参数提供）

### 飞书集成
- **飞书多维表格**: `integration-feishu-base`
- **飞书消息**: `integration-feishu-message`

## 分析报告结构

```markdown
## 📊 游戏数据分析报告
**数据时间**: [YYYY-MM-DD] 至 [YYYY-MM-DD]

### 1. 📈 基础数据趋势
- DAU趋势分析
- 新增用户趋势分析
- 收入趋势分析
- 付费率变化分析

### 2. 🎯 渠道数据对比
- 各渠道DAU对比
- 各渠道收入贡献
- 付费率差异分析

### 3. 🌍 主要国家数据对比
- 各国家DAU分布
- 各国家收入贡献
- 市场潜力评估

### 4. 📋 关键发现
- 列出3-5个最重要的发现

### 5. 💡 优化建议
- 基于数据的具体建议
```

## 数据准确性保证

1. **真实数据源**: 所有数据来自飞书多维表格，拒绝编造
2. **代码层处理**: 数据解析和处理在代码层面完成，避免模型幻觉
3. **低温度设置**: 使用 temperature=0.1 减少模型不确定性
4. **明确时间范围**: 报告必须明确标注数据分析的时间范围
5. **数据验证**: 添加数据验证流程，确保只使用实际存在的数据

## 定时任务配置

### 方式 1: 使用 crontab
```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天早上9点）
0 9 * * * cd /workspace/projects && python scripts/daily_analysis_multi.py >> logs/daily_analysis.log 2>&1
```

### 方式 2: 使用 shell 脚本
```bash
# 运行分析脚本
bash scripts/run_daily_analysis.sh
```

## 常见问题

### Q1: 如何查看所有可用的表格？
```bash
python scripts/list_tables.py
```

### Q2: 如何修改分析的数据范围？
编辑 `scripts/daily_analysis_multi.py` 中的 `table_configs` 列表，修改 `last_n` 参数。

### Q3: 如何修改飞书机器人 webhook？
修改环境变量或配置文件中的 webhook URL。

### Q4: 为什么数据取值很准确？
- 使用代码层处理数据，避免模型幻觉
- 使用 DeepSeek-V3 模型，降低温度设置
- 添加数据验证流程
- 明确的时间范围标注

## 技术栈
- Python 3.12
- LangChain 1.0
- LangGraph
- DeepSeek-V3 (deepseek-v3-2-251201)
- 飞书多维表格集成
- 飞书消息集成

## 更新日志
### v2.0 (2026-02-03)
- ✨ 新增多表格支持：游戏基础数据、渠道数据、国家数据
- ✨ 优化数据准确性：代码层处理，避免模型幻觉
- ✨ 改进报告结构：更专业的分析维度
- 🔧 切换模型：从 doubao-seed 切换到 DeepSeek-V3
- 🔧 降低温度：从 0.7 降至 0.1

### v1.0 (初始版本)
- ✅ 基础数据分析功能
- ✅ 飞书多维表格集成
- ✅ 飞书消息推送
- ✅ AI 分析报告生成
