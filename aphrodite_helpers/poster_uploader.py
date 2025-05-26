#!/usr/bin/env python3
# aphrodite_helpers/poster_uploader.py  –  stateless, Base64-body upload

import os
import sys
import time
import random
import logging
import base64
from pathlib import Path

import requests

# Make “aphrodite_helpers” importable when the file is run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("poster_uploader")


class PosterUploader:
    """
    Uploads modified posters to Jellyfin using Base64-encoded bodies.

    Key points
    ----------
    • Stateless – no StateManager.
    • Sends posters as raw Base64 in the request body with the correct Content-Type.
    • Built-in retry with exponential back-off + jitter.
    • Verifies upload by re-downloading the image.
    """

    def __init__(self, jellyfin_url: str, api_key: str, user_id: str | None = None):
        self.jellyfin_url = jellyfin_url.rstrip("/")
        self.api_key = api_key
        self.user_id = user_id

    def upload_poster(
        self,
        item_id: str,
        poster_path: str | Path,
        max_retries: int = 3,
        retry_delay: int = 2,
    ) -> bool:
        """
        Replace the primary image for a Jellyfin item using a Base64-encoded body.
        Returns True if successful, False otherwise.
        """
        poster_path = Path(poster_path)
        if not poster_path.exists():
            logger.error("Poster file not found: %s", poster_path)
            return False

        # Determine the content type from file extension
        ext = poster_path.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            content_type = "image/jpeg"
        elif ext == ".png":
            content_type = "image/png"
        else:
            logger.warning("Unknown extension %s; defaulting to image/jpeg", ext)
            content_type = "image/jpeg"
        content_type += "; charset=utf-8"

        url = f"{self.jellyfin_url}/Items/{item_id}/Images/Primary"

        # Read & Base64 encode
        try:
            raw = poster_path.read_bytes()
            b64data = base64.b64encode(raw)
        except Exception as exc:
            logger.error("Failed to read or encode image %s: %s", poster_path, exc)
            return False

        headers = {
            "X-Emby-Token": self.api_key,
            "Content-Type": content_type,
        }

        for attempt in range(1, max_retries + 1):
            logger.info(
                "Uploading poster for %s (attempt %s/%s) via Base64 body",
                item_id, attempt, max_retries,
            )
            try:
                resp = requests.post(url, headers=headers, data=b64data, timeout=30)
                if resp.status_code in (200, 204):
                    logger.info("✅ Upload success for %s", item_id)
                    if self._verify_upload(item_id):
                        logger.info("✅ Verification success for %s", item_id)
                        return True
                    logger.warning("❌ Verification failed for %s — retrying", item_id)
                else:
                    logger.warning(
                        "❌ Upload error for %s — %s: %s",
                        item_id, resp.status_code, resp.text.strip(),
                    )
            except requests.RequestException as exc:
                logger.warning(
                    "❌ Upload error for %s — request exception: %s",
                    item_id, exc,
                )

            if attempt < max_retries:
                backoff = retry_delay * (2 ** (attempt - 1))
                jitter = random.uniform(0, backoff * 0.5)
                wait = backoff + jitter
                logger.info("Retrying in %.2f seconds…", wait)
                time.sleep(wait)

        logger.error(
            "❌ Failed to upload poster for %s after %s attempts",
            item_id, max_retries,
        )
        return False

    def _verify_upload(self, item_id: str, timeout: int = 5) -> bool:
        """
        Confirm the new image is retrievable (checks first 256 bytes).
        """
        time.sleep(1)
        url = f"{self.jellyfin_url}/Items/{item_id}/Images/Primary"
        try:
            resp = requests.get(
                url,
                headers={"X-Emby-Token": self.api_key},
                timeout=timeout,
                stream=True,
            )
            if resp.status_code != 200:
                return False
            sig = next(resp.iter_content(256), b"")
            return (
                sig.startswith(b"\xff\xd8\xff") or  # JPEG
                sig.startswith(b"\x89PNG\r\n\x1a\n") or  # PNG
                sig.startswith(b"GIF")  # GIF
            )
        except Exception:
            return False

    def batch_upload_posters(
        self,
        item_to_path: dict[str, str | Path],
        max_retries: int = 3,
        retry_delay: int = 2,
    ) -> dict[str, bool]:
        """
        Upload many posters via Base64 body. Returns a dict of {item_id: success_bool}.
        """
        results: dict[str, bool] = {}
        total = len(item_to_path)
        logger.info("Starting batch upload of %s posters", total)

        for i, (item_id, pth) in enumerate(item_to_path.items(), start=1):
            logger.info("Processing %s/%s – %s", i, total, item_id)
            results[item_id] = self.upload_poster(item_id, pth, max_retries, retry_delay)

        ok = sum(results.values())
        logger.info("Batch upload complete: %s/%s successful", ok, total)
        return results


# ---------------------------------------------------------------------- #
#  CLI helper (optional convenience)
# ---------------------------------------------------------------------- #
if __name__ == "__main__":
    import argparse
    from aphrodite_helpers.check_jellyfin_connection import load_settings

    parser = argparse.ArgumentParser(description="Upload a poster to Jellyfin.")
    parser.add_argument("--itemid", required=True, help="Jellyfin item ID")
    parser.add_argument("--poster", required=True, help="Path to poster image")
    parser.add_argument("--retries", type=int, default=3, help="Max retry attempts")
    args = parser.parse_args()

    settings = load_settings()
    if not settings:
        sys.exit(1)

    jf = settings["api_keys"]["Jellyfin"][0]
    uploader = PosterUploader(jf["url"], jf["api_key"], jf.get("user_id"))

    success = uploader.upload_poster(args.itemid, args.poster, args.retries)
    sys.exit(0 if success else 1)
