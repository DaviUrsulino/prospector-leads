import re
from datetime import datetime, timezone

import httpx

from app.config import settings

_TEMPLATE = (
    "Olá {nome}, tudo bem?\n\n"
    "Meu nome é Gerliane Fernandes, sou coordenadora do Viva Voz Podcast, aqui em Brasília. 📍\n\n"
    "Entrei em contato para apresentar o nosso podcast e convidar os profissionais aí para participarem dos próximos episódios.\n\n"
    "A proposta é um bate-papo leve sobre a área de atuação de vocês — compartilhando informações de valor com o público e ampliando a visibilidade do trabalho desenvolvido.\n\n"
    "Posso te passar mais detalhes sobre a proposta?"
)

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


async def enviar_mensagens(numero: str, nome: str) -> None:
    if not settings.whatsapp_phone_number_id or not settings.whatsapp_access_token:
        raise ValueError("Meta WhatsApp API não configurada (WHATSAPP_PHONE_NUMBER_ID / WHATSAPP_ACCESS_TOKEN)")

    numero_fmt = _formatar_numero(numero)
    texto = f"Olá {nome}, {_saudacao()}!\n\n" + _TEMPLATE.format(nome=nome).split("\n\n", 1)[1]

    url = f"https://graph.facebook.com/v21.0/{settings.whatsapp_phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": numero_fmt,
        "type": "text",
        "text": {"body": texto},
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
