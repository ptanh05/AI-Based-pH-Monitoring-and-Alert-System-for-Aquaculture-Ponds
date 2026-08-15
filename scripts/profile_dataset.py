"""
Comprehensive Dataset Profiling & Quality Audit Script.

Analyzes distributions, missing values, physical validity, statistical outliers,
and sampling regularity. Generates DATA_QUALITY_REPORT.md and JSON artifacts.

Usage:
  python scripts/profile_dataset.py --dataset mendeley_aquaculture
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
from datetime import datetime

# Fix Windows console UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_pipeline.dataset_loader import DatasetLoader
from data_pipeline.dataset_validator import DatasetValidator


def profile_dataset(dataset_name: str = "mendeley_aquaculture", output_report: str = "DATA_QUALITY_REPORT.md"):
    print("=" * 80)
    print("  AI AQUACULTURE GUARDIAN — DATASET PROFILING & QUALITY AUDIT")
    print(f"  Target: {dataset_name}")
    print("=" * 80)

    loader = DatasetLoader()
    df, meta = loader.load(dataset_name, physical_scale=True)
    validator = DatasetValidator()
    val_report = validator.validate(df, dataset_name=meta.name)

    # Statistical profiling
    numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in ["month", "day", "hour"]]
    stats = {}

    for c in numeric_cols:
        series = df[c].dropna()
        q25, q75 = np.percentile(series, [25, 75])
        iqr = q75 - q25
        low_bound = q25 - 3.0 * iqr
        high_bound = q75 + 3.0 * iqr
        outlier_count = int(((series < low_bound) | (series > high_bound)).sum())

        stats[c] = {
            "count": int(len(series)),
            "missing_pct": round(float(df[c].isna().mean() * 100.0), 2),
            "mean": round(float(series.mean()), 4),
            "std": round(float(series.std()), 4),
            "min": round(float(series.min()), 4),
            "q25": round(float(q25), 4),
            "median": round(float(series.median()), 4),
            "q75": round(float(q75), 4),
            "max": round(float(series.max()), 4),
            "outliers_3iqr": outlier_count,
            "outliers_3iqr_pct": round(float(outlier_count / len(series) * 100.0), 2),
        }

    # Time coverage
    time_start = df["timestamp"].min().isoformat() if "timestamp" in df.columns else "N/A"
    time_end = df["timestamp"].max().isoformat() if "timestamp" in df.columns else "N/A"
    total_duration_days = (df["timestamp"].max() - df["timestamp"].min()).total_seconds() / 86400.0 if "timestamp" in df.columns else 0.0

    profile_data = {
        "dataset_name": meta.name,
        "source": meta.source,
        "doi": meta.doi,
        "license": meta.license,
        "audited_at": datetime.now().isoformat(),
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "time_coverage": {
            "start": time_start,
            "end": time_end,
            "duration_days": round(total_duration_days, 1),
            "sampling_interval_seconds": val_report.estimated_sampling_interval_seconds,
            "sampling_interval_minutes": val_report.estimated_sampling_interval_seconds / 60.0,
        },
        "validation_summary": {
            "is_valid_for_training": val_report.is_valid_for_training,
            "duplicate_timestamps": val_report.duplicate_timestamps,
            "physical_violations": val_report.physical_violations_by_col,
            "issues": val_report.issues,
        },
        "feature_statistics": stats,
    }

    # Save JSON artifact
    os.makedirs("artifacts/reports", exist_ok=True)
    json_path = "artifacts/reports/data_quality_profile.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2, ensure_ascii=False)
    print(f"\n[✓] Saved profile JSON: {json_path}")

    # Generate Markdown Report
    _write_markdown_report(profile_data, output_report)
    print(f"[✓] Saved quality report: {output_report}")
    print("=" * 80)
    return profile_data


def _write_markdown_report(data: dict, out_file: str):
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"# Data Quality & Statistical Profile Report\n\n")
        f.write(f"**Dataset Name**: `{data['dataset_name']}`  \n")
        f.write(f"**Provenance / Source**: {data['source']} ({data.get('doi', 'N/A')})  \n")
        f.write(f"**License**: {data['license']}  \n")
        f.write(f"**Audited Timestamp**: {data['audited_at']}  \n\n")
        f.write("---\n\n")
        f.write("## 1. Executive Summary\n\n")
        f.write(f"- **Total Rows**: {data['total_rows']:,}\n")
        f.write(f"- **Total Features**: {data['total_columns']}\n")
        f.write(f"- **Time Coverage**: {data['time_coverage']['start']} to {data['time_coverage']['end']} ({data['time_coverage']['duration_days']} days)\n")
        f.write(f"- **Estimated Sampling Interval**: {data['time_coverage']['sampling_interval_seconds']:.0f}s ({data['time_coverage']['sampling_interval_minutes']:.1f} min)\n")
        f.write(f"- **Duplicate Timestamps**: {data['validation_summary']['duplicate_timestamps']}\n")
        f.write(f"- **Training Validity**: {'VALID ✓' if data['validation_summary']['is_valid_for_training'] else 'INVALID ✗'}\n\n")

        f.write("## 2. Statistical Distribution by Monitored Variable\n\n")
        f.write("| Variable | Missing % | Mean ± Std | Min | Median | Max | Outliers (3×IQR) |\n")
        f.write("|---|:---:|:---:|:---:|:---:|:---:|:---:|\n")
        for col, s in data["feature_statistics"].items():
            f.write(f"| **`{col}`** | {s['missing_pct']}% | {s['mean']:.2f} ± {s['std']:.2f} | {s['min']:.2f} | {s['median']:.2f} | {s['max']:.2f} | {s['outliers_3iqr']} ({s['outliers_3iqr_pct']}%) |\n")

        f.write("\n## 3. Physical Boundary Verification\n\n")
        f.write("| Parameter | Expected Physical Window | Violations Count | Status |\n")
        f.write("|---|:---:|:---:|:---:|\n")
        for col, v_cnt in data["validation_summary"]["physical_violations"].items():
            f.write(f"| `{col}` | Standard Aquaculture Range | {v_cnt} | {'PASSED ✓' if v_cnt == 0 else 'VIOLATIONS DETECTED'} |\n")

        f.write("\n## 4. Anomaly Classification & Provenance Protocol\n\n")
        f.write("All sensor fluctuations are classified into:\n")
        f.write("1. **Legitimate Environmental Dynamics**: Diurnal solar-photosynthetic rise in DO and pH during afternoon peak hours.\n")
        f.write("2. **Hardware Faults**: Flatline readings (variance = 0 for > 15 readings) and rate-of-change jumps exceeding physical kinetics (> 0.5 pH / 5 min).\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="mendeley_aquaculture")
    parser.add_argument("--output", type=str, default="DATA_QUALITY_REPORT.md")
    args = parser.parse_args()
    profile_dataset(args.dataset, args.output)
