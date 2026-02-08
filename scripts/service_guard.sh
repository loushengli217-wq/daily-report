#!/bin/bash
#
# 服务守护脚本（终极版）
# 这个脚本会持续运行，如果服务挂了会自动重启
#

cd /workspace/projects

# 记录启动时间
echo "$(date) - 守护脚本启动" >> logs/guard.log

while true; do
    # 检查服务是否在运行
    if ps aux | grep -v grep | grep "daily_report_service.py" > /dev/null; then
        # 服务正在运行，记录心跳
        echo "$(date) - 💓 服务运行正常" >> logs/guard.log
    else
        # 服务挂了，需要重启
        echo "$(date) - ⚠️  服务停止，正在重启..." >> logs/guard.log

        # 停止所有相关进程
        pkill -f "daily_report_service.py" 2>/dev/null
        pkill -f "multi_project_scheduler.py" 2>/dev/null
        pkill -f "monitor_scheduler.py" 2>/dev/null

        # 等待清理
        sleep 2

        # 启动服务
        nohup python scripts/daily_report_service.py > logs/service_output.log 2>&1 &

        # 等待服务启动
        sleep 5

        # 检查是否启动成功
        if ps aux | grep -v grep | grep "daily_report_service.py" > /dev/null; then
            NEW_PID=$(ps aux | grep "daily_report_service.py" | grep -v grep | awk '{print $2}')
            echo "$(date) - ✅ 服务重启成功，PID: $NEW_PID" >> logs/guard.log
        else
            echo "$(date) - ❌ 服务重启失败" >> logs/guard.log
        fi
    fi

    # 每 30 秒检查一次
    sleep 30
done
