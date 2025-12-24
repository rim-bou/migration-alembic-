from __future__ import annotations
import json, os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

from ..database import SessionLocal
from ..models import Client
from .preprocessing import fit_transform, save_artifacts

ARTIFACTS_DIR = Path(os.getenv("FASTIA_ARTIFACTS_DIR", "artifacts"))
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
TARGET_COL = "score_credit"

class MLP(torch.nn.Module):
    def __init__(self, in_dim: int):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(in_dim, 64),
            torch.nn.ReLU(),
            torch.nn.Linear(64, 32),
            torch.nn.ReLU(),
            torch.nn.Linear(32, 1),
        )
    def forward(self, x):
        return self.net(x).squeeze(-1)

def _fetch_df():
    db = SessionLocal()
    try:
        rows = db.query(Client).all()
        if not rows:
            return pd.DataFrame()
        data = []
        for r in rows:
            d = r.__dict__.copy()
            d.pop("_sa_instance_state", None)
            data.append(d)
        return pd.DataFrame(data)
    finally:
        db.close()

def train_from_db(epochs: int = 25, lr: float = 1e-3, batch_size: int = 256):
    df = _fetch_df()
    if df.empty:
        return {"status":"error","n_rows_used":0,"metrics":{"error":"Base vide. Ingerer data-all.csv"},"artifacts":{}}

    X, y, prep = fit_transform(df, TARGET_COL)
    n = len(y)
    if n < 50:
        return {"status":"error","n_rows_used":int(n),"metrics":{"error":"Pas assez de lignes avec score_credit"},"artifacts":{}}

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = MLP(X.shape[1]).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = torch.nn.MSELoss()

    def batches(Xa, ya):
        idx = np.arange(len(ya))
        np.random.shuffle(idx)
        for i in range(0, len(idx), batch_size):
            j = idx[i:i+batch_size]
            yield Xa[j], ya[j]

    train_losses, val_losses = [], []
    X_val_t = torch.tensor(X_val, device=device)
    y_val_t = torch.tensor(y_val, device=device)

    for _ in range(epochs):
        model.train()
        bl = []
        for xb, yb in batches(X_train, y_train):
            xb_t = torch.tensor(xb, device=device)
            yb_t = torch.tensor(yb, device=device)
            pred = model(xb_t)
            loss = loss_fn(pred, yb_t)
            opt.zero_grad()
            loss.backward()
            opt.step()
            bl.append(float(loss.detach().cpu().numpy()))
        train_losses.append(float(np.mean(bl)))

        model.eval()
        with torch.no_grad():
            vpred = model(X_val_t)
            val_losses.append(float(loss_fn(vpred, y_val_t).detach().cpu().numpy()))

    model.eval()
    with torch.no_grad():
        val_pred = model(X_val_t).detach().cpu().numpy()

    mae = float(mean_absolute_error(y_val, val_pred))
    rmse = float(np.sqrt(mean_squared_error(y_val, val_pred)))

    loss_path = ARTIFACTS_DIR / "loss_curve.png"
    model_path = ARTIFACTS_DIR / "model.pt"
    prep_path = ARTIFACTS_DIR / "preprocessing.json"
    metrics_path = ARTIFACTS_DIR / "metrics.json"

    plt.figure()
    plt.plot(train_losses, label="train")
    plt.plot(val_losses, label="val")
    plt.xlabel("epoch")
    plt.ylabel("MSE loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(loss_path)
    plt.close()

    torch.save(model.state_dict(), model_path)
    save_artifacts(prep, str(prep_path))

    metrics = {"MAE": mae, "RMSE": rmse, "epochs": epochs, "device": device, "n_features": int(X.shape[1])}
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    return {"status":"ok","n_rows_used":int(n),"metrics":metrics,"artifacts":{
        "loss_curve": str(loss_path),
        "model": str(model_path),
        "preprocessing": str(prep_path),
        "metrics": str(metrics_path),
    }}
