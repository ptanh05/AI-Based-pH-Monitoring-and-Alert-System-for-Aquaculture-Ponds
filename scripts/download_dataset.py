"""
Dataset Verification & Download CLI for AI Aquaculture Guardian.

Validates the presence and SHA-256 cryptographic checksums of registered datasets.

Usage:
  python scripts/download_dataset.py --dataset mendeley_aquaculture
"""

import os
import sys
import argparse

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_pipeline.downloader import DatasetDownloader
from data_pipeline.dataset_registry import list_registered_datasets, DATASET_REGISTRY


def main():
    parser = argparse.ArgumentParser(description="Verify and download aquaculture datasets.")
    parser.add_argument("--dataset", type=str, default="all", help="Dataset name to verify or 'all'")
    args = parser.parse_args()

    downloader = DatasetDownloader()
    datasets = list_registered_datasets() if args.dataset == "all" else [args.dataset]

    print("=" * 80)
    print("  AI AQUACULTURE GUARDIAN — DATASET INTEGRITY & VERIFICATION")
    print("=" * 80)

    for name in datasets:
        print(f"\n[*] Checking dataset: '{name}'...")
        res = downloader.verify_local_dataset(name)
        if res.get("status") == "present":
            print(f"    [✓] Status: PRESENT & VALID")
            print(f"    Path:       {res['path']}")
            print(f"    SHA-256:    {res['sha256']}")
            print(f"    Size:       {res['size_bytes']:,} bytes")
            print(f"    DOI:        {res.get('doi', 'N/A')}")
            print(f"    License:    {res.get('license', 'N/A')}")
        elif res.get("status") == "missing":
            print(f"    [!] Status: MISSING LOCAL FILE")
            print(f"    Expected:   {res['expected_path']}")
            print(f"    Source URL: {res['source_url']}")
        else:
            print(f"    [!] Error:  {res.get('message')}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
