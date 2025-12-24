"""Optionnel: cree la base a partir des modeles actuels.
Si vous venez du projet 1, vous avez deja une base; vous pouvez ignorer ce script.

Usage:
    python -m scripts.bootstrap_db
"""
from app.database import engine
from app.models import Base

def main():
    Base.metadata.create_all(bind=engine)
    print("OK: base creee (tables selon models.py)")

if __name__ == "__main__":
    main()
