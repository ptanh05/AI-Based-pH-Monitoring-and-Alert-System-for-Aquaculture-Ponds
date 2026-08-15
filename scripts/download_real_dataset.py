"""
Download Script for Official Mendeley Real-World Aquaculture Dataset.

Dataset:
    "Environmental Parameters in Aquaculture: Temperature, pH, Oxygen, and Turbidity Measurements"
    Version: 2
    DOI: 10.17632/8s73jfvgr5.2
    URL: https://data.mendeley.com/datasets/8s73jfvgr5/2
    Authors: Rubén Baena-Navarro, Yulieth Carriazo-Regino, Francisco Torres-Hoyos
    Institution: Universidad de Córdoba, Montería, Colombia (2023–2024)
    License: CC BY 4.0

Downloads official files directly from Mendeley Data API and saves to data/real/.
"""

import os
import sys
import json
import urllib.request
import hashlib

# Fix Windows console UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DATASET_API_URL = "https://data.mendeley.com/api/datasets/8s73jfvgr5/files?version=2"
DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "real")
METADATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "metadata")


def download_dataset(force: bool = False) -> dict:
    """
    Download official files from Mendeley Data repository.

    Returns:
        Dictionary mapping filename -> local path.
    """
    os.makedirs(DATASET_DIR, exist_ok=True)
    os.makedirs(METADATA_DIR, exist_ok=True)

    print("=" * 70)
    print("  Downloading Official Real-World Aquaculture Dataset")
    print("  Mendeley Data DOI: 10.17632/8s73jfvgr5.2")
    print("  License: CC BY 4.0")
    print("=" * 70)

    # 1. Fetch file list from API
    req = urllib.request.Request(
        DATASET_API_URL,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        files_meta = json.loads(resp.read().decode("utf-8"))

    # Save raw metadata
    meta_path = os.path.join(METADATA_DIR, "mendeley_dataset_files_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(files_meta, f, indent=2, ensure_ascii=False)
    print(f"[✓] Saved metadata to: {meta_path}")

    downloaded_files = {}

    for f_info in files_meta:
        filename = f_info.get("filename")
        file_id = f_info.get("id")
        content_details = f_info.get("content_details", {})
        expected_size = content_details.get("size", f_info.get("size", 0))
        expected_sha256 = content_details.get("sha256_hash")
        download_url = content_details.get("download_url")

        if not download_url:
            download_url = f"https://data.mendeley.com/public-files/datasets/8s73jfvgr5/files/{file_id}/file_downloaded"

        local_path = os.path.join(DATASET_DIR, filename)

        # Check if already downloaded and valid
        if os.path.exists(local_path) and not force:
            actual_size = os.path.getsize(local_path)
            if actual_size == expected_size:
                print(f"[•] Already downloaded: {filename} ({actual_size:,} bytes)")
                downloaded_files[filename] = local_path
                continue

        print(f"[↓] Downloading: {filename} ({expected_size:,} bytes)...")
        file_req = urllib.request.Request(
            download_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )

        with urllib.request.urlopen(file_req, timeout=60) as resp:
            content = resp.read()

        with open(local_path, "wb") as f:
            f.write(content)

        # Verify hash
        actual_sha256 = hashlib.sha256(content).hexdigest()
        if expected_sha256 and actual_sha256.lower() != expected_sha256.lower():
            print(f"[!] Warning: SHA-256 mismatch for {filename}")
        else:
            print(f"[✓] Verified SHA-256: {filename}")

        downloaded_files[filename] = local_path

    print("=" * 70)
    print(f"  All {len(downloaded_files)} official dataset files are ready in: {DATASET_DIR}")
    print("=" * 70)
    return downloaded_files


if __name__ == "__main__":
    download_dataset()
