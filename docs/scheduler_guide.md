# 日报定时调度器使用说明

## 快速开始

### 方式1：立即发送一次日报
```bash
cd /workspace/projects
python scripts/daily_report_main.py
```

### 方式2：启动定时调度器（每天上午10点自动发送）

**启动调度器：**
```bash
cd /workspace/projects
bash scripts/start_scheduler.sh
```

**启动后会显示：**
```
✅ 调度器已启动（PID: 12345）
📝 日志文件: logs/scheduler.log
⏰ 调度规则: 每天上午 10:00 执行

查看日志: tail -f logs/scheduler.log
停止调度器: bash scripts/stop_scheduler.sh
查看进程: ps aux | grep daily_report_scheduler
```

**停止调度器：**
```bash
bash scripts/stop_scheduler.sh
```

**查看日志：**
```bash
tail -f logs/scheduler.log
```

---

## 常见问题

### Q1：启动后可以关闭页面吗？
**A：** 可以！调度器是后台运行的，关闭页面/终端不会影响它。

### Q2：如何确认调度器是否在运行？
```bash
# 查看进程
ps aux | grep daily_report_scheduler

# 查看日志
tail -n 20 logs/scheduler.log
```

### Q3：如何修改执行时间？
编辑 `scripts/daily_report_scheduler.py`，修改这一行：
```python
# 改成你想要的时间，比如 "09:00" 或 "14:30"
schedule.every().day.at("10:00").do(run_report)
```

修改后需要重启调度器：
```bash
bash scripts/stop_scheduler.sh
bash scripts/start_scheduler.sh
```

### Q4：如何手动触发一次日报？
```bash
python scripts/daily_report_main.py
```

### Q5：服务器重启后怎么办？
需要重新启动调度器。如果希望开机自动启动，可以将启动命令添加到系统的启动脚本中。

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `scripts/daily_report_main.py` | 日报主程序（生成报告并发送） |
| `scripts/daily_report_scheduler.py` | 定时调度器（每天10点自动执行） |
| `scripts/start_scheduler.sh` | 启动脚本 |
| `scripts/stop_scheduler.sh` | 停止脚本 |
| `logs/scheduler.log` | 调度器日志 |
| `scheduler.pid` | 进程ID文件 |
| `daily_report.md` | 生成的日报文件 |

---

## 技术说明

- 使用 Python 的 `schedule` 库实现定时任务
- 使用 `nohup` 实现后台运行
- 每分钟检查一次是否到执行时间
- 支持优雅停止和日志记录

---

## 注意事项

1. 确保飞书 webhook 配置正确
2. 确保飞书多维表格有最新数据
3. 定期检查日志文件大小
4. 如需修改报告内容，编辑 `scripts/generate_daily_report.py`
