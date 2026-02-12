@echo off
chcp 65001 >nul
title 每日报告生成器

echo ========================================
echo    每日报告生成器
echo ========================================
echo.
echo [1/3] 生成二重螺旋-海外日报...
python scripts\generate_report.py --config scripts\projects\project_ershong.json

echo.
echo [2/3] 生成 Pocket-小程序日报...
python scripts\generate_report.py --config scripts\projects\project_pocket.json

echo.
echo [3/3] 生成 SGame-小程序日报...
python scripts\generate_report.py --config scripts\projects\project_sgame.json

echo.
echo ========================================
echo    完成！
echo ========================================
echo.
echo 按任意键关闭窗口...
pause >nul
