# 日报系统配置说明

## 系统配置

### 当前使用：简化版日报 ✅

**脚本位置：** `scripts/generate_simple_report.py`

**报告格式：**
```
🎮 二重螺旋-海外 数据日报

昨日（2026-02-05）总览数据
- DAU：36,010
- 新增用户：1,332
- 总收入：$23,689.53
- 付费用户数：792
- 付费率：2.20%
- ARPU：$0.66
- ARPPU：$29.91

对照前日（2026-02-04）变化：
- DAU：37,245 → 36,010 (-1,235, -3.32%)  [绿色]
- 新增用户：1,336 → 1,332 (-4, -0.3%)  [绿色]
- 总收入：$17,432.09 → $23,689.53 (6,257.44, +35.9%)  [红色]
- 付费用户数：752 → 792 (40, +5.32%)  [红色]
- 付费率：2.02% → 2.20% (0.18, +8.91%)  [红色]
- ARPU：$0.47 → $0.66 (0.19, +40.43%)  [红色]
- ARPPU：$23.18 → $29.91 (6.73, +29.03%)  [红色]

**变化原因细拆：**
- 收入增长29%来自Steam：该渠道收入增长$1,821.16，占总收入增长的29%
- DAU下降80%来自PC官包：该渠道DAU减少921，占总DAU下降的80%
- 收入增长49%来自美国：该国家收入增长$1,813.84，占总收入增长的49%
- DAU下降45%来自日本：该国家DAU减少213，占总DAU下降的45%
```

## 调度器配置

### 执行时间
⏰ **每天上午 10:01**

### 调用的脚本
✅ `scripts/generate_simple_report.py` (简化版)

### 调度器配置文件
- 调度器脚本：`scripts/daily_report_scheduler.py`
- 启动脚本：`scripts/start_scheduler.sh`

## Webhook配置

### 目标群组
🔗 **https://open.feishu.cn/open-apis/bot/v2/hook/9d70437e-690c-4f96-8601-5b7058db0ebd**

### 配置位置
所有脚本都统一使用此Webhook：
- ✅ `scripts/generate_simple_report.py`
- ✅ `scripts/daily_report_scheduler.py`

## 手动执行

### 发送简化版日报
```bash
python scripts/generate_simple_report.py
```

### 启动调度器
```bash
bash scripts/start_scheduler.sh
```

### 停止调度器
```bash
bash scripts/stop_scheduler.sh
```

### 查看日志
```bash
tail -f logs/scheduler.log
```

## 注意事项

⚠️ **不要使用以下脚本**：
- ❌ `scripts/daily_report_main.py` (完整版日报，已废弃)

✅ **只使用**：
- ✅ `scripts/generate_simple_report.py` (简化版日报)

## 系统状态

- ✅ Webhook已配置到新群组
- ✅ 调度器已配置为调用简化版日报
- ✅ 调度时间：每天上午 10:01
- ✅ 报告格式：简化版，带颜色标记
- ✅ 标题加粗，变化原因细拆
