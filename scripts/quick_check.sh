#!/bin/bash
#
# 快速检查日报系统状态
#

echo "======================================"
echo "日报系统状态检查"
echo "======================================"
echo "检查时间: $(date)"
echo ""

# 检查调度器
if [ -f logs/pids.txt ]; then
    SCHEDULER_PID=$(grep "调度器 PID" logs/pids.txt | awk '{print $3}')
    MONITOR_PID=$(grep "守护脚本 PID" logs/pids.txt | awk '{print $4}')
else
    SCHEDULER_PID=$(ps aux | grep "multi_project_scheduler" | grep -v grep | awk '{print $2}')
    MONITOR_PID=$(ps aux | grep "monitor_scheduler" | grep -v grep | awk '{print $2}')
fi

echo "📅 调度器状态:"
if [ -n "$SCHEDULER_PID" ] && ps -p $SCHEDULER_PID > /dev/null 2>&1; then
    echo "  ✅ 运行中 (PID: $SCHEDULER_PID)"
else
    echo "  ❌ 未运行"
fi

echo ""
echo "🛡️  守护脚本状态:"
if [ -n "$MONITOR_PID" ] && ps -p $MONITOR_PID > /dev/null 2>&1; then
    echo "  ✅ 运行中 (PID: $MONITOR_PID)"
else
    echo "  ❌ 未运行"
fi

echo ""
echo "======================================"
echo "下次执行时间: 明天 10:01"
echo "======================================"
echo ""
echo "📄 日志文件:"
echo "  - 调度器: logs/multi_project_scheduler.log"
echo "  - 守护: logs/monitor_scheduler.log"
echo "  - 启动: logs/startup.log"
