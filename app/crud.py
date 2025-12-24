from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import Client
from .schemas import ClientCreate

def list_clients(db: Session, skip: int = 0, limit: int = 50):
    stmt = select(Client).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())

def get_client(db: Session, client_id: int):
    return db.get(Client, client_id)

def create_client(db: Session, payload: ClientCreate):
    obj = Client(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def delete_client(db: Session, client_id: int) -> bool:
    obj = db.get(Client, client_id)
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    return True
