# Contributing

Thanks for your interest in improving **minimax-agent-automation**.

## Ways to contribute

- **Bug reports** — open an issue with the site behaviour, the exact step, and a
  redacted log. Never paste real tokens, cookies or passwords.
- **Selector fixes** — MiniMax changes its UI periodically. If a selector breaks,
  open a PR that updates the helper in `minimax_auto.py`.
- **New languages** — we ship READMEs in EN / ID / ES / ZH / JA. Add another by
  copying `README.md` and linking it from the language bar.
- **Docs** — clearer install steps, platform notes, troubleshooting.

## Development setup

```bash
git clone https://github.com/0xgetz/minimax-agent-automation.git
cd minimax-agent-automation
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

## Guidelines

1. Keep the script dependency-light (Playwright only).
2. Prefer real UI interaction over private/undocumented endpoints.
3. Never commit harvested credentials — `*.jsonl` is git-ignored on purpose.
4. One logical change per pull request; describe *why* in the body.
5. Run `python -m py_compile minimax_auto.py` before pushing.

## Commit style

```
feat: add --domain flag for znvx.me
fix: read verification code from email body only
docs: add Japanese README
```

## Code of conduct

Be respectful. This project is for educational and personal-automation use.
Do not use it to abuse a service, bypass rate limits at scale, or violate any
platform's terms.
