<div align="center">

# MiniMax Agent Automation

**Automated account signup · daily check-in · JWT &amp; session-cookie harvester for [agent.minimax.io](https://agent.minimax.io/)**

Powered by [Zenvex](https://zenvex.dev) disposable email + [Playwright](https://playwright.dev).

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF.svg?logo=githubactions&logoColor=white)](.github/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40%2B-2EAD33.svg?logo=playwright&logoColor=white)](https://playwright.dev)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-555.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Stars](https://img.shields.io/github/stars/0xgetz/minimax-agent-automation?style=social)](https://github.com/0xgetz/minimax-agent-automation/stargazers)

**English** · [Bahasa Indonesia](README.id.md) · [Español](README.es.md) · [中文](README.zh.md) · [日本語](README.ja.md)

</div>

---

## Overview

`minimax-agent-automation` drives a real browser to create a **MiniMax Agent**
account end-to-end with a throwaway email, performs the **daily check-in**, and
exports the resulting **JWT token + session cookies + browser storage** as JSON.

It does not replay MiniMax's private API (which is request-signed and uses an
encrypted auth token). Instead it clicks through the actual UI, so it keeps
working when the site changes its internals.

## Features

| | |
|---|---|
| 🚀 **One command** | `python3 minimax_auto.py` — signup, verify, check-in, export |
| 📧 **Disposable email** | Random `@souss.dev` inbox via Zenvex, read over its JSON API |
| 🔐 **Full credential export** | `_token` JWT, all cookies, `localStorage`, `sessionStorage` |
| ✅ **Daily check-in** | Claims the daily credits automatically |
| 🔢 **Bulk mode** | `--count N` creates N accounts sequentially |
| 🧩 **Zero API keys** | No signup, no keys — just a browser |

## How it works

```
Zenvex inbox ──► agent.minimax.io (Sign in) ──► email ──► terms ──► password
                                                              │
        token + cookies + storage ◄── check-in ◄── verify code ◄┘
```

1. Generate a random Zenvex address.
2. Open `agent.minimax.io` and click **Sign in** — this mints the OAuth `state`
   the callback needs.
3. Enter email → accept terms → **Continue** → create a password.
4. Poll the Zenvex API and read the 6-digit code **from the email body**.
5. Submit the code → land logged in.
6. Click **Check in for N** on the daily popup.
7. Dump `_token` + cookies + storage to a `.jsonl` file.

## Installation

```bash
git clone https://github.com/0xgetz/minimax-agent-automation.git
cd minimax-agent-automation

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

> If `--with-deps` can't reach your package mirror, install the Chromium shared
> libraries manually (`libglib2.0-0 libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0
> libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2
> libgbm1 libpango-1.0-0 libcairo2 libasound2 libatspi2.0-0`).

## Usage

```bash
python3 minimax_auto.py                     # 1 account
python3 minimax_auto.py --count 3           # 3 accounts, sequentially
python3 minimax_auto.py --domain souss.dev  # temp-email domain
python3 minimax_auto.py --headful           # watch the browser
python3 minimax_auto.py --out accounts.jsonl
python3 minimax_auto.py --keep-open         # keep browser open (debug)
```

| Flag | Default | Description |
|------|---------|-------------|
| `--count` | `1` | Number of accounts to create |
| `--domain` | `souss.dev` | Zenvex receiving domain |
| `--password` | `ZenvexMiniMax2026!x` | Password for created accounts |
| `--out` | `minimax_accounts.jsonl` | Output file (appended) |
| `--headful` | off | Show the browser window |
| `--keep-open` | off | Don't close the browser (debug) |

## Output format

One JSON object per line (see [`examples/minimax_account.example.json`](examples/minimax_account.example.json)):

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

## Implementation notes

- **MiniMax account API is request-signed** (`x-timestamp`, `x-signature`, `yy`
  headers + encrypted `authToken`). The script drives the UI instead of replaying it.
- **OAuth `state` is mandatory.** Opening `/unified-login` directly returns
  **HTTP 400** on callback — always start from `agent.minimax.io` → *Sign in*.
- **The terms checkbox is an unlabelled `<button>`** — Playwright's real mouse
  click toggles React state; a bare JS `.click()` does not.
- **Read the code from the email body only.** Matching `\d{6}` on the whole JSON
  catches digits in `received_at`/ids and returns the wrong code.
- **Zenvex needs the `x-zenvex-csrf` header** (value of the `zvx_csrf` cookie)
  and a browser origin, or it returns `403`. Its Turnstile gate passes in a real browser.
- **MiniMax reuses the same code on resend** and codes expire in ~5 minutes.

## Project layout

```
minimax-agent-automation/
├── minimax_auto.py                     # the automation script
├── requirements.txt
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── README.md  README.id.md  README.es.md  README.zh.md  README.ja.md
├── .github/workflows/ci.yml
└── examples/minimax_account.example.json
```

## Disclaimer

For **educational and personal-automation** use only. You are responsible for
complying with MiniMax's and Zenvex's terms of service. Do not use this to mass
register accounts, evade rate limits, or abuse the service. The authors are not
liable for any misuse.

## License

[MIT](LICENSE) © 2026 0xgetz
