from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Any
import numpy as np
import pandas as pd

@dataclass
class PreprocessArtifacts:
    feature_names: list[str]
    num_means: dict[str, float]
    num_stds: dict[str, float]
    cat_levels: dict[str, list[str]]

def _sanitize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # trim text
    for c in df.select_dtypes(include=["object"]).columns:
        df[c] = df[c].astype(str).str.strip()

    # anomalies -> NaN
    for col in ["nb_enfants", "quotient_caf", "loyer_mensuel"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df.loc[df[col] < 0, col] = np.nan

    return df

def fit_transform(df: pd.DataFrame, target_col: str):
    df = _sanitize(df)

    df = df[df[target_col].notna()].copy()
    y = df[target_col].astype(float).to_numpy()

    # drop identifiers and target
    drop_cols = [target_col, "id", "nom", "prenom"]
    Xdf = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")

    cat_cols = list(Xdf.select_dtypes(include=["object"]).columns)
    num_cols = [c for c in Xdf.columns if c not in cat_cols]

    # impute numeric
    for c in num_cols:
        Xdf[c] = pd.to_numeric(Xdf[c], errors="coerce")
        med = float(Xdf[c].median())
        Xdf[c] = Xdf[c].fillna(med)

    # impute categorical
    for c in cat_cols:
        Xdf[c] = Xdf[c].replace({"nan": np.nan, "None": np.nan}).fillna("inconnu")

    cat_levels = {c: sorted(Xdf[c].unique().tolist()) for c in cat_cols}

    # standardize numeric
    num_matrix = Xdf[num_cols].astype(float).to_numpy() if num_cols else np.zeros((len(Xdf), 0), dtype=float)
    num_means, num_stds = {}, {}
    feature_names = []
    if num_cols:
        means = num_matrix.mean(axis=0)
        stds = num_matrix.std(axis=0)
        stds = np.where(stds == 0, 1.0, stds)
        for i, c in enumerate(num_cols):
            num_means[c] = float(means[i])
            num_stds[c] = float(stds[i])
        num_matrix = (num_matrix - means) / stds
        feature_names.extend(num_cols)

    one_hots = []
    for c in cat_cols:
        for lvl in cat_levels[c]:
            one_hots.append((Xdf[c] == lvl).astype(float).to_numpy()[:, None])
            feature_names.append(f"{c}__{lvl}")

    X = num_matrix
    if one_hots:
        X = np.concatenate([num_matrix] + one_hots, axis=1)

    artifacts = PreprocessArtifacts(feature_names, num_means, num_stds, cat_levels)
    return X.astype(np.float32), y.astype(np.float32), artifacts

def save_artifacts(artifacts: PreprocessArtifacts, path: str):
    payload: dict[str, Any] = {
        "feature_names": artifacts.feature_names,
        "num_means": artifacts.num_means,
        "num_stds": artifacts.num_stds,
        "cat_levels": artifacts.cat_levels,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
