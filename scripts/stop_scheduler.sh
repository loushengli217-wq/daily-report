#!/bin/bash
# 停止日报定时调度器

if [ ! -f scheduler.pid ]; then
    echo "❌ 未找到调度器进程文件"
    exit 1
fi

PID=$(cat scheduler.pid)

if ps -p $PID > /dev/null 2>&1; then
    echo "正在停止调度器（PID: $PID）..."
    kill $PID
    sleep 2

    # 检查是否已停止
    if ps -p $PID > /dev/null 2>&1; then
        echo "强制停止调度器..."
        kill -9 $PID
    fi

    echo "✅ 调度器已停止"
    rm scheduler.pid
else
    echo "❌ 调度器未运行（PID: $PID）"
    rm scheduler.pid
fi
