# 新项目配置填写指南

## 📋 配置文件位置
`scripts/projects/project_template.json`

## 🔧 需要填写的字段

### 1. 项目基本信息

```json
"project_id": "new_miniprogram_id",
```
- **说明**: 项目的唯一标识（英文，不要有特殊字符）
- **示例**: `new_game_miniprogram`, `project_abc`
- **注意**: 不要和其他项目重复

```json
"project_name": "新小程序 - 项目名称",
```
- **说明**: 项目显示名称
- **示例**: "口袋妖怪-小程序", "新游戏-小程序"

```json
"description": "项目描述",
```
- **说明**: 项目描述
- **示例**: "RPG类游戏", "休闲游戏"

---

### 2. 报告配置

```json
"schedule_time": "10:05",
```
- **说明**: 每天发送时间
- **固定值**: `10:05`（和 GitHub Actions 配置一致）

```json
"currency_symbol": "¥",
```
- **说明**: 货币符号
- **选项**: `¥`（人民币）或 `$`（美元）

```json
"include_reason_analysis": false,
```
- **说明**: 是否包含"变化原因细拆"
- **选项**: `true`（包含）或 `false`（不包含）

---

### 3. 飞书多维表格配置 ⚠️ 重点

```json
"app_token": "【在这里填写飞书多维表格的 app_token】",
```
- **如何获取**: 打开飞书多维表格，浏览器地址栏中找到
- **示例**: `TmSCbqGjsaMy0csCmiocXsKjnJg`
- **URL格式**: `https://bytedance.feishu.cn/base/TmSCbqGjsaMy0csCmiocXsKjnJg`

```json
"table_id": "【在这里填写主表格的 table_id】",
```
- **如何获取**: URL中的 table 参数
- **示例**: `tblFh4Y0RMyd198t`
- **URL格式**: `https://bytedance.feishu.cn/base/...?table=tblFh4Y0RMyd198t`

```json
"view_id": "【在这里填写主表格的 view_id】",
```
- **如何获取**: URL中的 view 参数（可选）
- **示例**: `vewmziHJQQ`
- **URL格式**: `https://bytedance.feishu.cn/base/...?view=vewmziHJQQ`

```json
"webhook_url": "【在这里填写飞书群组的 Webhook URL】",
```
- **如何获取**: 在飞书群组中添加机器人，获取 Webhook URL
- **示例**: `https://open.feishu.cn/open-apis/bot/v2/hook/002e0a6c-6465-4faa-bce4-e3311406a876`

---

### 4. 表格配置

#### 主表格（必须）
```json
"base": {
  "name": "基础数据总览",
  "table_id": "【在这里填写主表格的 table_id】",
  "view_id": "【在这里填写主表格的 view_id】"
}
```

#### 渠道表格（可选）
```json
"channel": {
  "name": "基础数据-渠道",
  "table_id": "【在这里填写渠道表格的 table_id】",
  "view_id": "【在这里填写渠道表格的 view_id】"
}
```
- **如果没有渠道表格**: 可以删除这一段，或者 table_id 填空

#### 地区表格（可选）
```json
"country": {
  "name": "基础数据-媒体渠道",
  "table_id": "【在这里填写地区表格的 table_id】",
  "view_id": "【在这里填写地区表格的 view_id】"
}
```
- **如果没有地区表格**: 可以删除这一段，或者 table_id 填空

---

### 5. 字段映射（通常不需要修改）

这一部分定义了数据字段的名称和别名，通常不需要修改，除非你的表格字段名称和示例不同。

如果你的表格字段名称不同，需要修改 `aliases` 中的别名。

---

### 6. 术语配置（可选）

```json
"industry_terms": ["小程序", "游戏", "新游戏"],
```
- **说明**: 行业术语，用于生成报告时使用
- **示例**: ["小程序", "游戏", "RPG"]

```json
"increase_reasons": ["活动推广", "自然增长", "版本更新", "节假日效应"],
```
- **说明**: 数据增长的可能原因
- **用于**: 生成"变化原因细拆"部分

```json
"decrease_reasons": ["周末效应", "服务器问题", "竞品影响", "版本问题"],
```
- **说明**: 数据下降的可能原因
- **用于**: 生成"变化原因细拆"部分

---

## 🎯 填写完成后的步骤

1. **重命名文件**:
   - 将 `project_template.json` 改为 `project_你的项目ID.json`
   - 例如: `project_new_miniprogram.json`

2. **提交给我**:
   - 把填写好的配置文件内容发给我
   - 我会帮你创建并测试

---

## 💡 示例

假设你的项目信息：
- 项目名称: "超级游戏-小程序"
- 飞书 app_token: `AbCdEfGhIjKlMnOpQrStUvWxYz`
- 主表格 table_id: `tbl1234567890`
- 主表格 view_id: `vewABCDEFGH`
- Webhook URL: `https://open.feishu.cn/open-apis/bot/v2/hook/12345678-90ab-cdef-1234-567890abcdef`

填写后应该是：
```json
{
  "project_id": "super_game_miniprogram",
  "project_name": "超级游戏-小程序",
  "description": "休闲游戏",

  "report": {
    "title_template": "{project_name} - {date} 日报",
    "schedule_time": "10:05",
    "currency_symbol": "¥",
    "include_reason_analysis": false
  },

  "feishu": {
    "app_token": "AbCdEfGhIjKlMnOpQrStUvWxYz",
    "table_id": "tbl1234567890",
    "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/12345678-90ab-cdef-1234-567890abcdef",
    "tables": {
      "base": {
        "name": "基础数据总览",
        "table_id": "tbl1234567890",
        "view_id": "vewABCDEFGH"
      }
    }
  },

  ...
}
```

---

## ❓ 常见问题

**Q: 我没有渠道表格和地区表格怎么办？**
A: 可以不填写 `channel` 和 `country` 部分，或者 table_id 填空

**Q: 我的表格字段名称和示例不一样怎么办？**
A: 修改 `fields` 部分的 `aliases`，添加你的字段名称

**Q: 如何确认配置是否正确？**
A: 填写好后发给我，我会帮你测试

**有任何问题，随时问我！**
