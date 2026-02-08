#!/bin/bash
#
# 系统状态检查脚本
#

echo "======================================"
echo "📊 日报系统状态检查"
echo "======================================"
echo "检查时间: $(date)"
echo ""

# 检查 APScheduler 服务
echo "📅 APScheduler 服务:"
if ps aux | grep -v grep | grep "daily_report_service.py" > /dev/null; then
    PID=$(ps aux | grep "daily_report_service.py" | grep -v grep | awk '{print $2}')
    ELAPSED=$(ps -p $PID -o etime= 2>/dev/null | tr -d ' ')
    echo "  ✅ 运行中 (PID: $PID, 运行时间: $ELAPSED)"
else
    echo "  ❌ 未运行"
fi

echo ""

# 检查守护脚本
echo "🛡️  守护脚本:"
if ps aux | grep -v grep | grep "service_guard.sh" > /dev/null; then
    PID=$(ps aux | grep "service_guard.sh" | grep -v grep | awk '{print $2}')
    ELAPSED=$(ps -p $PID -o etime= 2>/dev/null | tr -d ' ')
    echo "  ✅ 运行中 (PID: $PID, 运行时间: $ELAPSED)"
else
    echo "  ❌ 未运行"
fi

echo ""
echo "======================================"
echo "📅 下次执行时间: 明天 10:01"
echo "======================================"
echo ""
echo "📄 日志文件:"
echo "  - 服务日志: logs/service.log"
echo "  - 守护日志: logs/guard.log"
echo "  - 服务输出: logs/service_output.log"
echo ""
echo "🔧 管理命令:"
echo "  - 重启服务: bash scripts/restart_service.sh"
echo "  - 停止服务: pkill -f daily_report_service.py"
