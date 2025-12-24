"""Analyse rapide de data-all.csv (missing + anomalies).

Usage:
    python -m scripts.analyze_data_all
"""
from pathlib import Path
import pandas as pd
import numpy as np

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "data-all.csv"

def main():
    df = pd.read_csv(DATA_PATH)
    print("Shape:", df.shape)

    miss = (df.isna().mean() * 100).sort_values(ascending=False)
    print("\nTop missing (%):")
    print(miss.head(10).round(2).to_string())

    # anomalies
    for col in ["nb_enfants", "quotient_caf", "loyer_mensuel"]:
        if col in df.columns:
            s = pd.to_numeric(df[col], errors="coerce")
            print(f"Anomalies {col} < 0:", int((s < 0).sum()))

if __name__ == "__main__":
    main()
