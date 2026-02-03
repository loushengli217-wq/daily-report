# 每日数据分析定时任务配置指南

## 概述

本指南将帮助您配置每天自动分析飞书多维表格数据并发送报告的功能。

## 配置步骤

### 1. 配置飞书多维表格信息

首先，需要配置要分析的飞书多维表格信息：

1. 复制配置文件模板：
```bash
cp scripts/daily_analysis_config.json.example scripts/daily_analysis_config.json
```

2. 编辑配置文件 `scripts/daily_analysis_config.json`：

```json
{
  "app_token": "你的飞书多维表格App Token",
  "table_id": "你的数据表Table ID",
  "report_title": "每日数据分析报告",
  "at_all": false,
  "custom_prompt": "自定义分析要求（可选）"
}
```

**参数说明：**
- `app_token`: 飞书多维表格的App Token（必填）
  - 在飞书多维表格中，点击右上角"高级设置" -> "开发者信息"查看
- `table_id`: 数据表的Table ID（必填）
  - 在表格URL中获取，格式为：`https://.../tables/{table_id}/...`
- `report_title`: 报告标题（可选，默认："每日数据分析报告"）
- `at_all`: 是否@所有人（可选，默认：false）
- `custom_prompt`: 自定义分析要求（可选）

### 2. 配置飞书消息集成

确保飞书消息集成已配置，包含正确的 webhook URL。这需要在平台环境中配置 `integration-feishu-message` 的凭证。

### 3. 手动测试

在配置定时任务前，建议先手动测试：

```bash
# 方法1：使用启动脚本
./scripts/run_daily_analysis.sh

# 方法2：直接运行Python脚本
python scripts/daily_analysis.py
```

如果测试成功，你应该会看到：
- Agent开始分析数据
- 分析报告发送到飞书群组

## 配置定时任务

### Linux/Mac (使用 Cron)

1. 打开终端，编辑 crontab：
```bash
crontab -e
```

2. 添加定时任务（例如：每天早上9点执行）：
```bash
0 9 * * * cd /workspace/projects && ./scripts/run_daily_analysis.sh >> logs/daily_analysis.log 2>&1
```

3. 保存并退出

**Cron 表达式说明：**
```
* * * * * command
│ │ │ │ │
│ │ │ │ └─── 星期几 (0-7, 0和7都表示周日)
│ │ │ └───── 月份 (1-12)
│ │ └─────── 日期 (1-31)
│ └───────── 小时 (0-23)
└─────────── 分钟 (0-59)
```

**常见示例：**
- 每天早上9点：`0 9 * * *`
- 每天晚上6点：`0 18 * * *`
- 每周一早上9点：`0 9 * * 1`
- 每天凌晨2点：`0 2 * * *`

### Windows (使用任务计划程序)

1. 打开"任务计划程序"
2. 点击"创建基本任务"
3. 输入任务名称："每日数据分析"
4. 触发器：选择"每天"
5. 设置执行时间：例如 9:00
6. 操作：选择"启动程序"
   - 程序或脚本：`python`
   - 添加参数：`scripts/daily_analysis.py`
   - 起始于：项目目录路径
7. 完成配置

### 使用 systemd 定时器 (Linux)

1. 创建 systemd 服务文件 `/etc/systemd/system/daily-analysis.service`：
```ini
[Unit]
Description=Daily Data Analysis Service

[Service]
Type=simple
User=your_username
WorkingDirectory=/workspace/projects
ExecStart=/usr/bin/python /workspace/projects/scripts/daily_analysis.py
```

2. 创建定时器文件 `/etc/systemd/system/daily-analysis.timer`：
```ini
[Unit]
Description=Run Daily Data Analysis at 9 AM

[Timer]
OnCalendar=*-*-* 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

3. 启用定时器：
```bash
sudo systemctl enable daily-analysis.timer
sudo systemctl start daily-analysis.timer
```

## 日志管理

### 查看日志

```bash
# 查看最新的日志
tail -f logs/daily_analysis.log

# 查看今天的日志
grep "$(date '+%Y-%m-%d')" logs/daily_analysis.log
```

### 日志轮转（可选）

为了防止日志文件过大，可以配置日志轮转。创建 `/etc/logrotate.d/daily-analysis`：

```
/workspace/projects/logs/daily_analysis.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 your_username your_group
}
```

## 常见问题

### 1. 权限问题

确保脚本有执行权限：
```bash
chmod +x scripts/run_daily_analysis.sh
chmod +x scripts/daily_analysis.py
```

### 2. Python 环境问题

确保 Python 路径正确，或者使用虚拟环境：
```bash
# 使用虚拟环境
source /path/to/venv/bin/activate
python scripts/daily_analysis.py
```

### 3. 环境变量问题

如果脚本需要环境变量，确保在 crontab 中加载：
```bash
0 9 * * * source ~/.bashrc && cd /workspace/projects && ./scripts/run_daily_analysis.sh >> logs/daily_analysis.log 2>&1
```

### 4. 飞书 API 权限问题

确保：
- 飞书多维表格的访问权限已正确配置
- 集成凭证已正确设置

## 高级配置

### 动态配置日期

如果需要分析特定日期的数据，可以在 `custom_prompt` 中指定：

```json
{
  "custom_prompt": "请分析今天（2024-01-15）的数据，重点关注..."
}
```

或者修改脚本以动态获取日期：

```python
from datetime import datetime, timedelta

# 分析昨天的数据
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
prompt = f"请分析 {yesterday} 的数据..."
```

### 多个表格分析

如果需要分析多个表格，可以：

1. 创建多个配置文件：
```
scripts/daily_analysis_config_sales.json
scripts/daily_analysis_config_users.json
scripts/daily_analysis_config_traffic.json
```

2. 在脚本中循环处理：
```python
configs = [
    "scripts/daily_analysis_config_sales.json",
    "scripts/daily_analysis_config_users.json",
    "scripts/daily_analysis_config_traffic.json"
]

for config_file in configs:
    # 加载配置并执行分析
    ...
```

## 联系支持

如果遇到问题，请检查：
1. 配置文件是否正确
2. 飞书集成凭证是否有效
3. 日志文件中的错误信息
4. 网络连接是否正常
