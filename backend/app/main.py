import asyncio
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import Base, engine
from app.routers.buscas import limiter, router as buscas_router
from app.services.auto_disparo import executar_disparo_diario


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
    # Dispara às 8:00 todo dia útil — a função espera offset aleatório de até 2h internamente
    scheduler.add_job(executar_disparo_diario, "cron", day_of_week="mon-fri", hour=8, minute=0)
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="Prospector de Leads", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(buscas_router)


@app.get("/health")
def health():
    return {"status": "ok"}
