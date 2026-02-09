# 创建 GitHub Personal Access Token 简易指南

## 📋 创建步骤（3 分钟完成）

### 1. 创建 Token
1. 打开这个网址：
   https://github.com/settings/tokens/new

2. 设置 Note（随便填）：
   - 输入：`daily-report-token`

3. 勾选权限（只勾选一个）：
   - ✅ **repo** (完整的仓库访问权限)

4. 点击页面底部的 **Generate token** 按钮

5. 复制显示的 Token（格式：`ghp_xxxxxxxxxxxxxxxx`）
   - ⚠️ **注意：Token 只显示一次，复制好！**

### 2. 告诉我 Token
把复制的 Token 发给我，格式：
```
Token: ghp_xxxxxxxxxxxxxxxx
```

然后我帮你推送代码！

---

## 💡 为什么需要 Token？

GitHub 为了安全，不允许命令行直接推送代码，需要一个"密码"来认证。

这个 Token 就是你的"密码"，可以用来推送代码。

---

## ⚠️ 安全提示

- Token 只显示一次，复制好
- 不要把这个 Token 告诉其他人
- 如果泄露了，可以在 GitHub 上删除重新创建
