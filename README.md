# 🌊 FlowSign · 每日流量签

> 为 Mefrp 量身打造的自动化签到助手，每日定时领取免费流量，告别手动操作。

![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-自动签到-blue?logo=githubactions)
![Python](https://img.shields.io/badge/Python-3.10%2B-green?logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ 亮点
- ⏰ **每日定时**：每天北京时间 08:00 自动执行，准时领取流量。
- 🖱️ **一键手动**：支持在 Actions 页面手动触发，随时测试。
- 📢 **清晰日志**：签到结果一目了然，失败原因快速定位。
- 🔒 **安全可靠**：敏感信息通过 GitHub Secrets 加密存储，绝不泄露。

---

## 📂 项目结构├── .github/workflows/sign.yml # GitHub Actions 工作流
├── sign.py # 签到核心脚本
└── README.md # 项目说明（就是你正在看的）
---

## 🔑 准备密钥（两个 Token）

在开始之前，您需要获取两个重要的 Token，并存入仓库 Secrets。

| 密钥名称 | 说明 |
|---------|------|
| `MEFRP_USER_TOKEN` | 您的 Mefrp 登录凭证（Bearer Token，不含 `Bearer ` 前缀） |
| `MEFRP_CAPTCHA_TOKEN` | 人机验证后获得的临时 Token（有有效期） |

### 获取方法

#### 1️⃣ 用户 Token（MEFRP_USER_TOKEN）
- 登录 [Mefrp 官网](https://www.mefrp.com)  
- 打开浏览器开发者工具（F12）→ 网络（Network）标签  
- 随便找一个 API 请求（比如个人中心），在请求头中找到 `Authorization` 字段，复制其值（类似 `eyJhbGciOiJIUzI1NiIs...`），**去掉前缀 `Bearer `**。

#### 2️⃣ 人机验证 Token（MEFRP_CAPTCHA_TOKEN）
- 用浏览器访问：（`client` 可自定义，建议保持 `FlowSign`）  
- 完成人机验证（点击、滑动等），页面会显示一串密文（如 `YWJjMTIz...`）。  
- 复制该密文，用 Base64 解码（可使用 Linux 命令 `echo "密文" | base64 -d` 或在线工具），得到 `token||client` 格式，取 `token` 部分即为 `CAPTCHA_TOKEN`。

---

## 🚀 部署到 GitHub Actions

### 第一步：创建仓库并上传代码
1. 在 GitHub 新建一个仓库（公开或私有均可），例如 `FlowSign`。
2. 将以下两个文件上传到仓库根目录（注意文件夹路径）：
 - `sign.py`（[点击下载脚本](#) 或从本文档下方复制）
 - `.github/workflows/sign.yml`（[点击下载工作流](#) 或从本文档下方复制）

### 第二步：配置 Secrets
进入仓库 `Settings` → `Secrets and variables` → `Actions`，点击 `New repository secret`，依次添加：
- `MEFRP_USER_TOKEN` → 粘贴您的用户 Token
- `MEFRP_CAPTCHA_TOKEN` → 粘贴您的人机验证 Token

### 第三步：等待或手动触发
- **自动**：每天 UTC 0:00（北京时间 8:00）工作流会自动运行。
- **手动**：进入仓库 `Actions` 标签页，选择 `Mefrp Auto Sign`，点击 `Run workflow`。

---

## 📝 运行日志示例
