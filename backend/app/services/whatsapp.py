import asyncio
import re

import httpx

from app.config import settings

_TEMPLATE = [
    "Olá {nome}, bom dia ☀️ Tudo bem?",
    "Meu nome é Gerliane Fernandes, sou coordenadora do Viva Voz Podcast, aqui em Brasília. 📍",
    "Entrei em contato com o {nome} para apresentar o nosso podcast e estender um convite aos profissionais da clínica para participarem dos próximos episódios do Viva Voz Podcast.",
    "A proposta é realizar um bate-papo leve e descontraído com um dos profissionais da clínica, abordando temas relacionados à sua área de atuação, com o objetivo de compartilhar informações de valor com o público, esclarecer dúvidas frequentes e ampliar a visibilidade do trabalho desenvolvido pela clínica e seus especialistas.",
    "Posso te passar mais informações sobre a proposta?",
]


def _formatar_numero(numero: str) -> str:
    digitos = re.sub(r"\D", "", numero)
    if not digitos.startswith("55"):
        digitos = "55" + digitos
    return digitos


async def enviar_mensagens(numero: str, nome: str) -> None:
    if not settings.evolution_api_url or not settings.evolution_api_key:
        raise ValueError("Evolution API não configurada (EVOLUTION_API_URL / EVOLUTION_API_KEY)")

    numero_fmt = _formatar_numero(numero)
    headers = {"apikey": settings.evolution_api_key}
    url = f"{settings.evolution_api_url}/message/sendText/{settings.evolution_instance}"

    async with httpx.AsyncClient(timeout=60) as client:
        for i, template in enumerate(_TEMPLATE):
            texto = template.format(nome=nome)
            resp = await client.post(url, json={"number": numero_fmt, "text": texto}, headers=headers)
            resp.raise_for_status()
            if i < len(_TEMPLATE) - 1:
                await asyncio.sleep(2)
