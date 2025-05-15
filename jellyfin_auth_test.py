#!/usr/bin/env python3
"""
jellyfin_auth_test.py   •   quick auth-mode smoke test

Usage:
    python jellyfin_auth_test.py --url https://your.jellyfin.server \
                                 --api_key YOUR_KEY \
                                 --user_id YOUR_USER_ID
"""

import argparse
import json
import textwrap

import requests


def run_test(name: str, url: str, headers: dict | None = None) -> tuple[int, str]:
    """Return (status_code, snippet) for this auth variant."""
    try:
        resp = requests.get(url, headers=headers or {}, timeout=10)
        snippet = resp.text[:80].replace("\n", "")
        return resp.status_code, snippet
    except Exception as exc:  # noqa: BLE001
        return -1, f"{type(exc).__name__}: {exc}"


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Try several Jellyfin auth styles against /Users/Me")
    ap.add_argument("--url", required=True,
                    help="Base Jellyfin URL, e.g. https://jellyfin.example.com")
    ap.add_argument("--api_key", required=True, help="API key (X-Emby-Token)")
    ap.add_argument("--user_id", required=True,
                    help="UserId GUID (find in user → advanced)")
    args = ap.parse_args()

    endpoint = f"{args.url.rstrip('/')}/Users/Me"

    tests = [
        {
            "name": "token-header",
            "url": endpoint,
            "headers": {"X-Emby-Token": args.api_key},
        },
        {
            "name": "auth-header",
            "url": endpoint,
            "headers": {
                "X-Emby-Authorization": (
                    f'MediaBrowser Token="{args.api_key}", '
                    f'UserId="{args.user_id}", '
                    'Device="AuthTest", DeviceId="auth-script"'
                )
            },
        },
        {
            "name": "query",
            "url": f"{endpoint}?api_key={args.api_key}",
            "headers": {},
        },
        {
            "name": "both-headers",
            "url": endpoint,
            "headers": {
                "X-Emby-Token": args.api_key,
                "X-Emby-Authorization": (
                    f'MediaBrowser Token="{args.api_key}", '
                    f'UserId="{args.user_id}", '
                    'Device="AuthTest", DeviceId="auth-script"'
                ),
            },
        },
    ]

    print("\nTesting Jellyfin authentication methods\n"
          "Endpoint: /Users/Me\n")

    for t in tests:
        code, snippet = run_test(t["name"], t["url"], t["headers"])
        verdict = "OK" if code == 200 else "FAIL"
        print(
            f"{t['name']:<14}  →  {code:<3}  {verdict}   "
            f"{snippet[:60]}{'…' if len(snippet) > 60 else ''}"
        )


if __name__ == "__main__":
    main()
