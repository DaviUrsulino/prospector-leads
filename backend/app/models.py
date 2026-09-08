import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


def _new_uuid() -> str:
    return str(uuid.uuid4())


class Busca(Base):
    __tablename__ = "buscas"

    id = Column(String(36), primary_key=True, default=_new_uuid)
    cidade = Column(String, nullable=False)
    termo = Column(String, nullable=False)
    quantidade_alvo = Column(Integer, nullable=False)
    criada_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    leads = relationship(
        "LeadEncontrado", back_populates="busca", cascade="all, delete-orphan"
    )


class LeadEncontrado(Base):
    __tablename__ = "leads_encontrados"

    id = Column(String(36), primary_key=True, default=_new_uuid)
    busca_id = Column(String(36), ForeignKey("buscas.id"), nullable=False)
    nome = Column(String, nullable=False)
    telefone = Column(String, nullable=True)
    endereco = Column(String, nullable=True)
    especialidade = Column(String, nullable=False)
    place_id = Column(String, nullable=True)
    link_perfil = Column(String, nullable=True)
    favorito = Column(Boolean, nullable=False, default=False)

    busca = relationship("Busca", back_populates="leads")
