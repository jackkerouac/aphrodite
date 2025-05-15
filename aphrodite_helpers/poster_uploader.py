#!/usr/bin/env python3
# aphrodite_helpers/poster_uploader.py  •  stateless edition

import os
import sys
import time
import random
import logging
import requests
from pathlib import Path

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("poster_uploader")


class PosterUploader:
    """
    Handles uploading modified posters back to Jellyfin.

    Features retained:
    • Built-in retry mechanism with exponential back-off + jitter
    • Upload verification by re-downloading the poster
    • Batch-mode helper

    State/workflow integration has been **completely removed**.
    """

    def __init__(self, jellyfin_url: str, api_key: str, user_id: str | None = None):
        self.jellyfin_url = jellyfin_url.rstrip("/")
        self.api_key = api_key
        self.user_id = user_id

    # --------------------------------------------------------------------- #
    #  SINGLE-ITEM UPLOAD
    # --------------------------------------------------------------------- #
    def upload_poster(
        self,
        item_id: str,
        poster_path: str | Path,
        max_retries: int = 3,
        retry_delay: int = 2,
    ) -> bool:
        """
        Upload a poster to Jellyfin for a specific item.

        Returns True on success, False on failure.
        """

        poster_path = Path(poster_path)

        if not poster_path.exists():
            logger.error("Poster file not found: %s", poster_path)
            return False

        upload_url = f"{self.jellyfin_url}/Items/{item_id}/Images/Primary"
        headers = {"X-Emby-Token": self.api_key}
        attempts = 0
        last_error = None

        while attempts < max_retries:
            attempts += 1
            try:
                with poster_path.open("rb") as f:
                    image_data = f.read()

                logger.info(
                    "Uploading poster for item %s (attempt %s/%s)",
                    item_id,
                    attempts,
                    max_retries,
                )
                resp = requests.post(upload_url, headers=headers, data=image_data, timeout=30)

                if resp.status_code in (200, 204):
                    logger.info("✅ Successfully uploaded poster for %s", item_id)
                    if self._verify_upload(item_id):
                        logger.info("✅ Verified upload for %s", item_id)
                        return True
                    logger.warning("❌ Verification failed for %s — will retry", item_id)
                    last_error = "verification failed"
                else:
                    last_error = f"HTTP {resp.status_code}: {resp.text}"
                    logger.warning("❌ Upload error for %s — %s", item_id, last_error)

            except requests.exceptions.RequestException as e:
                last_error = f"request error: {e}"
                logger.warning("❌ Upload error for %s — %s", item_id, last_error)
            except Exception as e:  # noqa: BLE001
                last_error = f"unexpected error: {e}"
                logger.warning("❌ Upload error for %s — %s", item_id, last_error)

            # back-off before next retry
            if attempts < max_retries:
                backoff = retry_delay * (2 ** (attempts - 1))
                jitter = random.uniform(0, 0.5 * backoff)
                wait = backoff + jitter
                logger.info("Retrying in %.2f s…", wait)
                time.sleep(wait)

        logger.error(
            "❌ Failed to upload poster for %s after %s attempts (%s)", item_id, max_retries, last_error
        )
        return False

    # --------------------------------------------------------------------- #
    #  VERIFY
    # --------------------------------------------------------------------- #
    def _verify_upload(self, item_id: str, timeout: int = 5) -> bool:
        """
        Confirm that Jellyfin accepted the new image by downloading a few bytes.
        """
        time.sleep(1)  # allow Jellyfin to process the upload
        url = f"{self.jellyfin_url}/Items/{item_id}/Images/Primary"
        headers = {"X-Emby-Token": self.api_key}

        try:
            resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
            if resp.status_code != 200:
                return False

            first_chunk = next(resp.iter_content(256), b"")
            # JPEG, PNG, GIF signatures
            return first_chunk.startswith(b"\xff\xd8\xff") or \
                   first_chunk.startswith(b"\x89PNG\r\n\x1a\n") or \
                   first_chunk.startswith(b"GIF")
        except Exception:  # noqa: BLE001
            return False

    # --------------------------------------------------------------------- #
    #  BATCH
    # --------------------------------------------------------------------- #
    def batch_upload_posters(
        self,
        item_to_path: dict[str, str | Path],
        max_retries: int = 3,
        retry_delay: int = 2,
    ) -> dict[str, bool]:
        """
        Upload multiple posters.  Returns a dict {item_id: success_bool}.
        """
        results: dict[str, bool] = {}
        total = len(item_to_path)
        logger.info("Starting batch upload of %s posters", total)

        for idx, (item_id, pth) in enumerate(item_to_path.items(), 1):
            logger.info("Processing %s/%s – %s", idx, total, item_id)
            results[item_id] = self.upload_poster(item_id, pth, max_retries, retry_delay)

        ok = sum(results.values())
        logger.info("Batch complete: %s/%s successful", ok, total)
        return results


# ------------------------------------------------------------------------- #
#  CLI helper (unchanged)
# ------------------------------------------------------------------------- #
if __name__ == "__main__":
    import argparse
    from aphrodite_helpers.check_jellyfin_connection import load_settings

    parser = argparse.ArgumentParser(description="Upload a poster to Jellyfin.")
    parser.add_argument("--itemid", required=True, help="Jellyfin item ID")
    parser.add_argument("--poster", required=True, help="Path to poster PNG/JPG")
    parser.add_argument("--retries", type=int, default=3, help="Max retries")

    args = parser.parse_args()

    settings = load_settings()
    if not settings:
        sys.exit(1)

    jf = settings["api_keys"]["Jellyfin"][0]
    uploader = PosterUploader(jf["url"], jf["api_key"], jf.get("user_id"))

    sys.exit(0 if uploader.upload_poster(args.itemid, args.poster, args.retries) else 1)
