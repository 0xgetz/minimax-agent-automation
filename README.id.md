<div align="center">

# MiniMax Agent Automation

**Daftar akun otomatis · check-in harian · pengambil JWT &amp; session cookie untuk [agent.minimax.io](https://agent.minimax.io/)**

Didukung email sementara [Zenvex](https://zenvex.dev) + [Playwright](https://playwright.dev).

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF.svg?logo=githubactions&logoColor=white)](.github/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40%2B-2EAD33.svg?logo=playwright&logoColor=white)](https://playwright.dev)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-555.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Stars](https://img.shields.io/github/stars/0xgetz/minimax-agent-automation?style=social)](https://github.com/0xgetz/minimax-agent-automation/stargazers)

[English](README.md) · **Bahasa Indonesia** · [Español](README.es.md) · [中文](README.zh.md) · [日本語](README.ja.md)

</div>

---

## Ringkasan

`minimax-agent-automation` menggerakkan browser sungguhan untuk membuat akun
**MiniMax Agent** dari awal memakai email sekali pakai, melakukan **check-in
harian**, lalu mengekspor **token JWT + session cookie + penyimpanan browser**
ke format JSON.

Script ini **tidak** memutar ulang API privat MiniMax (yang bertanda tangan dan
memakai auth token terenkripsi). Ia menekan tombol di UI asli, sehingga tetap
berfungsi saat situs berubah di dalam.

## Fitur

| | |
|---|---|
| 🚀 **Satu perintah** | `python3 minimax_auto.py` — daftar, verifikasi, check-in, ekspor |
| 📧 **Email sekali pakai** | Inbox acak `@souss.dev` via Zenvex, dibaca lewat JSON API-nya |
| 🔐 **Ekspor kredensial penuh** | JWT `_token`, semua cookie, `localStorage`, `sessionStorage` |
| ✅ **Check-in harian** | Mengambil kredit harian secara otomatis |
| 🔢 **Mode massal** | `--count N` membuat N akun berurutan |
| 🧩 **Tanpa API key** | Tidak perlu daftar, tidak perlu kunci — cukup browser |

## Cara kerja

```
Inbox Zenvex ──► agent.minimax.io (Sign in) ──► email ──► terms ──► password
                                                              │
        token + cookie + storage ◄── check-in ◄── kode verifikasi ◄┘
```

1. Buat alamat Zenvex acak.
2. Buka `agent.minimax.io` dan klik **Sign in** — ini membuat OAuth `state`
   yang dibutuhkan callback.
3. Isi email → setujui terms → **Continue** → buat password.
4. Polling API Zenvex dan baca kode 6 digit **dari body email**.
5. Kirim kode → otomatis login.
6. Klik **Check in for N** pada popup harian.
7. Simpan `_token` + cookie + storage ke file `.jsonl`.

## Instalasi

```bash
git clone https://github.com/0xgetz/minimax-agent-automation.git
cd minimax-agent-automation

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

> Jika `--with-deps` tidak bisa menjangkau mirror paket Anda, pasang manual
> library Chromium (`libglib2.0-0 libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0
> libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2
> libgbm1 libpango-1.0-0 libcairo2 libasound2 libatspi2.0-0`).

## Penggunaan

```bash
python3 minimax_auto.py                     # 1 akun
python3 minimax_auto.py --count 3           # 3 akun berurutan
python3 minimax_auto.py --domain souss.dev  # domain email sementara
python3 minimax_auto.py --headful           # lihat browsernya
python3 minimax_auto.py --out accounts.jsonl
python3 minimax_auto.py --keep-open         # biarkan browser terbuka (debug)
```

| Flag | Default | Keterangan |
|------|---------|------------|
| `--count` | `1` | Jumlah akun yang dibuat |
| `--domain` | `souss.dev` | Domain penerima Zenvex |
| `--password` | `ZenvexMiniMax2026!x` | Password untuk akun baru |
| `--out` | `minimax_accounts.jsonl` | File keluaran (ditambahkan) |
| `--headful` | nonaktif | Tampilkan jendela browser |
| `--keep-open` | nonaktif | Jangan tutup browser (debug) |

## Format keluaran

Satu objek JSON per baris (lihat [`examples/minimax_account.example.json`](examples/minimax_account.example.json)):

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

## Catatan implementasi

- **API akun MiniMax bertanda tangan** (`x-timestamp`, `x-signature`, `yy` +
  `authToken` terenkripsi). Script menggerakkan UI, bukan memutar ulang API.
- **OAuth `state` wajib.** Membuka `/unified-login` langsung → **HTTP 400** saat
  callback — selalu mulai dari `agent.minimax.io` → *Sign in*.
- **Checkbox terms adalah `<button>` tanpa label** — klik mouse asli Playwright
  mengubah state React; `.click()` JS biasa tidak.
- **Baca kode hanya dari body email.** Regex `\d{6}` pada seluruh JSON menangkap
  digit dari `received_at`/id dan menghasilkan kode salah.
- **Zenvex butuh header `x-zenvex-csrf`** (nilai cookie `zvx_csrf`) dan origin
  browser, kalau tidak → `403`. Turnstile-nya lolos di browser asli.
- **Kode MiniMax sama saat resend** dan kedaluwarsa ~5 menit.

## Struktur proyek

```
minimax-agent-automation/
├── minimax_auto.py                     # script otomasi
├── requirements.txt
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── README.md  README.id.md  README.es.md  README.zh.md  README.ja.md
├── .github/workflows/ci.yml
└── examples/minimax_account.example.json
```

## Penafian

Hanya untuk **pembelajaran dan otomasi pribadi**. Anda bertanggung jawab mematuhi
ketentuan layanan MiniMax dan Zenvex. Jangan gunakan untuk mendaftarkan akun
massal, menghindari rate limit, atau menyalahgunakan layanan. Penulis tidak
bertanggung jawab atas penyalahgunaan apa pun.

## Lisensi

[MIT](LICENSE) © 2026 0xgetz
