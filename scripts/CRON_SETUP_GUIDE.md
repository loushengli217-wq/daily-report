# 本地 Cron 定时任务配置指南

## 📋 概述

本系统使用本地 cron 服务实现每天北京时间 10:05 自动生成并发送日报。

## 🚀 快速开始

### 1. 安装 Cron 任务

```bash
# 方法 1：使用提供的配置文件
crontab scripts/crontab_config

# 方法 2：手动编辑 crontab
crontab -e
# 然后添加以下内容：
# 5 10 * * * /workspace/projects/scripts/run_all_reports.sh >> /workspace/projects/logs/cron.log 2>&1
```

### 2. 验证 Cron 任务

```bash
# 查看当前用户的 cron 任务列表
crontab -l

# 查看 cron 服务状态（Linux）
systemctl status cron
# 或
systemctl status crond
```

### 3. 测试执行

```bash
# 手动执行脚本测试
bash /workspace/projects/scripts/run_all_reports.sh

# 查看日志
tail -f /workspace/projects/logs/daily_report_$(date +%Y%m%d).log
```

## 📝 Cron 任务详情

### 执行时间
- **时间**：每天 10:05
- **时区**：CST（中国标准时间）
- **表达式**：`5 10 * * *`

### 执行内容
1. 生成二重螺旋-海外日报
2. 生成 Pocket-小程序日报
3. 生成 SGame-小程序日报
4. 自动发送到飞书群组
5. 记录日志

### 日志位置
- **详细日志**：`logs/daily_report_YYYYMMDD.log`
- **Cron 日志**：`logs/cron.log`

## 🔧 常用管理命令

### 查看和管理 Cron 任务

```bash
# 查看所有 cron 任务
crontab -l

# 编辑 cron 任务
crontab -e

# 删除所有 cron 任务
crontab -r

# 备份 cron 任务
crontab -l > cron_backup.txt

# 恢复 cron 任务
crontab cron_backup.txt
```

### 查看 Cron 日志

```bash
# 查看今天的日志
tail -n 50 /workspace/projects/logs/daily_report_$(date +%Y%m%d).log

# 实时监控日志
tail -f /workspace/projects/logs/cron.log

# 查看所有日志文件
ls -lh /workspace/projects/logs/
```

### 手动执行

```bash
# 执行所有项目的日报
bash /workspace/projects/scripts/run_all_reports.sh

# 执行单个项目的日报
python scripts/generate_report.py --config scripts/projects/project_ershong.json
python scripts/generate_report.py --config scripts/projects/project_pocket.json
python scripts/generate_report.py --config scripts/projects/project_sgame.json
```

## 🔍 故障排查

### 问题 1：Cron 任务未执行

**检查步骤**：
```bash
# 1. 检查 cron 服务是否运行
systemctl status cron

# 2. 查看 cron 日志
grep CRON /var/log/syslog | tail -20

# 3. 手动执行脚本，看是否有错误
bash /workspace/projects/scripts/run_all_reports.sh

# 4. 查看脚本权限
ls -l /workspace/projects/scripts/run_all_reports.sh
# 应该显示：-rwxr-xr-x (有执行权限)
```

**解决方案**：
```bash
# 如果 cron 服务未运行，启动它
sudo systemctl start cron
sudo systemctl enable cron

# 如果脚本没有执行权限
chmod +x /workspace/projects/scripts/run_all_reports.sh
```

### 问题 2：Python 路径问题

**症状**：cron 日志显示 `python: command not found`

**解决方案**：
```bash
# 找到 python 的完整路径
which python

# 修改 run_all_reports.sh，将 python 改为完整路径
# 例如：/usr/bin/python3 scripts/generate_report.py ...
```

### 问题 3：环境变量问题

**症状**：手动执行正常，但 cron 执行失败

**解决方案**：
```bash
# 方法 1：在 run_all_reports.sh 开头添加环境变量
#!/bin/bash
export PATH="/usr/local/bin:/usr/bin:/bin"
export HOME="/workspace/projects"

# 方法 2：使用完整路径
/usr/bin/python3 /workspace/projects/scripts/generate_report.py ...
```

## 📊 监控和维护

### 日志清理（每月执行一次）

```bash
# 删除 30 天前的日志
find /workspace/projects/logs/ -name "daily_report_*.log" -mtime +30 -delete

# 保留最近 10 个 cron 日志
ls -t /workspace/projects/logs/cron.log* | tail -n +11 | xargs -r rm
```

### 性能监控

```bash
# 查看 cron 执行耗时
tail -20 /workspace/projects/logs/daily_report_$(date +%Y%m%d).log | grep "时间"
```

## ⚙️ 高级配置

### 修改执行时间

如果需要在其他时间执行，编辑 crontab：

```bash
crontab -e

# 修改时间表达式
# 例如：每天 8:30 执行
30 8 * * * /workspace/projects/scripts/run_all_reports.sh >> /workspace/projects/logs/cron.log 2>&1

# 每周一早上 9:00 执行
0 9 * * 1 /workspace/projects/scripts/run_all_reports.sh >> /workspace/projects/logs/cron.log 2>&1

# 工作日（周一到周五）10:05 执行
5 10 * * 1-5 /workspace/projects/scripts/run_all_reports.sh >> /workspace/projects/logs/cron.log 2>&1
```

### 添加邮件通知

在 cron 任务中添加邮件通知：

```bash
5 10 * * * /workspace/projects/scripts/run_all_reports.sh 2>&1 | mail -s "日报生成报告" your_email@example.com
```

## 📞 获取帮助

如果遇到问题：
1. 查看日志：`tail -f /workspace/projects/logs/cron.log`
2. 检查 cron 服务：`systemctl status cron`
3. 手动测试：`bash /workspace/projects/scripts/run_all_reports.sh`
4. 查看系统日志：`grep CRON /var/log/syslog`

---

## ✅ 安装确认清单

- [ ] 已执行 `crontab scripts/crontab_config`
- [ ] 已执行 `crontab -l` 确认任务已添加
- [ ] 已执行 `bash scripts/run_all_reports.sh` 测试脚本
- [ ] 已查看日志确认脚本运行正常
- [ ] 已确认电脑每天 10:05 都会开机

**安装完成！明天 10:05 自动生成日报！** 🎉
