import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Especialidade(str, Enum):
    dentista = "dentista"
    medico = "medico"
    esteticista = "esteticista"
    biomedico = "biomedico"
    clinica_geral = "clinica_geral"


class BuscaCreate(BaseModel):
    cidade: str = Field(min_length=2, max_length=120)
    termo: Especialidade
    quantidade_alvo: int = Field(gt=0, le=200)


class LeadEncontradoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    telefone: str | None
    endereco: str | None
    especialidade: str
    place_id: str | None
    link_perfil: str | None
    favorito: bool


class BuscaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cidade: str
    termo: str
    quantidade_alvo: int
    criada_em: datetime


class BuscaComLeadsOut(BuscaOut):
    leads: list[LeadEncontradoOut] = []


class EstatisticasOut(BaseModel):
    total_buscas: int
    total_leads: int
    pct_leads_com_telefone: float
    total_favoritos: int
    ultimas_buscas: list[BuscaOut]
