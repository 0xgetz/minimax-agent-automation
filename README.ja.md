<div align="center">

# MiniMax Agent Automation

**[agent.minimax.io](https://agent.minimax.io/) のアカウント自動登録 · 毎日チェックイン · JWT / セッション Cookie 抽出**

[Zenvex](https://zenvex.dev) の使い捨てメール + [Playwright](https://playwright.dev) を使用。

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF.svg?logo=githubactions&logoColor=white)](.github/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40%2B-2EAD33.svg?logo=playwright&logoColor=white)](https://playwright.dev)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-555.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Stars](https://img.shields.io/github/stars/0xgetz/minimax-agent-automation?style=social)](https://github.com/0xgetz/minimax-agent-automation/stargazers)

[English](README.md) · [Bahasa Indonesia](README.id.md) · [Español](README.es.md) · [中文](README.zh.md) · **日本語**

</div>

---

## 概要

`minimax-agent-automation` は実ブラウザを操作して、使い捨てメールで **MiniMax
Agent** アカウントを最初から作成し、**毎日のチェックイン**を行い、**JWT トークン
+ セッション Cookie + ブラウザストレージ**を JSON として書き出します。

MiniMax の非公開 API（リクエスト署名と暗号化された auth token を使用）を再現する
のではなく、実際の UI をクリック操作するため、サイト内部が変わっても動作し続けます。

## 機能

| | |
|---|---|
| 🚀 **ワンコマンド** | `python3 minimax_auto.py` — 登録・認証・チェックイン・書き出し |
| 📧 **使い捨てメール** | Zenvex でランダムな `@souss.dev` 受信箱を作成、JSON API で取得 |
| 🔐 **完全な認証情報** | `_token` JWT、全 Cookie、`localStorage`、`sessionStorage` |
| ✅ **毎日チェックイン** | デイリークレジットを自動取得 |
| 🔢 **一括モード** | `--count N` で N アカウントを順番に作成 |
| 🧩 **API キー不要** | 登録もキーも不要 — ブラウザだけ |

## 仕組み

```
Zenvex 受信箱 ──► agent.minimax.io (Sign in) ──► メール ──► 規約 ──► パスワード
                                                                  │
      トークン + Cookie + ストレージ ◄── チェックイン ◄── 認証コード ◄┘
```

1. ランダムな Zenvex アドレスを生成。
2. `agent.minimax.io` を開き **Sign in** をクリック — コールバックに必要な
   OAuth `state` が生成されます。
3. メール入力 → 規約に同意 → **Continue** → パスワード作成。
4. Zenvex API をポーリングし、**メール本文**から 6 桁のコードを読み取る。
5. コードを送信 → 自動ログイン。
6. デイリーポップアップで **Check in for N** をクリック。
7. `_token` + Cookie + ストレージを `.jsonl` に書き出し。

## インストール

```bash
git clone https://github.com/0xgetz/minimax-agent-automation.git
cd minimax-agent-automation

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

> `--with-deps` がミラーに接続できない場合は、Chromium の共有ライブラリを手動で
> インストールしてください（`libglib2.0-0 libnss3 libnspr4 libatk1.0-0
> libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1
> libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2 libatspi2.0-0`）。

## 使い方

```bash
python3 minimax_auto.py                     # 1 アカウント
python3 minimax_auto.py --count 3           # 3 アカウントを順番に
python3 minimax_auto.py --domain souss.dev  # 一時メールのドメイン
python3 minimax_auto.py --headful           # ブラウザを表示
python3 minimax_auto.py --out accounts.jsonl
python3 minimax_auto.py --keep-open         # ブラウザを開いたまま（デバッグ）
```

| フラグ | 既定値 | 説明 |
|--------|--------|------|
| `--count` | `1` | 作成するアカウント数 |
| `--domain` | `souss.dev` | Zenvex の受信ドメイン |
| `--password` | `ZenvexMiniMax2026!x` | 新規アカウントのパスワード |
| `--out` | `minimax_accounts.jsonl` | 出力ファイル（追記） |
| `--headful` | オフ | ブラウザウィンドウを表示 |
| `--keep-open` | オフ | ブラウザを閉じない（デバッグ） |

## 出力形式

1 行につき 1 つの JSON オブジェクト（[`examples/minimax_account.example.json`](examples/minimax_account.example.json) 参照）：

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

## 実装メモ

- **MiniMax のアカウント API はリクエスト署名付き**（`x-timestamp`、`x-signature`、
  `yy` + 暗号化 `authToken`）。スクリプトは API を再現せず UI を操作します。
- **OAuth `state` は必須。** `/unified-login` を直接開くとコールバックで
  **HTTP 400** になります — 必ず `agent.minimax.io` → *Sign in* から開始。
- **規約チェックボックスはラベルのない `<button>`** — Playwright の実マウスクリック
  でないと React の状態が変わりません。素の JS `.click()` では動きません。
- **コードはメール本文からのみ抽出。** JSON 全体に `\d{6}` を当てると
  `received_at`/id の数字を拾い、誤ったコードになります。
- **Zenvex は `x-zenvex-csrf` ヘッダー**（`zvx_csrf` Cookie の値）とブラウザ
  オリジンが必要で、無いと `403`。Turnstile は実ブラウザで自動通過します。
- **MiniMax は再送時に同じコードを使い回し**、約 5 分で失効します。

## プロジェクト構成

```
minimax-agent-automation/
├── minimax_auto.py                     # 自動化スクリプト
├── requirements.txt
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── README.md  README.id.md  README.es.md  README.zh.md  README.ja.md
├── .github/workflows/ci.yml
└── examples/minimax_account.example.json
```

## 免責事項

**教育および個人の自動化**のみを目的としています。MiniMax と Zenvex の利用規約を
遵守する責任は利用者にあります。大量アカウント登録、レート制限の回避、サービスの
悪用には使用しないでください。作者はいかなる誤用についても責任を負いません。

## ライセンス

[MIT](LICENSE) © 2026 0xgetz
