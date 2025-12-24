"""Ingestion de data-all.csv dans la base + table sensible.

- Inserer les colonnes dans clients (y compris nb_enfants, quotient_caf)
- Inserer orientation_sexuelle dans client_sensitive

Usage:
    python -m scripts.ingest_data_all
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np

from app.database import SessionLocal, engine
from app.models import Client, ClientSensitive

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "data-all.csv"

EXPECTED_CLIENT_COLS = [
    "nom","prenom","age","taille","poids","sexe","sport_licence","niveau_etude","region",
    "smoker","nationalite_francaise","nb_enfants","quotient_caf",
    "revenu_estime_mois","situation_familiale","historique_credits","risque_personnel",
    "date_creation_compte","score_credit","loyer_mensuel","montant_pret"
]

def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    if "nationalité_francaise" in df.columns and "nationalite_francaise" not in df.columns:
        df = df.rename(columns={"nationalité_francaise": "nationalite_francaise"})

    # trim text
    for c in df.select_dtypes(include=["object"]).columns:
        df[c] = df[c].astype(str).str.strip()

    # numeric conversion
    num_cols = ["age","taille","poids","nb_enfants","quotient_caf","revenu_estime_mois",
                "historique_credits","risque_personnel","score_credit","loyer_mensuel","montant_pret"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # anomalies -> NaN
    for c in ["nb_enfants","quotient_caf","loyer_mensuel"]:
        if c in df.columns:
            df.loc[df[c] < 0, c] = np.nan

    return df

def main():
    df = pd.read_csv(DATA_PATH)
    df = _normalize(df)

    # split sensitive
    if "orientation_sexuelle" in df.columns:
        sens = df[["orientation_sexuelle"]].copy()
    else:
        sens = pd.DataFrame({"orientation_sexuelle": [None]*len(df)})

    # keep only expected client cols
    df_clients = df[[c for c in EXPECTED_CLIENT_COLS if c in df.columns]].copy()

    # Fill required non-null fields to avoid ORM errors
    # (dataset should already be complete, but on securise)
    df_clients["nom"] = df_clients["nom"].fillna("UNKNOWN")
    df_clients["prenom"] = df_clients["prenom"].fillna("UNKNOWN")
    df_clients["sexe"] = df_clients["sexe"].fillna("U")
    df_clients["sport_licence"] = df_clients["sport_licence"].fillna("non")
    df_clients["niveau_etude"] = df_clients["niveau_etude"].fillna("inconnu")
    df_clients["region"] = df_clients["region"].fillna("inconnu")
    df_clients["smoker"] = df_clients["smoker"].fillna("non")
    df_clients["nationalite_francaise"] = df_clients["nationalite_francaise"].fillna("non")
    df_clients["age"] = df_clients["age"].fillna(df_clients["age"].median()).astype(int)
    df_clients["revenu_estime_mois"] = df_clients["revenu_estime_mois"].fillna(df_clients["revenu_estime_mois"].median()).astype(int)
    df_clients["risque_personnel"] = df_clients["risque_personnel"].fillna(df_clients["risque_personnel"].median())
    df_clients["date_creation_compte"] = df_clients["date_creation_compte"].fillna("1970-01-01")

    db = SessionLocal()
    try:
        # bulk insert clients
        clients = []
        for row in df_clients.to_dict(orient="records"):
            clients.append(Client(**row))
        db.bulk_save_objects(clients)
        db.commit()

        # Need client ids after commit -> requery in same order by rowid
        # In SQLite, after bulk_save_objects, ids may not be populated.
        # So we fetch all clients inserted and zip in insertion order (best effort).
        inserted = db.query(Client).order_by(Client.id).all()[-len(df_clients):]

        sens_records = []
        for client_obj, orientation in zip(inserted, sens["orientation_sexuelle"].tolist()):
            # store but do not expose; keep None for 'nan'
            if isinstance(orientation, str) and orientation.lower() in {"nan","none",""}:
                orientation = None
            sens_records.append(ClientSensitive(client_id=client_obj.id, orientation_sexuelle=orientation))
        db.bulk_save_objects(sens_records)
        db.commit()

        print(f"OK: {len(df_clients)} clients inseres + {len(sens_records)} lignes sensibles")
    finally:
        db.close()

if __name__ == "__main__":
    main()
