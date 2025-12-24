from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class ClientCreate(BaseModel):
    nom: str
    prenom: str
    age: int = Field(..., ge=0, le=120)

    taille: Optional[float] = None
    poids: Optional[float] = None

    sexe: str
    sport_licence: str
    niveau_etude: str
    region: str

    smoker: str
    nationalite_francaise: str

    # nouveaux champs (option 2)
    nb_enfants: Optional[int] = Field(None, ge=0)
    quotient_caf: Optional[float] = Field(None, ge=0)

    revenu_estime_mois: int = Field(..., ge=0)
    situation_familiale: Optional[str] = None

    historique_credits: Optional[float] = None
    risque_personnel: float = Field(..., ge=0.0, le=1.0)

    date_creation_compte: str

    score_credit: Optional[float] = None
    loyer_mensuel: Optional[float] = None
    montant_pret: Optional[float] = None

class ClientRead(ClientCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int

class TrainResponse(BaseModel):
    status: str
    n_rows_used: int
    metrics: dict
    artifacts: dict
