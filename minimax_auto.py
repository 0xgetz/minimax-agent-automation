#!/usr/bin/env python3
"""
MiniMax Agent auto-signup + daily check-in + credential harvester.

Per account:
  1. Generate a fresh Zenvex temp address (souss.dev / znvx.me).
  2. Open the MiniMax OAuth login URL (with redirect state) and sign up:
       email -> terms -> Continue -> create password -> Continue.
  3. Poll the Zenvex API for the MiniMax verification email and read the code
     from the email BODY (not the whole JSON, which also contains timestamps).
  4. Enter the code -> Continue. The account is created and you land logged in.
  5. Perform the daily check-in ("Check in for N").
  6. Dump the JWT token + all cookies + localStorage/sessionStorage to JSON.

Why a browser, not raw HTTP:
  MiniMax's account calls are signed (x-timestamp / x-signature / yy) and the login
  posts an encrypted authToken, so plain HTTP replay is brittle. Driving the real UI
  rides whatever the site ships.

IMPORTANT timing note:
  The OAuth `state` embedded in the login URL expires quickly. Run the whole flow
  in ONE page without long pauses; this script does (code polling is the only wait,
  and it starts right after the email is submitted).

Requirements:
  pip install playwright
  python -m playwright install chromium     # plus system libs (see --with-deps)

Usage:
  python3 minimax_auto.py                     # 1 account
  python3 minimax_auto.py --count 3           # 3 accounts
  python3 minimax_auto.py --domain souss.dev
  python3 minimax_auto.py --headful           # watch it run
  python3 minimax_auto.py --out accounts.jsonl
  python3 minimax_auto.py --keep-open         # leave the browser open after success
"""

import argparse
import json
import random
import re
import string
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

MINIMAX_HOME = "https://agent.minimax.io/"
ZENVEX = "https://zenvex.dev"
DEFAULT_PASSWORD = "ZenvexMiniMax2026!x"


# ---------------------------------------------------------------- temp email


def zenvex_fetch(page, path: str):
    """Call the Zenvex API from inside the page (uses its cookies + csrf header)."""
    js = """
    async (path) => {
      const csrf = document.cookie.split(';').map(s => s.trim())
        .find(s => s.startsWith('zvx_csrf='));
      const token = csrf ? csrf.split('=').slice(1).join('=') : '';
      const res = await fetch('https://zenvex.dev' + path, {
        credentials: 'include',
        headers: { 'x-zenvex-csrf': token, 'accept': 'application/json' },
      });
      let body = null;
      try { body = await res.json(); } catch (e) { body = null; }
      return { status: res.status, body };
    }
    """
    return page.evaluate(js, path)


def new_address(page, domain: str, length: int = 10) -> str:
    """Zenvex builds the prefix client-side; pick a random one and confirm it works."""
    alphabet = string.ascii_lowercase + string.digits
    for _ in range(6):
        addr = "".join(random.choice(alphabet) for _ in range(length)) + f"@{domain}"
        r = zenvex_fetch(page, f"/api/emails/count/{addr}")
        if (r or {}).get("status") == 200:
            return addr
    raise RuntimeError("could not create a Zenvex address")


def extract_code(email_result: dict) -> str | None:
    """Pull the 6-digit code out of the email body only (never the envelope JSON)."""
    html = email_result.get("html_content") or ""
    text = email_result.get("text_content") or ""
    body = re.sub(r"<[^>]+>", " ", html) + " " + text
    # prefer the number right after "code is"
    m = re.search(r"code\s*(?:is)?\s*[:\-]?\s*(\d{4,8})", body, re.I)
    if m:
        return m.group(1)
    m = re.search(r"\b(\d{6})\b", body)
    return m.group(1) if m else None


def wait_for_code(page, address: str, timeout_s: int = 120, log=print) -> str:
    """Poll Zenvex for the newest MiniMax email and return its verification code."""
    deadline = time.time() + timeout_s
    seen = set()
    while time.time() < deadline:
        listing = zenvex_fetch(page, f"/api/emails/{address}?limit=20&offset=0")
        msgs = ((listing or {}).get("body") or {}).get("result", [])
        msgs.sort(key=lambda m: m.get("received_at", 0), reverse=True)
        for msg in msgs:
            if "minimax" not in (msg.get("from_address", "") + msg.get("subject", "")).lower():
                continue
            if msg["id"] in seen:
                continue
            seen.add(msg["id"])
            one = zenvex_fetch(page, f"/api/inbox/{msg['id']}")
            result = ((one or {}).get("body") or {}).get("result") or {}
            code = extract_code(result)
            if code:
                log(f"[email] code = {code}")
                return code
        time.sleep(3)
    raise TimeoutError("verification email did not arrive")


# ---------------------------------------------------------------- ui helpers


def click_button(page, text: str, timeout_ms: int = 15000) -> bool:
    """Click the first button whose visible text contains `text` (case-insensitive)."""
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        btns = page.locator("button")
        for i in range(btns.count()):
            try:
                label = (btns.nth(i).inner_text() or "").strip()
            except Exception:
                continue
            if text.lower() in label.lower():
                try:
                    btns.nth(i).click(timeout=3000)
                    return True
                except Exception:
                    pass
        page.wait_for_timeout(400)
    return False


def accept_terms(page):
    """MiniMax renders the terms checkbox as an unlabelled button; click it if unchecked."""
    try:
        cb = page.locator("div.mt-6 button[type=button]").first
        if cb.count():
            cb.click(timeout=3000)
    except Exception:
        pass


def fill_first(page, selectors, value) -> bool:
    for sel in selectors:
        loc = page.locator(sel).first
        try:
            if loc.count():
                loc.fill(value)
                return True
        except Exception:
            continue
    return False


def dismiss_overlays(page):
    for _ in range(2):
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass
        page.wait_for_timeout(300)


# ---------------------------------------------------------------- main flow


def run_account(pw, domain: str, password: str, headful: bool, keep_open: bool, log=print) -> dict:
    browser = pw.chromium.launch(
        headless=not headful,
        args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
    )
    ctx = browser.new_context(
        user_agent=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"),
        viewport={"width": 1440, "height": 900},
        locale="en-US",
    )
    page = ctx.new_page()
    try:
        # --- 1. temp email (this also seeds Zenvex cookies in this context)
        log("[1/6] creating temp email…")
        page.goto(ZENVEX + "/", wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        address = new_address(page, domain)
        log(f"[1/6] address = {address}")

        # --- 2. start signup by clicking "Sign in" on the agent home page.
        # This is REQUIRED: the home page generates the OAuth `state` (a CSRF uuid)
        # that the callback validates. Hitting /unified-login directly without it
        # returns HTTP 400 on the final redirect.
        log("[2/6] opening MiniMax sign-in…")
        page.goto(MINIMAX_HOME, wait_until="domcontentloaded")
        page.wait_for_timeout(3500)
        dismiss_overlays(page)
        if not click_button(page, "Sign in", 15000):
            raise RuntimeError("Sign in button not found on agent home")
        page.wait_for_url("**/unified-login**", timeout=30000)
        page.wait_for_timeout(1500)

        log("[3/6] submitting email…")
        fill_first(page, ["input[type=email]", "input[placeholder*='email' i]", "input"], address)
        page.wait_for_timeout(300)
        accept_terms(page)
        page.wait_for_timeout(300)
        click_button(page, "Continue", 10000)
        page.wait_for_timeout(2500)

        # --- password
        log("[4/6] setting password…")
        page.wait_for_selector("input[type=password]", timeout=20000)
        fill_first(page, ["input[type=password]"], password)
        page.wait_for_timeout(300)
        click_button(page, "Continue", 10000)

        # --- 3. verification code (poll Zenvex)
        log("[5/6] waiting for verification email…")
        page.wait_for_selector("input[placeholder*='verification' i]", timeout=30000)
        code = wait_for_code(page, address, log=log)
        fill_first(page, ["input[placeholder*='verification' i]", "input"], code)
        page.wait_for_timeout(300)
        click_button(page, "Continue", 10000)

        # wait until we are back on the agent app (logged in)
        try:
            page.wait_for_url("**/agent.minimax.io/**", timeout=45000)
        except PWTimeout:
            page.wait_for_timeout(6000)
        page.wait_for_timeout(4000)
        log(f"[5/6] logged in -> {page.url}")

        # --- 5. daily check-in
        log("[6/6] daily check-in…")
        checkin_ok = do_checkin(page, log=log)

        # --- 6. harvest
        creds = harvest(page, address, password)
        creds["checkin"] = checkin_ok
        log(f"[done] {address}  checkin={checkin_ok}")
        return creds
    finally:
        if not keep_open:
            ctx.close()
            browser.close()


def do_checkin(page, log=print) -> bool:
    """Click the daily check-in button. True if a check-in happened."""
    page.goto(MINIMAX_HOME, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    for _ in range(4):
        if click_button(page, "Check in for", 6000):
            page.wait_for_timeout(2500)
            log("[checkin] checked in")
            return True
        if "checked in today" in page.content().lower():
            log("[checkin] already checked in today")
            return False
        page.wait_for_timeout(2000)
    log("[checkin] button not found (already done or popup suppressed)")
    return False


def harvest(page, address: str, password: str) -> dict:
    """Collect token, cookies and storage from the logged-in agent page."""
    page.goto(MINIMAX_HOME, wait_until="domcontentloaded")
    page.wait_for_timeout(3500)
    cookies = page.context.cookies()
    ls = page.evaluate("Object.fromEntries(Object.entries(localStorage))")
    ss = page.evaluate("Object.fromEntries(Object.entries(sessionStorage))")
    token = ls.get("_token") or next((c["value"] for c in cookies if c["name"] == "_token"), None)
    try:
        user = json.loads(ls.get("user_detail_agent", "{}"))
    except Exception:
        user = {}
    return {
        "site": "https://agent.minimax.io/",
        "account": {
            "email": address,
            "email_provider": "zenvex.dev",
            "password": password,
            "userName": user.get("userName"),
            "userID": user.get("userID"),
            "realUserID": user.get("realUserID"),
        },
        "token_jwt": token,
        "cookie_header": "; ".join(f"{c['name']}={c['value']}" for c in cookies),
        "cookies": cookies,
        "localStorage": ls,
        "sessionStorage": ss,
        "captured_at": int(time.time()),
    }


def main():
    ap = argparse.ArgumentParser(description="MiniMax Agent auto-signup + check-in + harvest")
    ap.add_argument("--count", type=int, default=1, help="number of accounts to create")
    ap.add_argument("--domain", default="souss.dev", help="Zenvex temp-email domain")
    ap.add_argument("--password", default=DEFAULT_PASSWORD)
    ap.add_argument("--out", default="minimax_accounts.jsonl")
    ap.add_argument("--headful", action="store_true")
    ap.add_argument("--keep-open", action="store_true", help="keep the browser open (debug)")
    args = ap.parse_args()

    out = Path(args.out)
    results = []
    with sync_playwright() as pw:
        for i in range(1, args.count + 1):
            print(f"\n=== account {i}/{args.count} ===", flush=True)
            try:
                creds = run_account(pw, args.domain, args.password, args.headful, args.keep_open)
                results.append(creds)
                with out.open("a") as f:
                    f.write(json.dumps(creds) + "\n")
                print(f"[saved] {creds['account']['email']} -> {out}", flush=True)
            except Exception as e:
                print(f"[fail] account {i}: {e}", flush=True)
            if i < args.count:
                time.sleep(5)

    print(f"\n{len(results)}/{args.count} accounts written to {out}")


if __name__ == "__main__":
    main()
