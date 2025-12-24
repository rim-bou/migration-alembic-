from __future__ import annotations
from sqlalchemy import Integer, Float, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    nom: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    prenom: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)

    taille: Mapped[float | None] = mapped_column(Float, nullable=True)
    poids: Mapped[float | None] = mapped_column(Float, nullable=True)

    sexe: Mapped[str] = mapped_column(String(20), nullable=False)
    sport_licence: Mapped[str] = mapped_column(String(10), nullable=False)
    niveau_etude: Mapped[str] = mapped_column(String(50), nullable=False)
    region: Mapped[str] = mapped_column(String(80), nullable=False)

    smoker: Mapped[str] = mapped_column(String(10), nullable=False)
    nationalite_francaise: Mapped[str] = mapped_column(String(10), nullable=False)

    nb_enfants: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quotient_caf: Mapped[float | None] = mapped_column(Float, nullable=True)

    revenu_estime_mois: Mapped[int] = mapped_column(Integer, nullable=False)
    situation_familiale: Mapped[str | None] = mapped_column(String(50), nullable=True)

    historique_credits: Mapped[float | None] = mapped_column(Float, nullable=True)
    risque_personnel: Mapped[float] = mapped_column(Float, nullable=False)

    date_creation_compte: Mapped[str] = mapped_column(String(25), nullable=False)

    score_credit: Mapped[float | None] = mapped_column(Float, nullable=True)
    loyer_mensuel: Mapped[float | None] = mapped_column(Float, nullable=True)
    montant_pret: Mapped[float | None] = mapped_column(Float, nullable=True)

    sensitive: Mapped["ClientSensitive | None"] = relationship(
        back_populates="client", uselist=False, cascade="all, delete-orphan"
    )

class ClientSensitive(Base):
    __tablename__ = "client_sensitive"
    __table_args__ = (UniqueConstraint("client_id", name="uq_client_sensitive_client_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)

    # Donnee sensible -> stockage separe (non expose via API)
    orientation_sexuelle: Mapped[str | None] = mapped_column(String(50), nullable=True)

    client: Mapped[Client] = relationship(back_populates="sensitive")
