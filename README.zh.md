<div align="center">

<img src="assets/banner.png" alt="MiniMax Agent Automation" width="100%">

# MiniMax Agent 自动化

**自动注册账号 · 每日签到 · 提取 JWT 与 Session Cookie，适用于 [agent.minimax.io](https://agent.minimax.io/)**

基于 [Zenvex](https://zenvex.dev) 临时邮箱 + [Playwright](https://playwright.dev)。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40%2B-2EAD33.svg?logo=playwright&logoColor=white)](https://playwright.dev)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-555.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Stars](https://img.shields.io/github/stars/0xgetz/minimax-agent-automation?style=social)](https://github.com/0xgetz/minimax-agent-automation/stargazers)

[English](README.md) · [Bahasa Indonesia](README.id.md) · [Español](README.es.md) · **中文** · [日本語](README.ja.md)

</div>

---

## 简介

`minimax-agent-automation` 驱动真实浏览器，使用一次性邮箱完整创建 **MiniMax
Agent** 账号，执行**每日签到**，并将 **JWT Token + Session Cookie + 浏览器存储**
导出为 JSON。

它**不**重放 MiniMax 的私有 API（该 API 需要请求签名并使用加密的 auth token），
而是操作真实界面，因此即使网站内部实现变化也能继续工作。

## 功能特性

| | |
|---|---|
| 🚀 **一条命令** | `python3 minimax_auto.py` — 注册、验证、签到、导出 |
| 📧 **临时邮箱** | 通过 Zenvex 生成随机 `@souss.dev` 收件箱，用其 JSON API 读取 |
| 🔐 **完整凭证导出** | `_token` JWT、全部 Cookie、`localStorage`、`sessionStorage` |
| ✅ **每日签到** | 自动领取每日积分 |
| 🔢 **批量模式** | `--count N` 依次创建 N 个账号 |
| 🧩 **无需 API Key** | 无需注册、无需密钥 — 只要有浏览器 |

## 工作原理

```
Zenvex 收件箱 ──► agent.minimax.io（Sign in）──► 邮箱 ──► 条款 ──► 密码
                                                              │
     Token + Cookie + 存储 ◄── 签到 ◄── 验证码 ◄───────────────┘
```

1. 生成随机 Zenvex 地址。
2. 打开 `agent.minimax.io` 并点击 **Sign in** — 这会生成回调所需的 OAuth `state`。
3. 输入邮箱 → 同意条款 → **Continue** → 设置密码。
4. 轮询 Zenvex API，从**邮件正文**读取 6 位验证码。
5. 提交验证码 → 自动登录。
6. 在每日弹窗点击 **Check in for N**。
7. 将 `_token` + Cookie + 存储导出为 `.jsonl`。

## 安装

```bash
git clone https://github.com/0xgetz/minimax-agent-automation.git
cd minimax-agent-automation

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

> 若 `--with-deps` 无法访问软件源，请手动安装 Chromium 依赖
> （`libglib2.0-0 libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0
> libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2
> libgbm1 libpango-1.0-0 libcairo2 libasound2 libatspi2.0-0`）。

## 使用方法

```bash
python3 minimax_auto.py                     # 1 个账号
python3 minimax_auto.py --count 3           # 依次 3 个账号
python3 minimax_auto.py --domain souss.dev  # 临时邮箱域名
python3 minimax_auto.py --headful           # 显示浏览器窗口
python3 minimax_auto.py --out accounts.jsonl
python3 minimax_auto.py --keep-open         # 保持浏览器打开（调试）
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--count` | `1` | 创建的账号数量 |
| `--domain` | `souss.dev` | Zenvex 接收域名 |
| `--password` | `ZenvexMiniMax2026!x` | 新账号密码 |
| `--out` | `minimax_accounts.jsonl` | 输出文件（追加） |
| `--headful` | 关闭 | 显示浏览器窗口 |
| `--keep-open` | 关闭 | 不关闭浏览器（调试） |

## 输出格式

每行一个 JSON 对象（参见 [`examples/minimax_account.example.json`](examples/minimax_account.example.json)）：

```json
{
  "site": "https://agent.minimax.io/",
  "account": {
    "email": "5ie22i0f@souss.dev",
    "password": "ZenvexMiniMax2026!x",
    "userName": "MiniMax853738",
    "userID": "35zvxoxqYmQ2",
    "realUserID": "561636901788553221"
  },
  "token_jwt": "eyJhbGciOiJIUzI1NiIs...",
  "cookie_header": "_fbp=...; _token=eyJ...; _sid=...",
  "cookies": [ { "name": "_token", "value": "eyJ...", "domain": "agent.minimax.io" } ],
  "localStorage": { "_token": "eyJ...", "user_detail_agent": "{...}" },
  "sessionStorage": { "mavis:activeAgentId": "..." },
  "checkin": true,
  "captured_at": 1790762452
}
```

## 实现说明

- **MiniMax 账号 API 需要请求签名**（`x-timestamp`、`x-signature`、`yy` 及加密的
  `authToken`）。脚本操作 UI，而非重放 API。
- **OAuth `state` 必需。** 直接打开 `/unified-login` 会在回调时返回 **HTTP 400** —
  务必从 `agent.minimax.io` → *Sign in* 开始。
- **条款复选框是无标签的 `<button>`** — Playwright 的真实鼠标点击才能切换 React
  状态，普通 JS `.click()` 无效。
- **只从邮件正文读取验证码。** 对整个 JSON 用 `\d{6}` 会匹配到 `received_at`/id
  中的数字，返回错误的验证码。
- **Zenvex 需要 `x-zenvex-csrf` 请求头**（`zvx_csrf` Cookie 的值）和浏览器来源，
  否则返回 `403`。其 Turnstile 在真实浏览器中会自动通过。
- **MiniMax 重发时沿用同一验证码**，且约 5 分钟过期。

## 项目结构

```
minimax-agent-automation/
├── minimax_auto.py                     # 自动化脚本
├── requirements.txt
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── README.md  README.id.md  README.es.md  README.zh.md  README.ja.md
├── assets/                             # logo + banner (SVG & PNG)
└── examples/minimax_account.example.json
```

## 免责声明

仅供**学习与个人自动化**使用。您需自行遵守 MiniMax 与 Zenvex 的服务条款。请勿
用于批量注册账号、规避速率限制或滥用服务。作者不对任何误用负责。

## 许可证

[MIT](LICENSE) © 2026 0xgetz
