#!/bin/bash

# 每日数据分析启动脚本
# 使用方法: ./scripts/run_daily_analysis.sh

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 切换到项目目录
cd "$PROJECT_DIR"

# 加载环境变量
if [ -f "$SCRIPT_DIR/load_env.sh" ]; then
    source "$SCRIPT_DIR/load_env.sh"
fi

# 运行分析脚本
echo "=========================================="
echo "  开始执行每日数据分析任务"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo ""

python "$SCRIPT_DIR/daily_analysis.py"

# 检查执行结果
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "  任务执行成功！"
    echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="
    exit 0
else
    echo ""
    echo "=========================================="
    echo "  任务执行失败！"
    echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="
    exit 1
fi
