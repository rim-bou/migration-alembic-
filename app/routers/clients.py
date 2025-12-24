from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud
from ..schemas import ClientCreate, ClientRead

router = APIRouter(prefix="/clients", tags=["clients"])

@router.get("", response_model=list[ClientRead])
def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return crud.list_clients(db, skip=skip, limit=limit)

@router.get("/{client_id}", response_model=ClientRead)
def get_client(client_id: int, db: Session = Depends(get_db)):
    obj = crud.get_client(db, client_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Client introuvable")
    return obj

@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(payload: ClientCreate, db: Session = Depends(get_db)):
    return crud.create_client(db, payload)

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_client(client_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_client(db, client_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Client introuvable")
    return None
