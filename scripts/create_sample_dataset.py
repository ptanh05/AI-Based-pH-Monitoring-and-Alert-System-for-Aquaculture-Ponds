"""
Generate a sample CSV dataset for pipeline testing and verification.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Fix Windows console UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.real_data_loader import RealDataLoader

def create_sample_dataset():
    loader = RealDataLoader()
    df = loader.load_iot_stream(physical_scale=True, max_rows=500)
    
    # Save a 200-row sample to data/samples/sample_aquaculture_data.csv
    sample_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "samples", "sample_aquaculture_data.csv")
    df.to_csv(sample_path, index=False)
    print(f"[✓] Created sample dataset: {sample_path} ({len(df)} rows)")

if __name__ == "__main__":
    create_sample_dataset()
