#!/bin/bash
#
# 启动日报系统服务（容器环境适配版）
# 在容器环境中保持调度器持续运行
#

cd /workspace/projects

# 创建日志目录
mkdir -p logs

# 记录启动时间
echo "$(date) - 启动日报系统" >> logs/startup.log

# 启动调度器（使用后台进程）
nohup python scripts/multi_project_scheduler.py > logs/scheduler_output.log 2>&1 &
SCHEDULER_PID=$!
echo "调度器已启动，PID: $SCHEDULER_PID"

# 等待调度器启动
sleep 3

# 检查调度器是否在运行
if ps -p $SCHEDULER_PID > /dev/null 2>&1; then
    echo "$(date) - 调度器启动成功，PID: $SCHEDULER_PID" >> logs/startup.log
else
    echo "$(date) - 调度器启动失败" >> logs/startup.log
    exit 1
fi

# 启动守护脚本
nohup python scripts/monitor_scheduler.py > logs/monitor_output.log 2>&1 &
MONITOR_PID=$!
echo "守护脚本已启动，PID: $MONITOR_PID"

# 记录所有 PID
echo "调度器 PID: $SCHEDULER_PID" > logs/pids.txt
echo "守护脚本 PID: $MONITOR_PID" >> logs/pids.txt

echo "$(date) - 所有服务已启动" >> logs/startup.log
echo "======================================"
echo "调度器 PID: $SCHEDULER_PID"
echo "守护脚本 PID: $MONITOR_PID"
echo "======================================"
echo "服务已启动，将在每天 10:01 发送日报"
echo "日志位置: logs/"
