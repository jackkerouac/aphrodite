#!/usr/bin/env python3
import base64
import requests
from pathlib import Path

# ─── EDIT THESE ────────────────────────────────────────────────────────────────
JELLYFIN_URL = "https://jellyfin.okaymedia.ca"
ITEM_ID      = "804cbeeebfe3798b0239ba2fe57c1140"
API_KEY      = "6c921b79ca694f04b86c6e15a104e469"
POSTER_FILE  = Path("posters/modified/804cbeeebfe3798b0239ba2fe57c1140.jpg")
# ────────────────────────────────────────────────────────────────────────────────

if not POSTER_FILE.exists():
    raise SystemExit(f"❌ File not found: {POSTER_FILE}")

# 1) Read & Base-64 encode
with POSTER_FILE.open("rb") as f:
    b64data = base64.b64encode(f.read())

# 2) Build request
url = f"{JELLYFIN_URL}/Items/{ITEM_ID}/Images/Primary"
headers = {
    "X-Emby-Token": API_KEY,
    "Content-Type": "image/jpeg; charset=utf-8"
}

# 3) POST the raw Base-64 text, not JSON, not multipart
resp = requests.post(url, headers=headers, data=b64data, timeout=30)

print(f"{resp.status_code=}  {resp.text.strip()!r}")
