#!/bin/bash
#
# 日报服务启动/重启脚本
# 这个脚本会停止旧服务并启动新服务
#

cd /workspace/projects

# 停止旧服务
echo "停止旧服务..."
pkill -f "daily_report_service.py" 2>/dev/null
pkill -f "multi_project_scheduler.py" 2>/dev/null
pkill -f "monitor_scheduler.py" 2>/dev/null

# 等待进程停止
sleep 2

# 创建日志目录
mkdir -p logs

# 启动新服务
echo "启动新服务..."
nohup python scripts/daily_report_service.py > logs/service_output.log 2>&1 &
NEW_PID=$!

# 等待服务启动
sleep 3

# 检查服务是否启动成功
if ps -p $NEW_PID > /dev/null 2>&1; then
    echo "✅ 服务启动成功！PID: $NEW_PID"
    echo "启动时间: $(date)" >> logs/service.log
    echo "服务日志: logs/service.log"
    echo "======================================"
    echo "下次执行时间: 明天 10:01"
    echo "======================================"
    tail -n 20 logs/service.log
else
    echo "❌ 服务启动失败！"
    exit 1
fi
