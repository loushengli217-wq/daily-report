# GitHub Actions 自动日报部署指南

## 📋 概述

使用 GitHub Actions 实现每天自动发送日报，无需服务器，完全免费。

---

## 🚀 部署步骤

### 1. 创建 GitHub 仓库

```bash
# 初始化 Git 仓库（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "feat: 添加 GitHub Actions 自动日报"

# 创建 GitHub 仓库后，推送到 GitHub
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### 2. 配置 GitHub Secrets

在 GitHub 仓库中配置环境变量：

1. 进入仓库页面
2. 点击 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 添加以下 secrets：

| Secret 名称 | 值 | 说明 |
|-------------|-----|------|
| `COZE_API_KEY` | 你的 API Key | 从环境变量 `COZE_WORKLOAD_IDENTITY_API_KEY` 获取 |
| `COZE_MODEL_BASE_URL` | 模型服务地址 | 从环境变量 `COZE_INTEGRATION_MODEL_BASE_URL` 获取 |

**如何获取这些值**：
```bash
# 在当前容器中执行
echo $COZE_WORKLOAD_IDENTITY_API_KEY
echo $COZE_INTEGRATION_MODEL_BASE_URL
```

### 3. 启用 GitHub Actions

推送到 GitHub 后，Actions 会自动运行：
- 定时任务：每天 UTC 02:01（北京时间 10:01）
- 手动触发：在 GitHub 页面点击 "Run workflow"

---

## 📊 工作流程说明

### 定时触发
```yaml
schedule:
  - cron: '1 2 * * *'  # UTC 02:01 = 北京时间 10:01
```

### 执行步骤
1. ✅ 检出代码
2. ✅ 设置 Python 3.12
3. ✅ 安装依赖
4. ✅ 生成二重螺旋-海外报告
5. ✅ 生成 Pocket-小程序报告
6. ✅ 保存报告为 artifact

---

## 🔍 监控和管理

### 查看运行日志
1. 进入仓库页面
2. 点击 `Actions` 标签
3. 点击具体的工作流运行记录
4. 查看详细日志

### 手动触发
1. 进入 `Actions` 页面
2. 选择 `Daily Report Generator`
3. 点击 `Run workflow`
4. 选择分支并运行

### 查看历史报告
在工作流运行记录中，可以下载生成的 Markdown 报告文件。

---

## ⚠️ 注意事项

### 时区问题
- GitHub Actions 使用 UTC 时间
- `cron: '1 2 * * *'` = 北京时间 10:01
- 如果需要调整时间，修改 cron 表达式

### 依赖安装
确保 `requirements.txt` 包含所有必要的依赖：
```txt
langchain>=0.1.0
langgraph>=0.0.0
langchain-openai
schedule
pydantic
requests
```

### 环境变量
如果缺少环境变量，可以修改 workflow 文件，直接硬编码或通过 Secrets 传递。

---

## 💡 优势

| 特性 | 说明 |
|------|------|
| **完全免费** | GitHub Actions 公共仓库免费 |
| **可靠稳定** | GitHub 提供的基础设施 |
| **易于维护** | 代码即配置，无需服务器 |
| **自动重试** | GitHub Actions 支持失败重试 |
| **日志完整** | 每次运行都有详细日志 |

---

## 🎯 后续优化

### 添加通知
可以在工作流最后添加飞书通知：
```yaml
- name: Send notification
  run: |
    curl -X POST "YOUR_FEISHU_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d '{"msg_type":"text","content":{"text":"日报已生成并发送"}}'
```

### 支持多环境
为不同环境（开发、测试、生产）创建不同的 workflow 文件。

### 添加审批流程
重要报告可以添加人工审批步骤。

---

## 📞 需要帮助？

如果遇到问题：
1. 检查 GitHub Actions 日志
2. 确认 Secrets 配置正确
3. 验证 Python 依赖安装成功
4. 测试脚本能否在本地运行

---

**部署完成后，每天北京时间 10:01 会自动生成并发送日报！** 🎉
