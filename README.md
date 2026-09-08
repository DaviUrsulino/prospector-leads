# Prospector de Leads

MVP de uma plataforma de prospecção de leads B2B pro nicho de clínicas de saúde e
estética (dentistas, médicos, esteticistas, biomédicos): busca profissionais por
cidade e especialidade, mostra os resultados num dashboard e permite exportar em CSV.

Escopo do MVP (o resto — CRM, disparo de WhatsApp, agente de IA — fica pra depois):
busca por região/especialidade, dashboard de resultados, exportação CSV, histórico
de buscas salvas.

## Requisitos (resumo)

- **RF:** buscar leads por cidade + especialidade + quantidade alvo; listar e
  reabrir buscas anteriores; exportar leads de uma busca em CSV.
- **RNF:** chave da Places API nunca exposta no frontend; rate limit no endpoint de
  busca (10/min); dado de lead tratado como dado pessoal (LGPD), mesmo vindo de
  fonte pública.
- **Won't have (v1):** CRM/pipeline, disparo de WhatsApp, agente de IA, agendamento.

## Arquitetura

- `Busca` **contém** (composição) N `LeadEncontrado` — resultados de uma busca
  pertencem a ela; histórico é por execução de busca, não lead global deduplicado.
- Frontend (Next.js) → requer → Backend (FastAPI) → requer → Google Places API.
- Fluxo: form de busca → `POST /buscas` → backend consulta Places API (paginando
  até atingir a quantidade alvo) → salva no Postgres → frontend renderiza dashboard.

### ADR-001 — Fonte de dados dos leads

- **Contexto:** o sistema de referência (vídeo que motivou o projeto) faz scraping
  de Google Maps/Instagram/LinkedIn/Facebook. Isso viola Termos de Serviço dessas
  plataformas e é zona cinzenta de LGPD pra disparo em massa depois.
- **Decisão:** usar a Google Places API (oficial) como única fonte no MVP.
- **Consequência:** custo por request acima da cota grátis, e não cobre
  Instagram/LinkedIn — mas resultado estável, sem risco de bloqueio de conta/IP.
  Scraping como fonte complementar fica registrado como *should have* futuro, a
  avaliar risco antes de implementar.
- **Nota técnica:** a integração usa a **Places API (New)** — `POST
  places:searchText` com a chave no header `X-Goog-Api-Key` (não em query
  string) e um `X-Goog-FieldMask` explícito. Diferente da API legada, o Text
  Search da versão nova já retorna `internationalPhoneNumber` direto, sem
  chamada extra ao Place Details.

## Stack

Next.js + FastAPI + Postgres + Docker Compose — mesmo padrão validado no projeto
[podcasthub](../podcasthub), sem a peça de GPU/Modal (não se aplica aqui).

## Rodando localmente

```bash
docker compose up --build
```

- Frontend: http://localhost:3001
- Backend: http://localhost:8000 (docs em `/docs`)

Sem `GOOGLE_PLACES_API_KEY` configurada em `backend/.env`, o backend responde com
dados mockados (permite testar o fluxo completo antes de ter a chave real).

## Testes

```bash
cd backend
pip install -r requirements.txt
pytest
```
