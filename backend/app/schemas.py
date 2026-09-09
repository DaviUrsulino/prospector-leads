import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BuscaCreate(BaseModel):
    cidade: str = Field(min_length=2, max_length=120)
    termos: list[str] = Field(min_length=1, max_length=20)
    quantidade_alvo: int = Field(gt=0, le=200)

    @field_validator("termos")
    @classmethod
    def valida_termos(cls, valor: list[str]) -> list[str]:
        limpos = [t.strip() for t in valor if t.strip()]
        if not limpos:
            raise ValueError("Informe ao menos uma especialidade")
        for termo in limpos:
            if not (2 <= len(termo) <= 80):
                raise ValueError("Cada especialidade deve ter entre 2 e 80 caracteres")
        return limpos


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
    website: str | None
    instagram: str | None
    linkedin: str | None
    facebook: str | None
    email: str | None
    whatsapp_direto: str | None
    fonte: str


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
