#!/bin/bash
# 启动日报定时调度器（后台运行）

# 设置自定义 Webhook URL
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/5d969aa6-d165-4dc0-9165-bf20fb2a13ee"

# 创建日志目录
mkdir -p logs

# 停止已存在的调度器进程
echo "检查是否已有调度器在运行..."
if [ -f scheduler.pid ]; then
    OLD_PID=$(cat scheduler.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "发现已有调度器进程（PID: $OLD_PID），正在停止..."
        kill $OLD_PID
        sleep 2
    fi
fi

# 启动新的调度器（后台运行）
echo "启动日报定时调度器..."
nohup python -m scripts.daily_report_scheduler > logs/scheduler.log 2>&1 &

# 保存进程ID
echo $! > scheduler.pid

echo "✅ 调度器已启动（PID: $!）"
echo "📝 日志文件: logs/scheduler.log"
echo "⏰ 调度规则: 每天下午 17:30 执行"
echo "🔗 Webhook: ${FEISHU_WEBHOOK_URL:0:50}..."
echo ""
echo "查看日志: tail -f logs/scheduler.log"
echo "停止调度器: bash scripts/stop_scheduler.sh"
echo "查看进程: ps aux | grep daily_report_scheduler"
