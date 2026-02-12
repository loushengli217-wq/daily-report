#!/bin/bash
# 批量生成所有项目的日报

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 日志文件路径
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/daily_report_$(date +%Y%m%d).log"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 记录开始时间
echo "========================================" >> "$LOG_FILE"
echo "开始生成所有项目的日报" >> "$LOG_FILE"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "项目目录: $PROJECT_ROOT" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 进入项目目录
cd "$PROJECT_ROOT" || exit 1

# 执行顺序：二重螺旋-海外 -> Pocket-小程序 -> SGame-小程序
echo "" >> "$LOG_FILE"
echo "【1/3】生成二重螺旋-海外日报..." >> "$LOG_FILE"
python scripts/generate_report.py --config scripts/projects/project_ershong.json >> "$LOG_FILE" 2>&1

echo "" >> "$LOG_FILE"
echo "【2/3】生成 Pocket-小程序日报..." >> "$LOG_FILE"
python scripts/generate_report.py --config scripts/projects/project_pocket.json >> "$LOG_FILE" 2>&1

echo "" >> "$LOG_FILE"
echo "【3/3】生成 SGame-小程序日报..." >> "$LOG_FILE"
python scripts/generate_report.py --config scripts/projects/project_sgame.json >> "$LOG_FILE" 2>&1

# 记录结束时间
echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "所有日报生成完成" >> "$LOG_FILE"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 清理临时文件
rm -f "$PROJECT_ROOT"/daily_report_*.md 2>/dev/null

echo "✅ 日报生成完成，日志保存在: $LOG_FILE"
