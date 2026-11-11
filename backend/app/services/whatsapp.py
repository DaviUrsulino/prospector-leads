import asyncio
import random
import re
from datetime import datetime, timezone

import httpx

from app.config import settings

# Cada item vira uma mensagem separada (simula digitação humana)
_BLOCOS = [
    "Olá {nome}, {saudacao}!",
    "Meu nome é Gerliane Fernandes, sou coordenadora do Viva Voz Podcast, aqui em Brasília. 📍",
    "Entrei em contato para apresentar o nosso podcast e convidar os profissionais aí para participarem dos próximos episódios.",
    "A proposta é um bate-papo leve sobre a área de atuação de vocês — compartilhando informações de valor com o público e ampliando a visibilidade do trabalho desenvolvido.",
    "Posso te passar mais detalhes sobre a proposta?",
]

_SAUDACAO = {
    range(5, 12): "bom dia ☀️",
    range(12, 18): "boa tarde 🌤",
    range(18, 24): "boa noite 🌙",
}


def _saudacao() -> str:
    hora = datetime.now(timezone.utc).astimezone().hour
    for intervalo, texto in _SAUDACAO.items():
        if hora in intervalo:
            return texto
    return "olá"


def _formatar_numero(numero: str) -> str:
    digitos = re.sub(r"\D", "", numero)
    if not digitos.startswith("55"):
        digitos = "55" + digitos
    return digitos


async def _enviar_texto(numero_fmt: str, texto: str) -> None:
    url = f"{settings.evolution_api_url}/message/sendText/{settings.evolution_instance}"
    headers = {"apikey": settings.evolution_api_key, "Content-Type": "application/json"}
    payload = {"number": numero_fmt, "text": texto}
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()


async def enviar_mensagens(numero: str, nome: str) -> None:
    if not settings.evolution_api_key:
        raise ValueError("EVOLUTION_API_KEY não configurada")

    numero_fmt = _formatar_numero(numero)
    saudacao = _saudacao()

    for i, bloco in enumerate(_BLOCOS):
        texto = bloco.format(nome=nome, saudacao=saudacao)
        await _enviar_texto(numero_fmt, texto)
        if i < len(_BLOCOS) - 1:
            await asyncio.sleep(random.uniform(6, 9))
